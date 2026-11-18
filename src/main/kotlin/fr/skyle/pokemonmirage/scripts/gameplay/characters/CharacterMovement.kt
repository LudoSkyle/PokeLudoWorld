package fr.skyle.pokemonmirage.scripts.gameplay.characters

import fr.skyle.pokemonmirage.scripts.autoload.Globals
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.Node
import godot.api.Node2D
import godot.api.PhysicsPointQueryParameters2D
import godot.api.StaticBody2D
import godot.core.Vector2
import godot.core.Vector2i
import fr.skyle.pokemonmirage.scripts.gameplay.levels.Water
import kotlin.math.floor
import kotlin.math.round

/**
 * Déplacement case par case : un pas occupe exactement une case et ne peut pas
 * être interrompu. L'origine du personnage est le CENTRE de sa case, ce qui
 * place son point de tri Y entre deux rangées de décor.
 */
@Script
class CharacterMovement : Node() {

	companion object {
		/** Cases réservées par un pas en cours, tous personnages confondus. */
		private val claims = HashMap<Long, CharacterMovement>()
	}

	@Category("Movement")
	@Export
	var tilesPerSecond: Double = 4.0

	/**
	 * Calques qui arrêtent ce personnage. Le joueur est sur le calque 2 : lui
	 * ne s'arrête que sur le décor et les PNJ (1), un PNJ s'arrête aussi sur
	 * le joueur (3).
	 */
	@Category("Movement")
	@Export
	var obstacleMask: Int = 1

	var isWalking: Boolean = false
		private set

	/** Vrai pendant le saut d'un rebord : un pas de deux cases, par-dessus la case du rebord. */
	var isJumping: Boolean = false
		private set

	/** De combien de pixels le personnage est en l'air, à cet instant du saut. 0 au sol. */
	var lift: Double = 0.0
		private set

	private var jumpLength = 0.0

	/** Le nombre de pas engagés depuis le début, et la place d'où est parti le dernier : ce que suit un [Follower]. */
	var steps: Int = 0
		private set
	var origin: Vector2 = Vector2.ZERO
		private set

	/** L'allure du pas en cours, en cases par seconde. */
	val paceNow: Double
		get() = if (isJumping) JUMP_TILES_PER_SECOND else tilesPerSecond

	/** Case visée par le pas en cours, réservée tant qu'il dure. */
	private var claimed: Long? = null

	private var body: Node2D? = null
	private var target: Vector2 = Vector2.ZERO

	fun attach(node: Node2D) {
		body = node
		snapToGrid()
	}

	private fun gridSize(): Double = Globals.instance.gridSize.toDouble()

	/** Tente un pas. Renvoie false si la case visée est occupée ou si un pas est en cours. */
	fun tryWalk(direction: Vector2, mask: Int = obstacleMask): Boolean {
		val node = body ?: return false
		if (isWalking) return false

		val step = direction * gridSize()
		val destination = node.globalPosition + step

		// La case visée est testée en coordonnées globales, au centre de la case.
		if (isBlocked(destination, mask)) return false

		// Un rebord — le bord haut d'un plateau — ne se franchit pas, alors que
		// les deux cases se foulent : la tuile porte une bande fine le long de
		// son bord, sur sa propre couche. On la cherche de part et d'autre de
		// la frontière entre les deux cases.
		val border = node.globalPosition + step * 0.5
		if (isBlocked(border - direction * LEDGE_REACH, LEDGE_MASK) || isBlocked(border + direction * LEDGE_REACH, LEDGE_MASK)) return false

		// Un corps n'occupe sa case d'arrivée qu'à la fin du pas : sans cette
		// réservation, deux personnages partis en même temps s'y retrouvent.
		val key = cellKey(destination)
		val owner = claims[key]
		if (owner != null && owner !== this) return false
		claims[key] = this
		claimed = key

		origin = node.position
		steps++
		target = node.position + step
		isWalking = true
		return true
	}

	/**
	 * Tente de sauter le rebord qui est sur la case voisine. Un rebord est une
	 * case pleine, qui ne se saute que dans **un** sens — celui que sa tuile
	 * porte dans la donnée `jump` du TileSet : du haut vers le bas. On retombe
	 * une case plus loin, si elle est libre. Renvoie false s'il n'y a pas là de
	 * rebord tourné dans ce sens, ou pas la place de retomber.
	 *
	 * À appeler quand [tryWalk] a refusé le pas. Seul le joueur saute : un PNJ
	 * s'arrête devant un rebord comme devant un mur.
	 */
	fun tryJump(direction: Vector2): Boolean {
		val node = body ?: return false
		if (isWalking) return false

		val step = direction * gridSize()
		if (!jumpsAt(node.globalPosition + step, direction)) return false
		val landing = node.globalPosition + step * 2.0
		if (isBlocked(landing, obstacleMask)) return false

		val key = cellKey(landing)
		val owner = claims[key]
		if (owner != null && owner !== this) return false
		claims[key] = this
		claimed = key

		origin = node.position
		steps++
		target = node.position + step * 2.0
		jumpLength = gridSize() * 2.0
		isWalking = true
		isJumping = true
		return true
	}

	/** La case qui contient [globalPoint] porte-t-elle un rebord qui se saute dans le sens [direction] ? */
	private fun jumpsAt(globalPoint: Vector2, direction: Vector2): Boolean {
		val node = body ?: return false
		val level = Water.levelOf(node) ?: return false
		val background = Water.backgroundOf(level) ?: return false
		val way = Vector2i(direction.x.toInt(), direction.y.toInt())
		return Water.groundLayers(background).any { layer ->
			val cell = layer.localToMap(layer.toLocal(globalPoint))
			layer.getCellSourceId(cell) != -1 && layer.getCellTileData(cell)?.getCustomData(JUMP) as? Vector2i == way
		}
	}

	fun process(delta: Double) {
		val node = body ?: return
		if (!isWalking) return

		// Un saut a son allure à lui : le même bond, qu'on arrive au pas ou en courant.
		val pace = if (isJumping) JUMP_TILES_PER_SECOND else tilesPerSecond
		node.position = node.position.moveToward(target, delta * gridSize() * pace)

		if (isJumping) {
			// Une cloche : au sol au départ et à l'arrivée, au plus haut au-dessus du rebord.
			val done = (1.0 - node.position.distanceTo(target) / jumpLength).coerceIn(0.0, 1.0)
			lift = JUMP_HEIGHT * 4.0 * done * (1.0 - done)
		}

		if (node.position.distanceTo(target) < 0.01) {
			node.position = target
			isWalking = false
			isJumping = false
			lift = 0.0
			release()
		}
	}

	@Register
	override fun _exitTree() {
		release()
	}

	private fun release() {
		val key = claimed ?: return
		if (claims[key] === this) claims.remove(key)
		claimed = null
	}

	private fun cellKey(globalPoint: Vector2): Long {
		val grid = gridSize()
		val x = floor(globalPoint.x / grid).toLong()
		val y = floor(globalPoint.y / grid).toLong()
		return x * 100_000L + y
	}

	private fun isBlocked(globalPoint: Vector2, mask: Int): Boolean {
		val node = body ?: return true
		val space = node.getWorld2d()?.directSpaceState ?: return true

		val params = PhysicsPointQueryParameters2D()
		params.position = globalPoint
		params.collisionMask = mask.toLong()
		params.collideWithBodies = true
		params.collideWithAreas = false

		return space.intersectPoint(params, 1).size > 0
	}

	/**
	 * Si un corps occupe la case où l'on se tient — une carte rechargée a pu y
	 * poser quelque chose —, se pose sur la première case libre parmi
	 * [directions]. Renvoie true si l'on a dû bouger.
	 */
	fun stepOutOfSolid(directions: List<Vector2>): Boolean {
		val node = body ?: return false
		if (!isBlocked(node.globalPosition, obstacleMask)) return false

		val free = directions.firstOrNull { !isBlocked(node.globalPosition + it * gridSize(), obstacleMask) }
			?: return false
		stop()
		node.position += free * gridSize()
		return true
	}

	/**
	 * Premier corps présent sur la case voisine dans [direction], ou null.
	 * Sert à interagir avec ce qu'on regarde — le même test que le déplacement,
	 * mais on veut ici savoir *quoi* bloque, pas seulement si ça bloque.
	 */
	fun colliderAt(direction: Vector2): Node? {
		val node = body ?: return null
		val space = node.getWorld2d()?.directSpaceState ?: return null

		val params = PhysicsPointQueryParameters2D()
		params.position = node.globalPosition + direction * gridSize()
		params.collisionMask = 1
		params.collideWithBodies = true
		params.collideWithAreas = false

		val hits = space.intersectPoint(params, 8)

		// Un meuble examinable partage sa case avec la tuile qui le dessine :
		// c'est lui qu'on veut, pas le calque de tuiles.
		// Pareil pour un personnage assis sur un banc : la tuile du banc est
		// pleine, et c'est à lui qu'on parle.
		var first: Node? = null
		var seated: Node? = null
		for (i in 0 until hits.size) {
			val collider = hits.get(i).get("collider") as? Node ?: continue
			if (collider is StaticBody2D) return collider
			if (collider is Npc && seated == null) seated = collider
			if (first == null) first = collider
		}

		return seated ?: first
	}

	/**
	 * Zone (porte) sur laquelle le personnage se tient, ou null. Les portes
	 * sont sur le calque de collision 3 pour pouvoir être retrouvées ainsi.
	 */
	fun areaUnderfoot(): Node? {
		val node = body ?: return null
		val space = node.getWorld2d()?.directSpaceState ?: return null

		val params = PhysicsPointQueryParameters2D()
		params.position = node.globalPosition
		params.collisionMask = 4
		params.collideWithBodies = false
		params.collideWithAreas = true

		val hits = space.intersectPoint(params, 4)

		// Un meuble examinable partage sa case avec la tuile qui le dessine :
		// c'est lui qu'on veut, pas le calque de tuiles.
		var first: Node? = null
		for (i in 0 until hits.size) {
			val collider = hits.get(i).get("collider") as? Node ?: continue
			if (collider is StaticBody2D) return collider
			if (first == null) first = collider
		}

		return first
	}

	/**
	 * Abandonne le pas en cours. Indispensable après une téléportation : la
	 * cible du pas est exprimée dans l'ancienne carte, et le personnage
	 * glisserait vers elle à travers les murs de la nouvelle.
	 */
	fun stop() {
		isWalking = false
		isJumping = false
		lift = 0.0
		release()
	}

	/** Recale sur le centre de case le plus proche. */
	fun snapToGrid() {
		val node = body ?: return
		val grid = gridSize()
		val half = grid / 2.0

		node.position = Vector2(
			round((node.position.x - half) / grid) * grid + half,
			round((node.position.y - half) / grid) * grid + half,
		)
	}
}

/** La couche physique des rebords (`physics_layer_1` du TileSet) : aucun corps n'y est, seulement des bandes de tuile. */
private const val LEDGE_MASK = 8

/** À combien de pixels de la frontière entre deux cases on cherche un rebord. */
private const val LEDGE_REACH = 2.0

/** La donnée du TileSet qui dit dans quel sens une tuile de rebord se saute (un `Vector2i` ; nul : elle ne se saute pas). */
private const val JUMP = "jump"

/** L'allure d'un saut, en cases par seconde : deux cases en 0,4 s. */
private const val JUMP_TILES_PER_SECOND = 5.0

/** La hauteur du bond à son sommet, en pixels. */
private const val JUMP_HEIGHT = 8.0
