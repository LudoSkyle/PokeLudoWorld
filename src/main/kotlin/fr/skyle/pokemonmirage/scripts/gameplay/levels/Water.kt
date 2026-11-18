package fr.skyle.pokemonmirage.scripts.gameplay.levels

import godot.api.Node
import godot.api.Node2D
import godot.api.TileMapLayer
import godot.core.Vector2

/**
 * Ce que le jeu appelle de l'eau : les tuiles qui portent la donnée perso
 * `water` du TileSet (voir docs/tilesets.md).
 *
 * Deux composants s'en servent — le reflet d'un personnage, et l'ombre d'un
 * Pokémon en vol qui bleuit au-dessus de la mer —, d'où ce petit atelier
 * commun plutôt que deux fois le même parcours de calques.
 */
object Water {

	private const val LEVEL = "Level"
	private const val BACKGROUND = "Background"
	private const val NAME = "water"

	/** La carte où vit ce nœud, en remontant ses parents. */
	fun levelOf(node: Node): Node? {
		var level: Node? = node
		while (level != null && level.name.toString() != LEVEL) level = level.getParent()
		return level
	}

	/** Le fond de la carte : c'est là que sont les sols, et là qu'on range ce qui s'y pose. */
	fun backgroundOf(level: Node): Node2D? =
		(if (level.hasNode(BACKGROUND)) level.getNode(BACKGROUND) else null) as? Node2D

	/** Les calques de sol, dans leur ordre de dessin. */
	fun groundLayers(background: Node2D): List<TileMapLayer> {
		val found = ArrayList<TileMapLayer>()
		for (index in 0 until background.getChildCount()) {
			(background.getChild(index) as? TileMapLayer)?.let { found.add(it) }
		}
		return found
	}

	/**
	 * La case qui contient [point] est-elle de l'eau ? **C'est le calque le plus
	 * haut qui le dit** : une planche de ponton posée sur la mer n'est pas de
	 * l'eau, et rien ne s'y mire ni ne s'y projette.
	 */
	fun isWater(layers: List<TileMapLayer>, point: Vector2): Boolean {
		for (index in layers.indices.reversed()) {
			val layer = layers[index]
			val cell = layer.localToMap(layer.toLocal(point))
			if (layer.getCellSourceId(cell) == -1) continue
			return layer.getCellTileData(cell)?.getCustomData(NAME) as? Boolean == true
		}
		return false
	}
}
