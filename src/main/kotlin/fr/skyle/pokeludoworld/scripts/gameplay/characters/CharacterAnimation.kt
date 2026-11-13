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

	private fun suffixOf(direction: Vector2): String = when (direction) {
		Vector2.UP -> "up"
		Vector2.LEFT -> "left"
		Vector2.RIGHT -> "right"
		else -> "down"
	}

	/**
	 * Petit sursaut joué quand on pivote sur place : une image de pas puis
	 * l'image fixe. C'est ce qui donne le « à-coup » des jeux d'origine quand
	 * on change de direction sans avancer.
	 */
	fun playTurn(direction: Vector2) {
		play("turn_" + suffixOf(direction))
	}

	fun refresh(direction: Vector2, walking: Boolean) {
		val suffix = suffixOf(direction)

		// Laisser le sursaut aller au bout avant de retomber sur l'image fixe.
		if (!walking && animation.toString() == "turn_$suffix" && isPlaying()) return

		val next = (if (walking) "walk_" else "idle_") + suffix

		// Ne pas relancer l'animation en cours, sinon le cycle de marche repart
		// à zéro à chaque frame et le personnage semble figé.
		if (animation.toString() != next) play(next)
	}
}
