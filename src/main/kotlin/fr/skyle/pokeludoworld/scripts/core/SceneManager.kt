package fr.skyle.pokeludoworld.scripts.core

import fr.skyle.pokeludoworld.scripts.autoload.Globals
import fr.skyle.pokeludoworld.scripts.gameplay.characters.CharacterMovement
import fr.skyle.pokeludoworld.scripts.gameplay.items.Inventory
import fr.skyle.pokeludoworld.scripts.gameplay.characters.PlayerCamera
import fr.skyle.pokeludoworld.scripts.gameplay.characters.PlayerInput
import fr.skyle.pokeludoworld.scripts.gameplay.levels.SceneTrigger
import fr.skyle.pokeludoworld.scripts.gameplay.story.StoryFlags
import fr.skyle.pokeludoworld.scripts.log.Logger
import fr.skyle.pokeludoworld.scripts.ui.LocationBanner
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.CanvasModulate
import godot.api.ColorRect
import godot.api.Control
import godot.api.Node
import godot.api.Node2D
import godot.api.PackedScene
import godot.api.RenderingServer
import godot.api.ResourceLoader
import godot.api.Shader
import godot.api.ShaderMaterial
import godot.api.Texture2D
import godot.api.TileMapLayer
import godot.core.Color
import godot.core.Rect2
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

		/** Métadonnée de la racine d'une carte : vrai si elle est dehors, sous le ciel. */
		private const val DAYLIGHT_META = "daylight"
		private const val DAYLIGHT_NODE = "Daylight"

		/** Le voile clair et nuageux du dehors : un rectangle sur toute la carte, au-dessus du décor. */
		private const val HAZE_NODE = "Haze"
		private const val HAZE_SHADER = "res://src/main/kotlin/fr/skyle/pokeludoworld/resources/shaders/sky.gdshader"
		private const val HAZE_Z = 50

		/** Le temps qu'il fait : une scène à elle seule, juste au-dessus du voile. */
		private const val WEATHER_NODE = "Weather"
		private const val WEATHER_SCENE = "res://src/main/kotlin/fr/skyle/pokeludoworld/scenes/levels/weather.tscn"
		private const val WEATHER_Z = 51

		/** Ce que lit le shader des fenêtres : la teinte du dehors, et la force des lumières. */
		private const val TINT_UNIFORM = "day_tint"
		private const val LIGHT_UNIFORM = "night_light"
		private val DAY = Color(1.0, 1.0, 1.0, 1.0)

		/** Métadonnée de la racine d'une carte : sa musique. */
		private const val MUSIC_META = "music"

		/**
		 * Métadonnée de la racine d'une carte : ce que la quitter change à
		 * l'histoire. `drapeau posé > drapeau à poser`, plusieurs règles
		 * séparées par `|`. Sur l'île : `bell_hung > vigil_over` — sortir de
		 * l'île après la Veillée y met fin.
		 */
		private const val LEAVE_META = "on_leave"

		private const val SETTLE_FRAMES = 4
	}

	/** La carte où commence une nouvelle partie, à son `SpawnPoint` : la chambre de Ludo, au milieu du tapis. */
	@Category("Scenes")
	@Export
	var startScene: String = "res://src/main/kotlin/fr/skyle/pokeludoworld/scenes/levels/ludo_bedroom.tscn"

	@Export
	var playerScene: String = "res://src/main/kotlin/fr/skyle/pokeludoworld/scenes/characters/player.tscn"

	@Category("Transition")
	@Export
	var fadeSeconds: Double = 0.25

	/**
	 * Reprendre la sauvegarde au lancement, s'il y en a une. Ne compte que sans
	 * écran titre ([showTitle]) : avec lui, c'est le joueur qui choisit.
	 */
	@Category("Sauvegarde")
	@Export
	var loadSave: Boolean = true

	/**
	 * Attendre l'écran titre avant de lancer la partie (voir TitleScreen). Sans
	 * lui la partie démarre aussitôt : c'est ainsi que les tests arrivent
	 * directement sur leur carte.
	 */
	@Category("Titre")
	@Export
	var showTitle: Boolean = true

	/** Durée du fondu qui mène de l'écran titre à la partie, au noir puis du noir. */
	@Export
	var titleFadeSeconds: Double = 0.6

	/** Temps de jeu total de la partie, en secondes. */
	var playSeconds: Double = 0.0
		private set

	/** Nom du lieu où l'on se trouve, en français. */
	var location: String = ""
		private set

	private var banner = ""
	private var currentScene = ""
	private var restore: SaveGame.State? = null
	private var reloading = false

	private var levelHost: Node? = null
	private var fade: ColorRect? = null
	private var level: Node2D? = null

	/** La teinte du jour sur la carte courante, si elle est dehors. */
	private var daylight: CanvasModulate? = null
	private var player: Node2D? = null

	/** Le joueur, où qu'il soit, ou null avant qu'une partie ait commencé (l'écran titre). */
	val playerNode: Node2D?
		get() = player

	private var phase = Phase.IDLE
	private var progress = 0.0
	private var pendingScene = ""
	private var pendingDoor = ""
	private var bootstrapped = false

	/** Faux tant que l'écran titre a la main : aucune carte n'est chargée, le temps de jeu ne tourne pas. */
	private var started = false

	/** Durée du fondu en cours : celle des portes, ou celle de l'écran titre. */
	private var fadeDuration = 0.0

	/** Vrai dès que la première carte est à l'écran. */
	val hasLevel: Boolean
		get() = level != null

	/** Images à attendre après un rechargement avant de vérifier la case du joueur. */
	private var settleFrames = 0

	/** Vrai pendant tout le fondu : le joueur ne doit pas bouger. */
	val isChanging: Boolean
		get() = phase != Phase.IDLE

	@Register
	override fun _ready() {
		instance = this
		levelHost = getParent()

		if (hasNode("../Fade/Rect")) fade = getNode("../Fade/Rect") as? ColorRect
		setFadeAlpha(0.0)

		fadeDuration = fadeSeconds

		// Avec l'écran titre, rien ne se charge avant que le joueur ait choisi
		// (voir start). Sans lui, la partie se prépare tout de suite ; son
		// premier chargement attend la frame suivante : pendant `_ready` le
		// parent construit encore ses enfants et refuse un `add_child`.
		SaveGame.adoptOldSave()
		if (!showTitle) prepare(loadSave)

		Logger.i("Loading scene manager ...")
	}

	/**
	 * Prépare la partie : [resume] reprend la sauvegarde là où elle s'est
	 * arrêtée, s'il y en a une ; sinon tout repart de zéro, sac vide et sans
	 * aucun drapeau.
	 */
	private fun prepare(resume: Boolean) {
		// Le joueur n'existe qu'une fois la partie lancée : sur l'écran titre il
		// ne serait dans aucune carte, et resterait orphelin si l'on quittait là.
		if (player == null) player = (ResourceLoader.load(playerScene) as? PackedScene)?.instantiate() as? Node2D

		pendingScene = startScene
		pendingDoor = ""

		playSeconds = 0.0
		Inventory.clear()
		StoryFlags.clear()
		restore = if (resume) SaveGame.read() else null
		restore?.let {
			if (ResourceLoader.exists(it.scene)) {
				pendingScene = it.scene
				playSeconds = it.seconds
				Inventory.restore(it.items)
				StoryFlags.restore(it.flags)
			} else {
				Logger.e("Sauvegarde ignoree, carte introuvable : ${it.scene}")
				restore = null
			}
		}
		started = true
	}

	/**
	 * Lance la partie depuis l'écran titre : l'écran part au noir, la première
	 * carte se charge, puis le noir se lève. La partie occupe l'emplacement
	 * [slot] ; [resume] reprend ce qui y est sauvegardé (« Continuer »), sinon
	 * tout repart de zéro (« Nouvelle partie »). Sans effet une fois la partie
	 * lancée.
	 */
	fun start(slot: Int, resume: Boolean) {
		if (started) return
		SaveGame.use(slot)
		prepare(resume)

		// La carte arrive au bout du fondu, pas tout de suite.
		bootstrapped = true
		fadeDuration = titleFadeSeconds
		progress = 0.0
		phase = Phase.FADE_OUT

		Logger.i("Starting game (slot=$slot, resume=$resume)")
	}

	@Register
	override fun _process(delta: Double) {
		// L'écran titre a la main : la partie n'a pas commencé.
		if (!started) return

		// Comme dans les jeux d'origine, le temps de jeu tourne aussi dans les menus.
		playSeconds += delta

		// Dehors, la teinte suit l'heure, et les fenêtres s'allument avec la nuit.
		val sky = daylight
		val tint = if (sky != null) DayNight.tint() else DAY
		sky?.color = tint
		RenderingServer.globalShaderParameterSet(TINT_UNIFORM, tint)
		RenderingServer.globalShaderParameterSet(LIGHT_UNIFORM, if (sky != null) DayNight.light() else 0.0)

		if (!bootstrapped) {
			bootstrapped = true
			swap()
			return
		}

		if (settleFrames > 0 && --settleFrames == 0) settlePlayer()

		if (phase == Phase.IDLE) return

		progress += if (fadeDuration > 0.0) delta / fadeDuration else 1.0
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
			if (t >= 1.0) {
				phase = Phase.IDLE
				fadeDuration = fadeSeconds
			}
		}
	}

	/**
	 * Demande un changement de carte. Ignoré si un fondu est déjà en cours.
	 * [leaving] : on sort par un paillasson ou un tapis d'escalier.
	 */
	fun changeLevel(scenePath: String, door: String, leaving: Boolean = false) {
		if (isChanging) return

		leave(level)
		pendingScene = scenePath
		pendingDoor = door
		progress = 0.0
		phase = Phase.FADE_OUT

		// On n'entend pas la même porte en entrant quelque part et en en sortant.
		AudioManager.instance?.sfx(if (leaving) "door_exit" else "door")

		Logger.i("Changing level to $scenePath (door=$door)")
	}

	/** Dehors, un voile clair et nuageux par-dessus toute la carte (voir sky.gdshader). */
	private fun addHaze(map: Node2D) {
		val rect = skyRect(map) ?: return
		val shader = ResourceLoader.load(HAZE_SHADER) as? Shader ?: return

		val material = ShaderMaterial()
		material.shader = shader

		val haze = ColorRect()
		haze.setName(HAZE_NODE)
		haze.setPosition(rect.position)
		haze.setSize(rect.size)
		haze.setMouseFilter(Control.MouseFilter.IGNORE)
		haze.zIndex = HAZE_Z
		haze.material = material
		map.addChild(haze)
	}

	/**
	 * Dehors, le temps qu'il fait par-dessus le voile : ce qui tombe, la nappe,
	 * et la teinte d'écran. Tout est dans la scène, animé par WeatherLayer.kt.
	 */
	private fun addWeather(map: Node2D) {
		val scene = ResourceLoader.load(WEATHER_SCENE) as? PackedScene ?: return
		val sky = scene.instantiate() as? Node2D ?: return

		sky.setName(WEATHER_NODE)
		sky.zIndex = WEATHER_Z
		map.addChild(sky)
	}

	/** L'étendue de la carte, en pixels : ce que couvre le voile. */
	private fun skyRect(map: Node2D): Rect2? {
		val ground = (if (map.hasNode("Background/Ground")) map.getNode("Background/Ground") else null) as? TileMapLayer ?: return null
		val cells = ground.getUsedRect()
		val grid = Globals.instance.gridSize.toDouble()
		return Rect2(
			Vector2(cells.position.x * grid, cells.position.y * grid),
			Vector2(cells.size.x * grid, cells.size.y * grid),
		)
	}

	/** Applique les règles `on_leave` de la carte qu'on quitte. Un rechargement n'est pas un départ. */
	private fun leave(from: Node2D?) {
		val rules = from?.getMeta(LEAVE_META, "")?.toString() ?: return
		rules.split('|').forEach { rule ->
			val parts = rule.split('>').map { it.trim() }
			if (parts.size == 2 && parts[0].isNotEmpty() && parts[1].isNotEmpty() && StoryFlags.has(parts[0])) StoryFlags.set(parts[1])
		}
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

		// Une carte d'extérieur prend la teinte de l'heure ; un intérieur reste éclairé.
		daylight = null
		if (next.getMeta(DAYLIGHT_META, false) == true) {
			val sky = CanvasModulate()
			sky.setName(DAYLIGHT_NODE)
			sky.color = DayNight.tint()
			next.addChild(sky)
			daylight = sky
			addHaze(next)
			addWeather(next)
		}

		host.addChild(next)
		level = next
		currentScene = pendingScene
		location = next.getMeta(LOCATION_META, "").toString()
		banner = next.getMeta(BANNER_META, "").toString()

		AudioManager.instance?.playMusic(next.getMeta(MUSIC_META, "").toString())

		// Le bandeau attend que le fondu d'arrivée soit levé pour descendre.
		LocationBanner.instance?.announce(
			next.getMeta(LOCATION_META, "").toString(),
			next.getMeta(BANNER_META, "").toString(),
			fadeDuration,
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
		// Les corps de la nouvelle carte n'existent pour la physique qu'après
		// quelques images : la case du joueur se vérifie alors (voir settlePlayer).
		if (reloading) {
			reloading = false
			settleFrames = SETTLE_FRAMES
		}
		// Les limites de caméra dépendent de la carte : elles doivent être reprises.
		if (currentPlayer.hasNode("Camera")) {
			(currentPlayer.getNode("Camera") as? PlayerCamera)?.applyLimits()
		}
	}

	/**
	 * Recharge la carte courante dans un fondu, le joueur gardant sa place et
	 * son regard. C'est au chargement d'une carte que se décide qui s'y trouve
	 * (voir StoryFlags.allows) : après un drapeau qui change le village, c'est
	 * ce qui le montre. Ignoré si un fondu est déjà en cours.
	 */
	@Register
	fun reload() {
		val current = player ?: return
		if (isChanging || currentScene.isEmpty()) return

		val input = (if (current.hasNode("Input")) current.getNode("Input") else null) as? PlayerInput
		restore = SaveGame.State(
			scene = currentScene,
			position = current.position,
			facing = input?.direction ?: Vector2.DOWN,
			location = location,
			banner = banner,
			seconds = playSeconds,
		)
		pendingScene = currentScene
		pendingDoor = ""
		progress = 0.0
		phase = Phase.FADE_OUT
		reloading = true

		Logger.i("Reloading level $currentScene")
	}

	/**
	 * Après un rechargement, la carte a pu poser quelque chose là où se tient
	 * le joueur (la cloche sous le portique où il vient de l'accrocher). Il
	 * recule alors d'une case, sans se retourner — pendant que l'écran est
	 * encore noir.
	 */
	private fun settlePlayer() {
		val current = player ?: return
		val movement = (if (current.hasNode("Movement")) current.getNode("Movement") else null) as? CharacterMovement
		val input = (if (current.hasNode("Input")) current.getNode("Input") else null) as? PlayerInput
		val back = (input?.direction ?: Vector2.DOWN) * -1.0
		movement?.stepOutOfSolid(listOf(back, Vector2.DOWN, Vector2.LEFT, Vector2.RIGHT, Vector2.UP))
	}

	/**
	 * Enregistre la partie : la carte, la place et le regard du joueur, le
	 * temps de jeu, le sac et les drapeaux d'histoire. À n'appeler qu'entre deux pas (le menu ne s'ouvre que là).
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
				items = Inventory.snapshot(),
				flags = StoryFlags.snapshot(),
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
