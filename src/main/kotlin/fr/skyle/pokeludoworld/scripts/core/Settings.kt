package fr.skyle.pokeludoworld.scripts.core

import fr.skyle.pokeludoworld.scripts.log.Logger
import godot.api.ConfigFile
import godot.api.TranslationServer
import godot.core.Error

/**
 * Réglages du joueur, gardés d'un lancement à l'autre (voir [GameFiles]) :
 * la vitesse du texte, la langue, et les trois volumes — musique, cris des
 * Pokémon, autres sons.
 */
object Settings {

	/** Multiplicateurs proposés : x0.5, x1, x2, x4. */
	val TEXT_SPEEDS = listOf(0.5, 1.0, 2.0, 4.0)

	/** Secondes par lettre à la vitesse x1. */
	const val BASE_SECONDS_PER_LETTER = 0.02

	const val DEFAULT_TEXT_SPEED = 1

	/**
	 * Langues proposées. Les textes sont écrits en français dans le jeu ; les
	 * autres langues sont des traductions (`locale/<code>.po`).
	 */
	val LANGUAGES = listOf("fr", "en")

	/** Indice dans [TEXT_SPEEDS]. */
	var textSpeed: Int = DEFAULT_TEXT_SPEED
		private set

	/** Indice dans [LANGUAGES]. */
	var language: Int = 0
		private set

	/** Un volume va de 0 (muet) à [VOLUME_STEPS], par crans de dix pour cent. */
	const val VOLUME_STEPS = 10

	/** Les trois volumes que le joueur règle : la musique, les cris des Pokémon, et tout le reste (bruitages, jingles). */
	enum class Volume(val key: String) { MUSIC("volume_music"), CRIES("volume_cries"), SOUNDS("volume_sounds") }

	private val volumes = IntArray(Volume.entries.size) { VOLUME_STEPS }

	/** Le cran de [volume], de 0 à [VOLUME_STEPS]. */
	fun volume(volume: Volume): Int = volumes[volume.ordinal]

	/** Le même, en part de 0 à 1 : ce par quoi l'AudioManager multiplie ce qu'il joue. */
	fun gain(volume: Volume): Double = volumes[volume.ordinal].toDouble() / VOLUME_STEPS

	fun setVolume(volume: Volume, step: Int) {
		volumes[volume.ordinal] = step.coerceIn(0, VOLUME_STEPS)
		save()
	}

	val secondsPerLetter: Double
		get() = BASE_SECONDS_PER_LETTER / TEXT_SPEEDS[textSpeed]

	private var loaded = false

	fun load() {
		if (loaded) return
		loaded = true

		val file = ConfigFile()
		if (file.load(GameFiles.settings) == Error.OK) {
			textSpeed = int(file, TEXT_SPEED, DEFAULT_TEXT_SPEED).coerceIn(0, TEXT_SPEEDS.size - 1)
			language = LANGUAGES.indexOf(file.getValue(SECTION, LANGUAGE, LANGUAGES[0]).toString()).coerceAtLeast(0)
			Volume.entries.forEach { volumes[it.ordinal] = int(file, it.key, VOLUME_STEPS).coerceIn(0, VOLUME_STEPS) }
		}
		// Toujours, même sans fichier : sinon Godot suit la langue du système.
		TranslationServer.setLocale(LANGUAGES[language])
	}

	fun setTextSpeed(index: Int) {
		textSpeed = index.coerceIn(0, TEXT_SPEEDS.size - 1)
		save()
	}

	fun setLanguage(index: Int) {
		language = index.coerceIn(0, LANGUAGES.size - 1)
		TranslationServer.setLocale(LANGUAGES[language])
		save()
	}

	private fun int(file: ConfigFile, key: String, default: Int): Int =
		(file.getValue(SECTION, key, default) as? Number)?.toInt() ?: default

	private fun save() {
		val file = ConfigFile()
		file.setValue(SECTION, TEXT_SPEED, textSpeed)
		file.setValue(SECTION, LANGUAGE, LANGUAGES[language])
		Volume.entries.forEach { file.setValue(SECTION, it.key, volumes[it.ordinal]) }
		if (file.save(GameFiles.settings) != Error.OK) Logger.e("Reglages non enregistres : ${GameFiles.settings}")
	}

	private const val SECTION = "options"
	// Nouvelle clé : l'ancienne rangeait des vitesses nommées, dans un autre ordre.
	private const val TEXT_SPEED = "text_speed_factor"
	private const val LANGUAGE = "language"
}
