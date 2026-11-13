package fr.skyle.pokeludoworld.scripts.gameplay.characters

import fr.skyle.pokeludoworld.scripts.core.SceneManager
import fr.skyle.pokeludoworld.scripts.gameplay.levels.Readable
import fr.skyle.pokeludoworld.scripts.gameplay.levels.Roadblock
import fr.skyle.pokeludoworld.scripts.gameplay.levels.SceneTrigger
import fr.skyle.pokeludoworld.scripts.gameplay.levels.Sign
import fr.skyle.pokeludoworld.scripts.log.Logger
import fr.skyle.pokeludoworld.scripts.ui.MessageBox
import fr.skyle.pokeludoworld.scripts.ui.PauseMenu
import godot.annotation.Register
import godot.annotation.Script
import godot.api.CharacterBody2D
import godot.api.Input
import godot.core.Vector2

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

	/** Vrai pendant une scène jouée par le jeu : le joueur ne répond plus aux touches. */
	var isLocked: Boolean = false
		private set

	val isWalking: Boolean
		get() = movement?.isWalking ?: false

	fun lock() {
		isLocked = true
	}

	/**
	 * Rend la main. [blocked] est ignorée tant que sa touche reste enfoncée :
	 * c'est la direction qui relancerait aussitôt la scène.
	 */
	fun unlock(blocked: Vector2) {
		isLocked = false
		input?.blockUntilReleased(blocked)
	}

	/** Recule d'une case sans se retourner. Renvoie false si la case est occupée. */
	fun stepBack(direction: Vector2): Boolean = movement?.tryWalk(direction) ?: false

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

		val wasWalking = currentMovement.isWalking
		currentMovement.process(delta)

		// Un passage gardé se déclenche à l'instant où l'on se pose dessus,
		// avant que la touche tenue n'engage le pas suivant.
		if (wasWalking && !currentMovement.isWalking && !isLocked) {
			(currentMovement.areaUnderfoot() as? Roadblock)?.intercept(this)
		}

		// Pendant un fondu, le pas engagé se termine mais plus aucune entrée
		// n'est lue : le joueur finit d'entrer dans la porte, puis attend.
		if (SceneManager.instance?.isChanging == true) {
			sprite?.refresh(currentInput.direction, currentMovement.isWalking)
			return
		}

		// Une seule lecture de la touche d'interaction dans tout le jeu : sans
		// ça, la pression qui ouvre la boîte la ferait avancer aussitôt.
		val interact = Input.isActionJustPressed("interact")
		val box = MessageBox.instance

		if (box != null && box.isOpen) {
			if (interact) box.advance()
			sprite?.refresh(currentInput.direction, false)
			return
		}

		if (isLocked) {
			sprite?.refresh(currentInput.direction, currentMovement.isWalking)
			return
		}

		// Menu ouvert : les flèches déplacent son curseur, plus le personnage.
		val menu = PauseMenu.instance
		if (menu != null && menu.isOpen) {
			menu.handle(interact)
			sprite?.refresh(currentInput.direction, false)
			return
		}

		// Il ne s'ouvre qu'entre deux pas, jamais au milieu d'une case.
		if (menu != null && !currentMovement.isWalking && Input.isActionJustPressed(PauseMenu.ACTION)) {
			menu.open()
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
				MoveIntent.WALK -> {
					// Sur un paillasson, avancer vers la sortie quitte la pièce
					// au lieu de buter contre le mur.
					val door = currentMovement.areaUnderfoot() as? SceneTrigger
					if (door != null && door.isExit && door.exitDirection == currentInput.direction) {
						door.activate()
					} else {
						currentMovement.tryWalk(currentInput.direction)
					}
				}
				MoveIntent.TURN -> sprite?.playTurn(currentInput.direction)
				MoveIntent.NONE -> {}
			}
		}

		sprite?.refresh(currentInput.direction, currentMovement.isWalking)
	}

	private fun readFacingObject() {
		val facing = input?.direction ?: return
		val target = movement?.colliderAt(facing) ?: return

		when (target) {
			is Sign -> target.read()
			is Readable -> target.read()
			is Npc -> target.talk(facing)
		}
	}
}
