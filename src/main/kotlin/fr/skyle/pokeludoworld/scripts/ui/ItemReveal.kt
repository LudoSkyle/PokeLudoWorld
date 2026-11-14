package fr.skyle.pokeludoworld.scripts.ui

import fr.skyle.pokeludoworld.scripts.gameplay.items.Item
import fr.skyle.pokeludoworld.scripts.gameplay.items.ItemIcons
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.CanvasLayer
import godot.api.Control
import godot.api.TextureRect
import godot.core.Color
import kotlin.math.max
import kotlin.math.min

/**
 * Montre un objet rare qu'on vient de trouver ou de recevoir : son icône au
 * centre de l'écran, dans un cadre de menu, qui apparaît et disparaît en
 * fondu.
 *
 * C'est la boîte de dialogue qui le pilote (voir MessageBox et le préfixe
 * `@give:`) : elle l'ouvre avec le texte qui annonce l'objet, et le referme
 * avant de passer à la suite.
 */
@Script
class ItemReveal : CanvasLayer() {

	companion object {
		var instance: ItemReveal? = null
			private set
	}

	@Category("Affichage")
	@Export
	var fadeSeconds: Double = 0.2

	private var panel: Control? = null
	private var icon: TextureRect? = null

	/** 0 = invisible, 1 = pleinement affiché. */
	private var shown = 0.0
	private var target = 0.0

	/** Vrai une fois le fondu d'apparition terminé. */
	val isFullyShown: Boolean
		get() = shown >= 1.0

	@Register
	override fun _ready() {
		instance = this
		panel = getNode("Control/Panel") as? Control
		icon = getNode("Control/Panel/Icon") as? TextureRect
		apply()
	}

	fun reveal(item: Item) {
		icon?.texture = ItemIcons.of(item.icon)
		target = 1.0
	}

	fun dismiss() {
		target = 0.0
	}

	@Register
	override fun _process(delta: Double) {
		if (shown == target) return
		val step = if (fadeSeconds > 0.0) delta / fadeSeconds else 1.0
		shown = if (target > shown) min(target, shown + step) else max(target, shown - step)
		apply()
	}

	private fun apply() {
		panel?.visible = shown > 0.0
		panel?.modulate = Color(1.0, 1.0, 1.0, shown)
	}
}
