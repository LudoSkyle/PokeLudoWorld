package fr.skyle.pokeludoworld.scripts.ui

import fr.skyle.pokeludoworld.scripts.core.Settings
import godot.annotation.Register
import godot.annotation.Script
import godot.api.CanvasLayer
import godot.api.Control
import godot.api.Input
import godot.api.Label
import godot.core.Color
import godot.core.Vector2

/**
 * Écran des options, ouvert depuis le menu de pause et posé par-dessus lui.
 *
 * Une ligne par réglage : Haut/Bas changent de ligne, Gauche/Droite changent
 * la valeur, qui s'applique et s'enregistre aussitôt. La dernière ligne,
 * Retour, ramène au menu — comme la touche du menu.
 *
 * Comme le menu, il ne lit pas la touche d'interaction : il la reçoit par
 * [handle], appelé par le menu de pause.
 */
@Script
class OptionsMenu : CanvasLayer() {

	companion object {
		var instance: OptionsMenu? = null
			private set
	}

	private var screen: Control? = null
	private var cursor: Control? = null
	private var rows: List<Control> = emptyList()
	private var speeds: List<Label> = emptyList()

	private var row = 0

	val isOpen: Boolean
		get() = screen?.visible == true

	@Register
	override fun _ready() {
		instance = this
		screen = getNode("Control/Screen") as? Control
		cursor = getNode("Control/Screen/Cursor") as? Control

		val list = getNode("Control/Screen/Rows")
		rows = (0 until (list?.getChildCount() ?: 0)).mapNotNull { list?.getChild(it) as? Control }

		val choices = getNode("Control/Screen/Rows/TextSpeed/Choices")
		speeds = (0 until (choices?.getChildCount() ?: 0)).mapNotNull { choices?.getChild(it) as? Label }

		UiFonts.applyMenuFont(screen)
		screen?.visible = false
	}

	fun open() {
		if (isOpen) return
		row = 0
		screen?.visible = true
		refresh()
	}

	fun close() {
		screen?.visible = false
	}

	/** À appeler à chaque image tant que l'écran est ouvert. */
	fun handle(interact: Boolean) {
		if (!isOpen) return

		if (Input.isActionJustPressed(PauseMenu.ACTION)) {
			close()
			return
		}

		if (Input.isActionJustPressed("ui_down")) row = (row + 1) % rows.size
		if (Input.isActionJustPressed("ui_up")) row = (row - 1 + rows.size) % rows.size

		when (rows.getOrNull(row)?.name?.toString()) {
			"TextSpeed" -> {
				// Pas de boucle ici : Lente et Instantanée sont les deux bouts.
				if (Input.isActionJustPressed("ui_right")) setTextSpeed(Settings.textSpeed + 1)
				if (Input.isActionJustPressed("ui_left")) setTextSpeed(Settings.textSpeed - 1)
			}
			"Back" -> if (interact) {
				close()
				return
			}
		}

		refresh()
	}

	private fun setTextSpeed(index: Int) {
		Settings.setTextSpeed(index)
		MessageBox.instance?.secondsPerLetter = Settings.secondsPerLetter
	}

	private fun refresh() {
		speeds.forEachIndexed { index, label ->
			label.addThemeColorOverride("font_color", if (index == Settings.textSpeed) CHOSEN else INK)
		}

		val current = rows.getOrNull(row) ?: return
		val list = current.getParent() as? Control ?: return
		val arrow = cursor ?: return
		val y = list.getPosition().y + current.getPosition().y + (current.getSize().y - arrow.getSize().y) / 2.0
		arrow.setPosition(Vector2(arrow.getPosition().x, y))
	}
}

private val INK = Color(0.376471, 0.376471, 0.376471, 1.0)
private val CHOSEN = Color(0.878431, 0.188235, 0.125490, 1.0)
