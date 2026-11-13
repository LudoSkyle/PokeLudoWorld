package fr.skyle.pokeludoworld.scripts.gameplay.characters

import fr.skyle.pokeludoworld.scripts.autoload.Globals
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Script
import godot.api.Node
import godot.api.Node2D
import godot.api.PhysicsPointQueryParameters2D
import godot.core.Vector2
import kotlin.math.round

/**
 * Déplacement case par case : un pas occupe exactement une case et ne peut pas
 * être interrompu. L'origine du personnage est le CENTRE de sa case, ce qui
 * place son point de tri Y entre deux rangées de décor.
 */
@Script
class CharacterMovement : Node() {

	@Category("Movement")
	@Export
	var tilesPerSecond: Double = 4.0

	var isWalking: Boolean = false
		private set

	private var body: Node2D? = null
	private var target: Vector2 = Vector2.ZERO

	fun attach(node: Node2D) {
		body = node
		snapToGrid()
	}

	private fun gridSize(): Double = Globals.instance.gridSize.toDouble()

	/** Tente un pas. Renvoie false si la case visée est occupée ou si un pas est en cours. */
	fun tryWalk(direction: Vector2): Boolean {
		val node = body ?: return false
		if (isWalking) return false

		val step = direction * gridSize()

		// La case visée est testée en coordonnées globales, au centre de la case.
		if (isBlocked(node.globalPosition + step)) return false

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
		}
	}

	private fun isBlocked(globalPoint: Vector2): Boolean {
		val node = body ?: return true
		val space = node.getWorld2d()?.directSpaceState ?: return true

		val params = PhysicsPointQueryParameters2D()
		params.position = globalPoint
		params.collisionMask = 1
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

		for (i in 0 until hits.size) {
			val collider = hits.get(i).get("collider")
			if (collider is Node) return collider
		}

		return null
	}

	/**
	 * Abandonne le pas en cours. Indispensable après une téléportation : la
	 * cible du pas est exprimée dans l'ancienne carte, et le personnage
	 * glisserait vers elle à travers les murs de la nouvelle.
	 */
	fun stop() {
		isWalking = false
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
