package fr.skyle.pokeludoworld.scripts.gameplay.items

import godot.api.AtlasTexture
import godot.api.ResourceLoader
import godot.api.Texture2D
import godot.core.Rect2

/**
 * Icônes d'objets, découpées à la demande dans les trois atlas de
 * `assets/items` (voir son CREDITS.md pour retrouver une icône) :
 *
 * - `frlg:<numéro>` — les icônes officielles, numérotées de 0 à 266 ;
 * - `dex:<bloc>:<rangée>:<colonne>` — l'ItemDex, en hexadécimal comme sur la
 *   planche d'origine : `dex:01:0:3` ;
 * - `custom:<numéro>` — les icônes faites pour le jeu, à partir de 0.
 */
object ItemIcons {

	const val BACK = "frlg:226"
	const val UNKNOWN = "frlg:227"

	private const val DIR = "res://src/main/kotlin/fr/skyle/pokeludoworld/assets/items/"
	private const val SIZE = 24.0
	private const val ROW_COLUMNS = 16
	private const val DEX_BLOCKS_PER_ROW = 4
	private const val DEX_BLOCK_CELLS = 16

	private val cache = HashMap<String, Texture2D?>()

	/** L'icône désignée par [ref], ou le point d'interrogation si elle ne mène à rien. */
	fun of(ref: String): Texture2D? = cut(ref) ?: cut(UNKNOWN)

	private fun cut(ref: String): Texture2D? = cache.getOrPut(ref) {
		val parts = ref.split(":")
		val cell = when (parts[0]) {
			"frlg", "custom" -> parts.getOrNull(1)?.toIntOrNull()?.takeIf { it >= 0 }
				?.let { (it % ROW_COLUMNS) to (it / ROW_COLUMNS) }
			"dex" -> {
				val block = parts.getOrNull(1)?.toIntOrNull(16)
				val row = parts.getOrNull(2)?.toIntOrNull(16)
				val column = parts.getOrNull(3)?.toIntOrNull(16)
				if (block == null || row == null || column == null) {
					null
				} else {
					((block % DEX_BLOCKS_PER_ROW) * DEX_BLOCK_CELLS + column) to
						((block / DEX_BLOCKS_PER_ROW) * DEX_BLOCK_CELLS + row)
				}
			}
			else -> null
		} ?: return@getOrPut null

		val file = when (parts[0]) {
			"frlg" -> "frlg.png"
			"custom" -> "custom.png"
			else -> "itemdex.png"
		}
		val sheet = ResourceLoader.load(DIR + file) as? Texture2D ?: return@getOrPut null
		// Une case hors de la planche ne montre rien : autant dire que la référence est fausse.
		if ((cell.first + 1) * SIZE > sheet.getWidth() || (cell.second + 1) * SIZE > sheet.getHeight()) {
			return@getOrPut null
		}

		AtlasTexture().apply {
			atlas = sheet
			region = Rect2(cell.first * SIZE, cell.second * SIZE, SIZE, SIZE)
		}
	}
}
