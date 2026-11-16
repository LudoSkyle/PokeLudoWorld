package fr.skyle.pokeludoworld.scripts.gameplay.characters

import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.AnimatedSprite2D
import godot.api.Node
import godot.api.Node2D
import godot.api.PackedScene
import godot.api.ResourceLoader
import godot.api.Sprite2D
import godot.api.Texture2D
import godot.api.TileMapLayer
import fr.skyle.pokeludoworld.scripts.gameplay.levels.Water
import godot.core.Rect2
import godot.core.Vector2
import kotlin.math.floor

/**
 * Le reflet d'un personnage dans l'eau qu'il longe : le joueur et les PNJ.
 * Un Pokémon qui vole n'en a pas — trop haut, et de lui on ne voit déjà qu'une
 * ombre, qui bleuit sur l'eau (`WaterShadow.kt`).
 *
 * Le reflet est **l'image du moment, retournée**, et il la reprend à chaque
 * frame : la même pose, la même direction, au même instant que le personnage.
 * Rien n'est pré-calculé, donc marcher, courir, pivoter ou battre des ailes se
 * voit aussitôt dans l'eau.
 *
 * Il est posé en **miroir de la ligne où le personnage touche le sol**
 * ([groundOffset]) : ses pieds, soit le bas de sa case.
 *
 * Il n'apparaît que si **la case qui commence sous cette ligne est de l'eau**,
 * ce que dit la donnée perso `water` de la tuile (voir docs/tilesets.md), lue
 * sur le calque le plus haut : sous un ponton, pas de reflet.
 *
 * Les reflets sont rangés dans un `Background/Reflections` posé **juste
 * au-dessus du calque d'eau** : un reflet qui dépasse sur le sable est donc
 * recouvert par le calque du sable, sans rien avoir à découper.
 */
@Script
class Reflection : Node() {

	/** La ligne où le personnage touche le sol, depuis son origine, en pixels. */
	@Category("Reflet")
	@Export
	var groundOffset: Double = 8.0

	/**
	 * De combien le reflet remonte vers le personnage, en pixels. Le bas d'une
	 * image de personnage est transparent sur deux ou trois pixels ; le miroir
	 * double cet écart et décollerait le reflet de ses pieds.
	 */
	@Category("Reflet")
	@Export
	var lift: Double = 5.0

	/** Le nœud frère qui porte son image. */
	@Category("Reflet")
	@Export
	var spriteName: String = "Sprite"

	private var body: Node2D? = null
	private var art: Node2D? = null
	private var scene: PackedScene? = null

	/** La carte où l'on a cherché l'eau, pour la rechercher quand le personnage en change. */
	private var searchedIn: Node? = null
	private var layers: List<TileMapLayer> = emptyList()
	private var holder: Node2D? = null

	/** Le reflet lui-même : il vit dans la carte, pas sous le personnage. */
	private var glass: Sprite2D? = null

	private var clock: Double = 0.0

	@Register
	override fun _ready() {
		body = getParent() as? Node2D
		art = (body?.getNodeOrNull(spriteName)) as? Node2D
		scene = ResourceLoader.load(REFLECTION) as? PackedScene
	}

	@Register
	override fun _process(delta: Double) {
		clock += delta

		val node = body ?: return
		val image = art ?: return
		findWater(node)

		val mirror = glass ?: hang() ?: return
		val frame = frameOf(image)
		if (frame == null) {
			mirror.visible = false
			return
		}

		// L'eau bouge : le reflet glisse d'un pixel, au même rythme que ses rides.
		val tick = floor(clock * STEPS_PER_SECOND).toInt()
		val sway = SWAY[((tick % SWAY.size) + SWAY.size) % SWAY.size]
		val axis = node.globalPosition.x + image.position.x + sway

		// Miroir de la ligne de sol : un point à y se retrouve à 2 * sol - y.
		val middle = node.globalPosition.y + 2.0 * groundOffset - image.position.y - lift
		val height = frame.size.y * image.scale.y
		val top = middle - height / 2.0

		// On ne montre du reflet que ce qui tombe dans l'eau. En approchant du
		// bord, la tête sort donc la première et le reflet monte au fil du pas ;
		// au bord d'une eau basse, il s'arrête là où elle s'arrête.
		val span = waterSpan(axis, top, middle + height / 2.0)
		if (span == null) {
			mirror.visible = false
			return
		}
		val (shown, hidden) = span
		if (hidden - shown <= 1.0) {
			mirror.visible = false
			return
		}

		mirror.visible = true
		mirror.scale = image.scale
		mirror.flipV = true
		mirror.texture = textureOf(image)
		mirror.regionEnabled = true

		// Le reflet est retourné : la tranche visible de son haut se prend donc
		// au bas de l'image.
		val near = (shown - top) / image.scale.y
		val far = (hidden - top) / image.scale.y
		mirror.regionRect = Rect2(
			frame.position.x,
			frame.position.y + frame.size.y - far,
			frame.size.x,
			far - near,
		)
		mirror.globalPosition = Vector2(axis, (shown + hidden) / 2.0)
	}

	/** La texture où prendre l'image du moment : la planche, ou l'image seule d'une animation. */
	private fun textureOf(image: Node2D): Texture2D? = when (image) {
		is AnimatedSprite2D -> image.spriteFrames?.getFrameTexture(image.animation, image.frame)
		is Sprite2D -> image.texture
		else -> null
	}

	/** Où l'image du moment se trouve dans cette texture. */
	private fun frameOf(image: Node2D): Rect2? {
		val texture = textureOf(image) ?: return null
		return when {
			image is Sprite2D && image.regionEnabled -> image.regionRect
			else -> Rect2(0.0, 0.0, texture.getWidth().toDouble(), texture.getHeight().toDouble())
		}
	}

	/**
	 * La première nappe d'eau rencontrée entre [from] et [to], à la verticale
	 * de [x] : son début et sa fin, bornés à cet intervalle. Null s'il n'y en a
	 * pas. On descend de case en case et on s'arrête à la première case sèche
	 * qui suit l'eau — une berge coupe le reflet, elle ne le reprend pas plus bas.
	 */
	private fun waterSpan(x: Double, from: Double, to: Double): Pair<Double, Double>? {
		val layer = layers.firstOrNull() ?: return null

		var start: Double? = null
		var end = from
		var y = from + 0.5
		while (y < to) {
			val cell = layer.localToMap(layer.toLocal(Vector2(x, y)))
			val centre = layer.toGlobal(layer.mapToLocal(cell)).y
			if (Water.isWater(layers, Vector2(x, y))) {
				if (start == null) start = maxOf(from, centre - HALF_CELL)
				end = centre + HALF_CELL
			} else if (start != null) {
				break
			}
			y = centre + HALF_CELL + 0.5
		}
		val first = start ?: return null
		return first to minOf(end, to)
	}

	/** Accroche un reflet dans la carte. */
	private fun hang(): Sprite2D? {
		val holder = holder ?: return null
		val made = (scene?.instantiate()) as? Sprite2D ?: return null
		made.visible = false
		holder.addChild(made)
		glass = made
		return made
	}

	/** Trouve les calques de sol de la carte où se trouve le personnage, et où ranger le reflet. */
	private fun findWater(node: Node2D) {
		val parent = node.getParent()
		if (parent === searchedIn) return

		// Changement de carte : le reflet reste avec l'ancienne, qui s'en va.
		searchedIn = parent
		layers = emptyList()
		holder = null
		glass = null

		val level = Water.levelOf(parent ?: node) ?: return
		val background = Water.backgroundOf(level) ?: return
		layers = Water.groundLayers(background)
		holder = (background.getNodeOrNull(HOLDER)) as? Node2D ?: dig(background)
	}

	/**
	 * Crée le nœud qui portera les reflets, **juste au-dessus du calque d'eau** :
	 * le sable, les pontons et tout le reste du décor se dessinent par-dessus,
	 * ce qui suffit à couper un reflet qui déborderait de l'eau.
	 */
	private fun dig(background: Node2D): Node2D {
		val made = Node2D()
		made.setName(HOLDER)
		background.addChild(made)

		val water = if (background.hasNode(GROUND)) background.getNode(GROUND) else null
		if (water != null) background.moveChild(made, water.getIndex() + 1)
		return made
	}

	@Register
	override fun _exitTree() {
		// Un personnage qui s'en va n'oublie pas son reflet dans l'eau.
		if (glass?.isInsideTree() == true) glass?.queueFree()
		glass = null
		searchedIn = null
		layers = emptyList()
		holder = null
	}

	companion object {
		private const val GROUND = "Ground"
		private const val HOLDER = "Reflections"

		private const val REFLECTION = "res://src/main/kotlin/fr/skyle/pokeludoworld/scenes/characters/reflection.tscn"

		/** Le balancement du reflet, en pixels, au rythme des rides de l'eau. */
		private const val STEPS_PER_SECOND = 4.0
		private val SWAY = listOf(0.0, 1.0, 0.0, -1.0)

		/** Demi-case, pour descendre du centre d'une case à son bas. */
		private const val HALF_CELL = 8.0
	}
}
