package fr.skyle.pokeludoworld.scripts.gameplay.levels

import fr.skyle.pokeludoworld.scripts.core.DayNight
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.PointLight2D
import godot.api.StaticBody2D

/**
 * Lampadaire. Un objet posé sur une case, solide comme un panneau, dont la
 * lumière suit l'heure : éteinte en plein jour, elle monte au crépuscule,
 * brille toute la nuit et s'éteint à l'aube (voir DayNight).
 *
 * La nuit teinte tout le dehors ; cette lumière est ce qui perce la teinte
 * autour du lampadaire.
 */
@Script
class StreetLamp : StaticBody2D() {

	/** Intensité de la lumière en pleine nuit. */
	@Category("Lumiere")
	@Export
	var brightness: Double = 1.1

	private var light: PointLight2D? = null

	/** Vrai tant que la lampe éclaire. */
	val isLit: Boolean
		get() = light?.visible == true

	@Register
	override fun _ready() {
		light = getNode("Light") as? PointLight2D
		refresh()
	}

	@Register
	override fun _process(delta: Double) {
		refresh()
	}

	private fun refresh() {
		val lamp = light ?: return
		val level = DayNight.light()
		lamp.energy = (brightness * level).toFloat()
		// Éteinte, elle ne coûte rien à dessiner.
		lamp.visible = level > 0.01
	}
}
