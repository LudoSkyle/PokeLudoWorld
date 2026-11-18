package fr.skyle.pokemonmirage.scripts.ui

import fr.skyle.pokemonmirage.scripts.core.AudioManager
import fr.skyle.pokemonmirage.scripts.core.SaveGame
import fr.skyle.pokemonmirage.scripts.log.Logger
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.Control
import godot.api.Input
import godot.api.Label
import godot.api.PackedScene
import godot.api.ResourceLoader
import godot.core.Color
import godot.core.Vector2
import kotlin.math.abs
import kotlin.math.min
import kotlin.math.sin

/**
 * L'écran de sélection des parties, ouvert par l'écran titre : une rangée de
 * cartes qu'on fait défiler de gauche à droite, celle du milieu étant choisie.
 *
 * - une carte par partie sauvegardée, dans l'ordre des emplacements ;
 * - « Nouvelle partie », tant qu'il reste un emplacement libre ;
 * - « Options ».
 *
 * Valider une partie ouvre trois réponses : Continuer, Effacer, Retour.
 * Effacer demande confirmation, le curseur sur Non.
 *
 * Comme les menus, il ne lit pas la touche d'interaction : il la reçoit par
 * [handle], et dit en retour ce qui a été choisi.
 */
@Script
class SaveSlots : Control() {

	enum class Kind { CONTINUE, NEW_GAME, OPTIONS, BACK }

	/** Ce que le joueur a choisi ; [slot] est l'emplacement de la partie à reprendre ou à créer. */
	class Choice(val kind: Kind, val slot: Int = 0)

	private enum class Mode { BROWSE, ACTIONS, CONFIRM }

	private class Entry(val name: String, val slot: Int, val card: SaveCard)

	/** Écart entre deux cartes, en pixels d'écran : la voisine dépasse du bord. */
	@Category("Rangee")
	@Export
	var pitch: Double = 992.0

	/** Vitesse du glissement d'une carte à l'autre : la part du chemin faite par seconde. */
	@Export
	var slide: Double = 14.0

	/** Opacité des cartes qui ne sont pas choisies. */
	@Export
	var dimmed: Double = 0.55

	private var strip: Control? = null
	private var left: Control? = null
	private var right: Control? = null
	private var hint: Label? = null
	private var choices: ChoiceBox? = null

	private var entries: List<Entry> = emptyList()
	private var mode = Mode.BROWSE
	private var clock = 0.0
	private var arrowHome = 0.0

	/** La carte choisie, comptée à partir de 0. */
	var selected: Int = 0
		private set

	val isOpen: Boolean
		get() = visible

	@Register
	override fun _ready() {
		strip = getNode("Strip") as? Control
		left = getNode("Left") as? Control
		right = getNode("Right") as? Control
		hint = getNode("Footer/Hint") as? Label
		choices = getNode("Choices") as? ChoiceBox
		arrowHome = left?.getPosition()?.y ?: 0.0
		PixelShadow.attachAll(getNode("Header"))
		PixelShadow.attachAll(getNode("Footer"))
		visible = false
	}

	/**
	 * Ouvre l'écran, les cartes refaites d'après les sauvegardes du moment. Le
	 * curseur va sur la carte nommée [on] (`Save1`, `New`, `Options`) si elle
	 * existe, sinon sur la première.
	 */
	fun open(on: String = "") {
		build()
		selected = entries.indexOfFirst { it.name == on }.coerceAtLeast(0)
		mode = Mode.BROWSE
		choices?.close()
		PixelShadow.setText(hint, "")
		visible = true
		// Pas de glissement à l'ouverture : la carte choisie est déjà au milieu.
		strip?.let { it.setPosition(Vector2(target(), it.getPosition().y)) }
		refresh()
	}

	fun close() {
		choices?.close()
		visible = false
	}

	private fun build() {
		val host = strip ?: return
		entries.forEach {
			host.removeChild(it.card)
			it.card.queueFree()
		}
		val scene = ResourceLoader.load(CARD) as? PackedScene
		if (scene == null) {
			Logger.e("Carte de partie introuvable : $CARD")
			entries = emptyList()
			return
		}

		val made = ArrayList<Entry>()
		fun add(name: String, slot: Int, fill: (SaveCard) -> Unit) {
			val card = scene.instantiate() as? SaveCard ?: return
			card.setName(name)
			host.addChild(card)
			card.setPosition(Vector2((host.getSize().x - card.getSize().x) / 2.0 + made.size * pitch, 0.0))
			fill(card)
			made.add(Entry(name, slot, card))
		}

		SaveGame.used().forEach { slot ->
			val state = SaveGame.read(slot) ?: return@forEach
			add("Save$slot", slot) { it.showSave(slot, state) }
		}
		// Sans emplacement libre, pas de nouvelle partie : il faut d'abord en effacer une.
		SaveGame.firstFree()?.let { free -> add("New", free) { it.showAction(T(NEW_GAME)) } }
		add("Options", 0) { it.showAction(T(OPTIONS)) }
		entries = made
	}

	/**
	 * À appeler à chaque image tant que l'écran est ouvert. Renvoie ce qui a
	 * été choisi, ou null tant que rien ne l'est.
	 */
	fun handle(interact: Boolean): Choice? {
		if (!isOpen || entries.isEmpty()) return null
		val audio = AudioManager.instance
		val entry = entries[selected]

		when (mode) {
			Mode.BROWSE -> {
				if (Input.isActionJustPressed(PauseMenu.ACTION)) {
					audio?.sfx("cancel")
					return Choice(Kind.BACK)
				}
				if (MenuKeys.step("ui_right")) move(1)
				if (MenuKeys.step("ui_left")) move(-1)
				if (!interact) return null

				audio?.sfx("confirm")
				return when (entry.name) {
					"New" -> Choice(Kind.NEW_GAME, entry.slot)
					"Options" -> Choice(Kind.OPTIONS)
					else -> {
						mode = Mode.ACTIONS
						choices?.open(listOf(T(CONTINUE), T(DELETE), T(BACK)))
						// Les flèches s'effacent : on ne change plus de carte tant qu'on lui répond.
						refresh()
						null
					}
				}
			}
			Mode.ACTIONS -> {
				// La touche du menu répond la dernière réponse : Retour.
				val answer = choices?.handle(interact) ?: return null
				audio?.sfx(if (answer == 2) "cancel" else "confirm")
				when (answer) {
					0 -> {
						choices?.close()
						return Choice(Kind.CONTINUE, entry.slot)
					}
					1 -> {
						mode = Mode.CONFIRM
						PixelShadow.setText(hint, T(DELETE_ASK).format(entry.slot))
						// Le curseur attend sur Non : effacer ne se fait pas d'une pression de trop.
						choices?.open(listOf(T(YES), T(NO)), 1)
					}
					else -> browse()
				}
			}
			Mode.CONFIRM -> {
				val answer = choices?.handle(interact) ?: return null
				audio?.sfx(if (answer == 0) "confirm" else "cancel")
				if (answer == 0) {
					SaveGame.delete(entry.slot)
					// La carte disparaît ; le curseur reste où il était, sur celle qui prend sa place.
					val keep = selected
					build()
					selected = keep.coerceIn(0, (entries.size - 1).coerceAtLeast(0))
					strip?.let { it.setPosition(Vector2(target(), it.getPosition().y)) }
				}
				browse()
			}
		}
		return null
	}

	private fun browse() {
		mode = Mode.BROWSE
		choices?.close()
		PixelShadow.setText(hint, "")
		refresh()
	}

	/** La rangée boucle : après la dernière carte, la première. */
	private fun move(step: Int) {
		selected = (selected + step + entries.size) % entries.size
		refresh()
	}

	/** La carte choisie est pleine, les autres estompées. */
	private fun refresh() {
		entries.forEachIndexed { index, entry ->
			entry.card.modulate = Color(1.0, 1.0, 1.0, if (index == selected) 1.0 else dimmed)
		}
		val several = entries.size > 1 && mode == Mode.BROWSE
		left?.visible = several
		right?.visible = several
	}

	/** Où doit se trouver la rangée pour que la carte choisie soit au milieu. */
	private fun target(): Double = -selected * pitch

	@Register
	override fun _process(delta: Double) {
		if (!isOpen) return
		clock += delta

		// La rangée glisse vers la carte choisie, de plus en plus doucement.
		strip?.let {
			val x = it.getPosition().x
			val goal = target()
			val next = if (abs(goal - x) < 1.0) goal else x + (goal - x) * min(delta * slide, 1.0)
			it.setPosition(Vector2(next, it.getPosition().y))
		}

		// Les flèches battent, par crans d'un pixel de jeu.
		val beat = if (sin(clock * 5.0) > 0.0) 0.0 else 4.0
		left?.setPosition(Vector2(LEFT_X - beat, arrowHome))
		right?.setPosition(Vector2(RIGHT_X + beat, arrowHome))
	}

	// --- vu de Godot : ce que les tests regardent

	/** Les noms des cartes, dans l'ordre, séparés par des virgules : `Save1,New,Options`. */
	@Register
	fun cardNames(): String = entries.joinToString(",") { it.name }

	/** Le nom de la carte choisie. */
	@Register
	fun selectedName(): String = entries.getOrNull(selected)?.name ?: ""

	/** Vrai quand la rangée a fini de glisser. */
	@Register
	fun isSettled(): Boolean = abs((strip?.getPosition()?.x ?: 0.0) - target()) < 1.0
}

private const val CARD = "res://src/main/kotlin/fr/skyle/pokemonmirage/scenes/ui/save_card.tscn"
private const val LEFT_X = 24.0
private const val RIGHT_X = 1192.0
private val NEW_GAME = N("Nouvelle partie")
private val OPTIONS = N("Options")
private val CONTINUE = N("Continuer")
private val DELETE = N("Effacer")
private val BACK = N("Retour")
private val DELETE_ASK = N("Effacer la partie %d ?")
private val YES = N("Oui")
private val NO = N("Non")
