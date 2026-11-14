package fr.skyle.pokeludoworld.scripts.gameplay.characters

import fr.skyle.pokeludoworld.scripts.core.AudioManager
import fr.skyle.pokeludoworld.scripts.core.SceneManager
import fr.skyle.pokeludoworld.scripts.gameplay.levels.Readable
import fr.skyle.pokeludoworld.scripts.gameplay.levels.Roadblock
import fr.skyle.pokeludoworld.scripts.gameplay.levels.SceneTrigger
import fr.skyle.pokeludoworld.scripts.gameplay.levels.Sign
import fr.skyle.pokeludoworld.scripts.log.Logger
import fr.skyle.pokeludoworld.scripts.ui.MessageBox
import fr.skyle.pokeludoworld.scripts.ui.PauseMenu
import godot.annotation.Category
import godot.annotation.Export
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

	/** Cases par seconde en marchant. */
	@Category("Deplacement")
	@Export
	var walkPace: Double = 4.0

	/** Cases par seconde en courant, touche de course tenue. */
	@Category("Deplacement")
	@Export
	var runPace: Double = 8.0

	/** Vrai si le pas en cours, ou le dernier fait, est un pas de course. */
	var isRunning: Boolean = false
		private set

	private var input: PlayerInput? = null
	private var movement: CharacterMovement? = null
	private var sprite: CharacterAnimation? = null

	/** Temps restant avant de pouvoir refaire entendre un choc contre un mur. */
	private var bumpWait = 0.0

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
	fun stepBack(direction: Vector2): Boolean {
		// Une scène règle l'allure : on recule au pas, même si l'on arrivait en courant.
		setPace(running = false)
		return movement?.tryWalk(direction) ?: false
	}

	/**
	 * Règle l'allure du prochain pas. Elle ne change qu'entre deux pas : un pas
	 * engagé va jusqu'au bout à l'allure où il a commencé. Les jambes suivent —
	 * la planche n'a pas d'images de course, c'est la marche qui s'accélère.
	 */
	private fun setPace(running: Boolean) {
		isRunning = running
		val pace = if (running) runPace else walkPace
		movement?.tilesPerSecond = pace
		sprite?.speedScale = (pace / walkPace).toFloat()
	}

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

		// Menu ouvert : les flèches déplacent son curseur, plus le personnage.
		// Il passe avant la boîte de dialogue, dont ses écrans se servent pour
		// poser leurs questions.
		val menu = PauseMenu.instance
		val audio = AudioManager.instance
		bumpWait -= delta
		if (menu != null && menu.isOpen) {
			// Valider s'entend, refermer aussi.
			if (interact) audio?.sfx("confirm")
			if (Input.isActionJustPressed(PauseMenu.ACTION)) audio?.sfx("cancel")
			menu.handle(interact)
			sprite?.refresh(currentInput.direction, false)
			return
		}

		if (box != null && box.isOpen) {
			if (interact) audio?.sfx("confirm")
			if (box.isAsking && Input.isActionJustPressed(PauseMenu.ACTION)) audio?.sfx("cancel")
			box.handle(interact)
			sprite?.refresh(currentInput.direction, false)
			return
		}

		if (isLocked) {
			sprite?.refresh(currentInput.direction, currentMovement.isWalking)
			return
		}

		// Il ne s'ouvre qu'entre deux pas, jamais au milieu d'une case.
		if (menu != null && !currentMovement.isWalking && Input.isActionJustPressed(PauseMenu.ACTION)) {
			audio?.sfx("menu")
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
					// On court tant que la touche de course est tenue.
					setPace(Input.isActionPressed(RUN))
					// Sur un paillasson, avancer vers la sortie quitte la pièce
					// au lieu de buter contre le mur.
					val door = currentMovement.areaUnderfoot() as? SceneTrigger
					if (door != null && door.isExit && door.exitDirection == currentInput.direction) {
						door.activate()
					} else if (!currentMovement.tryWalk(currentInput.direction) && bumpWait <= 0.0) {
						// On bute : le choc s'entend, à la cadence des pas.
						audio?.sfx("bump")
						bumpWait = BUMP_SECONDS
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
			else -> return
		}
		AudioManager.instance?.sfx("confirm")
	}
}

private const val BUMP_SECONDS = 0.3
private const val RUN = "run"
