package fr.skyle.pokemonmirage.scripts.gameplay.characters

import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.Node
import godot.api.Node2D
import godot.api.PackedScene
import godot.api.ResourceLoader
import godot.api.TileMapLayer
import godot.core.Rect2
import godot.core.Vector2
import godot.core.Vector2i
import kotlin.math.abs

/**
 * Les traces de pas qu'un personnage laisse dans le sable, puis qui s'effacent.
 *
 * Ce nœud, enfant du personnage comme [TallGrass], regarde la case qu'il vient
 * de quitter : si son sol est du sable, il y pose **une paire d'empreintes**,
 * un pied de chaque côté de sa trajectoire, l'un un peu en avant de l'autre.
 * Le pied qui mène change à chaque pas, ce qui donne la démarche en zigzag des
 * jeux d'origine.
 *
 * Chaque empreinte s'efface ensuite toute seule ([Footprint]) : rien n'est
 * accroché au personnage, qui peut repartir, courir ou changer de carte.
 *
 * **Ce qui est du sable se déclare dans le TileSet**, pas ici : la tuile porte
 * la donnée perso `sand` (voir docs/tilesets.md). On lit le **calque le plus
 * haut** qui couvre la case — un ponton posé par-dessus le sable n'en est pas,
 * et on n'y laisse donc pas de traces.
 */
@Script
class Footprints : Node() {

	/** Combien de temps une trace reste visible, en secondes. */
	@Category("Traces")
	@Export
	var lifeSeconds: Double = 1.0

	/** De combien une trace fraîche assombrit le sable (0 à 1). */
	@Category("Traces")
	@Export
	var darkness: Double = 0.26

	private var body: Node2D? = null
	private var scene: PackedScene? = null

	/** La carte où l'on a cherché les calques, pour les rechercher quand le personnage en change. */
	private var searchedIn: Node? = null

	/** Les calques de sol de la carte, dans leur ordre de dessin. */
	private var layers: List<TileMapLayer> = emptyList()

	/** Où les empreintes sont rangées : un nœud du fond, juste au-dessus du sable. */
	private var holder: Node2D? = null

	private var lastCell: Vector2i? = null

	/** Quel pied mène : il change à chaque pas. */
	private var leading: Boolean = false

	@Register
	override fun _ready() {
		body = getParent() as? Node2D
		scene = ResourceLoader.load(FOOTPRINT) as? PackedScene
	}

	@Register
	override fun _process(delta: Double) {
		val node = body ?: return
		findGround(node)

		val reference = layers.firstOrNull() ?: return
		val cell = reference.localToMap(reference.toLocal(node.globalPosition))
		val previous = lastCell
		lastCell = cell
		if (previous == null || previous == cell) return

		// Une téléportation — un changement de carte, une porte — n'a pas laissé de pas derrière elle.
		val stepX = cell.x - previous.x
		val stepY = cell.y - previous.y
		if (abs(stepX) + abs(stepY) != 1) return

		val point = reference.toGlobal(reference.mapToLocal(previous))
		if (!isSand(point)) return
		drop(point, Vector2(stepX.toDouble(), stepY.toDouble()))
	}

	/**
	 * Pose la paire d'empreintes de la case que l'on quitte. [step] est le pas
	 * qui vient d'être fait, une case dans l'une des quatre directions.
	 */
	private fun drop(centre: Vector2, step: Vector2) {
		val scene = scene ?: return
		val holder = holder ?: return

		// Les pieds s'écartent de part et d'autre de la trajectoire, et l'un devance l'autre.
		val side = Vector2(-step.y, step.x)
		val lead = if (leading) 1.0 else -1.0
		leading = !leading

		// On marche sur la moitié basse de la case : c'est là que sont les pieds du personnage.
		val feet = centre + Vector2(0.0, FEET)
		plant(scene, holder, feet + side * SPREAD + step * STRIDE * lead, step, side)
		plant(scene, holder, feet - side * SPREAD - step * STRIDE * lead, step, -side)
	}

	/** Une empreinte, à [at], orientée par [step] ; [side] dit duquel des deux pieds il s'agit. */
	private fun plant(scene: PackedScene, holder: Node2D, at: Vector2, step: Vector2, side: Vector2) {
		val print = scene.instantiate() as? Footprint ?: return
		print.lifeSeconds = lifeSeconds
		print.darkness = darkness

		val direction = when {
			step.y > 0.0 -> 0      // vers le bas
			step.x < 0.0 -> 1      // vers la gauche
			step.x > 0.0 -> 2      // vers la droite
			else -> 3              // vers le haut
		}
		// Dans chaque paire de la planche vient d'abord le pied le plus haut ou le plus à gauche.
		val foot = if (if (step.x == 0.0) side.x < 0.0 else side.y < 0.0) 0 else 1
		print.regionRect = Rect2((direction * 2 + foot) * CELL, 0.0, CELL, CELL)

		holder.addChild(print)
		// Un pixel entier : une empreinte posée entre deux pixels se dessinerait floue.
		print.globalPosition = Vector2(at.x.toInt().toDouble(), at.y.toInt().toDouble())
	}

	/** Le sol de la case qui porte [point] est-il du sable ? C'est le calque le plus haut qui le dit. */
	private fun isSand(point: Vector2): Boolean {
		for (index in layers.indices.reversed()) {
			val layer = layers[index]
			val cell = layer.localToMap(layer.toLocal(point))
			if (layer.getCellSourceId(cell) == -1) continue
			return layer.getCellTileData(cell)?.getCustomData(SAND) as? Boolean == true
		}
		return false
	}

	/** Trouve les calques de sol de la carte où se trouve le personnage, et où ranger les traces. */
	private fun findGround(node: Node2D) {
		val parent = node.getParent()
		if (parent === searchedIn) return

		// Le joueur change de carte en changeant de parent : ses traces restent
		// dans l'ancienne, qui part avec elles.
		searchedIn = parent
		lastCell = null
		layers = emptyList()
		holder = null

		var level: Node? = parent
		while (level != null && level.name.toString() != LEVEL) level = level.getParent()
		val root = level ?: return
		val background = (if (root.hasNode(BACKGROUND)) root.getNode(BACKGROUND) else null) as? Node2D ?: return

		val found = ArrayList<TileMapLayer>()
		for (index in 0 until background.getChildCount()) {
			(background.getChild(index) as? TileMapLayer)?.let { found.add(it) }
		}
		layers = found
		holder = (background.getNodeOrNull(HOLDER)) as? Node2D ?: dig(background)
	}

	/**
	 * Crée le nœud qui portera les traces, **juste au-dessus du sable** : sous le
	 * relief, les pontons, les décors et les herbes, qui se posent dessus. Le
	 * premier personnage qui marche sur la carte s'en charge, les autres le trouvent.
	 */
	private fun dig(background: Node2D): Node2D {
		val made = Node2D()
		made.setName(HOLDER)
		background.addChild(made)

		val sand = (if (background.hasNode(PATHS)) background.getNode(PATHS) else null)
			?: (if (background.hasNode(GROUND)) background.getNode(GROUND) else null)
		if (sand != null) background.moveChild(made, sand.getIndex() + 1)
		return made
	}

	@Register
	override fun _exitTree() {
		searchedIn = null
		layers = emptyList()
		holder = null
		lastCell = null
	}

	companion object {
		private const val LEVEL = "Level"
		private const val BACKGROUND = "Background"
		private const val GROUND = "Ground"
		private const val PATHS = "Paths"
		private const val HOLDER = "Footprints"

		/** La donnée perso du TileSet qui dit qu'une tuile se foule et garde la marque du pied. */
		private const val SAND = "sand"

		private const val FOOTPRINT = "res://src/main/kotlin/fr/skyle/pokemonmirage/scenes/characters/footprint.tscn"

		/** Côté d'une case de la planche d'empreintes. */
		private const val CELL = 8.0

		/** À quelle hauteur de la case tombent les pieds, depuis son centre. */
		private const val FEET = 4.0

		/** De combien les deux pieds s'écartent de la trajectoire, et de combien l'un devance l'autre. */
		private const val SPREAD = 3.0
		private const val STRIDE = 2.0
	}
}
