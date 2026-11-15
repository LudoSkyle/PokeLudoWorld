package fr.skyle.pokeludoworld.scripts.gameplay.characters

import fr.skyle.pokeludoworld.scripts.autoload.Globals
import fr.skyle.pokeludoworld.scripts.log.Logger
import godot.annotation.Register
import godot.annotation.Script
import godot.api.Camera2D
import godot.api.Node
import godot.api.TileMapLayer
import godot.core.Rect2i
import godot.core.Side
import godot.core.Vector2
import godot.core.Vector2i
import kotlin.math.roundToInt

/**
 * Caméra centrée sur le joueur, bornée à l'étendue réelle du calque Ground.
 * Les limites sont déduites de la carte : rien à régler à la main quand elle
 * change — mais [applyLimits] doit être rappelée après un changement de carte,
 * le joueur étant reparenté sans repasser par `_ready`.
 */
@Script
class PlayerCamera : Camera2D() {

	@Register
	override fun _ready() {
		applyLimits()
	}

	fun applyLimits() {
		val ground = findGroundLayer()

		if (ground == null) {
			Logger.w("Aucun calque Background/Ground trouve : camera non bornee")
			return
		}

		val rect = contentRect(ground)
		val grid = Globals.instance.gridSize

		val origin = ground.globalPosition
		val topLeft = origin + Vector2((rect.position.x * grid).toDouble(), (rect.position.y * grid).toDouble())
		val bottomRight = topLeft + Vector2((rect.size.x * grid).toDouble(), (rect.size.y * grid).toDouble())

		// Ce que l'écran montre du monde : une carte plus petite que lui sur un
		// axe est centrée sur cet axe, au lieu d'être plaquée contre un bord.
		val view = getViewportRect().size / zoom
		val (left, right) = centered(topLeft.x, bottomRight.x, view.x)
		val (top, bottom) = centered(topLeft.y, bottomRight.y, view.y)

		setLimit(Side.LEFT, left)
		setLimit(Side.TOP, top)
		setLimit(Side.RIGHT, right)
		setLimit(Side.BOTTOM, bottom)

		Logger.i("Limites camera : $topLeft -> $bottomRight")
	}

	/**
	 * L'étendue de la carte, en cases : son sol, sans le **noir de remplissage**
	 * qui entoure les pièces d'intérieur, plus ce que portent les autres calques
	 * du fond (les murs dépassent du sol par le haut). Une carte d'extérieur n'a
	 * pas de noir : c'est tout son sol.
	 */
	private fun contentRect(ground: TileMapLayer): Rect2i {
		var rect: Rect2i? = null
		fun add(cell: Vector2i) {
			val one = Rect2i(cell, Vector2i(1, 1))
			rect = rect?.merge(one) ?: one
		}

		val cells = ground.getUsedCells()
		for (index in 0 until cells.size) {
			val cell = cells[index]
			if (ground.getCellSourceId(cell) == VOID_SOURCE && ground.getCellAtlasCoords(cell) == VOID_TILE) continue
			add(cell)
		}

		val siblings = ground.getParent()?.getChildren()
		if (siblings != null) {
			for (index in 0 until siblings.size) {
				val layer = siblings[index] as? TileMapLayer ?: continue
				if (layer === ground) continue
				val used = layer.getUsedCells()
				for (at in 0 until used.size) add(used[at])
			}
		}
		return rect ?: ground.getUsedRect()
	}

	/**
	 * Les limites d'un axe, de [from] à [to]. Si la carte y est plus courte que
	 * l'écran ([span]), elles sont élargies d'autant de chaque côté : la carte
	 * se retrouve au milieu, et la caméra ne bouge plus sur cet axe.
	 */
	private fun centered(from: Double, to: Double, span: Double): Pair<Int, Int> {
		if (to - from >= span) return from.toInt() to to.toInt()
		val middle = (from + to) / 2.0
		return (middle - span / 2.0).roundToInt() to (middle + span / 2.0).roundToInt()
	}

	/** Remonte jusqu'au noeud Level puis descend sur le calque de sol. */
	private fun findGroundLayer(): TileMapLayer? {
		var node: Node? = this

		while (node != null) {
			if (node.name.toString() == "Level") {
				return if (node.hasNode("Background/Ground")) {
					node.getNode("Background/Ground") as? TileMapLayer
				} else {
					null
				}
			}
			node = node.getParent()
		}

		return null
	}

	companion object {
		/** La tuile noire qui remplit le tour des pièces d'intérieur, dans `Background/Ground`. */
		private const val VOID_SOURCE = 5
		private val VOID_TILE = Vector2i(65, 49)
	}
}
