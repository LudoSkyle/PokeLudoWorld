package fr.skyle.pokeludoworld.scripts.gameplay.wild

import fr.skyle.pokeludoworld.scripts.log.Logger
import fr.skyle.pokeludoworld.scripts.ui.MessageBox
import fr.skyle.pokeludoworld.scripts.ui.N
import godot.api.Node
import godot.api.Node2D
import godot.api.TileMapLayer
import kotlin.random.Random

/**
 * Les rencontres de Pokémon sauvages dans les hautes herbes.
 *
 * Chaque fois que le joueur **se pose** sur une case d'herbe, on tire au sort :
 * la carte donne la chance d'une rencontre, en pour cent par pas
 * (`metadata/encounter_rate` sur son nœud `Level`). Sans ce réglage, ou à 0,
 * ses herbes sont vides.
 *
 * Pour l'instant une rencontre ne fait que s'annoncer : il n'y a ni espèces ni
 * combat. C'est ici qu'ils se brancheront.
 */
object WildEncounters {

	/** Le réglage de la carte : la chance d'une rencontre à chaque pas dans l'herbe, de 0 à 100. */
	const val RATE_META = "encounter_rate"

	/** L'annonce d'une rencontre, en attendant le combat. */
	val ANNOUNCE = N("Un Pokémon sauvage apparaît !")

	/**
	 * Le sort imposé : true, chaque pas dans l'herbe d'une carte peuplée donne
	 * une rencontre ; false, aucun ; null, le hasard décide. Sert à la mise au
	 * point et aux tests, qui ne peuvent pas compter sur la chance.
	 */
	var forced: Boolean? = null

	/** Le nombre de rencontres depuis le lancement. */
	var count = 0
		private set

	/**
	 * Le joueur [player] vient de se poser sur une case. Tire une rencontre
	 * s'il est dans l'herbe ; renvoie true si elle a lieu.
	 */
	fun step(player: Node2D): Boolean {
		val level = levelOf(player) ?: return false
		val rate = rateOf(level)
		if (rate <= 0 || !inGrass(level, player)) return false
		if (!roll(rate)) return false

		count++
		Logger.i("Wild encounter! (rate $rate %)")
		MessageBox.instance?.play(listOf(ANNOUNCE))
		return true
	}

	/** Tire au sort : vrai [rate] fois sur cent. */
	fun roll(rate: Int): Boolean = forced ?: (Random.nextInt(100) < rate)

	/** La chance d'une rencontre sur la carte [level], bornée de 0 à 100. */
	fun rateOf(level: Node): Int =
		(level.getMeta(RATE_META, 0).toString().toDoubleOrNull() ?: 0.0).toInt().coerceIn(0, 100)

	private fun inGrass(level: Node, player: Node2D): Boolean {
		val grass = (if (level.hasNode(GRASS)) level.getNode(GRASS) else null) as? TileMapLayer ?: return false
		return grass.getCellSourceId(grass.localToMap(grass.toLocal(player.globalPosition))) != -1
	}

	private fun levelOf(player: Node2D): Node? {
		var node: Node? = player.getParent()
		while (node != null && node.name.toString() != LEVEL) node = node.getParent()
		return node
	}

	private const val LEVEL = "Level"
	private const val GRASS = "Background/Grass"
}
