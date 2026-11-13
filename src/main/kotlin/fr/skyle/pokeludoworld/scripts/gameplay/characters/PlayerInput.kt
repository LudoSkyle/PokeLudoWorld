package fr.skyle.pokeludoworld.scripts.gameplay.characters

import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Script
import godot.api.Input
import godot.api.Node
import godot.core.Vector2

/** Ce que l'entrée demande à ce pas de temps. */
enum class MoveIntent {
	NONE,
	TURN,
	WALK,
}

/**
 * Lit les touches directionnelles à la façon des Pokémon 2D :
 * une pression brève fait pivoter sur place, une pression maintenue fait marcher.
 */
@Script
class PlayerInput : Node() {

	@Category("Input")
	@Export
	var holdThreshold: Double = 0.12

	/** Direction regardée, même à l'arrêt. */
	var direction: Vector2 = Vector2.DOWN
		private set

	private var holdTime: Double = 0.0
	private var waitForRelease: Boolean = false

	/** Oriente le personnage sans passer par une touche (arrivée par une porte). */
	fun face(newDirection: Vector2) {
		direction = newDirection
	}

	/**
	 * Ignore la touche tenue jusqu'à ce qu'elle soit relâchée. Sans ça, monter
	 * un escalier en maintenant Haut fait arriver au pied de l'escalier d'en
	 * face, toujours Haut enfoncé : on y rentre aussitôt, en boucle.
	 */
	fun requireFreshPress() {
		waitForRelease = true
		holdTime = 0.0
	}

	private val bindings = listOf(
		"ui_up" to Vector2.UP,
		"ui_down" to Vector2.DOWN,
		"ui_left" to Vector2.LEFT,
		"ui_right" to Vector2.RIGHT,
	)

	private fun justPressedDirection(): Vector2? =
		bindings.firstOrNull { Input.isActionJustPressed(it.first) }?.second

	private fun heldDirection(): Vector2? =
		bindings.firstOrNull { Input.isActionPressed(it.first) }?.second

	/**
	 * À appeler une fois par frame, seulement quand le personnage est immobile :
	 * le compteur de maintien ne doit pas avancer pendant un déplacement.
	 */
	fun poll(delta: Double): MoveIntent {
		if (waitForRelease) {
			if (heldDirection() == null) waitForRelease = false
			return MoveIntent.NONE
		}

		// Une nouvelle pression réoriente tout de suite et relance le compteur.
		val pressed = justPressedDirection()
		if (pressed != null) {
			direction = pressed
			holdTime = 0.0
		}

		val held = heldDirection()

		if (held == null) {
			// Relâchée avant le seuil : c'était un demi-tour, pas un pas.
			val wasTap = holdTime > 0.0
			holdTime = 0.0
			return if (wasTap) MoveIntent.TURN else MoveIntent.NONE
		}

		direction = held
		holdTime += delta

		return if (holdTime > holdThreshold) MoveIntent.WALK else MoveIntent.NONE
	}
}
