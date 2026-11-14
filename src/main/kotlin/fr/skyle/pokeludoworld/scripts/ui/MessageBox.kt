package fr.skyle.pokeludoworld.scripts.ui

import fr.skyle.pokeludoworld.scripts.core.Settings
import fr.skyle.pokeludoworld.scripts.gameplay.items.Inventory
import fr.skyle.pokeludoworld.scripts.gameplay.items.Items
import fr.skyle.pokeludoworld.scripts.gameplay.story.StoryFlags
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
 * Elle ne lit jamais la touche d'interaction elle-même : c'est le joueur qui
 * la lui passe par [handle]. Un seul endroit lit la touche, donc la pression
 * qui ouvre la boîte ne peut pas la faire avancer dans la foulée.
 *
 * Une boîte peut commencer par des consignes, qui s'exécutent au moment où
 * elle s'affiche : `@give:<objet>` et `@flag:<drapeau>` (voir [directives]).
 * [ask] pose d'abord une question Oui / Non.
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

	/** Oui / Non, au-dessus de la boîte, pendant une question. */
	private var choices: ChoiceBox? = null
	private var asking = false
	private var afterYes: List<String> = emptyList()

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
		choices = getNode("Control/Choices") as? ChoiceBox
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
	 * Ouvre la boîte sur une question. Oui / Non apparaît une fois la question
	 * écrite, le curseur sur Oui. **Oui** enchaîne sur [then] ; **Non** — ou la
	 * touche du menu — referme la boîte sans rien dire de plus. Sans effet si
	 * la boîte est déjà ouverte.
	 */
	fun ask(question: String, then: List<String>) {
		if (isOpen) return

		pending.clear()
		asking = true
		afterYes = then
		box?.visible = true
		fullText = T(question)
		shown = 0
		elapsed = 0.0
		PixelShadow.setText(label, "")
	}

	/**
	 * À appeler à chaque image tant que la boîte d'un dialogue est ouverte.
	 * [interact] est la pression d'interaction lue par le joueur.
	 */
	fun handle(interact: Boolean) {
		if (!asking) {
			if (interact) advance()
			return
		}

		// La question s'écrit d'abord ; une pression la termine d'un coup.
		if (isScrolling) {
			if (interact) advance()
			return
		}

		val answers = choices ?: return
		if (!answers.isOpen) {
			answers.open()
			return
		}

		when (answers.handle(interact)) {
			YES -> {
				asking = false
				answers.close()
				pending.addAll(afterYes)
				next()
			}

			NO -> close()
			else -> {}
		}
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
		asking = false
		choices?.close()
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

		// Pendant qu'un objet rare est montré, aucune touche ne presse la suite ;
		// une question attend sa réponse (voir handle).
		if (revealing || asking) return

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
		fullText = T(directives(message))
		shown = 0
		elapsed = 0.0
		PixelShadow.setText(label, "")
	}

	/**
	 * Exécute les consignes en tête d'une boîte, au moment où elle s'affiche,
	 * et renvoie le texte sans elles. Plusieurs peuvent se suivre, chacune
	 * terminée par une espace :
	 *
	 * - `@give:<objet>` ou `@give:<objet>*<nombre>` met l'objet dans le sac ;
	 *   un objet rare est alors montré au centre de l'écran ;
	 * - `@flag:<drapeau>` pose un drapeau d'histoire.
	 */
	private fun directives(message: String): String {
		var text = message
		while (true) {
			val match = DIRECTIVE.matchEntire(text) ?: return text
			val (order, name, amount, rest) = match.destructured
			when (order) {
				"give" -> give(name, amount.toIntOrNull() ?: 1)
				"flag" -> StoryFlags.set(name)
			}
			text = rest
		}
	}

	private fun give(id: String, amount: Int) {
		val item = Items.get(id)
		if (item == null) {
			Logger.e("Objet inconnu dans un dialogue : $id")
			return
		}

		Inventory.add(id, amount)
		if (item.isKey) {
			revealing = true
			held = 0.0
			ItemReveal.instance?.reveal(item)
		}
	}
}

private const val REVEAL_SECONDS = 1.0
private const val YES = 0
private const val NO = 1
private val DIRECTIVE = Regex("""@(give|flag):(\w+)(?:\*(\d+))? (.*)""", RegexOption.DOT_MATCHES_ALL)
