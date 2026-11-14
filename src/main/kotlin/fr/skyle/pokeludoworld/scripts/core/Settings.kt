package fr.skyle.pokeludoworld.scripts.core

import fr.skyle.pokeludoworld.scripts.log.Logger
import godot.api.ConfigFile
import godot.core.Error

/**
 * Réglages du joueur, gardés d'un lancement à l'autre dans
 * `user://settings.cfg`. Un seul pour l'instant : la vitesse du texte.
 */
object Settings {

	/** Multiplicateurs proposés : x0.5, x1, x2, x4. */
	val TEXT_SPEEDS = listOf(0.5, 1.0, 2.0, 4.0)

	/** Secondes par lettre à la vitesse x1. */
	const val BASE_SECONDS_PER_LETTER = 0.02

	const val DEFAULT_TEXT_SPEED = 1

	/** Indice dans [TEXT_SPEEDS]. */
	var textSpeed: Int = DEFAULT_TEXT_SPEED
		private set

	val secondsPerLetter: Double
		get() = BASE_SECONDS_PER_LETTER / TEXT_SPEEDS[textSpeed]

	private var loaded = false

	fun load() {
		if (loaded) return
		loaded = true

		val file = ConfigFile()
		if (file.load(PATH) != Error.OK) return
		val saved = (file.getValue(SECTION, TEXT_SPEED, DEFAULT_TEXT_SPEED) as? Number)?.toInt() ?: DEFAULT_TEXT_SPEED
		textSpeed = saved.coerceIn(0, TEXT_SPEEDS.size - 1)
	}

	fun setTextSpeed(index: Int) {
		textSpeed = index.coerceIn(0, TEXT_SPEEDS.size - 1)
		save()
	}

	private fun save() {
		val file = ConfigFile()
		file.setValue(SECTION, TEXT_SPEED, textSpeed)
		if (file.save(PATH) != Error.OK) Logger.e("Reglages non enregistres : $PATH")
	}

	private const val PATH = "user://settings.cfg"
	private const val SECTION = "options"
	// Nouvelle clé : l'ancienne rangeait des vitesses nommées, dans un autre ordre.
	private const val TEXT_SPEED = "text_speed_factor"
}
