package fr.skyle.pokeludoworld.scripts.ui

import fr.skyle.pokeludoworld.scripts.log.Logger
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.CanvasLayer
import godot.api.Control
import godot.api.RichTextLabel

/**
 * Boîte de dialogue, affichée lettre par lettre.
 *
 * Elle ne lit jamais l'entrée elle-même : c'est le joueur qui appelle
 * [advance]. Un seul endroit lit la touche, donc la pression qui ouvre la
 * boîte ne peut pas la faire avancer dans la foulée.
 */
@Script
class MessageBox : CanvasLayer() {

	companion object {
		var instance: MessageBox? = null
			private set
	}

	@Category("Affichage")
	@Export
	var secondsPerLetter: Double = 0.02

	private var box: Control? = null
	private var label: RichTextLabel? = null

	private val pending = ArrayDeque<String>()
	private var fullText: String = ""
	private var shown: Int = 0
	private var elapsed: Double = 0.0

	val isOpen: Boolean
		get() = box?.visible == true

	/** Vrai tant que le texte courant n'est pas entièrement affiché. */
	val isScrolling: Boolean
		get() = shown < fullText.length

	@Register
	override fun _ready() {
		instance = this
		box = getNode("Control/Box") as? Control
		label = getNode("Control/Box/Text") as? RichTextLabel
		box?.visible = false

		Logger.i("Loading message box ...")
	}

	@Register
	override fun _process(delta: Double) {
		if (!isOpen || !isScrolling) return

		elapsed += delta
		while (elapsed >= secondsPerLetter && shown < fullText.length) {
			elapsed -= secondsPerLetter
			shown++
		}

		label?.text = fullText.substring(0, shown)
	}

	/** Ouvre la boîte sur une suite de messages. Sans effet si elle est déjà ouverte. */
	fun play(messages: List<String>) {
		if (isOpen || messages.isEmpty()) return

		pending.clear()
		pending.addAll(messages)
		box?.visible = true
		next()
	}

	/**
	 * Termine le défilement en cours, ou passe au message suivant s'il est déjà
	 * entier. Ferme la boîte quand il n'y a plus rien à dire.
	 */
	fun advance() {
		if (isScrolling) {
			shown = fullText.length
			label?.text = fullText
			return
		}

		next()
	}

	private fun next() {
		val message = pending.removeFirstOrNull()

		if (message == null) {
			box?.visible = false
			fullText = ""
			shown = 0
			label?.text = ""
			return
		}

		fullText = message
		shown = 0
		elapsed = 0.0
		label?.text = ""
	}
}
