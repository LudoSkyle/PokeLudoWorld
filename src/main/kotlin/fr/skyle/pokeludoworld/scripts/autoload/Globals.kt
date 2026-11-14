package fr.skyle.pokeludoworld.scripts.autoload

import fr.skyle.pokeludoworld.scripts.core.DayNight
import fr.skyle.pokeludoworld.scripts.gameplay.story.StoryFlags
import fr.skyle.pokeludoworld.scripts.log.Logger
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.Node

@Script
class Globals : Node() {

	companion object {
		lateinit var instance: Globals
			private set
	}

	@Category("Gameplay")
	@Export
	var gridSize: Int = 16

	@Register
	override fun _ready() {
		instance = this

		Logger.i("Loading Globals ...")
	}

	/**
	 * Les drapeaux d'histoire, vus de Godot : `Globals.has_flag("bell_told")`.
	 * Le code Kotlin s'adresse directement à [StoryFlags] ; ces deux fonctions
	 * servent aux scripts qui n'y ont pas accès, les tests en premier.
	 */
	@Register
	fun hasFlag(flag: String): Boolean = StoryFlags.has(flag)

	@Register
	fun setFlag(flag: String) {
		StoryFlags.set(flag)
	}

	/**
	 * L'heure du jeu, vue de Godot. `set_hour(23.0)` impose une heure, de 0 à
	 * 24 ; une valeur négative rend la main à l'horloge réelle.
	 */
	@Register
	fun hour(): Double = DayNight.hour()

	@Register
	fun setHour(hour: Double) {
		DayNight.forcedHour = hour.takeIf { it >= 0.0 }
	}
}
