package fr.skyle.pokeludoworld.scripts.ui

import fr.skyle.pokeludoworld.scripts.gameplay.items.Inventory
import fr.skyle.pokeludoworld.scripts.gameplay.items.Item
import fr.skyle.pokeludoworld.scripts.gameplay.items.ItemIcons
import fr.skyle.pokeludoworld.scripts.gameplay.items.Pocket
import godot.annotation.Register
import godot.annotation.Script
import godot.api.CanvasLayer
import godot.api.Control
import godot.api.Input
import godot.api.Label
import godot.api.ResourceLoader
import godot.api.Texture2D
import godot.api.TextureRect
import godot.core.Vector2

/**
 * Le sac, ouvert depuis le menu de pause : une poche à la fois, la liste de
 * ses objets, et la description de celui que le curseur désigne.
 *
 * - Haut / Bas : parcourir la liste, qui se termine toujours par **Retour**.
 *   Une poche vide ne contient que lui.
 * - Gauche / Droite : changer de poche.
 * - Retour, ou la touche du menu : refermer le sac.
 *
 * Valider un objet ouvre ses **actions** : Annuler seul pour un objet rare,
 * Jeter et Annuler pour les autres. Jeter demande combien, puis confirmation.
 */
@Script
class BagMenu : CanvasLayer() {

	companion object {
		var instance: BagMenu? = null
			private set
	}

	private enum class Mode { LIST, ACTIONS, AMOUNT, CONFIRM, DONE }

	private var screen: Control? = null
	private var title: Label? = null
	private var bag: TextureRect? = null
	private var left: Control? = null
	private var right: Control? = null
	private var up: Control? = null
	private var down: Control? = null
	private var cursor: Control? = null
	private var icon: TextureRect? = null
	private var description: Label? = null
	private var names: List<Label> = emptyList()
	private var amounts: List<Label> = emptyList()
	private var choices: ChoiceBox? = null
	private var amountPanel: Control? = null
	private var amountLabel: Label? = null

	private var mode = Mode.LIST
	private var pocket = 0
	private var line = 0
	private var top = 0
	private var entries: List<Pair<Item, Int>> = emptyList()

	/** Actions proposées pour l'objet choisi, dans l'ordre de la boîte. */
	private var actions: List<String> = emptyList()
	private var amount = 1

	val isOpen: Boolean
		get() = screen?.visible == true

	@Register
	override fun _ready() {
		instance = this
		screen = getNode("Control/Screen") as? Control
		title = getNode("Control/Screen/Title") as? Label
		bag = getNode("Control/Screen/Bag") as? TextureRect
		left = getNode("Control/Screen/PocketLeft") as? Control
		right = getNode("Control/Screen/PocketRight") as? Control
		up = getNode("Control/Screen/ScrollUp") as? Control
		down = getNode("Control/Screen/ScrollDown") as? Control
		cursor = getNode("Control/Screen/Cursor") as? Control
		icon = getNode("Control/Screen/Icon") as? TextureRect
		description = getNode("Control/Screen/Description") as? Label
		names = labels("Control/Screen/Names")
		amounts = labels("Control/Screen/Amounts")
		choices = getNode("Control/Screen/Choices") as? ChoiceBox
		amountPanel = getNode("Control/Screen/Amount") as? Control
		amountLabel = getNode("Control/Screen/Amount/Value") as? Label

		// La boîte de choix pose elle-même ses ombres.
		listOf(title, description, amountLabel).forEach { PixelShadow.attachAll(it) }
		(names + amounts).forEach { PixelShadow.attachAll(it) }
		amountPanel?.visible = false
		screen?.visible = false
	}

	/** S'ouvre sur la première poche, en haut de la liste. */
	fun open() {
		if (isOpen) return
		pocket = 0
		mode = Mode.LIST
		showPocket()
		screen?.visible = true
	}

	fun close() {
		choices?.close()
		amountPanel?.visible = false
		mode = Mode.LIST
		screen?.visible = false
	}

	/** À appeler à chaque image tant que le sac est ouvert. */
	fun handle(interact: Boolean) {
		if (!isOpen) return

		when (mode) {
			Mode.LIST -> browse(interact)
			Mode.ACTIONS -> when (actions.getOrNull(choices?.handle(interact) ?: -1)) {
				TOSS -> askAmount()
				CANCEL -> backToList()
			}
			Mode.AMOUNT -> pickAmount(interact)
			Mode.CONFIRM -> when (choices?.handle(interact)) {
				YES -> toss()
				NO -> backToList()
			}
			// Le message de fin attend une touche, n'importe laquelle.
			Mode.DONE -> if (interact || Input.isActionJustPressed(PauseMenu.ACTION)) backToList()
		}
	}

	// --- la liste

	private fun browse(interact: Boolean) {
		if (Input.isActionJustPressed(PauseMenu.ACTION)) {
			close()
			return
		}

		// Les poches ne bouclent pas : les flèches disent où l'on peut aller.
		if (Input.isActionJustPressed("ui_right") && pocket < POCKETS.size - 1) {
			pocket++
			showPocket()
		}
		if (Input.isActionJustPressed("ui_left") && pocket > 0) {
			pocket--
			showPocket()
		}

		// La liste non plus : Retour en est le bout.
		if (MenuKeys.down() && line < entries.size) move(line + 1)
		if (MenuKeys.up() && line > 0) move(line - 1)

		if (!interact) return
		if (line == entries.size) close() else askAction()
	}

	/** Affiche la poche courante depuis le haut. */
	private fun showPocket() {
		entries = Inventory.contents(POCKETS[pocket])
		line = 0
		top = 0
		refresh()
	}

	private fun move(to: Int) {
		line = to
		follow()
		refresh()
	}

	/** La fenêtre de six lignes suit le curseur. */
	private fun follow() {
		if (line < top) top = line
		if (line >= top + names.size) top = line - names.size + 1
		// Jamais de vide en bas si la liste peut remplir la fenêtre.
		top = top.coerceIn(0, maxOf(0, entries.size + 1 - names.size))
	}

	// --- les actions sur un objet

	private val selected: Item?
		get() = entries.getOrNull(line)?.first

	private fun askAction() {
		val item = selected ?: return
		// Un objet rare ne se jette pas.
		actions = if (item.isKey) listOf(CANCEL) else listOf(TOSS, CANCEL)
		mode = Mode.ACTIONS
		say(T("Objet choisi : %s.").format(T(item.name)))
		choices?.open(actions.map { T(it) })
	}

	private fun askAmount() {
		choices?.close()
		amount = 1
		mode = Mode.AMOUNT
		say(T("Combien en jeter ?"))
		amountPanel?.visible = true
		showAmount()
	}

	private fun pickAmount(interact: Boolean) {
		if (Input.isActionJustPressed(PauseMenu.ACTION)) {
			backToList()
			return
		}

		val most = entries.getOrNull(line)?.second ?: 1
		// La quantité boucle : sous 1 on saute au maximum, et inversement.
		if (MenuKeys.up()) amount = if (amount >= most) 1 else amount + 1
		if (MenuKeys.down()) amount = if (amount <= 1) most else amount - 1
		showAmount()

		if (!interact) return
		val item = selected ?: return
		amountPanel?.visible = false
		mode = Mode.CONFIRM
		say(T("Jeter %s x%d ?").format(T(item.name), amount))
		choices?.open(listOf(T(N("Oui")), T(N("Non"))))
	}

	private fun toss() {
		val item = selected ?: return
		choices?.close()
		Inventory.remove(item.id, amount)
		mode = Mode.DONE
		say(T("Vous jetez %s x%d.").format(T(item.name), amount))
		// La liste montre tout de suite ce qu'il reste ; le message, lui, attend une touche.
		reload()
		drawList()
	}

	private fun backToList() {
		choices?.close()
		amountPanel?.visible = false
		mode = Mode.LIST
		reload()
		refresh()
	}

	/** Relit la poche sans bouger le curseur, sauf s'il pointait une ligne disparue. */
	private fun reload() {
		entries = Inventory.contents(POCKETS[pocket])
		line = line.coerceAtMost(entries.size)
		follow()
	}

	private fun showAmount() {
		PixelShadow.setText(amountLabel, "x$amount")
	}

	// --- l'affichage

	private fun say(text: String) {
		PixelShadow.setText(description, text)
	}

	private fun refresh() {
		val current = POCKETS[pocket]
		PixelShadow.setText(title, current.title)
		bag?.texture = texture("${UI_DIR}bag_${current.bag}.png")
		left?.visible = pocket > 0
		right?.visible = pocket < POCKETS.size - 1

		drawList()

		val item = selected
		say(item?.description ?: BACK_DESCRIPTION)
		icon?.texture = ItemIcons.of(item?.icon ?: ItemIcons.BACK)
	}

	/** Les lignes : les objets, puis Retour, puis du vide. */
	private fun drawList() {
		names.forEachIndexed { row, label ->
			val index = top + row
			val entry = entries.getOrNull(index)
			PixelShadow.setText(
				label,
				when {
					entry != null -> entry.first.name
					index == entries.size -> BACK
					else -> ""
				},
			)
			PixelShadow.setText(amounts.getOrNull(row), if (entry != null && !entry.first.isKey) "x${entry.second}" else "")
		}
		up?.visible = top > 0
		down?.visible = top + names.size < entries.size + 1

		val arrow = cursor ?: return
		val list = names.firstOrNull()?.getParent() as? Control ?: return
		val y = list.getPosition().y + ROW * (line - top) + (ROW - arrow.getSize().y) / 2.0
		arrow.setPosition(Vector2(arrow.getPosition().x, y))
	}

	private fun labels(path: String): List<Label> {
		val parent = getNode(path)
		return (0 until (parent?.getChildCount() ?: 0)).mapNotNull { parent?.getChild(it) as? Label }
	}

	private fun texture(path: String): Texture2D? =
		if (ResourceLoader.exists(path)) ResourceLoader.load(path) as? Texture2D else null
}

private val POCKETS = Pocket.entries
private val BACK = N("Retour")
private val BACK_DESCRIPTION = N("Refermer le sac.")
private val TOSS = N("Jeter")
private val CANCEL = N("Annuler")
private const val YES = 0
private const val NO = 1
private const val ROW = 64.0
private const val UI_DIR = "res://src/main/kotlin/fr/skyle/pokeludoworld/assets/ui/bag/"
