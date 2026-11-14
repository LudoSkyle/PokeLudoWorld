package fr.skyle.pokeludoworld.scripts.core

import godot.api.OS

/**
 * Fichiers que le jeu écrit chez le joueur. Lancé avec `-- --test`, il écrit
 * ailleurs : les tests ne touchent ni aux réglages ni à la sauvegarde du
 * joueur.
 */
object GameFiles {

	val testing: Boolean by lazy {
		val args = OS.getCmdlineUserArgs()
		(0 until args.size).any { args[it] == "--test" }
	}

	val settings: String
		get() = if (testing) "user://test_settings.cfg" else "user://settings.cfg"

	val save: String
		get() = if (testing) "user://test_save.cfg" else "user://save.cfg"
}
