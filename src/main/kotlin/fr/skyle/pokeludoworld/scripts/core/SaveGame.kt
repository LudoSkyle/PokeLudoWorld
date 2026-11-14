package fr.skyle.pokeludoworld.scripts.core

import fr.skyle.pokeludoworld.scripts.log.Logger
import godot.api.ConfigFile
import godot.api.FileAccess
import godot.core.Error
import godot.core.Vector2

/**
 * La sauvegarde : une seule, dans un fichier chez le joueur (voir
 * [GameFiles]). Elle retient où l'on est et depuis combien de temps on joue.
 */
object SaveGame {

	data class State(
		/** Chemin de la scène de la carte. */
		val scene: String,
		/** Position du joueur dans la carte : un centre de case. */
		val position: Vector2,
		val facing: Vector2,
		/** Nom du lieu, en français (il se traduit à l'affichage). */
		val location: String,
		/** Bandeau du lieu. */
		val banner: String,
		/** Temps de jeu total, en secondes. */
		val seconds: Double,
	)

	fun exists(): Boolean = FileAccess.fileExists(GameFiles.save)

	fun read(): State? {
		val file = ConfigFile()
		if (file.load(GameFiles.save) != Error.OK) return null

		val scene = file.getValue(SECTION, "scene", "").toString()
		if (scene.isEmpty()) return null

		return State(
			scene = scene,
			position = Vector2(number(file, "x"), number(file, "y")),
			facing = Vector2(number(file, "facing_x"), number(file, "facing_y")),
			location = file.getValue(SECTION, "location", "").toString(),
			banner = file.getValue(SECTION, "banner", "").toString(),
			seconds = number(file, "seconds"),
		)
	}

	fun write(state: State): Boolean {
		val file = ConfigFile()
		file.setValue(SECTION, "scene", state.scene)
		file.setValue(SECTION, "x", state.position.x)
		file.setValue(SECTION, "y", state.position.y)
		file.setValue(SECTION, "facing_x", state.facing.x)
		file.setValue(SECTION, "facing_y", state.facing.y)
		file.setValue(SECTION, "location", state.location)
		file.setValue(SECTION, "banner", state.banner)
		file.setValue(SECTION, "seconds", state.seconds)

		val saved = file.save(GameFiles.save) == Error.OK
		if (!saved) Logger.e("Sauvegarde impossible : ${GameFiles.save}")
		return saved
	}

	/** Temps de jeu au format des jeux d'origine : heures et minutes. */
	fun clock(seconds: Double): String {
		val minutes = (seconds / 60.0).toInt()
		return "%02d:%02d".format(minutes / 60, minutes % 60)
	}

	private fun number(file: ConfigFile, key: String): Double =
		(file.getValue(SECTION, key, 0.0) as? Number)?.toDouble() ?: 0.0

	private const val SECTION = "save"
}
