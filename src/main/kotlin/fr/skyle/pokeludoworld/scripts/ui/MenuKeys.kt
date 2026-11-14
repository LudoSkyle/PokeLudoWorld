package fr.skyle.pokeludoworld.scripts.ui

import godot.api.Engine
import godot.api.Input
import godot.api.Time

/**
 * Touches des menus avec **répétition** : une pression déplace le curseur
 * d'un cran ; si la touche reste enfoncée, il repart après un court délai puis
 * avance à cadence régulière, pour descendre vite une longue liste.
 *
 * Une touche déjà enfoncée quand le menu s'ouvre ne compte pas : il faut
 * l'avoir pressée menu ouvert.
 */
object MenuKeys {

	/** Attente avant la première répétition, en millisecondes. */
	private const val DELAY = 350L

	/** Écart entre deux répétitions. */
	private const val INTERVAL = 110L

	private class Key {
		var next = 0L
		var armed = false
		var frame = -1L
		var fired = false
	}

	private val keys = HashMap<String, Key>()

	/** Vrai à l'image où [action] doit agir : pression, ou répétition. */
	fun step(action: String): Boolean {
		val key = keys.getOrPut(action) { Key() }

		// Une seule décision par image, même si deux menus posent la question.
		val frame = Engine.getProcessFrames()
		if (key.frame == frame) return key.fired
		key.frame = frame

		val now = Time.getTicksMsec()
		key.fired = when {
			Input.isActionJustPressed(action) -> {
				key.armed = true
				key.next = now + DELAY
				true
			}
			!Input.isActionPressed(action) -> {
				key.armed = false
				false
			}
			key.armed && now >= key.next -> {
				key.next = now + INTERVAL
				true
			}
			else -> false
		}
		return key.fired
	}

	fun up(): Boolean = step("ui_up")

	fun down(): Boolean = step("ui_down")
}
