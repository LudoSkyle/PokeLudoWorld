package fr.skyle.pokemonmirage.scripts.gameplay.levels

import fr.skyle.pokemonmirage.scripts.core.DayNight
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.PointLight2D

/**
 * Une lumière qui suit l'heure : éteinte en plein jour, elle monte au
 * crépuscule, brille toute la nuit et faiblit à l'aube (voir DayNight). C'est
 * la lueur qu'une fenêtre éclairée répand sur le mur et le sol devant elle.
 */
@Script
class NightLight : PointLight2D() {

	/** Intensité en pleine nuit. */
	@Category("Lumiere")
	@Export
	var brightness: Double = 0.7

	@Register
	override fun _ready() {
		refresh()
	}

	@Register
	override fun _process(delta: Double) {
		refresh()
	}

	private fun refresh() {
		val level = DayNight.light()
		energy = (brightness * level).toFloat()
		// Éteinte, elle ne coûte rien à dessiner.
		visible = level > 0.01
	}
}
