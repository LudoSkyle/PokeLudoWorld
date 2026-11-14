package fr.skyle.pokeludoworld.scripts.ui

import fr.skyle.pokeludoworld.scripts.core.Settings
import fr.skyle.pokeludoworld.scripts.gameplay.items.Inventory
import fr.skyle.pokeludoworld.scripts.gameplay.items.Items
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

	/** Réglée par les options (voir Settings) ; 0 = le texte apparaît d'un coup. */
	@Category("Affichage")
	@Export
	var secondsPerLetter: Double = 0.02

	private var box: Control? = null
	private var label: RichTextLabel? = null

	private val pending = ArrayDeque<String>()
	private var fullText: String = ""
	private var shown: Int = 0
	private var elapsed: Double = 0.0

	/** Vrai pendant qu'un objet rare est montré : la boîte passe seule à la suite. */
	private var revealing = false
	private var held = 0.0

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
		PixelShadow.attachAll(label)
		box?.visible = false

		Settings.load()
		secondsPerLetter = Settings.secondsPerLetter

		Logger.i("Loading message box ...")
	}

	@Register
	override fun _process(delta: Double) {
		if (!isOpen) return

		if (!isScrolling) {
			// Objet rare à l'écran : une seconde une fois le texte écrit, puis la suite.
			if (!revealing || ItemReveal.instance?.isFullyShown == false) return
			held += delta
			if (held >= REVEAL_SECONDS) {
				revealing = false
				ItemReveal.instance?.dismiss()
				next()
			}
			return
		}

		elapsed += delta
		while (elapsed >= secondsPerLetter && shown < fullText.length) {
			elapsed -= secondsPerLetter
			shown++
		}

		PixelShadow.setText(label, fullText.substring(0, shown))
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
	 * Écrit un texte et le laisse à l'écran : aucune touche ne le fait passer,
	 * c'est l'appelant qui enchaîne ou qui referme avec [close]. Sert aux
	 * questions (voir SaveMenu). Le texte est dit tel quel, déjà traduit.
	 */
	fun say(text: String) {
		pending.clear()
		box?.visible = true
		fullText = text
		shown = 0
		elapsed = 0.0
		PixelShadow.setText(label, "")
	}

	fun close() {
		revealing = false
		ItemReveal.instance?.dismiss()
		pending.clear()
		box?.visible = false
		fullText = ""
		shown = 0
		PixelShadow.setText(label, "")
	}

	/**
	 * Termine le défilement en cours, ou passe au message suivant s'il est déjà
	 * entier. Ferme la boîte quand il n'y a plus rien à dire.
	 */
	fun advance() {
		if (isScrolling) {
			shown = fullText.length
			PixelShadow.setText(label, fullText)
			return
		}

		// Pendant qu'un objet rare est montré, aucune touche ne presse la suite.
		if (revealing) return

		next()
	}

	private fun next() {
		val message = pending.removeFirstOrNull()

		if (message == null) {
			box?.visible = false
			fullText = ""
			shown = 0
			PixelShadow.setText(label, "")
			return
		}

		// Les textes arrivent en français, la boîte les dit dans la langue choisie.
		fullText = T(give(message))
		shown = 0
		elapsed = 0.0
		PixelShadow.setText(label, "")
	}

	/**
	 * Un message qui commence par `@give:<objet>` (ou `@give:<objet>*<nombre>`)
	 * met l'objet dans le sac au moment où il s'affiche. Si c'est un objet
	 * rare, il est montré au centre de l'écran. Renvoie le texte sans le
	 * préfixe.
	 */
	private fun give(message: String): String {
		val match = GIVE.matchEntire(message) ?: return message
		val (id, amount, text) = match.destructured
		val item = Items.get(id)

		if (item == null) {
			Logger.e("Objet inconnu dans un dialogue : $id")
			return text
		}

		Inventory.add(id, amount.toIntOrNull() ?: 1)
		if (item.isKey) {
			revealing = true
			held = 0.0
			ItemReveal.instance?.reveal(item)
		}
		return text
	}
}

private const val REVEAL_SECONDS = 1.0
private val GIVE = Regex("""@give:(\w+)(?:\*(\d+))? (.*)""", RegexOption.DOT_MATCHES_ALL)
