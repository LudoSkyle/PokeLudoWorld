package fr.skyle.pokeludoworld.scripts.gameplay.items

import godot.api.ResourceLoader
import godot.api.Texture2D

/**
 * Les icônes d'objets : **un fichier par icône**, sous `assets/items/icons/`.
 *
 * - `named/` : les objets officiels qu'on sait nommer — `potion.png`,
 *   `super_repel.png`. Quand un objet a plusieurs dessins, le premier porte
 *   son nom et les autres leur origine (`old_rod-old_colors.png`) ; une
 *   ancienne version officielle porte sa génération (`town_map_gen3.png`).
 * - `unnamed/` : les objets officiels dont on n'a pas le nom, sous le numéro
 *   de leur case — `07_F_2_fan.png`.
 * - `custom/` : les icônes faites pour ce jeu — `clear_bell.png`.
 *
 * Une icône se désigne par son nom seul quand elle est dans `named/`
 * (`potion`), par son dossier et son fichier sinon (`custom/clear_bell`,
 * `unnamed/07_F_2_fan`). **Le nom d'un fichier dit ce qu'est l'icône, jamais
 * à quoi le jeu l'emploie** : se servir d'une icône sans nom ne la renomme
 * pas.
 *
 * Les dossiers sont fabriqués par `tools/item_icons.py` (voir
 * `assets/items/CREDITS.md`).
 */
object ItemIcons {

	/** La flèche de la ligne « Retour » du sac, et l'icône d'un objet qui n'en a pas. */
	const val BACK = "unnamed/00_F_F_special"
	const val UNKNOWN = "unnamed/frlg_227"

	private const val DIR = "res://src/main/kotlin/fr/skyle/pokeludoworld/assets/items/icons/"

	private val cache = HashMap<String, Texture2D?>()

	/** L'icône désignée par [icon], ou le point d'interrogation si aucun fichier ne lui répond. */
	fun of(icon: String): Texture2D? = load(icon) ?: load(UNKNOWN)

	/** Vrai si le fichier que désigne [icon] existe. */
	fun has(icon: String): Boolean = ResourceLoader.exists(path(icon))

	private fun load(icon: String): Texture2D? = cache.getOrPut(icon) {
		if (has(icon)) ResourceLoader.load(path(icon)) as? Texture2D else null
	}

	/** Un nom seul est dans `named/` ; `dossier/fichier` se lit tel quel. */
	private fun path(icon: String): String = if ('/' in icon) "$DIR$icon.png" else "${DIR}named/$icon.png"
}
