package fr.skyle.pokeludoworld.scripts.gameplay.characters

import fr.skyle.pokeludoworld.scripts.log.Logger
import godot.annotation.Register
import godot.annotation.Script
import godot.api.CharacterBody2D

/**
 * Assemble les trois composants du joueur : entrée, déplacement, animation.
 *
 * Pas de machine à états pour l'instant : il n'y a qu'un seul état. Elle
 * deviendra utile quand les boîtes de dialogue arriveront, et viendra
 * s'intercaler ici sans toucher aux composants.
 */
@Script
class Player : CharacterBody2D() {

	private var input: PlayerInput? = null
	private var movement: CharacterMovement? = null
	private var sprite: CharacterAnimation? = null

	@Register
	override fun _ready() {
		input = getNode("Input") as? PlayerInput
		movement = getNode("Movement") as? CharacterMovement
		sprite = getNode("Sprite") as? CharacterAnimation

		movement?.attach(this)

		Logger.i("Loading player ...")
	}

	@Register
	override fun _process(delta: Double) {
		val currentInput = input ?: return
		val currentMovement = movement ?: return

		currentMovement.process(delta)

		// L'entrée n'est lue qu'entre deux pas : un pas engagé va toujours
		// jusqu'au bout, sinon le personnage s'arrête entre deux cases.
		if (!currentMovement.isWalking) {
			when (currentInput.poll(delta)) {
				MoveIntent.WALK -> currentMovement.tryWalk(currentInput.direction)
				MoveIntent.TURN -> sprite?.playTurn(currentInput.direction)
				MoveIntent.NONE -> {}
			}
		}

		sprite?.refresh(currentInput.direction, currentMovement.isWalking)
	}
}
