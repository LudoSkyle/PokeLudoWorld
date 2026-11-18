package fr.skyle.pokemonmirage.scripts.gameplay.levels

import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.Node2D
import godot.core.Color
import godot.core.Vector2
import kotlin.math.PI
import kotlin.math.sin

/**
 * Un éclat qui scintille : il enfle et pâlit tour à tour, avec de loin en loin
 * un éclair plus vif. C'est ce qui fait remarquer une chose qui brille au
 * fond de l'eau sans qu'il faille la chercher du regard.
 *
 * Se pose sur n'importe quel dessin (un `Polygon2D`, un `Sprite2D`) : il n'en
 * change que la taille et la transparence, autour de celles de la scène.
 */
@Script
class Twinkle : Node2D() {

	/** La durée d'un battement, en secondes. */
	@Category("Scintillement")
	@Export
	var period: Double = 1.1

	/** De combien l'éclat enfle et rétrécit autour de sa taille : 0,35 = de 65 % à 135 %. */
	@Category("Scintillement")
	@Export
	var swell: Double = 0.35

	/** Sa transparence au plus pâle, de 0 à 1. */
	@Category("Scintillement")
	@Export
	var dim: Double = 0.35

	private var clock = 0.0
	private var rest = Vector2.ONE
	private var tint = Color(1.0, 1.0, 1.0, 1.0)

	@Register
	override fun _ready() {
		rest = scale
		tint = modulate
	}

	@Register
	override fun _process(delta: Double) {
		clock += delta
		// Un battement régulier, et par-dessus un second, trois fois plus lent : l'éclat n'est jamais deux fois le même.
		val beat = 0.5 + 0.5 * sin(2.0 * PI * clock / period)
		val slow = 0.5 + 0.5 * sin(2.0 * PI * clock / (period * 3.3))
		val glow = (0.7 * beat + 0.3 * slow).coerceIn(0.0, 1.0)
		scale = rest * (1.0 - swell + 2.0 * swell * glow)
		modulate = Color(tint.r, tint.g, tint.b, tint.a * (dim + (1.0 - dim) * glow))
	}
}
