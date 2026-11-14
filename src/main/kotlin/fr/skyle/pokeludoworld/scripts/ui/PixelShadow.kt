package fr.skyle.pokeludoworld.scripts.ui

import godot.api.Control
import godot.api.Label
import godot.api.Node
import godot.api.RichTextLabel
import godot.core.Color
import godot.core.Side
import godot.core.asStringName

/**
 * Ombre de texte à la façon des jeux d'origine : chaque pixel de lettre porte
 * une ombre **à droite, en dessous et en diagonale**. Godot ne sait décaler
 * l'ombre d'un texte que dans une seule direction — on lui laisse la
 * diagonale, et on ajoute ici les deux autres : deux copies du texte, de la
 * couleur de l'ombre, glissées derrière l'original.
 */
object PixelShadow {

	/** Un pixel de police, en pixels écran. */
	private const val PIXEL = 4.0

	private const val PREFIX = "PixelShadow"
	private val OFFSETS = listOf(PIXEL to 0.0, 0.0 to PIXEL)
	private val NONE = Color(0.0, 0.0, 0.0, 0.0)

	/** Ajoute l'ombre à tous les textes sous [root]. */
	fun attachAll(root: Node?) {
		val node = root ?: return
		// La liste est figée avant d'ajouter des copies, qui sont elles-mêmes des textes.
		val children = (0 until node.getChildCount()).mapNotNull { node.getChild(it) }
		if (node is Label || node is RichTextLabel) attach(node as Control)
		children.forEach { attachAll(it) }
	}

	private fun attach(text: Control) {
		if (text.name.toString().startsWith(PREFIX) || text.hasNode("${PREFIX}0")) return

		val colorName = if (text is RichTextLabel) "default_color" else "font_color"
		val shadow = text.getThemeColor("font_shadow_color".asStringName())

		// Toutes les copies sont faites AVANT d'en accrocher une : sinon la
		// seconde emporterait la première avec elle, et cette copie de copie
		// garderait l'ancien texte à chaque changement.
		val copies = OFFSETS.map { text.duplicate() as? Control }

		OFFSETS.forEachIndexed { index, (x, y) ->
			val copy = copies[index] ?: return@forEachIndexed
			copy.setName("$PREFIX$index")
			copy.addThemeColorOverride(colorName, shadow)
			copy.addThemeColorOverride("font_shadow_color", NONE)
			copy.showBehindParent = true
			copy.setMouseFilter(Control.MouseFilter.IGNORE)
			text.addChild(copy)

			// Même cadre que l'original, décalé d'un pixel de police.
			copy.setAnchor(Side.LEFT, 0.0f)
			copy.setAnchor(Side.TOP, 0.0f)
			copy.setAnchor(Side.RIGHT, 1.0f)
			copy.setAnchor(Side.BOTTOM, 1.0f)
			copy.setOffset(Side.LEFT, x.toFloat())
			copy.setOffset(Side.TOP, y.toFloat())
			copy.setOffset(Side.RIGHT, x.toFloat())
			copy.setOffset(Side.BOTTOM, y.toFloat())
		}
	}

	/** Change le texte d'un libellé et de ses ombres. */
	fun setText(text: Control?, value: String) {
		val label = text ?: return
		write(label, value)
		for (index in OFFSETS.indices) {
			if (label.hasNode("$PREFIX$index")) write(label.getNode("$PREFIX$index"), value)
		}
	}

	private fun write(node: Node?, value: String) {
		when (node) {
			is RichTextLabel -> node.text = value
			is Label -> node.text = value
			else -> {}
		}
	}
}
