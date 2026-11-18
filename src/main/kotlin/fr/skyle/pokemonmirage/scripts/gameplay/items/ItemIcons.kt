package fr.skyle.pokemonmirage.scripts.gameplay.items

import godot.api.ResourceLoader
import godot.api.Texture2D

/**
 * Les icônes d'objets : **un fichier par icône**, de 32 x 32, sous `assets/items/icons/`.
 *
 * - à la racine : les objets du pack de données, sous leur nom — `potion.png`,
 *   `super_repel.png` (`tools/gamedata.py`) ;
 * - `custom/` : les icônes faites pour ce jeu — `clear_bell.png` ;
 * - `other/` : les quelques icônes venues d'ailleurs, sous le nom de leur
 *   case d'origine — `07_F_2_fan.png`.
 *
 * Une icône se désigne par son nom seul quand elle vient du pack (`potion`),
 * par son dossier et son fichier sinon (`custom/clear_bell`,
 * `other/07_F_2_fan`). **Le nom d'un fichier dit ce qu'est l'icône, jamais à
 * quoi le jeu l'emploie.** Voir `assets/items/CREDITS.md`.
 */
object ItemIcons {

	/** La flèche de la ligne « Retour » du sac, et l'icône d'un objet qui n'en a pas. */
	const val BACK = "other/00_F_F_special"
	const val UNKNOWN = "other/frlg_227"

	private const val DIR = "res://src/main/kotlin/fr/skyle/pokemonmirage/assets/items/icons/"

	private val cache = HashMap<String, Texture2D?>()

	/** L'icône désignée par [icon], ou le point d'interrogation si aucun fichier ne lui répond. */
	fun of(icon: String): Texture2D? = load(icon) ?: load(UNKNOWN)

	/** Vrai si le fichier que désigne [icon] existe. */
	fun has(icon: String): Boolean = ResourceLoader.exists(path(icon))

	private fun load(icon: String): Texture2D? = cache.getOrPut(icon) {
		if (has(icon)) ResourceLoader.load(path(icon)) as? Texture2D else null
	}

	/** Un nom seul est à la racine, celle du pack ; `dossier/fichier` se lit tel quel. */
	private fun path(icon: String): String = "$DIR$icon.png"
}
