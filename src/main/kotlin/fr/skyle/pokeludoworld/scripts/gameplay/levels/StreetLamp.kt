package fr.skyle.pokeludoworld.scripts.gameplay.levels

import fr.skyle.pokeludoworld.scripts.core.DayNight
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.PointLight2D
import godot.api.StaticBody2D
import kotlin.math.sin

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

	/** L'ampleur du vacillement de la flamme, en part de l'éclat : très léger, à peine un souffle. 0 l'arrête. */
	@Category("Lumiere")
	@Export
	var flicker: Double = 0.05

	private var light: PointLight2D? = null
	private var clock = 0.0

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
		clock += delta
		refresh()
	}

	/**
	 * Le vacillement : deux ondes lentes de périodes sans commune mesure, pour qu'on n'y lise
	 * pas de battement, décalées d'une lanterne à l'autre par sa place sur la carte.
	 */
	private fun waver(): Double {
		val phase = position.x * 0.37 + position.y * 0.11
		return 1.0 + flicker * (0.6 * sin(clock * 5.3 + phase) + 0.4 * sin(clock * 11.7 + phase * 1.7))
	}

	private fun refresh() {
		val lamp = light ?: return
		val level = DayNight.light()
		lamp.energy = (brightness * level * waver()).toFloat()
		// Éteinte, elle ne coûte rien à dessiner.
		lamp.visible = level > 0.01
	}
}
