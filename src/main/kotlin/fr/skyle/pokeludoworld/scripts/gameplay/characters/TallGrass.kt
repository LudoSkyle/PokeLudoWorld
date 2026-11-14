package fr.skyle.pokeludoworld.scripts.gameplay.characters

import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.Node
import godot.api.Node2D
import godot.api.TileMapLayer
import godot.core.Vector2i

/**
 * Les hautes herbes sous un personnage, joueur ou PNJ, comme dans les jeux
 * d'origine. Chaque case d'herbe est faite de **deux tuiles** :
 *
 * - la touffe entière, dans `Background/Grass`, **sous** les personnages ;
 * - sa moitié basse, dans `World/GrassFront`, **par-dessus** celui qui se
 *   tient sur la case : il a l'air d'être dans l'herbe jusqu'à la taille.
 *
 * Les deux sont fixées à la case : rien n'est attaché au personnage, donc rien
 * ne le suit quand il marche. Le calque de devant est trié en Y comme le
 * décor : il passe devant le personnage de sa case, et derrière la tête de
 * celui de la case du dessous.
 *
 * Ce nœud, enfant du personnage, fait deux choses : il crée le calque de
 * devant s'il manque, et il fait **bruisser** la case où le personnage vient
 * d'entrer — la touffe s'écarte puis se referme, sur place.
 */
@Script
class TallGrass : Node() {

	/** Durée de chaque état de la touffe qui bruisse, en secondes. */
	@Category("Animation")
	@Export
	var frameSeconds: Double = 0.07

	private var body: Node2D? = null

	/** La carte où l'on a cherché les calques, pour les rechercher quand le personnage en change. */
	private var searchedIn: Node? = null
	private var grass: TileMapLayer? = null
	private var front: TileMapLayer? = null

	private var lastCell: Vector2i? = null

	/** Une case qui bruisse : la case, et le temps écoulé. */
	private class Rustle(val cell: Vector2i, var elapsed: Double = 0.0)

	private val rustles = ArrayList<Rustle>()

	@Register
	override fun _ready() {
		body = getParent() as? Node2D
	}

	@Register
	override fun _process(delta: Double) {
		val node = body ?: return
		findLayers(node)
		animate(delta)

		val layer = grass
		if (layer == null) {
			lastCell = null
			return
		}

		val cell = layer.localToMap(layer.toLocal(node.globalPosition))
		if (cell == lastCell) return
		lastCell = cell
		if (layer.getCellSourceId(cell) != -1 && rustles.none { it.cell == cell }) rustles.add(Rustle(cell))
	}

	/** Fait passer chaque case qui bruisse par ses états, puis la remet dressée. */
	private fun animate(delta: Double) {
		if (rustles.isEmpty()) return

		val done = ArrayList<Rustle>()
		for (rustle in rustles) {
			rustle.elapsed += delta
			val step = (rustle.elapsed / frameSeconds).toInt()
			if (step >= STATES.size) {
				show(rustle.cell, STANDING)
				done.add(rustle)
			} else {
				show(rustle.cell, STATES[step])
			}
		}
		rustles.removeAll(done)
	}

	/** Montre l'état [state] sur les deux tuiles de la case. */
	private fun show(cell: Vector2i, state: Int) {
		val layer = grass ?: return
		// La case a pu être retirée entre-temps : on ne repose pas d'herbe là où il n'y en a plus.
		if (layer.getCellSourceId(cell) == -1) return
		layer.setCell(cell, WHOLE, Vector2i(state, 0))
		front?.setCell(cell, BOTTOM, Vector2i(state, 0))
	}

	/** Trouve les deux calques d'herbe de la carte où se trouve le personnage. */
	private fun findLayers(node: Node2D) {
		val holder = node.getParent()
		if (holder === searchedIn) return

		// Le joueur change de carte en changeant de parent : l'ancienne part avec
		// ses herbes, on cherche celles de la nouvelle.
		searchedIn = holder
		rustles.clear()
		lastCell = null
		grass = null
		front = null

		var level: Node? = holder
		while (level != null && level.name.toString() != LEVEL) level = level.getParent()
		val root = level ?: return
		val layer = (if (root.hasNode(GRASS)) root.getNode(GRASS) else null) as? TileMapLayer ?: return
		grass = layer
		front = (if (root.hasNode("$WORLD/$FRONT")) root.getNode("$WORLD/$FRONT") else null) as? TileMapLayer
			?: plantFront(root, layer)
	}

	/**
	 * Crée le calque de devant : la moitié basse de chaque touffe, sur les
	 * mêmes cases, parmi le décor trié en Y. Le premier personnage qui arrive
	 * sur la carte s'en charge ; les autres le trouvent.
	 */
	private fun plantFront(root: Node, layer: TileMapLayer): TileMapLayer? {
		val world = (if (root.hasNode(WORLD)) root.getNode(WORLD) else null) as? Node2D ?: return null

		val bottoms = TileMapLayer()
		bottoms.setName(FRONT)
		bottoms.tileSet = layer.tileSet
		bottoms.ySortEnabled = true
		world.addChild(bottoms)
		bottoms.globalPosition = layer.globalPosition

		val cells = layer.getUsedCells()
		for (index in 0 until cells.size) {
			val cell = cells[index]
			bottoms.setCell(cell, BOTTOM, Vector2i(layer.getCellAtlasCoords(cell).x, 0))
		}
		return bottoms
	}

	@Register
	override fun _exitTree() {
		// Une herbe ne reste pas écartée derrière un personnage qui disparaît.
		if (grass?.isInsideTree() == true) rustles.forEach { show(it.cell, STANDING) }
		rustles.clear()
		searchedIn = null
		grass = null
		front = null
	}

	companion object {
		private const val LEVEL = "Level"
		private const val WORLD = "World"
		private const val GRASS = "Background/Grass"
		private const val FRONT = "GrassFront"

		/** Sources du TileSet : la touffe entière, et sa moitié basse. */
		private const val WHOLE = 5
		private const val BOTTOM = 9

		/** Les trois états de la touffe, colonnes de la rangée 0 : dressée, qui s'écarte, écartée. */
		private const val STANDING = 6
		private val STATES = listOf(7, 8, 8, 7)
	}
}
