package fr.skyle.pokeludoworld.scripts.ui

import godot.api.FontFile
import godot.api.Label
import godot.api.Node
import godot.api.ResourceLoader

/**
 * Police des menus. Celle qu'on veut a une licence qui interdit de la
 * redistribuer : elle ne peut pas être dans le dépôt. Elle se pose donc à la
 * main dans `assets/fonts/local/` (voir son README), et sans elle les menus
 * gardent la police écrite dans leur scène.
 */
object UiFonts {

	private const val MENU_FONT = "res://src/main/kotlin/fr/skyle/pokeludoworld/assets/fonts/local/menu.ttf"

	/** Un pixel de la police = 4 pixels écran, comme le décor et les cadres. */
	private const val MENU_SIZE = 40
	private const val MENU_SHADOW = 4

	private var menuFont: FontFile? = null
	private var searched = false

	val hasMenuFont: Boolean
		get() = menuFont() != null

	private fun menuFont(): FontFile? {
		if (!searched) {
			searched = true
			if (ResourceLoader.exists(MENU_FONT)) menuFont = ResourceLoader.load(MENU_FONT) as? FontFile
		}
		return menuFont
	}

	/** Passe tous les Label sous [root] à la police des menus, si elle est là. */
	fun applyMenuFont(root: Node?) {
		val font = menuFont() ?: return
		val node = root ?: return

		if (node is Label) {
			node.addThemeFontOverride("font", font)
			node.addThemeFontSizeOverride("font_size", MENU_SIZE)
			node.addThemeConstantOverride("shadow_offset_x", MENU_SHADOW)
			node.addThemeConstantOverride("shadow_offset_y", MENU_SHADOW)
		}
		for (i in 0 until node.getChildCount()) applyMenuFont(node.getChild(i))
	}
}
