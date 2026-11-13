package fr.skyle.pokeludoworld.scripts.gameplay.characters

import fr.skyle.pokeludoworld.scripts.autoload.Globals
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.Node
import godot.api.Node2D
import godot.api.PhysicsPointQueryParameters2D
import godot.api.StaticBody2D
import godot.core.Vector2
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

		// Un corps n'occupe sa case d'arrivée qu'à la fin du pas : sans cette
		// réservation, deux personnages partis en même temps s'y retrouvent.
		val key = cellKey(destination)
		val owner = claims[key]
		if (owner != null && owner !== this) return false
		claims[key] = this
		claimed = key

		target = node.position + step
		isWalking = true
		return true
	}

	fun process(delta: Double) {
		val node = body ?: return
		if (!isWalking) return

		node.position = node.position.moveToward(target, delta * gridSize() * tilesPerSecond)

		if (node.position.distanceTo(target) < 0.01) {
			node.position = target
			isWalking = false
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
		var first: Node? = null
		for (i in 0 until hits.size) {
			val collider = hits.get(i).get("collider") as? Node ?: continue
			if (collider is StaticBody2D) return collider
			if (first == null) first = collider
		}

		return first
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
