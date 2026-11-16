package fr.skyle.pokeludoworld.scripts.ui

import godot.annotation.Register
import godot.annotation.Script
import godot.api.Control
import godot.api.Input
import godot.api.Label
import godot.core.Vector2

/**
 * Petite boîte de choix : des réponses l'une sous l'autre, avec le curseur des
 * menus. Posée au-dessus de la boîte de dialogue pour une question, ou dans un
 * coin d'un écran pour les actions possibles sur ce qu'on a choisi.
 *
 * Les réponses sont les `Label` de `Entries`. [open] sans argument les montre
 * telles que la scène les a écrites ; avec une liste, il les remplace et la
 * boîte s'ajuste en hauteur, **son bord bas restant en place**. S'il faut plus
 * de lignes que la scène n'en a, elle en ajoute, et grandit alors vers le bas
 * à partir de son bord haut d'origine.
 *
 * Elle ne lit pas la touche d'interaction : elle la reçoit par [handle], comme
 * les menus.
 */
@Script
class ChoiceBox : Control() {

	private var cursor: Control? = null
	private var frame: Control? = null
	private var labels: List<Label> = emptyList()
	private var count = 0
	private var bottom = 0.0
	private var top = 0.0

	var selected: Int = 0
		private set

	val isOpen: Boolean
		get() = visible

	@Register
	override fun _ready() {
		cursor = getNode("Cursor") as? Control
		frame = getNode("Frame") as? Control
		val list = getNode("Entries")
		labels = (0 until (list?.getChildCount() ?: 0)).mapNotNull { list?.getChild(it) as? Label }
		count = labels.size
		top = getPosition().y
		bottom = getPosition().y + getSize().y
		PixelShadow.attachAll(this)
		visible = false
	}

	/** S'ouvre sur la première réponse, avec les réponses écrites dans la scène. */
	fun open() {
		selected = 0
		visible = true
		placeCursor()
	}

	/** S'ouvre sur ces réponses-ci, déjà traduites, le curseur sur la réponse [start]. */
	fun open(answers: List<String>, start: Int = 0) {
		// Une ligne de plus que la scène n'en a : on recopie la dernière, ombre comprise.
		while (labels.size < answers.size) {
			val model = labels.lastOrNull() ?: break
			val extra = model.duplicate() as? Label ?: break
			extra.setName("Entry${labels.size}")
			model.getParent()?.addChild(extra)
			labels = labels + extra
		}
		count = minOf(answers.size, labels.size)
		labels.forEachIndexed { index, label ->
			label.visible = index < count
			if (index < count) PixelShadow.setText(label, answers[index])
		}

		val height = MARGINS + ROW * count
		setSize(Vector2(getSize().x, height))
		// Tant qu'elle tient dans sa hauteur d'origine, son bord bas ne bouge pas ; au-delà, c'est le haut.
		setPosition(Vector2(getPosition().x, if (height <= bottom - top) bottom - height else top))
		frame?.setSize(Vector2(getSize().x / SCALE, height / SCALE))
		open()
		if (start in 1 until count) {
			selected = start
			placeCursor()
		}
	}

	/** Change le texte d'une réponse sans refermer la boîte ni bouger le curseur. */
	fun relabel(index: Int, text: String) {
		labels.getOrNull(index)?.let { PixelShadow.setText(it, text) }
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
		if (!isOpen || count == 0) return null

		if (Input.isActionJustPressed(PauseMenu.ACTION)) return count - 1
		if (MenuKeys.down()) move(1)
		if (MenuKeys.up()) move(-1)
		return if (interact) selected else null
	}

	private fun move(step: Int) {
		selected = (selected + step + count) % count
		placeCursor()
	}

	private fun placeCursor() {
		val entry = labels.getOrNull(selected) ?: return
		val list = entry.getParent() as? Control ?: return
		val arrow = cursor ?: return
		// Les lignes ont toutes la même hauteur : pas besoin d'attendre que le
		// conteneur les ait replacées après un changement de réponses.
		val y = list.getPosition().y + ROW * selected + (ROW - arrow.getSize().y) / 2.0
		arrow.setPosition(Vector2(arrow.getPosition().x, y))
	}
}

private const val ROW = 64.0
private const val MARGINS = 64.0
private const val SCALE = 4.0
