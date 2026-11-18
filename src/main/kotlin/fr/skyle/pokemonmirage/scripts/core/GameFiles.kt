package fr.skyle.pokemonmirage.scripts.core

import godot.api.OS

/**
 * Fichiers que le jeu écrit chez le joueur. Lancé avec `-- --test`, il écrit
 * ailleurs : les tests ne touchent ni aux réglages ni aux sauvegardes du
 * joueur.
 */
object GameFiles {

	val testing: Boolean by lazy {
		val args = OS.getCmdlineUserArgs()
		(0 until args.size).any { args[it] == "--test" }
	}

	val settings: String
		get() = if (testing) "user://test_settings.cfg" else "user://settings.cfg"

	/** La sauvegarde de l'emplacement [slot], compté à partir de 1. */
	fun save(slot: Int): String = if (testing) "user://test_save_$slot.cfg" else "user://save_$slot.cfg"

	/** L'unique sauvegarde d'avant les emplacements : elle devient celle du premier. */
	val oldSave: String
		get() = if (testing) "user://test_save.cfg" else "user://save.cfg"
}
