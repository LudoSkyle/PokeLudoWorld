package fr.skyle.pokeludoworld.scripts.gameplay.levels

import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.Node
import godot.api.Node2D
import godot.api.Polygon2D
import godot.api.TileMapLayer
import godot.core.Color
import godot.core.Vector2

/**
 * L'ombre d'un Pokémon qui vole **bleuit au-dessus de l'eau**.
 *
 * On ne lui donne pas de reflet : de lui on ne voit déjà, sur terre, qu'une
 * tache d'ombre, et il vole trop haut pour que l'eau en renvoie l'image. Ce
 * qu'on voit dessous reste donc une ombre — mais l'eau ne l'avale pas comme la
 * terre : elle la teinte.
 *
 * Rien d'autre ne change : l'ombre garde sa forme, sa taille et sa place sous
 * lui. C'est [Water] qui dit ce qui est de l'eau, une tuile à la fois.
 */
@Script
class WaterShadow : Node() {

	/** Le nœud frère qui porte l'ombre. */
	@Category("Ombre")
	@Export
	var shadowName: String = "Shadow"

	/** La ligne où son ombre se pose, depuis son origine, en pixels. */
	@Category("Ombre")
	@Export
	var groundOffset: Double = 6.0

	/** Sa couleur sur la terre ferme. */
	@Category("Ombre")
	@Export
	var onLand: Color = Color(0.0, 0.0, 0.0, 0.26)

	/**
	 * Sa couleur sur l'eau : un turquoise sombre, choisi sur rendu parmi trois.
	 * Il se fond dans la mer — on dirait une ondulation de plus —, là où un bleu
	 * franc faisait une tache qui tirait l'œil plus que l'oiseau lui-même.
	 */
	@Category("Ombre")
	@Export
	var onWater: Color = Color(0.0, 0.33, 0.4, 0.33)

	private var body: Node2D? = null
	private var shadow: Polygon2D? = null

	/** La carte où l'on a cherché l'eau, pour la rechercher quand il en change. */
	private var searchedIn: Node? = null
	private var layers: List<TileMapLayer> = emptyList()

	@Register
	override fun _ready() {
		body = getParent() as? Node2D
		shadow = (body?.getNodeOrNull(shadowName)) as? Polygon2D
	}

	@Register
	override fun _process(delta: Double) {
		val node = body ?: return
		val shadow = shadow ?: return
		findWater(node)

		val under = node.globalPosition + Vector2(0.0, groundOffset + 1.0)
		shadow.color = if (Water.isWater(layers, under)) onWater else onLand
	}

	private fun findWater(node: Node2D) {
		val parent = node.getParent()
		if (parent === searchedIn) return

		searchedIn = parent
		layers = emptyList()
		val level = Water.levelOf(parent ?: node) ?: return
		val background = Water.backgroundOf(level) ?: return
		layers = Water.groundLayers(background)
	}

	@Register
	override fun _exitTree() {
		searchedIn = null
		layers = emptyList()
	}
}
