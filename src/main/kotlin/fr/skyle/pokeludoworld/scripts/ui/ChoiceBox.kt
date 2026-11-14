package fr.skyle.pokeludoworld.scripts.ui

import godot.annotation.Register
import godot.annotation.Script
import godot.api.Control
import godot.api.Input
import godot.core.Vector2

/**
 * Petite boîte de choix posée au-dessus de la boîte de dialogue : les réponses
 * à une question, l'une sous l'autre, avec le curseur des menus.
 *
 * Les réponses sont les enfants de `Entries`. Elle ne lit pas la touche
 * d'interaction : elle la reçoit par [handle], comme les menus.
 */
@Script
class ChoiceBox : Control() {

	private var cursor: Control? = null
	private var entries: List<Control> = emptyList()

	var selected: Int = 0
		private set

	val isOpen: Boolean
		get() = visible

	@Register
	override fun _ready() {
		cursor = getNode("Cursor") as? Control
		val list = getNode("Entries")
		entries = (0 until (list?.getChildCount() ?: 0)).mapNotNull { list?.getChild(it) as? Control }
		PixelShadow.attachAll(this)
		visible = false
	}

	/** S'ouvre sur la première réponse. */
	fun open() {
		selected = 0
		visible = true
		placeCursor()
	}

	fun close() {
		visible = false
	}

	/**
	 * À appeler à chaque image. Renvoie l'indice de la réponse validée, ou
	 * null tant que rien n'est choisi. La touche du menu répond la **dernière**
	 * réponse, qui est par convention le refus.
	 */
	fun handle(interact: Boolean): Int? {
		if (!isOpen || entries.isEmpty()) return null

		if (Input.isActionJustPressed(PauseMenu.ACTION)) return entries.size - 1
		if (Input.isActionJustPressed("ui_down")) move(1)
		if (Input.isActionJustPressed("ui_up")) move(-1)
		return if (interact) selected else null
	}

	private fun move(step: Int) {
		selected = (selected + step + entries.size) % entries.size
		placeCursor()
	}

	private fun placeCursor() {
		val entry = entries.getOrNull(selected) ?: return
		val list = entry.getParent() as? Control ?: return
		val arrow = cursor ?: return
		val y = list.getPosition().y + entry.getPosition().y + (entry.getSize().y - arrow.getSize().y) / 2.0
		arrow.setPosition(Vector2(arrow.getPosition().x, y))
	}
}
