package fr.skyle.pokemonmirage.scripts.gameplay.pokemon

import fr.skyle.pokemonmirage.scripts.ui.N

/** Le type d'une espèce. Rien ne s'en sert encore : il attend le combat. */
enum class PokemonType {
	NORMAL, FIRE, WATER, GRASS, ELECTRIC, ICE, FIGHTING, POISON, GROUND,
	FLYING, PSYCHIC, BUG, ROCK, GHOST, DRAGON, DARK, STEEL, FAIRY,
}

/** Les six statistiques de base d'une espèce. */
data class BaseStats(
	val hp: Int,
	val attack: Int,
	val defense: Int,
	val specialAttack: Int,
	val specialDefense: Int,
	val speed: Int,
)

/**
 * Une espèce de Pokémon. [id] est son nom dans les tables de rencontre des
 * cartes, et plus tard dans la sauvegarde. [name] est en français et se
 * traduit à l'affichage. Une espèce a un ou deux [types].
 */
data class Species(
	val id: String,
	val name: String,
	val types: List<PokemonType>,
	val stats: BaseStats,
)

/**
 * Le catalogue des espèces. Ajouter une espèce : une ligne ici, et son nom
 * dans `locale/en.po`.
 *
 * Les trois espèces ci-dessous sont **provisoires**, inventées pour faire
 * tourner les rencontres : à remplacer par les vraies.
 */
object Dex {

	val ALL = listOf(
		Species("mulotin", N("Mulotin"), listOf(PokemonType.NORMAL), BaseStats(32, 50, 34, 26, 34, 68)),
		Species("piafeuille", N("Piafeuille"), listOf(PokemonType.NORMAL, PokemonType.FLYING), BaseStats(40, 44, 40, 36, 36, 56)),
		Species("chenibulle", N("Chenibulle"), listOf(PokemonType.BUG), BaseStats(44, 30, 36, 22, 22, 44)),
	)

	private val byId = ALL.associateBy { it.id }

	fun get(id: String): Species? = byId[id]
}
