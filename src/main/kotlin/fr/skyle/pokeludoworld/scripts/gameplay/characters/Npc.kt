package fr.skyle.pokeludoworld.scripts.gameplay.characters

import fr.skyle.pokeludoworld.scripts.autoload.Globals
import fr.skyle.pokeludoworld.scripts.core.SceneManager
import fr.skyle.pokeludoworld.scripts.gameplay.story.StoryFlags
import fr.skyle.pokeludoworld.scripts.gameplay.story.StoryText
import fr.skyle.pokeludoworld.scripts.log.Logger
import fr.skyle.pokeludoworld.scripts.ui.MessageBox
import fr.skyle.pokeludoworld.scripts.ui.PauseMenu
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.MultilineText
import godot.annotation.Register
import godot.annotation.Script
import godot.api.CharacterBody2D
import godot.api.Node
import godot.api.Node2D
import godot.api.ResourceLoader
import godot.api.SpriteFrames
import godot.api.Texture2D
import godot.api.TileMapLayer
import godot.core.PackedStringArray
import godot.core.PackedVector2Array
import godot.core.Vector2
import kotlin.math.abs
import kotlin.math.floor
import kotlin.math.round
import kotlin.random.Random

/**
 * Personnage non joueur : il se tient sur une case, bloque le passage, et
 * parle quand on l'examine en se tournant vers celui qui lui parle.
 *
 * Il réutilise les composants du joueur — [CharacterMovement] pour les pas,
 * [CharacterAnimation] pour le sprite — sans composant d'entrée. Il bouge
 * seul selon [movement], ou quand un autre script le fait marcher (voir
 * Roadblock).
 */
@Script
class Npc : CharacterBody2D() {

	/** Nom d'une planche de `assets/characters`, sans l'extension. */
	@Category("Apparence")
	@Export
	var appearance: String = "worker"

	/** Direction regardée au repos. */
	@Category("Apparence")
	@Export
	var facing: Vector2 = Vector2.DOWN

	/** Ce qu'il dit. Une barre verticale `|` sépare deux boîtes. */
	@Category("Contenu")
	@MultilineText
	@Export
	var text: String = ""

	/**
	 * Ce qu'il dit selon l'histoire : des entrées `drapeau > texte`, lues de
	 * bas en haut. [text] reste le défaut (voir StoryText).
	 */
	@Category("Contenu")
	@Export
	var states: PackedStringArray = PackedStringArray()

	/**
	 * Question Oui / Non posée avant d'agir : `Question ?` devant [text],
	 * `drapeau > Question ?` devant le texte de cet état. Non ne dit rien.
	 */
	@Category("Contenu")
	@Export
	var ask: String = ""

	/** Drapeau sans lequel il n'est pas sur la carte. */
	@Category("Histoire")
	@Export
	var requiredFlag: String = ""

	/** Drapeau avec lequel il n'est plus sur la carte. */
	@Category("Histoire")
	@Export
	var forbiddenFlag: String = ""

	/** `static` : immobile. `wander` : erre dans une zone. `patrol` : suit [route]. */
	@Category("Deplacement")
	@Export
	var movement: String = "static"

	/** Cases par seconde. 4 = la marche du joueur, 2 = celle des PNJ du projet de référence. */
	@Category("Deplacement")
	@Export
	var pace: Double = 4.0

	/**
	 * Errance : calque de tuiles, depuis la racine de la carte, dont il ne
	 * sort pas. Il ne marche que sur les cases que ce calque dessine.
	 */
	@Category("Deplacement")
	@Export
	var wanderLayer: String = ""

	/** Errance : pause entre deux gestes, tirée entre ces deux durées (secondes). */
	@Category("Deplacement")
	@Export
	var wanderPause: Vector2 = Vector2(2.0, 5.0)

	/** Ronde : cases à rejoindre l'une après l'autre, en boucle. */
	@Category("Deplacement")
	@Export
	var route: PackedVector2Array = PackedVector2Array()

	/** Direction regardée en ce moment. */
	var direction: Vector2 = Vector2.DOWN
		private set

	val isWalking: Boolean
		get() = mover?.isWalking ?: false

	private var mover: CharacterMovement? = null
	private var sprite: CharacterAnimation? = null

	private var pause = 0.0
	private var routeIndex = 0
	private var wantsToTalk = false
	private var inConversation = false
	private var zone: TileMapLayer? = null

	@Register
	override fun _ready() {
		// Absent de cette étape de l'histoire : il quitte la carte avant d'y avoir servi.
		if (!StoryFlags.allows(requiredFlag, forbiddenFlag)) {
			queueFree()
			return
		}

		mover = getNode("Movement") as? CharacterMovement
		sprite = getNode("Sprite") as? CharacterAnimation
		mover?.attach(this)
		mover?.tilesPerSecond = pace
		// Les jambes suivent l'allure : un coureur ne glisse pas.
		sprite?.speedScale = (pace / WALK_PACE).toFloat()

		val frames = framesOf(appearance)
		if (frames == null) {
			Logger.e("Apparence de PNJ inconnue : $appearance")
		} else {
			sprite?.spriteFrames = frames
		}

		direction = facing
		sprite?.refresh(direction, false)
		pause = nextPause()
	}

	@Register
	override fun _process(delta: Double) {
		val wasWalking = isWalking
		mover?.process(delta)

		if (wasWalking && !isWalking && wantsToTalk) answer()

		// Le dialogue fini, celui qui se tient à un poste reprend sa pose :
		// le pêcheur se retourne vers l'eau.
		if (inConversation && MessageBox.instance?.isOpen != true) {
			inConversation = false
			if (movement == "static") faceHome()
		}
		if (!isWalking && !isHeld()) {
			when (movement) {
				"wander" -> wander(delta)
				"patrol" -> patrol()
			}
		}

		sprite?.refresh(direction, isWalking)
	}

	fun face(newDirection: Vector2) {
		direction = newDirection
	}

	/** Reprend la direction de repos. */
	fun faceHome() {
		direction = facing
	}

	/**
	 * Fait un pas d'une case, sur ordre d'une scène : le joueur ne l'arrête
	 * pas, puisque c'est la scène qui règle leurs places. Renvoie false si la
	 * case est occupée par le décor.
	 */
	fun walk(step: Vector2): Boolean {
		direction = step
		return mover?.tryWalk(step, SCENERY) ?: false
	}

	/** Dit son texte du moment, sans se tourner. */
	fun speak() {
		StoryText.say(text, states, ask)
	}

	/**
	 * On lui parle depuis une case voisine, en regardant dans [fromDirection].
	 * S'il marche, il termine son pas puis répond.
	 */
	fun talk(fromDirection: Vector2) {
		if (isWalking) {
			wantsToTalk = true
			return
		}
		direction = fromDirection * -1.0
		speak()
		inConversation = true
		pause = nextPause()
	}

	/** Répond à qui l'a interpellé pendant son pas, s'il est encore à côté. */
	private fun answer() {
		wantsToTalk = false
		val parent = getParent() ?: return
		val player = (if (parent.hasNode("Player")) parent.getNode("Player") else null) as? Node2D ?: return
		val gap = (player.position - position) / grid()
		val step = Vector2(round(gap.x), round(gap.y))
		if (abs(step.x) + abs(step.y) != 1.0) return
		direction = step
		speak()
		inConversation = true
		pause = nextPause()
	}

	/** Personne ne bouge de soi-même pendant un dialogue, un fondu ou le menu. */
	private fun isHeld(): Boolean =
		MessageBox.instance?.isOpen == true || SceneManager.instance?.isChanging == true ||
			PauseMenu.instance?.isOpen == true

	// --- errance

	private fun wander(delta: Double) {
		pause -= delta
		if (pause > 0.0) return
		pause = nextPause()

		val step = DIRECTIONS[Random.nextInt(DIRECTIONS.size)]
		// Il regarde d'abord où il va ; s'il ne peut pas y aller, il aura au
		// moins tourné la tête, comme quelqu'un qui cherche.
		direction = step
		if (Random.nextDouble() < LOOK_ONLY) return
		if (!inZone(globalPosition + step * grid())) return
		mover?.tryWalk(step)
	}

	private fun nextPause(): Double =
		wanderPause.x + Random.nextDouble() * (wanderPause.y - wanderPause.x).coerceAtLeast(0.0)

	private fun inZone(globalPoint: Vector2): Boolean {
		if (wanderLayer.isEmpty()) return true
		val layer = zone ?: findZone() ?: return false
		val cell = layer.localToMap(layer.toLocal(globalPoint))
		return layer.getCellSourceId(cell) != -1
	}

	private fun findZone(): TileMapLayer? {
		var node: Node? = this
		while (node != null && node.name.toString() != "Level") node = node.getParent()
		val level = node ?: return null
		zone = (if (level.hasNode(wanderLayer)) level.getNode(wanderLayer) else null) as? TileMapLayer
		if (zone == null) Logger.e("Zone d'errance introuvable : $wanderLayer")
		return zone
	}

	// --- ronde

	private fun patrol() {
		if (route.size == 0) return
		var goal = route[routeIndex]
		val here = cell()

		if (here == goal) {
			routeIndex = (routeIndex + 1) % route.size
			goal = route[routeIndex]
			if (here == goal) return
		}

		val step = when {
			goal.x > here.x -> Vector2.RIGHT
			goal.x < here.x -> Vector2.LEFT
			goal.y > here.y -> Vector2.DOWN
			else -> Vector2.UP
		}
		direction = step
		// Case occupée : il attend sur place et réessaie à l'image suivante.
		mover?.tryWalk(step)
	}

	private fun cell(): Vector2 = Vector2(floor(position.x / grid()), floor(position.y / grid()))

	private fun grid(): Double = Globals.instance.gridSize.toDouble()

	companion object {
		private const val SHEETS_DIR = "res://src/main/kotlin/fr/skyle/pokeludoworld/assets/characters/"
		private const val WALK_PACE = 4.0
		private const val LOOK_ONLY = 0.3

		/** Décor et autres PNJ, sans le joueur. */
		private const val SCENERY = 1

		private val DIRECTIONS = listOf(Vector2.UP, Vector2.DOWN, Vector2.LEFT, Vector2.RIGHT)

		/** Une planche n'est découpée qu'une fois, même portée par dix PNJ. */
		private val cache = HashMap<String, SpriteFrames>()

		private fun framesOf(name: String): SpriteFrames? {
			cache[name]?.let { return it }
			val sheet = ResourceLoader.load("$SHEETS_DIR$name.png") as? Texture2D ?: return null
			return CharacterFrames.build(sheet).also { cache[name] = it }
		}
	}
}
