package fr.skyle.pokemonmirage.scripts.gameplay.pokemon

import fr.skyle.pokemonmirage.scripts.log.Logger
import godot.api.FileAccess

/**
 * Une espèce du Pokédex national : son numéro, ses noms et sa catégorie en
 * français et en anglais, sa taille en mètres, son poids en kilos, ses deux
 * descriptions, et ce qu'on a d'elle en image — son icône, son sprite de marche.
 * Un champ de texte vide, une taille à zéro : la donnée manque.
 */
data class DexEntry(
	val number: Int,
	val id: String,
	val generation: Int,
	val nameFr: String,
	val nameEn: String,
	val genusFr: String,
	val genusEn: String,
	val height: Double,
	val weight: Double,
	val hasIcon: Boolean,
	val hasOverworld: Boolean,
	val textFr: String,
	val textEn: String,
) {
	/** Ce qui manque à cette espèce, en clair : vide quand tout y est. */
	val missing: List<String>
		get() = buildList {
			if (nameFr.isEmpty()) add("nom FR")
			if (nameEn.isEmpty()) add("nom EN")
			if (height <= 0.0) add("taille")
			if (weight <= 0.0) add("poids")
			if (textFr.isEmpty()) add("texte FR")
			if (textEn.isEmpty()) add("texte EN")
			if (!hasIcon) add("icône")
			if (!hasOverworld) add("sprite")
		}
}

/**
 * Le Pokédex national : toutes les espèces qui existent, dans l'ordre de leur
 * numéro. Il se lit dans `resources/pokedex/national.tsv`, que fabrique
 * `tools/pokedex.py` — une espèce par ligne, ses champs séparés par des
 * tabulations. Ce n'est pas le catalogue des espèces du jeu ([Dex]) : pour
 * l'instant il ne sert qu'à la vue de debug, qui montre ce qui est renseigné.
 */
object NationalDex {

	const val PATH = "res://src/main/kotlin/fr/skyle/pokemonmirage/resources/pokedex/national.tsv"
	const val ICONS = "res://src/main/kotlin/fr/skyle/pokemonmirage/assets/pokemon/icons.png"

	/**
	 * Le dossier des sprites de marche : un fichier par espèce, `<id>.png` — deux colonnes de quatre images carrées
	 * (dos, dos, face, face ; gauche, gauche, droite, droite), de 32 pixels de côté, ou 64 pour un gros Pokémon.
	 */
	const val OVERWORLD_DIR = "res://src/main/kotlin/fr/skyle/pokemonmirage/assets/pokemon/overworld/"

	/** Espèces par rangée de la planche d'icônes ; une case fait 64 x 32 (deux images de 32 x 32). */
	const val ICON_COLUMNS = 25

	val all: List<DexEntry> by lazy { read() }

	fun get(number: Int): DexEntry? = all.getOrNull(number - 1)

	private fun read(): List<DexEntry> {
		val text = FileAccess.getFileAsString(PATH)
		if (text.isEmpty()) {
			Logger.e("Pokedex national illisible : $PATH")
			return emptyList()
		}
		return text.lineSequence()
			.filter { it.isNotBlank() && !it.startsWith("#") }
			.mapNotNull { line -> entry(line.split('\t')) }
			.toList()
	}

	private fun entry(cells: List<String>): DexEntry? {
		if (cells.size < FIELDS) {
			Logger.e("Pokedex national : ligne incomplete (${cells.size} champs)")
			return null
		}
		return DexEntry(
			number = cells[0].toIntOrNull() ?: return null,
			id = cells[1],
			generation = cells[2].toIntOrNull() ?: 0,
			nameFr = cells[3],
			nameEn = cells[4],
			genusFr = cells[5],
			genusEn = cells[6],
			height = cells[7].toDoubleOrNull() ?: 0.0,
			weight = cells[8].toDoubleOrNull() ?: 0.0,
			hasIcon = cells[9] == "1",
			hasOverworld = cells[10] == "1",
			textFr = cells[11],
			textEn = cells[12],
		)
	}

	private const val FIELDS = 13
}
