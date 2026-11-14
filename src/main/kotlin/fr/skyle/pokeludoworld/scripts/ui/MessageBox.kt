package fr.skyle.pokeludoworld.scripts.ui

import fr.skyle.pokeludoworld.scripts.core.AudioManager
import fr.skyle.pokeludoworld.scripts.core.SceneManager
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
import godot.api.Label
import godot.api.RichTextLabel
import godot.core.Color
import godot.core.Vector2

/**
 * Boîte de dialogue, affichée lettre par lettre.
 *
 * Elle ne lit jamais la touche d'interaction elle-même : c'est le joueur qui
 * la lui passe par [handle]. Un seul endroit lit la touche, donc la pression
 * qui ouvre la boîte ne peut pas la faire avancer dans la foulée.
 *
 * Une boîte peut commencer par des consignes, qui s'exécutent au moment où
 * elle s'affiche : `@give:<objet>`, `@take:<objet>`, `@flag:<drapeau>`,
 * `@sound:<jingle>` et `@reload` (voir [directives]). Tant qu'un jingle joue,
 * la boîte ne passe pas à la suite.
 * [ask] pose d'abord une question Oui / Non.
 *
 * Quand celui qui parle a un nom, il s'affiche dans un encart au-dessus de la
 * boîte, à gauche — en rouge pour une femme, en bleu pour un homme. Une boîte qui donne un objet est dite par le jeu, pas par
 * lui : l'encart s'efface le temps de cette boîte.
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

	/** L'encart du nom, et le nom de celui qui parle (vide : personne). */
	private var speakerTag: Control? = null
	private var speakerLabel: Label? = null
	private var speaker = ""
	private var speakerGender = ""
	private var narrated = false

	/** Demandé par `@reload` : la carte est rechargée quand le dialogue se referme. */
	private var reloadWhenClosed = false

	val isOpen: Boolean
		get() = box?.visible == true

	/** Vrai pendant une question : Oui / Non attend sa réponse. */
	val isAsking: Boolean
		get() = asking

	/** Vrai tant que le texte courant n'est pas entièrement affiché. */
	val isScrolling: Boolean
		get() = shown < fullText.length

	@Register
	override fun _ready() {
		instance = this
		box = getNode("Control/Box") as? Control
		label = getNode("Control/Box/Text") as? RichTextLabel
		choices = getNode("Control/Choices") as? ChoiceBox
		speakerTag = getNode("Control/Speaker") as? Control
		speakerLabel = getNode("Control/Speaker/Name") as? Label
		PixelShadow.attachAll(speakerLabel)
		speakerTag?.visible = false
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
			// Au moins une seconde, et jusqu'au bout du jingle de l'objet.
			if (held >= REVEAL_SECONDS && AudioManager.instance?.isJinglePlaying != true) {
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

	/**
	 * Ouvre la boîte sur une suite de messages. Sans effet si elle est déjà
	 * ouverte. [speaker] est le nom de celui qui parle, en français, et
	 * [gender] son genre (`female`, `male`), qui donne sa couleur au nom.
	 */
	fun play(messages: List<String>, speaker: String = "", gender: String = "") {
		if (isOpen || messages.isEmpty()) return

		this.speaker = speaker
		speakerGender = gender
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
	fun ask(question: String, then: List<String>, speaker: String = "", gender: String = "") {
		if (isOpen) return

		this.speaker = speaker
		speakerGender = gender
		narrated = false
		showSpeaker()
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
		speaker = ""
		showSpeaker()
		pending.clear()
		box?.visible = true
		fullText = text
		shown = 0
		elapsed = 0.0
		PixelShadow.setText(label, "")
	}

	fun close() {
		speaker = ""
		showSpeaker()
		reloadWhenClosed = false
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
		// une question attend sa réponse (voir handle) ; un jingle se laisse finir.
		if (revealing || asking || AudioManager.instance?.isJinglePlaying == true) return

		next()
	}

	private fun next() {
		val message = pending.removeFirstOrNull()

		if (message == null) {
			speaker = ""
			showSpeaker()
			box?.visible = false
			fullText = ""
			shown = 0
			PixelShadow.setText(label, "")
			// Le dialogue a changé le monde : la carte se recharge dans un fondu.
			if (reloadWhenClosed) {
				reloadWhenClosed = false
				SceneManager.instance?.reload()
			}
			return
		}

		// Les textes arrivent en français, la boîte les dit dans la langue choisie.
		narrated = false
		fullText = T(directives(message))
		showSpeaker()
		shown = 0
		elapsed = 0.0
		PixelShadow.setText(label, "")
	}

	/** Montre l'encart du nom, à la largeur du nom, ou le cache s'il n'y a personne à nommer. */
	private fun showSpeaker() {
		val tag = speakerTag ?: return
		if (speaker.isBlank() || narrated) {
			tag.visible = false
			return
		}

		speakerLabel?.addThemeColorOverride("font_color", SPEAKER_COLORS[speakerGender] ?: SPEAKER_INK)
		PixelShadow.setText(speakerLabel, T(speaker))
		val width = (speakerLabel?.getMinimumSize()?.x ?: 0.0) + SPEAKER_MARGINS
		speakerLabel?.setSize(Vector2(width - SPEAKER_MARGINS, speakerLabel?.getSize()?.y ?: 64.0))
		tag.setSize(Vector2(width, tag.getSize().y))
		tag.visible = true
	}

	/**
	 * Exécute les consignes en tête d'une boîte, au moment où elle s'affiche,
	 * et renvoie le texte sans elles. Plusieurs peuvent se suivre, chacune
	 * terminée par une espace :
	 *
	 * - `@give:<objet>` ou `@give:<objet>*<nombre>` met l'objet dans le sac ;
	 *   un objet rare est alors montré au centre de l'écran ;
	 * - `@take:<objet>` ou `@take:<objet>*<nombre>` le retire du sac ;
	 * - `@flag:<drapeau>` pose un drapeau d'histoire ;
	 * - `@sound:<jingle>` joue un jingle, musique en pause (voir AudioManager) ;
	 * - `@reload` recharge la carte dans un fondu **une fois le dialogue
	 *   refermé** : c'est au chargement que se décide qui est sur la carte.
	 */
	private fun directives(message: String): String {
		var text = message
		while (true) {
			if (text.startsWith(RELOAD)) {
				reloadWhenClosed = true
				text = text.removePrefix(RELOAD)
				continue
			}
			val match = DIRECTIVE.matchEntire(text) ?: return text
			val (order, name, amount, rest) = match.destructured
			when (order) {
				"give" -> give(name, amount.toIntOrNull() ?: 1)
				"take" -> if (!Inventory.remove(name, amount.toIntOrNull() ?: 1)) {
					Logger.e("Objet à reprendre absent du sac : $name")
				}
				"flag" -> StoryFlags.set(name)
				"sound" -> AudioManager.instance?.jingle(name)
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
		// « Vous recevez... » : c'est le jeu qui le dit, pas le personnage.
		narrated = true
		AudioManager.instance?.jingle(if (item.isKey) "key_item" else "item")
		if (item.isKey) {
			revealing = true
			held = 0.0
			ItemReveal.instance?.reveal(item)
		}
	}
}

private const val REVEAL_SECONDS = 1.0
private const val SPEAKER_MARGINS = 56.0

/** Couleur du nom selon le genre, comme dans les jeux d'origine ; sans genre, l'encre du texte. */
private val SPEAKER_INK = Color(0.345098, 0.345098, 0.313725, 1.0)
private val SPEAKER_COLORS = mapOf(
	"female" to Color(0.878431, 0.188235, 0.156863, 1.0),
	"male" to Color(0.188235, 0.313725, 0.784314, 1.0),
)
private const val RELOAD = "@reload "
private const val YES = 0
private const val NO = 1
private val DIRECTIVE = Regex("""@(give|take|flag|sound):(\w+)(?:\*(\d+))? (.*)""", RegexOption.DOT_MATCHES_ALL)
