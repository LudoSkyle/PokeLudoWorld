package fr.skyle.pokeludoworld.scripts.core

import fr.skyle.pokeludoworld.scripts.autoload.Globals
import fr.skyle.pokeludoworld.scripts.gameplay.characters.CharacterMovement
import fr.skyle.pokeludoworld.scripts.gameplay.characters.PlayerCamera
import fr.skyle.pokeludoworld.scripts.gameplay.characters.PlayerInput
import fr.skyle.pokeludoworld.scripts.gameplay.levels.SceneTrigger
import fr.skyle.pokeludoworld.scripts.log.Logger
import fr.skyle.pokeludoworld.scripts.ui.LocationBanner
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.ColorRect
import godot.api.Node
import godot.api.Node2D
import godot.api.PackedScene
import godot.api.ResourceLoader
import godot.core.Color
import godot.core.Vector2
import kotlin.math.min

private enum class Phase { IDLE, FADE_OUT, FADE_IN }

/**
 * Charge et remplace les niveaux. **Le joueur n'appartient à aucun niveau** :
 * il est instancié une fois ici et reparenté dans le `World/Entities` de la
 * carte courante, ce qui préserve son tri Y tout en gardant son état d'une
 * carte à l'autre.
 */
@Script
class SceneManager : Node() {

	companion object {
		var instance: SceneManager? = null
			private set

		/** Métadonnée de la racine d'une carte : le nom affiché par le bandeau. */
		private const val LOCATION_META = "location"

		/** Métadonnée de la racine d'une carte : le bandeau qui porte ce nom. */
		private const val BANNER_META = "banner"
	}

	@Category("Scenes")
	@Export
	var startScene: String = "res://src/main/kotlin/fr/skyle/pokeludoworld/scenes/levels/start_town.tscn"

	@Export
	var playerScene: String = "res://src/main/kotlin/fr/skyle/pokeludoworld/scenes/characters/player.tscn"

	@Category("Transition")
	@Export
	var fadeSeconds: Double = 0.25

	/** Reprendre la sauvegarde au lancement, s'il y en a une. Les tests s'en passent. */
	@Category("Sauvegarde")
	@Export
	var loadSave: Boolean = true

	/** Temps de jeu total de la partie, en secondes. */
	var playSeconds: Double = 0.0
		private set

	/** Nom du lieu où l'on se trouve, en français. */
	var location: String = ""
		private set

	private var banner = ""
	private var currentScene = ""
	private var restore: SaveGame.State? = null

	private var levelHost: Node? = null
	private var fade: ColorRect? = null
	private var level: Node2D? = null
	private var player: Node2D? = null

	private var phase = Phase.IDLE
	private var progress = 0.0
	private var pendingScene = ""
	private var pendingDoor = ""
	private var bootstrapped = false

	/** Vrai pendant tout le fondu : le joueur ne doit pas bouger. */
	val isChanging: Boolean
		get() = phase != Phase.IDLE

	@Register
	override fun _ready() {
		instance = this
		levelHost = getParent()

		if (hasNode("../Fade/Rect")) fade = getNode("../Fade/Rect") as? ColorRect
		setFadeAlpha(0.0)

		player = (ResourceLoader.load(playerScene) as? PackedScene)?.instantiate() as? Node2D

		pendingScene = startScene
		pendingDoor = ""

		// Une partie sauvegardée reprend là où elle s'est arrêtée.
		playSeconds = 0.0
		restore = if (loadSave) SaveGame.read() else null
		restore?.let {
			if (ResourceLoader.exists(it.scene)) {
				pendingScene = it.scene
				playSeconds = it.seconds
			} else {
				Logger.e("Sauvegarde ignoree, carte introuvable : ${it.scene}")
				restore = null
			}
		}
		// Le premier chargement attend la frame suivante : pendant `_ready` le
		// parent construit encore ses enfants et refuse un `add_child`.

		Logger.i("Loading scene manager ...")
	}

	@Register
	override fun _process(delta: Double) {
		// Comme dans les jeux d'origine, le temps de jeu tourne aussi dans les menus.
		playSeconds += delta

		if (!bootstrapped) {
			bootstrapped = true
			swap()
			return
		}

		if (phase == Phase.IDLE) return

		progress += if (fadeSeconds > 0.0) delta / fadeSeconds else 1.0
		val t = min(progress, 1.0)

		if (phase == Phase.FADE_OUT) {
			setFadeAlpha(t)
			if (t >= 1.0) {
				swap()
				progress = 0.0
				phase = Phase.FADE_IN
			}
		} else {
			setFadeAlpha(1.0 - t)
			if (t >= 1.0) phase = Phase.IDLE
		}
	}

	/** Demande un changement de carte. Ignoré si un fondu est déjà en cours. */
	fun changeLevel(scenePath: String, door: String) {
		if (isChanging) return

		pendingScene = scenePath
		pendingDoor = door
		progress = 0.0
		phase = Phase.FADE_OUT

		Logger.i("Changing level to $scenePath (door=$door)")
	}

	private fun swap() {
		val host = levelHost ?: return
		val currentPlayer = player

		// Sortir le joueur AVANT de détruire l'ancienne carte, sinon il part avec.
		currentPlayer?.getParent()?.removeChild(currentPlayer)

		level?.let {
			host.removeChild(it)
			it.queueFree()
		}

		val next = (ResourceLoader.load(pendingScene) as? PackedScene)?.instantiate() as? Node2D
		if (next == null) {
			Logger.e("Scene introuvable : $pendingScene")
			return
		}

		host.addChild(next)
		level = next
		currentScene = pendingScene
		location = next.getMeta(LOCATION_META, "").toString()
		banner = next.getMeta(BANNER_META, "").toString()

		// Le bandeau attend que le fondu d'arrivée soit levé pour descendre.
		LocationBanner.instance?.announce(
			next.getMeta(LOCATION_META, "").toString(),
			next.getMeta(BANNER_META, "").toString(),
			fadeSeconds,
		)

		if (currentPlayer == null) return

		val entities = if (next.hasNode("World/Entities")) next.getNode("World/Entities") else null
		if (entities == null) {
			Logger.e("La carte $pendingScene n'a pas de noeud World/Entities")
			return
		}

		entities.addChild(currentPlayer)

		val door = arrivalDoor(next, pendingDoor)
		currentPlayer.position = arrivalPosition(next, door)

		// Reprise d'une sauvegarde : la place et le regard d'alors, une seule fois.
		val saved = restore
		restore = null
		if (saved != null) {
			currentPlayer.position = saved.position
			(if (currentPlayer.hasNode("Input")) currentPlayer.getNode("Input") else null)
				.let { it as? PlayerInput }?.face(saved.facing)
		}

		if (currentPlayer.hasNode("Input")) {
			val input = currentPlayer.getNode("Input") as? PlayerInput
			// On sort d'une porte en lui tournant le dos ; sur un paillasson,
			// on regarde vers l'intérieur de la pièce.
			if (door != null) {
				input?.face(if (door.isExit) door.exitDirection * -1.0 else door.entryDirection)
			}
			// Une touche tenue continue de faire marcher après la porte, sauf si
			// elle ferait aussitôt repartir par où l'on vient d'arriver : la
			// direction de sortie d'un paillasson, ou le demi-tour vers une
			// porte à contact (on entre dans un tunnel en maintenant Haut).
			if (door != null) {
				input?.blockUntilReleased(if (door.isExit) door.exitDirection else door.entryDirection * -1.0)
			}
		}

		if (currentPlayer.hasNode("Movement")) {
			val movement = currentPlayer.getNode("Movement") as? CharacterMovement
			// Le pas qui a franchi la porte visait une case de l'ANCIENNE carte.
			movement?.stop()
			movement?.snapToGrid()
		}
		// Les limites de caméra dépendent de la carte : elles doivent être reprises.
		if (currentPlayer.hasNode("Camera")) {
			(currentPlayer.getNode("Camera") as? PlayerCamera)?.applyLimits()
		}
	}

	/**
	 * Enregistre la partie : la carte, la place et le regard du joueur, le
	 * temps de jeu. À n'appeler qu'entre deux pas (le menu ne s'ouvre que là).
	 */
	fun save(): Boolean {
		val current = player ?: return false
		if (currentScene.isEmpty()) return false

		val input = (if (current.hasNode("Input")) current.getNode("Input") else null) as? PlayerInput
		return SaveGame.write(
			SaveGame.State(
				scene = currentScene,
				position = current.position,
				facing = input?.direction ?: Vector2.DOWN,
				location = location,
				banner = banner,
				seconds = playSeconds,
			),
		)
	}

	private fun arrivalDoor(target: Node2D, door: String): SceneTrigger? {
		if (door.isEmpty() || !target.hasNode("Doors/$door")) return null
		return target.getNode("Doors/$door") as? SceneTrigger
	}

	/** Case d'arrivée : devant la porte visée, ou le point d'apparition au premier chargement. */
	private fun arrivalPosition(target: Node2D, door: SceneTrigger?): Vector2 {
		if (door != null) {
			// Une sortie ne se redéclenche pas au contact : on arrive dessus.
			if (door.isExit) return door.position
			return door.position + door.entryDirection * Globals.instance.gridSize.toDouble()
		}

		if (target.hasNode("SpawnPoint")) {
			val spawn = target.getNode("SpawnPoint") as? Node2D
			if (spawn != null) return spawn.position
		}

		Logger.w("Ni porte ni SpawnPoint : arrivee en (0,0)")
		return Vector2.ZERO
	}

	private fun setFadeAlpha(alpha: Double) {
		val rect = fade ?: return
		rect.color = Color(0.0, 0.0, 0.0, alpha)
	}
}
