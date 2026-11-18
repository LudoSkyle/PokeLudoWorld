package fr.skyle.pokemonmirage.scripts.gameplay.levels

import fr.skyle.pokemonmirage.scripts.autoload.Globals
import fr.skyle.pokemonmirage.scripts.core.AudioManager
import fr.skyle.pokemonmirage.scripts.core.SceneManager
import fr.skyle.pokemonmirage.scripts.ui.MessageBox
import fr.skyle.pokemonmirage.scripts.log.Logger
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.Node2D
import godot.api.ResourceLoader
import godot.api.Sprite2D
import godot.api.Texture2D
import godot.core.Rect2
import godot.core.Rect2i
import godot.core.Vector2
import kotlin.math.floor
import kotlin.random.Random

/**
 * Un Pokémon qui vole au-dessus de la carte : du décor vivant. Il n'a aucun
 * corps — on ne le heurte pas, on ne lui parle pas — et passe au-dessus de
 * tout, la mer comprise. Une ombre au sol, sous lui, dit qu'il est en l'air.
 *
 * Il ne quitte pas sa [zone]. Il avance par **trajets de une à trois cases**
 * en ligne droite ; à chaque trajet le hasard est rejoué, mais il ne rebrousse
 * jamais chemin : après être allé à gauche il peut monter, descendre ou
 * continuer à gauche, pas repartir à droite. Entre deux trajets, il plane un
 * instant sur place.
 *
 * Avec [drift], il ne vole pas : **le vent le porte**. Il traverse sa zone
 * d'un bord à l'autre sans jamais s'arrêter, en montant et descendant
 * doucement, et revient par le bord d'où il était parti. Ceux qui partagent
 * une [seed] sont pris dans le même souffle — même allure, mêmes
 * ondulations : ils voyagent en groupe.
 *
 * Son image vient de `assets/pokemon/overworld/<species>.png` : quatre rangées
 * — bas, gauche, droite, haut — de quatre images carrées (voir
 * `PokemonFrames`).
 *
 * Il n'a pas de reflet : trop haut, et de lui on ne voit déjà, sur terre,
 * qu'une tache d'ombre. Au-dessus de l'eau c'est donc son **ombre qui bleuit**
 * — `WaterShadow.kt`, le nœud `Shade` de sa scène.
 */
@Script
class Flyer : Node2D() {

	/** Nom du fichier de `assets/pokemon/overworld/`, sans extension. */
	@Category("Espece")
	@Export
	var species: String = "wingull"

	/** La zone qu'il ne quitte pas, en cases : coin haut-gauche et taille. */
	@Category("Vol")
	@Export
	var zone: Rect2i = Rect2i(0, 0, 10, 10)

	/** Sa vitesse, en cases par seconde. */
	@Category("Vol")
	@Export
	var pace: Double = 2.5

	/** Le temps qu'il plane entre deux trajets, en secondes : au moins, au plus. */
	@Category("Vol")
	@Export
	var rest: Vector2 = Vector2(0.3, 1.6)

	/** Graine du hasard, pour un vol rejouable. 0 : un vrai hasard. */
	@Category("Vol")
	@Export
	var seed: Int = 0

	/** Le temps entre deux cris, en secondes : au moins, au plus. (0, 0) : il se tait. */
	@Category("Cri")
	@Export
	var cryEvery: Vector2 = Vector2(10.0, 24.0)

	/** Il ne crie que si le joueur est à moins de tant de cases : c'est en passant au-dessus de lui qu'on l'entend. */
	@Category("Cri")
	@Export
	var cryRange: Double = 4.0

	/** Le volume de son cri, de 0 à 1 : un bruit de fond, pas un événement. */
	@Category("Cri")
	@Export
	var cryVolume: Double = 0.45

	/** Le vent qui le porte : 1 vers l'est, -1 vers l'ouest, 0 s'il vole de lui-même. */
	@Category("Vol")
	@Export
	var drift: Int = 0

	/** Le sens du trajet en cours ou du dernier : (-1, 0), (1, 0), (0, -1) ou (0, 1). */
	var heading: Pair<Int, Int> = 0 to 1
		private set

	/** Le nombre de cases du trajet en cours ou du dernier. */
	var stride: Int = 0
		private set

	private var sprite: Sprite2D? = null
	private var random: Random = Random.Default
	private var target = Vector2.ZERO
	private var gliding = false
	private var wait = 0.0
	private var clock = 0.0
	private var cryWait = 0.0

	/** Porté par le vent : sa hauteur de route, le temps du souffle (commun au groupe), sa propre phase. */
	private var lane = 0.0
	private var gust = 0.0
	private var bob = 0.0

	@Register
	override fun _ready() {
		sprite = getNode("Sprite") as? Sprite2D
		val sheet = ResourceLoader.load("$SHEETS$species.png") as? Texture2D
		if (sheet == null) Logger.e("Pokemon volant sans image : $species")
		sprite?.texture = sheet
		if (seed != 0) random = Random(seed)
		// Chacun part à son heure : sans ça, tous les oiseaux de la carte bougeraient ensemble.
		wait = random.nextDouble() * rest.y
		clock = random.nextDouble()
		cryWait = nextCry() * Random.Default.nextDouble()          // chacun son heure, dès le premier cri
		if (drift != 0) {
			heading = drift.coerceIn(-1, 1) to 0
			lane = position.y
			// Le souffle se tire de la graine : le même pour tout le groupe. La phase, elle, est à chacun.
			gust = random.nextDouble() * 100.0
			bob = Random.Default.nextDouble() * 100.0
		}
		flap()
	}

	@Register
	override fun _process(delta: Double) {
		clock += delta
		flap()
		call(delta)

		if (drift != 0) {
			float(delta)
			return
		}

		if (gliding) {
			position = position.moveToward(target, delta * grid() * pace)
			if (position.distanceTo(target) < 0.01) {
				position = target
				gliding = false
				wait = rest.x + random.nextDouble() * (rest.y - rest.x).coerceAtLeast(0.0)
			}
			return
		}

		wait -= delta
		if (wait <= 0.0) launch()
	}

	private fun nextCry(): Double = cryEvery.x + Random.Default.nextDouble() * (cryEvery.y - cryEvery.x).coerceAtLeast(0.0)

	/**
	 * Pousse son cri de loin en loin, quand il passe au-dessus du joueur — pas
	 * pendant un dialogue. Hors de portée, ou si un autre crie déjà, il
	 * réessaie une seconde plus tard : l'occasion n'est pas perdue.
	 */
	private fun call(delta: Double) {
		if (cryEvery.y <= 0.0) return
		cryWait -= delta
		if (cryWait > 0.0) return
		val player = SceneManager.instance?.playerNode
		val near = player != null && player.isInsideTree() && globalPosition.distanceTo(player.globalPosition) <= cryRange * grid()
		cryWait = if (near && MessageBox.instance?.isOpen != true && AudioManager.instance?.cry(species, cryVolume) == true) nextCry() else CRY_RETRY
	}

	/**
	 * Porté par le vent : il file sans s'arrêter, plus ou moins vite selon le
	 * souffle, et sa route ondule d'une case de part et d'autre. Sorti par un
	 * bord de la zone, il rentre par l'autre.
	 */
	private fun float(delta: Double) {
		gust += delta
		val way = heading.first
		val speed = pace * (1.0 + GUST_SWING * kotlin.math.sin(gust * GUST_BEAT))
		var x = position.x + way * speed * grid() * delta
		val left = (zone.position.x - EDGE) * grid()
		val right = (zone.position.x + zone.size.x + EDGE) * grid()
		if (way > 0 && x > right) x -= right - left
		if (way < 0 && x < left) x += right - left
		position = Vector2(x, lane + LANE_SWING * grid() * kotlin.math.sin(gust * LANE_BEAT))
		// Chacun flotte un peu pour lui-même, au-dessus de son ombre.
		sprite?.position = Vector2(0.0, ALTITUDE + BOB * kotlin.math.sin((clock + bob) * BOB_BEAT))
	}

	/**
	 * Choisit le trajet suivant : un sens qui n'est pas le demi-tour, une
	 * longueur de une à trois cases, raccourcie au bord de la zone. Coincé
	 * dans un coin, il repart par où il est venu : c'est le seul cas.
	 */
	private fun launch() {
		val cellX = floor(position.x / grid()).toInt()
		val cellY = floor(position.y / grid()).toInt()
		val back = -heading.first to -heading.second
		val ways = DIRECTIONS.filter { it != back }.shuffled(random) + back

		for (way in ways) {
			val wanted = random.nextInt(1, MAX_STRIDE + 1)
			var steps = 0
			while (steps < wanted && inZone(cellX + way.first * (steps + 1), cellY + way.second * (steps + 1))) steps++
			if (steps == 0) continue

			heading = way
			stride = steps
			target = position + Vector2(way.first * steps * grid(), way.second * steps * grid())
			gliding = true
			return
		}
		// Une zone d'une seule case : il plane sur place.
		wait = rest.y
	}

	private fun inZone(x: Int, y: Int): Boolean =
		x >= zone.position.x && y >= zone.position.y && x < zone.position.x + zone.size.x && y < zone.position.y + zone.size.y

	private fun grid(): Double = Globals.instance.gridSize.toDouble()

	/**
	 * L'image du moment : la rangée du sens, et le battement d'ailes — les colonnes 0 et 2, les deux dessins, sans le
	 * petit saut des colonnes 1 et 3 : en l'air il ne rebondit pas, c'est le vent qui le porte.
	 */
	private fun flap() {
		val beat = (clock * BEATS_PER_SECOND).toInt() % 2
		val row = when (heading) {
			0 to 1 -> 0
			-1 to 0 -> 1
			0 to -1 -> 3
			else -> 2
		}
		val frame = (sprite?.texture?.getWidth() ?: 128) / 4.0
		sprite?.regionRect = Rect2(beat * 2 * frame, row * frame, frame, frame)
	}

	companion object {
		private const val SHEETS = "res://src/main/kotlin/fr/skyle/pokemonmirage/assets/pokemon/overworld/"
		private const val BEATS_PER_SECOND = 5.0
		private const val MAX_STRIDE = 3
		private const val CRY_RETRY = 1.0

		/** Porté par le vent : marge hors de la zone avant de rentrer par l'autre bord, en cases. */
		private const val EDGE = 1.5

		/** L'allure varie d'un quart autour de [pace], sur une douzaine de secondes. */
		private const val GUST_SWING = 0.25
		private const val GUST_BEAT = 0.5

		/** La route ondule d'une case de part et d'autre, sur une vingtaine de secondes. */
		private const val LANE_SWING = 1.0
		private const val LANE_BEAT = 0.3

		/** La hauteur de l'image au-dessus de l'ombre (celle de `flyer.tscn`), et son flottement, en pixels. */
		private const val ALTITUDE = -14.0
		private const val BOB = 2.0
		private const val BOB_BEAT = 2.2
		private val DIRECTIONS = listOf(-1 to 0, 1 to 0, 0 to -1, 0 to 1)
	}
}
