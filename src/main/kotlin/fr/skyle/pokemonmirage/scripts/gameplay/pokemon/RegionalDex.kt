package fr.skyle.pokemonmirage.scripts.gameplay.pokemon

import fr.skyle.pokemonmirage.scripts.log.Logger
import godot.api.FileAccess

/**
 * Le Pokédex régional : **le seul qu'on ouvre en jeu**. C'est une liste
 * d'espèces dans l'ordre de la région — le numéro régional d'une espèce est sa
 * place dans la liste — et rien d'autre : leurs noms, leurs textes et leurs
 * images sont ceux du [NationalDex].
 *
 * La liste se lit dans `resources/pokedex/regional.json`, **au format des
 * Pokédex de Pokémon Studio** (les fichiers de `Data/Studio/dex/` du pack de données) :
 * un tableau `creatures` de `{ "dbSymbol": "bulbasaur", "form": 0 }`. Elle se
 * modifie à la main, ou dans Pokémon Studio. Pour l'instant ce sont les 151
 * espèces de la première génération, dans leur ordre.
 */
object RegionalDex {

	const val PATH = "res://src/main/kotlin/fr/skyle/pokemonmirage/resources/pokedex/regional.json"

	/** Les identifiants des espèces de la région, dans l'ordre. */
	val ids: List<String> by lazy { read() }

	/** Les fiches des espèces de la région, dans l'ordre. Une espèce inconnue du national est signalée et sautée. */
	val all: List<DexEntry> by lazy {
		ids.mapNotNull { id -> NationalDex.find(id) ?: null.also { Logger.e("Pokedex regional : espece inconnue du national : $id") } }
	}

	/** Le numéro régional de l'espèce [id], à partir de 1 ; 0 si elle n'est pas de la région. */
	fun number(id: String): Int = ids.indexOf(id) + 1

	fun has(id: String): Boolean = id in ids

	private fun read(): List<String> {
		val text = FileAccess.getFileAsString(PATH)
		if (text.isEmpty()) {
			Logger.e("Pokedex regional illisible : $PATH")
			return emptyList()
		}
		return parse(text)
	}

	/**
	 * Les identifiants que liste un Pokédex au format de Pokémon Studio, dans
	 * l'ordre, sans doublon. Seule la forme de base compte : une autre forme de
	 * la même espèce ne fait pas une seconde ligne.
	 */
	fun parse(json: String): List<String> {
		val creatures = json.substringAfter("\"creatures\"", "").substringAfter('[', "").substringBefore(']')
		return SYMBOL.findAll(creatures).map { it.groupValues[1] }.distinct().toList()
	}

	private val SYMBOL = Regex("\"dbSymbol\"\\s*:\\s*\"([^\"]+)\"")
}
