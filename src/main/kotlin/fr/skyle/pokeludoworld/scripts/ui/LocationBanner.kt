package fr.skyle.pokeludoworld.scripts.ui

import fr.skyle.pokeludoworld.scripts.log.Logger
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.CanvasLayer
import godot.api.Label
import godot.api.ResourceLoader
import godot.api.Texture2D
import godot.api.TextureRect
import godot.core.Color
import godot.core.Vector2
import kotlin.math.min

/**
 * Bandeau de lieu : il descend du haut de l'écran quand on arrive quelque
 * part, reste un instant, puis remonte.
 *
 * Il ne s'annonce que si le lieu **change** : monter à l'étage d'une maison
 * ne le fait pas réapparaître.
 */
@Script
class LocationBanner : CanvasLayer() {

	companion object {
		var instance: LocationBanner? = null
			private set
	}

	@Category("Affichage")
	@Export
	var slideSeconds: Double = 0.3

	@Category("Affichage")
	@Export
	var holdSeconds: Double = 2.2

	private enum class Phase { HIDDEN, WAITING, SLIDE_IN, HOLD, SLIDE_OUT }

	private var panel: TextureRect? = null
	private var label: Label? = null

	private var phase = Phase.HIDDEN
	private var elapsed = 0.0
	private var delay = 0.0
	private var pending = ""
	private var pendingStyle = DEFAULT_STYLE

	/** Dernier lieu annoncé. */
	var location: String = ""
		private set

	val isShowing: Boolean
		get() = phase != Phase.HIDDEN

	@Register
	override fun _ready() {
		instance = this
		panel = getNode("Control/Panel") as? TextureRect
		label = getNode("Control/Panel/Name") as? Label
		panel?.visible = false
	}

	/**
	 * Annonce [name] après [after] secondes — le temps que le fondu d'arrivée
	 * se lève. Sans effet si l'on y est déjà, ou si le nom est vide.
	 * [style] est le nom d'un bandeau de `assets/ui/banners`.
	 */
	fun announce(name: String, style: String, after: Double) {
		if (name.isEmpty() || name == location) return

		location = name
		pending = name
		pendingStyle = style.ifEmpty { DEFAULT_STYLE }
		delay = after
		elapsed = 0.0
		phase = Phase.WAITING
		panel?.visible = false
	}

	@Register
	override fun _process(delta: Double) {
		if (phase == Phase.HIDDEN) return
		elapsed += delta

		when (phase) {
			Phase.HIDDEN -> {}

			Phase.WAITING -> if (elapsed >= delay) {
				open()
				next(Phase.SLIDE_IN)
			}

			Phase.SLIDE_IN -> {
				place(progress())
				if (elapsed >= slideSeconds) next(Phase.HOLD)
			}

			Phase.HOLD -> if (elapsed >= holdSeconds) next(Phase.SLIDE_OUT)

			Phase.SLIDE_OUT -> {
				place(1.0 - progress())
				if (elapsed >= slideSeconds) {
					panel?.visible = false
					next(Phase.HIDDEN)
				}
			}
		}
	}

	private fun open() {
		val box = panel ?: return
		val text = label ?: return

		text.text = pending

		val texture = ResourceLoader.load("$BANNERS_DIR$pendingStyle.png") as? Texture2D
		if (texture == null) {
			Logger.e("Bandeau de lieu inconnu : $pendingStyle")
		} else {
			box.texture = texture
			// Un pixel du bandeau vaut un pixel du jeu, comme le décor.
			box.setSize(Vector2(texture.getWidth() * PIXEL, texture.getHeight() * PIXEL))
		}

		// Texte clair sur les bandeaux sombres, sombre sur les clairs.
		val dark = pendingStyle in DARK_STYLES
		text.addThemeColorOverride("font_color", if (dark) LIGHT_INK else DARK_INK)
		text.addThemeColorOverride("font_shadow_color", if (dark) LIGHT_SHADOW else DARK_SHADOW)
		place(0.0)
		box.visible = true
	}

	private fun next(to: Phase) {
		phase = to
		elapsed = 0.0
	}

	private fun progress(): Double = if (slideSeconds > 0.0) min(elapsed / slideSeconds, 1.0) else 1.0

	/** 0 = caché au-dessus de l'écran, 1 = posé à sa place. */
	private fun place(t: Double) {
		val box = panel ?: return
		val hidden = -box.getSize().y - 8.0
		box.setPosition(Vector2(MARGIN, hidden + (MARGIN - hidden) * t))
	}

}

private const val MARGIN = 24.0
private const val PIXEL = 4.0
private const val DEFAULT_STYLE = "wood"
private const val BANNERS_DIR = "res://src/main/kotlin/fr/skyle/pokeludoworld/assets/ui/banners/"

private val DARK_STYLES = setOf("cave", "forest", "water")
private val DARK_INK = Color(0.19, 0.19, 0.19, 1.0)
private val DARK_SHADOW = Color(0.0, 0.0, 0.0, 0.25)
private val LIGHT_INK = Color(1.0, 1.0, 1.0, 1.0)
private val LIGHT_SHADOW = Color(0.0, 0.0, 0.0, 0.6)
