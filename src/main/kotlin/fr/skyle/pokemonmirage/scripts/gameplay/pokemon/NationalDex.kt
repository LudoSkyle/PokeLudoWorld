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
	/** Son portrait de face, 96 x 96, est-il là ? C'est lui que montre la fiche du Pokédex. */
	val hasFront: Boolean = false,
	/** Ses types, un ou deux, par leur nom dans le pack de données (`grass`, `poison`). */
	val types: List<String> = emptyList(),
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
			if (!hasFront) add("portrait")
		}
}

/**
 * Le Pokédex national : toutes les espèces qui existent, dans l'ordre de leur
 * numéro. Il se lit dans `resources/pokedex/national.tsv`, que fabrique
 * `tools/gamedata.py`, depuis le pack de données — une espèce par ligne, ses champs séparés par des
 * tabulations. Ce n'est pas le catalogue des espèces du jeu ([Dex]) : pour
 * l'instant il ne sert qu'à la vue de debug, qui montre ce qui est renseigné.
 */
object NationalDex {

	const val PATH = "res://src/main/kotlin/fr/skyle/pokemonmirage/resources/pokedex/national.tsv"
	/** Le dossier des icônes : un fichier par espèce, `<id>.png`, de 64 x 32 — deux images de 32 x 32. */
	const val ICONS_DIR = "res://src/main/kotlin/fr/skyle/pokemonmirage/assets/pokemon/icons/"

	/**
	 * Le dossier des sprites sur la carte : un fichier par espèce, `<id>.png` — quatre rangées (bas, gauche, droite,
	 * haut) de quatre images carrées, de 32 pixels de côté ou plus pour un gros Pokémon.
	 */
	const val OVERWORLD_DIR = "res://src/main/kotlin/fr/skyle/pokemonmirage/assets/pokemon/overworld/"

	/** Le dossier des portraits de face : un fichier par espèce, `<id>.png`, de 96 x 96. */
	const val FRONT_DIR = "res://src/main/kotlin/fr/skyle/pokemonmirage/assets/pokemon/front/"
	val all: List<DexEntry> by lazy { read() }
	private val byId: Map<String, DexEntry> by lazy { all.associateBy { it.id } }
	/** L'espèce d'identifiant [id] (`bulbasaur`), ou null. */
	fun find(id: String): DexEntry? = byId[id]

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
			hasFront = cells.getOrNull(13) == "1",
			types = listOfNotNull(cells.getOrNull(14), cells.getOrNull(15)).filter { it.isNotBlank() },
		)
	}

	private const val FIELDS = 13
}
