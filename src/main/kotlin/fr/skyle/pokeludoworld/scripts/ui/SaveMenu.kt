package fr.skyle.pokeludoworld.scripts.ui

import fr.skyle.pokeludoworld.scripts.core.AudioManager
import fr.skyle.pokeludoworld.scripts.core.SaveGame
import fr.skyle.pokeludoworld.scripts.core.SceneManager
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.CanvasLayer
import godot.api.Control
import godot.api.Label

/**
 * Écran de sauvegarde, ouvert depuis le menu de pause : un résumé de la partie
 * en haut à gauche, la question dans la boîte de dialogue, et Oui/Non
 * au-dessus d'elle.
 *
 * 1. « Voulez-vous sauvegarder la partie ? »
 * 2. s'il existe déjà une sauvegarde : « Voulez-vous l'écraser ? »
 * 3. « La partie est sauvegardée. », qui reste [holdSeconds] à l'écran, puis
 *    tout se referme, menu compris.
 *
 * Non — ou la touche du menu — ramène au menu de pause sans rien écrire.
 */
@Script
class SaveMenu : CanvasLayer() {

	companion object {
		var instance: SaveMenu? = null
			private set
	}

	/** Durée d'affichage du message final, une fois entièrement écrit. */
	@Category("Affichage")
	@Export
	var holdSeconds: Double = 1.0

	private enum class Phase { CLOSED, ASK, OVERWRITE, SAVED }

	private var summary: Control? = null
	private var location: Label? = null
	private var time: Label? = null
	private var choices: ChoiceBox? = null

	private var phase = Phase.CLOSED
	private var held = 0.0

	val isOpen: Boolean
		get() = phase != Phase.CLOSED

	@Register
	override fun _ready() {
		instance = this
		summary = getNode("Control/Summary") as? Control
		location = getNode("Control/Summary/Location") as? Label
		time = getNode("Control/Summary/Time") as? Label
		choices = getNode("Control/Choices") as? ChoiceBox
		PixelShadow.attachAll(summary)
		summary?.visible = false
	}

	fun open() {
		if (isOpen) return
		val scenes = SceneManager.instance ?: return

		PixelShadow.setText(location, scenes.location)
		PixelShadow.setText(time, SaveGame.clock(scenes.playSeconds))
		summary?.visible = true
		PauseMenu.instance?.showPanel(false)
		ask(Phase.ASK, "Voulez-vous sauvegarder la partie ?")
	}

	/** À appeler à chaque image tant que l'écran est ouvert. */
	fun handle(interact: Boolean) {
		val box = MessageBox.instance ?: return
		if (phase != Phase.ASK && phase != Phase.OVERWRITE) return

		// La question s'écrit d'abord ; une pression la termine d'un coup.
		if (box.isScrolling) {
			if (interact) box.advance()
			return
		}

		val answers = choices ?: return
		if (!answers.isOpen) {
			answers.open()
			return
		}

		when (answers.handle(interact)) {
			YES -> if (phase == Phase.ASK && SaveGame.exists()) {
				ask(Phase.OVERWRITE, "Une sauvegarde existe déjà.\nVoulez-vous l'écraser ?")
			} else {
				save()
			}
			NO -> close()
			else -> {}
		}
	}

	@Register
	override fun _process(delta: Double) {
		if (phase != Phase.SAVED) return
		if (MessageBox.instance?.isScrolling == true) return

		held += delta
		if (held < holdSeconds) return

		// Tout se referme, le menu de pause avec.
		close()
		PauseMenu.instance?.close()
	}

	private fun ask(next: Phase, question: String) {
		phase = next
		choices?.close()
		MessageBox.instance?.say(T(question))
	}

	private fun save() {
		choices?.close()
		SceneManager.instance?.save()
		AudioManager.instance?.jingle("save")
		held = 0.0
		phase = Phase.SAVED
		MessageBox.instance?.say(T("La partie est sauvegardée."))
	}

	private fun close() {
		phase = Phase.CLOSED
		choices?.close()
		summary?.visible = false
		MessageBox.instance?.close()
		PauseMenu.instance?.showPanel(true)
	}
}

private const val YES = 0
private const val NO = 1
