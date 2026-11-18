package fr.skyle.pokemonmirage.scripts.gameplay.wild

import fr.skyle.pokemonmirage.scripts.gameplay.pokemon.Dex
import fr.skyle.pokemonmirage.scripts.gameplay.pokemon.Species
import kotlin.random.Random

/** Un Pokémon sauvage rencontré : son espèce et son niveau. */
data class WildPokemon(val species: Species, val level: Int)

/** Une ligne de table : une espèce, sa fourchette de niveaux, et son poids dans le tirage. */
data class WildSlot(val species: Species, val levels: IntRange, val weight: Int)

/**
 * La table de rencontres d'une carte : qui vit dans ses herbes, à quel niveau,
 * et en quelle proportion.
 *
 * Elle s'écrit sur le nœud `Level` de la carte, en une ligne :
 *
 * ```
 * metadata/wild = "mulotin:2-4*50 | piafeuille:2-5*35 | chenibulle:3*15"
 * ```
 *
 * Chaque entrée est `espèce:niveaux*poids`. Les niveaux sont une fourchette
 * (`2-4`) ou un seul (`3`). Le poids est la part de l'espèce dans le tirage,
 * par rapport au total — ici 50, 35 et 15 sur 100 ; sans `*poids`, il vaut 1.
 */
class WildTable(val slots: List<WildSlot>, val errors: List<String> = emptyList()) {

	val isEmpty: Boolean
		get() = slots.isEmpty()

	/** Tire un Pokémon : une ligne selon les poids, puis un niveau dans sa fourchette. */
	fun pick(random: Random): WildPokemon? {
		if (slots.isEmpty()) return null

		var draw = random.nextInt(slots.sumOf { it.weight })
		val slot = slots.first { draw -= it.weight; draw < 0 }
		return WildPokemon(slot.species, slot.levels.random(random))
	}

	companion object {
		const val MAX_LEVEL = 100

		private val ENTRY = Regex("""(\w+)\s*:\s*(\d+)(?:\s*-\s*(\d+))?(?:\s*\*\s*(\d+))?""")

		/**
		 * Lit une table. Une entrée mal écrite est écartée et signalée dans
		 * [errors] : la carte garde ses autres espèces.
		 */
		fun parse(text: String): WildTable {
			val slots = ArrayList<WildSlot>()
			val errors = ArrayList<String>()

			for (raw in text.split("|").map { it.trim() }.filter { it.isNotEmpty() }) {
				val match = ENTRY.matchEntire(raw)
				if (match == null) {
					errors.add("'$raw' : attendu espèce:niveaux*poids")
					continue
				}
				val (id, from, to, weight) = match.destructured
				val species = Dex.get(id)
				val low = from.toInt()
				val high = to.toIntOrNull() ?: low
				val share = weight.toIntOrNull() ?: 1
				when {
					species == null -> errors.add("'$raw' : espèce inconnue '$id'")
					low < 1 || high > MAX_LEVEL || low > high -> errors.add("'$raw' : niveaux de 1 à $MAX_LEVEL, du plus bas au plus haut")
					share < 1 -> errors.add("'$raw' : le poids vaut au moins 1")
					else -> slots.add(WildSlot(species, low..high, share))
				}
			}
			return WildTable(slots, errors)
		}
	}
}
