package fr.skyle.pokeludoworld.scripts.gameplay.characters

import fr.skyle.pokeludoworld.scripts.gameplay.levels.Sign
import fr.skyle.pokeludoworld.scripts.log.Logger
import fr.skyle.pokeludoworld.scripts.ui.MessageBox
import godot.annotation.Register
import godot.annotation.Script
import godot.api.CharacterBody2D
import godot.api.Input

/**
 * Assemble les trois composants du joueur : entrée, déplacement, animation,
 * et porte l'interaction avec ce qui se trouve devant lui.
 *
 * Pas de machine à états : une boîte de dialogue ouverte se contente de
 * court-circuiter le déplacement. Elle s'imposera le jour où un troisième
 * mode apparaîtra (combat, menu).
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

		// Une seule lecture de la touche d'interaction dans tout le jeu : sans
		// ça, la pression qui ouvre la boîte la ferait avancer aussitôt.
		val interact = Input.isActionJustPressed("interact")
		val box = MessageBox.instance

		if (box != null && box.isOpen) {
			if (interact) box.advance()
			sprite?.refresh(currentInput.direction, false)
			return
		}

		if (!currentMovement.isWalking && interact) {
			readFacingObject()
			sprite?.refresh(currentInput.direction, false)
			return
		}

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

	private fun readFacingObject() {
		val facing = input?.direction ?: return
		val target = movement?.colliderAt(facing) ?: return

		if (target is Sign) target.read()
	}
}
