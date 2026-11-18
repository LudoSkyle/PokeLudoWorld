package fr.skyle.pokemonmirage.scripts.gameplay.wild

import fr.skyle.pokemonmirage.scripts.log.Logger
import fr.skyle.pokemonmirage.scripts.ui.MessageBox
import fr.skyle.pokemonmirage.scripts.ui.N
import fr.skyle.pokemonmirage.scripts.ui.T
import godot.api.Node
import godot.api.Node2D
import godot.api.TileMapLayer
import kotlin.random.Random

/**
 * Les rencontres de Pokémon sauvages dans les hautes herbes.
 *
 * Chaque fois que le joueur **se pose** sur une case d'herbe, on tire au sort :
 * la carte donne la chance d'une rencontre, en pour cent par pas
 * (`metadata/encounter_rate` sur son nœud `Level`), et qui l'on y croise
 * (`metadata/wild`, voir [WildTable]). Sans l'un ou l'autre, ses herbes sont
 * vides.
 *
 * **Courir dans l'herbe dérange davantage** : un pas couru tire sur
 * `metadata/encounter_rate_run` si la carte le donne — 5 % contre 3 % au pas,
 * sur les cartes du jeu. Sans ce second réglage, courir ou marcher revient au
 * même.
 *
 * Pour l'instant une rencontre ne fait que s'annoncer, par le nom de l'espèce :
 * il n'y a pas encore de combat. C'est ici qu'il se branchera.
 */
object WildEncounters {

	/** Le réglage de la carte : la chance d'une rencontre à chaque pas dans l'herbe, de 0 à 100. */
	const val RATE_META = "encounter_rate"

	/** Le réglage de la carte : la même chance pour un pas couru. Absent : celle du pas marché. */
	const val RUN_RATE_META = "encounter_rate_run"

	/** Le réglage de la carte : sa table de rencontres. */
	const val TABLE_META = "wild"

	/** L'annonce d'une rencontre, en attendant le combat. Le trou est le nom de l'espèce. */
	val ANNOUNCE = N("Un %s sauvage apparaît !")

	/** Le hasard des rencontres. Les tests le remplacent par un hasard à graine, rejouable. */
	var random: Random = Random.Default

	/** Le dernier Pokémon rencontré, ou null s'il n'y en a pas encore eu. */
	var last: WildPokemon? = null
		private set

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
	 * Le joueur [player] vient de se poser sur une case, en courant ou non
	 * ([running]). Tire une rencontre s'il est dans l'herbe ; renvoie true si
	 * elle a lieu.
	 */
	fun step(player: Node2D, running: Boolean = false): Boolean {
		val level = levelOf(player) ?: return false
		val rate = rateOf(level, running)
		if (rate <= 0 || !inGrass(level, player)) return false
		if (!roll(rate)) return false
		val wild = tableOf(level).pick(random) ?: return false

		count++
		last = wild
		Logger.i("Wild encounter! ${wild.species.id} level ${wild.level} (rate $rate %)")
		// La phrase est déjà traduite, nom compris : la boîte la dira telle quelle.
		MessageBox.instance?.play(listOf(T(ANNOUNCE).format(T(wild.species.name))))
		return true
	}

	/** Tire au sort : vrai [rate] fois sur cent. */
	fun roll(rate: Int): Boolean = forced ?: (random.nextInt(100) < rate)

	/** La table de rencontres de la carte [level]. Ses entrées mal écrites sont signalées au journal. */
	fun tableOf(level: Node): WildTable {
		val table = WildTable.parse(level.getMeta(TABLE_META, "").toString())
		table.errors.forEach { Logger.e("Wild table: $it") }
		return table
	}

	/** La chance d'une rencontre par pas sur la carte [level], marché ou couru ([running]), bornée de 0 à 100. */
	fun rateOf(level: Node, running: Boolean = false): Int {
		val meta = if (running && level.hasMeta(RUN_RATE_META)) RUN_RATE_META else RATE_META
		return (level.getMeta(meta, 0).toString().toDoubleOrNull() ?: 0.0).toInt().coerceIn(0, 100)
	}

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
