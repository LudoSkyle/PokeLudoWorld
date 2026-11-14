package fr.skyle.pokeludoworld.scripts.ui

import fr.skyle.pokeludoworld.scripts.gameplay.items.Inventory
import fr.skyle.pokeludoworld.scripts.gameplay.items.Item
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
 * Valider un objet ne fait encore rien : il n'y a pas d'usage à leur donner.
 */
@Script
class BagMenu : CanvasLayer() {

	companion object {
		var instance: BagMenu? = null
			private set
	}

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

	private var pocket = 0
	private var line = 0
	private var top = 0
	private var entries: List<Pair<Item, Int>> = emptyList()

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

		PixelShadow.attachAll(screen)
		screen?.visible = false
	}

	/** S'ouvre sur la première poche, en haut de la liste. */
	fun open() {
		if (isOpen) return
		pocket = 0
		showPocket()
		screen?.visible = true
	}

	fun close() {
		screen?.visible = false
	}

	/** À appeler à chaque image tant que le sac est ouvert. */
	fun handle(interact: Boolean) {
		if (!isOpen) return

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
		if (Input.isActionJustPressed("ui_down") && line < entries.size) move(line + 1)
		if (Input.isActionJustPressed("ui_up") && line > 0) move(line - 1)

		if (interact && line == entries.size) close()
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
		// La fenêtre suit le curseur.
		if (line < top) top = line
		if (line >= top + names.size) top = line - names.size + 1
		refresh()
	}

	private fun refresh() {
		val current = POCKETS[pocket]
		PixelShadow.setText(title, current.title)
		bag?.texture = texture("${UI_DIR}bag_${current.bag}.png")
		left?.visible = pocket > 0
		right?.visible = pocket < POCKETS.size - 1

		// Les lignes : les objets, puis Retour, puis du vide.
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
			PixelShadow.setText(amounts.getOrNull(row), if (entry != null && entry.first.counted) "x${entry.second}" else "")
		}
		up?.visible = top > 0
		down?.visible = top + names.size < entries.size + 1

		names.getOrNull(line - top)?.let { label ->
			val list = label.getParent() as? Control
			val arrow = cursor
			if (list != null && arrow != null) {
				val y = list.getPosition().y + label.getPosition().y + (label.getSize().y - arrow.getSize().y) / 2.0
				arrow.setPosition(Vector2(arrow.getPosition().x, y))
			}
		}

		val selected = entries.getOrNull(line)?.first
		PixelShadow.setText(description, selected?.description ?: BACK_DESCRIPTION)
		icon?.texture = texture("$ITEMS_DIR${selected?.id ?: "_back"}.png") ?: texture("${ITEMS_DIR}_unknown.png")
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
private const val UI_DIR = "res://src/main/kotlin/fr/skyle/pokeludoworld/assets/ui/bag/"
private const val ITEMS_DIR = "res://src/main/kotlin/fr/skyle/pokeludoworld/assets/items/"
