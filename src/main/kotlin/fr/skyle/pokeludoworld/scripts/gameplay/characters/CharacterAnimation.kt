package fr.skyle.pokeludoworld.scripts.gameplay.characters

import godot.annotation.Script
import godot.api.AnimatedSprite2D
import godot.core.Vector2

/**
 * Choisit l'animation à partir de la direction et de l'état de marche.
 * Les animations sont nommées `<etat>_<direction>` dans player.tres.
 */
@Script
class CharacterAnimation : AnimatedSprite2D() {

	fun refresh(direction: Vector2, walking: Boolean) {
		val suffix = when (direction) {
			Vector2.UP -> "up"
			Vector2.LEFT -> "left"
			Vector2.RIGHT -> "right"
			else -> "down"
		}

		val next = (if (walking) "walk_" else "idle_") + suffix

		// Ne pas relancer l'animation en cours, sinon le cycle de marche repart
		// à zéro à chaque frame et le personnage semble figé.
		if (animation.toString() != next) play(next)
	}
}
