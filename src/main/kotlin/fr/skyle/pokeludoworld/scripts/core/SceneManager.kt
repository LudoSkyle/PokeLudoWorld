package fr.skyle.pokeludoworld.scripts.core

import fr.skyle.pokeludoworld.scripts.autoload.Globals
import fr.skyle.pokeludoworld.scripts.gameplay.characters.CharacterMovement
import fr.skyle.pokeludoworld.scripts.gameplay.characters.PlayerCamera
import fr.skyle.pokeludoworld.scripts.gameplay.levels.SceneTrigger
import fr.skyle.pokeludoworld.scripts.log.Logger
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
	}

	@Category("Scenes")
	@Export
	var startScene: String = "res://src/main/kotlin/fr/skyle/pokeludoworld/scenes/levels/start_town.tscn"

	@Export
	var playerScene: String = "res://src/main/kotlin/fr/skyle/pokeludoworld/scenes/characters/player.tscn"

	@Category("Transition")
	@Export
	var fadeSeconds: Double = 0.25

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
		// Le premier chargement attend la frame suivante : pendant `_ready` le
		// parent construit encore ses enfants et refuse un `add_child`.

		Logger.i("Loading scene manager ...")
	}

	@Register
	override fun _process(delta: Double) {
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

		if (currentPlayer == null) return

		val entities = if (next.hasNode("World/Entities")) next.getNode("World/Entities") else null
		if (entities == null) {
			Logger.e("La carte $pendingScene n'a pas de noeud World/Entities")
			return
		}

		entities.addChild(currentPlayer)
		currentPlayer.position = arrivalPosition(next, pendingDoor)

		if (currentPlayer.hasNode("Movement")) {
			(currentPlayer.getNode("Movement") as? CharacterMovement)?.snapToGrid()
		}
		// Les limites de caméra dépendent de la carte : elles doivent être reprises.
		if (currentPlayer.hasNode("Camera")) {
			(currentPlayer.getNode("Camera") as? PlayerCamera)?.applyLimits()
		}
	}

	/** Case d'arrivée : devant la porte visée, ou le point d'apparition au premier chargement. */
	private fun arrivalPosition(target: Node2D, door: String): Vector2 {
		if (door.isNotEmpty() && target.hasNode("Doors/$door")) {
			val trigger = target.getNode("Doors/$door") as? SceneTrigger
			if (trigger != null) {
				return trigger.position + trigger.entryDirection * Globals.instance.gridSize.toDouble()
			}
		}

		if (target.hasNode("SpawnPoint")) {
			val spawn = target.getNode("SpawnPoint") as? Node2D
			if (spawn != null) return spawn.position
		}

		Logger.w("Ni porte '$door' ni SpawnPoint : arrivee en (0,0)")
		return Vector2.ZERO
	}

	private fun setFadeAlpha(alpha: Double) {
		val rect = fade ?: return
		rect.color = Color(0.0, 0.0, 0.0, alpha)
	}
}
