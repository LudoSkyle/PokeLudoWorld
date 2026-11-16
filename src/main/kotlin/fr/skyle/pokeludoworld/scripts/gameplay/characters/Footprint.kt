package fr.skyle.pokeludoworld.scripts.gameplay.characters

import godot.annotation.Register
import godot.annotation.Script
import godot.api.Sprite2D
import godot.core.Color

/**
 * Une trace de pas dans le sable : une marque qui s'efface toute seule.
 *
 * Elle ne dessine pas une couleur de sable, elle **assombrit** celui qui est
 * dessous — un noir à 20 % d'opacité, comme dans les jeux d'origine. La même
 * empreinte va donc sur la plage claire comme sur le rivage mouillé.
 *
 * Elle vit sa vie seule, sans rien demander à celui qui l'a posée : il peut
 * continuer sa route, changer de carte ou disparaître, elle s'efface quand même.
 *
 * [Footprints] la pose, règle sa région de planche et son orientation.
 */
@Script
class Footprint : Sprite2D() {

	/** Combien de temps la trace reste visible, en secondes. */
	var lifeSeconds: Double = 1.0

	/** De combien elle assombrit le sable au moment où elle est posée (0 à 1). */
	var darkness: Double = 0.26

	private var elapsed: Double = 0.0

	@Register
	override fun _ready() {
		shade(1.0)
	}

	@Register
	override fun _process(delta: Double) {
		elapsed += delta

		val left = if (lifeSeconds > 0.0) 1.0 - elapsed / lifeSeconds else 0.0
		if (left <= 0.0) {
			queueFree()
			return
		}
		shade(left)
	}

	/**
	 * La trace garde toute sa force la première moitié de sa vie, puis le sable
	 * reprend sa couleur. Un fondu dès le premier instant rendait pâles les
	 * traces juste derrière le personnage, celles qu'on regarde.
	 */
	private fun shade(left: Double) {
		val strength = if (left > FADE) 1.0 else left / FADE
		modulate = Color(0.0, 0.0, 0.0, darkness * strength)
	}

	companion object {
		/** La part de la vie où la trace est encore franche. */
		private const val FADE = 0.5
	}
}
