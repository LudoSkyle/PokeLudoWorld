package fr.skyle.pokeludoworld.scripts.core

import fr.skyle.pokeludoworld.scripts.log.Logger
import godot.api.ConfigFile
import godot.api.DirAccess
import godot.api.FileAccess
import godot.core.Error
import godot.core.Vector2

/**
 * Les sauvegardes : [SLOTS] emplacements, un fichier chacun chez le joueur
 * (voir [GameFiles]). Une partie retient où l'on est, depuis combien de temps
 * on joue, le contenu du sac et les drapeaux d'histoire.
 *
 * La partie en cours occupe l'emplacement [slot] : c'est lui qu'écrit le menu
 * de pause. On le choisit à l'écran titre (voir SaveSlots).
 */
object SaveGame {

	/** Nombre d'emplacements, numérotés de 1 à [SLOTS]. */
	const val SLOTS = 3

	/** L'emplacement de la partie en cours. */
	var slot: Int = 1
		private set

	/** Fait de [chosen] l'emplacement de la partie en cours. */
	fun use(chosen: Int) {
		slot = chosen.coerceIn(1, SLOTS)
	}

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
		/** Contenu du sac : quantité par identifiant d'objet, dans l'ordre d'arrivée. */
		val items: Map<String, Int> = emptyMap(),
		/** Drapeaux d'histoire posés, dans l'ordre où ils l'ont été. */
		val flags: Set<String> = emptySet(),
		/** Badges gagnés. Rien ne les compte encore : la carte de la partie les affiche déjà. */
		val badges: Int = 0,
		/** Espèces inscrites au Pokédex. Même remarque. */
		val pokedex: Int = 0,
		/** L'équipe, jusqu'à six espèces, dans l'ordre. Même remarque. */
		val team: List<String> = emptyList(),
	)

	fun exists(at: Int = slot): Boolean = FileAccess.fileExists(GameFiles.save(at))

	/** Les emplacements occupés, dans l'ordre. */
	fun used(): List<Int> = (1..SLOTS).filter { exists(it) }

	/** Le premier emplacement libre, ou null s'ils sont tous pris. */
	fun firstFree(): Int? = (1..SLOTS).firstOrNull { !exists(it) }

	/** Efface la partie de l'emplacement [at]. */
	fun delete(at: Int): Boolean {
		if (!exists(at)) return true
		val gone = DirAccess.removeAbsolute(GameFiles.save(at)) == Error.OK
		if (!gone) Logger.e("Sauvegarde non effacee : ${GameFiles.save(at)}")
		return gone
	}

	/**
	 * Avant les emplacements il n'y avait qu'une sauvegarde : si elle est
	 * encore là et que le premier emplacement est libre, elle le prend.
	 */
	fun adoptOldSave() {
		if (!FileAccess.fileExists(GameFiles.oldSave) || exists(1)) return
		if (DirAccess.renameAbsolute(GameFiles.oldSave, GameFiles.save(1)) != Error.OK) {
			Logger.e("Ancienne sauvegarde non reprise : ${GameFiles.oldSave}")
		}
	}

	fun read(at: Int = slot): State? {
		val file = ConfigFile()
		if (file.load(GameFiles.save(at)) != Error.OK) return null

		val scene = file.getValue(SECTION, "scene", "").toString()
		if (scene.isEmpty()) return null

		return State(
			scene = scene,
			position = Vector2(number(file, "x"), number(file, "y")),
			facing = Vector2(number(file, "facing_x"), number(file, "facing_y")),
			location = file.getValue(SECTION, "location", "").toString(),
			banner = file.getValue(SECTION, "banner", "").toString(),
			seconds = number(file, "seconds"),
			items = items(file),
			flags = flags(file),
			badges = number(file, "badges").toInt(),
			pokedex = number(file, "pokedex").toInt(),
			team = file.getValue(SECTION, "team", "").toString().split(',').filter { it.isNotBlank() }.take(TEAM),
		)
	}

	private fun flags(file: ConfigFile): Set<String> {
		val found = LinkedHashSet<String>()
		if (!file.hasSection(FLAGS)) return found
		val keys = file.getSectionKeys(FLAGS)
		for (index in 0 until keys.size) {
			if (file.getValue(FLAGS, keys[index], false) == true) found.add(keys[index])
		}
		return found
	}

	private fun items(file: ConfigFile): Map<String, Int> {
		val found = LinkedHashMap<String, Int>()
		if (!file.hasSection(ITEMS)) return found
		val keys = file.getSectionKeys(ITEMS)
		for (index in 0 until keys.size) {
			val id = keys[index]
			found[id] = (file.getValue(ITEMS, id, 0) as? Number)?.toInt() ?: 0
		}
		return found
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
		file.setValue(SECTION, "badges", state.badges)
		file.setValue(SECTION, "pokedex", state.pokedex)
		file.setValue(SECTION, "team", state.team.take(TEAM).joinToString(","))
		state.items.forEach { (id, amount) -> file.setValue(ITEMS, id, amount) }
		state.flags.forEach { file.setValue(FLAGS, it, true) }

		val saved = file.save(GameFiles.save(slot)) == Error.OK
		if (!saved) Logger.e("Sauvegarde impossible : ${GameFiles.save(slot)}")
		return saved
	}

	/** Temps de jeu au format des jeux d'origine : heures et minutes. */
	fun clock(seconds: Double): String {
		val minutes = (seconds / 60.0).toInt()
		return "%02d:%02d".format(minutes / 60, minutes % 60)
	}

	private fun number(file: ConfigFile, key: String): Double =
		(file.getValue(SECTION, key, 0.0) as? Number)?.toDouble() ?: 0.0

	/** Taille d'une équipe. */
	const val TEAM = 6

	private const val SECTION = "save"
	private const val ITEMS = "items"
	private const val FLAGS = "flags"
}
