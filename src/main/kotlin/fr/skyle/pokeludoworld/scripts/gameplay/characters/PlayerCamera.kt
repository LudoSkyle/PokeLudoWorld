package fr.skyle.pokeludoworld.scripts.gameplay.characters

import fr.skyle.pokeludoworld.scripts.autoload.Globals
import fr.skyle.pokeludoworld.scripts.log.Logger
import godot.annotation.Register
import godot.annotation.Script
import godot.api.Camera2D
import godot.api.Node
import godot.api.TileMapLayer
import godot.core.Side
import godot.core.Vector2

/**
 * Caméra centrée sur le joueur, bornée à l'étendue réelle du calque Ground.
 * Les limites sont déduites de la map : rien à régler à la main quand elle change.
 */
@Script
class PlayerCamera : Camera2D() {

	@Register
	override fun _ready() {
		val ground = findGroundLayer()

		if (ground == null) {
			Logger.w("Aucun calque Background/Ground trouve : camera non bornee")
			return
		}

		applyLimits(ground)
	}

	/** Remonte jusqu'au noeud Level puis descend sur le calque de sol. */
	private fun findGroundLayer(): TileMapLayer? {
		var node: Node? = this

		while (node != null) {
			if (node.name.toString() == "Level") {
				return node.getNode("Background/Ground") as? TileMapLayer
			}
			node = node.getParent()
		}

		return null
	}

	private fun applyLimits(ground: TileMapLayer) {
		val rect = ground.getUsedRect()
		val grid = Globals.instance.gridSize

		val origin = ground.globalPosition
		val topLeft = origin + Vector2((rect.position.x * grid).toDouble(), (rect.position.y * grid).toDouble())
		val bottomRight = topLeft + Vector2((rect.size.x * grid).toDouble(), (rect.size.y * grid).toDouble())

		setLimit(Side.LEFT, topLeft.x.toInt())
		setLimit(Side.TOP, topLeft.y.toInt())
		setLimit(Side.RIGHT, bottomRight.x.toInt())
		setLimit(Side.BOTTOM, bottomRight.y.toInt())

		Logger.i("Limites camera : $topLeft -> $bottomRight")
	}
}
