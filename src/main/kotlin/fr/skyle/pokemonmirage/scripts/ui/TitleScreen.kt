package fr.skyle.pokemonmirage.scripts.ui

import fr.skyle.pokemonmirage.scripts.core.AudioManager
import fr.skyle.pokemonmirage.scripts.core.SceneManager
import fr.skyle.pokemonmirage.scripts.log.Logger
import godot.annotation.Category
import godot.annotation.Export
import godot.annotation.Register
import godot.annotation.Script
import godot.api.CanvasLayer
import godot.api.ColorRect
import godot.api.Control
import godot.api.Input
import godot.api.Node
import godot.api.ResourceLoader
import godot.api.Sprite2D
import godot.api.Texture2D
import godot.core.Color
import godot.core.Rect2
import godot.core.Vector2
import kotlin.math.PI
import kotlin.math.min
import kotlin.math.pow
import kotlin.math.sin
import kotlin.random.Random

private enum class Step { BOOT, INTRO, WAITING, MENU, LEAVING, GONE }

/**
 * L'écran titre : ce qu'on voit au lancement, avant toute carte. Trois images
 * superposées, **indépendantes** l'une de l'autre — on en change une sans
 * toucher aux deux autres, dans la scène :
 *
 * - `Backdrop` : le fond, en calques étirés sur tout l'écran — le ciel, des
 *   nuages qui défilent derrière la tour, la tour, la mer de nuages devant
 *   elle — entre lesquels volent des Pokémon ([flyerSpecies]) ;
 * - `Logo` : le logo, ramené dans un cadre de [logoWidth] × [logoHeight] ;
 * - `Prompt` : le texte du bas, « Press Enter », qui clignote.
 *
 * La touche d'interaction ouvre la sélection des parties ([SaveSlots]) : une
 * carte par partie sauvegardée, « Nouvelle partie », « Options ». Le logo
 * s'efface pour lui laisser la place. C'est [SceneManager] qui lance ensuite
 * la partie, dans un fondu.
 *
 * Tant que la partie n'a pas commencé, le joueur n'existe dans aucune carte et
 * ne lit rien : c'est cet écran qui lit la touche d'interaction. Il s'efface
 * dès que la première carte est là, et ne lit alors plus rien.
 */
@Script
class TitleScreen : CanvasLayer() {

	companion object {
		var instance: TitleScreen? = null
			private set

		/** Le décor est dessiné à cette échelle : un pixel de jeu vaut quatre pixels d'écran. */
		private const val PIXEL = 4.0

		private val BLACK = Color(0.0, 0.0, 0.0, 1.0)

		/** Les planches des Pokémon en vol : deux colonnes de quatre images de 32 × 32, la seconde de profil. */
		private const val FLYERS = "res://src/main/kotlin/fr/skyle/pokemonmirage/assets/pokemon/overworld/"
		private const val MUSIC = "res://src/main/kotlin/fr/skyle/pokemonmirage/assets/audio/music/"
		private const val FLYER_FRAME = 32.0
		private const val FLYER_BEATS = 5.0

		/** De combien un oiseau sort de l'écran avant de faire demi-tour, en pixels d'écran. */
		private const val FLYER_MARGIN = 90.0
	}

	/** Cadre dans lequel tient le logo, en pixels d'écran : il y est ramené sans être déformé. */
	@Category("Logo")
	@Export
	var logoWidth: Double = 1000.0

	@Export
	var logoHeight: Double = 350.0

	/** De combien le logo monte et descend, en pixels d'écran, et en combien de secondes. */
	@Export
	var floatPixels: Double = 6.0

	@Export
	var floatSeconds: Double = 3.6

	/** Le noir se lève, puis le logo arrive : durées en secondes. */
	@Category("Arrivee")
	@Export
	var fadeInSeconds: Double = 0.5

	@Export
	var logoInSeconds: Double = 0.6

	/** « Press Enter » : secondes affiché, puis secondes caché. */
	@Category("Clignotement")
	@Export
	var blinkOnSeconds: Double = 0.7

	@Export
	var blinkOffSeconds: Double = 0.4

	/**
	 * Les Pokémon qui traversent le ciel : un fichier de `assets/pokemon/overworld`,
	 * sans extension, découpé comme pour les cartes (voir Flyer). Vide : personne.
	 */
	@Category("Vol")
	@Export
	var flyerSpecies: String = "wingull"

	/** Combien volent au loin, derrière la tour, et combien devant elle. */
	@Export
	var farFlyers: Int = 3

	@Export
	var nearFlyers: Int = 1

	/** Ceux du loin sont dessinés plus petits et pâlis par la distance. */
	@Export
	var farFlyerScale: Double = 2.0

	/**
	 * Musique de l'écran titre : un fichier de `assets/audio/music`, sans
	 * extension. Tant que ce fichier n'existe pas, l'écran titre est silencieux.
	 */
	@Category("Son")
	@Export
	var music: String = "title"

	private var screen: Control? = null
	private var logo: Sprite2D? = null
	private var prompt: Sprite2D? = null
	private var veil: ColorRect? = null
	private var slots: SaveSlots? = null

	private var step = Step.BOOT
	private var clock = 0.0
	private var blink = 0.0
	private var logoScale = 1.0
	private var logoHome = Vector2.ZERO

	/** Vrai tant que l'écran titre est affiché. */
	val isShown: Boolean
		get() = step != Step.GONE && step != Step.BOOT

	/** Vrai quand la sélection des parties est ouverte. */
	val isMenuOpen: Boolean
		get() = step == Step.MENU

	@Register
	override fun _ready() {
		instance = this
		screen = getNode("Control") as? Control
		logo = getNode("Control/Logo") as? Sprite2D
		prompt = getNode("Control/Prompt") as? Sprite2D
		veil = getNode("Control/Veil") as? ColorRect
		slots = getNode("Control/Slots") as? SaveSlots

		prompt?.scale = Vector2(PIXEL, PIXEL)
		prompt?.visible = false
		logo?.visible = false
		veil?.color = BLACK
	}

	/** Le logo, quelle que soit sa taille, tient dans son cadre sans être déformé. */
	private fun fitLogo() {
		val image = logo ?: return
		val size = image.texture?.getSize() ?: return
		if (size.x <= 0.0 || size.y <= 0.0) return
		logoScale = min(logoWidth / size.x, logoHeight / size.y)
		logoHome = image.position
		image.scale = Vector2(logoScale, logoScale)
	}

	@Register
	override fun _process(delta: Double) {
		if (step == Step.GONE) return

		val scenes = SceneManager.instance
		if (step == Step.BOOT) {
			// Sans écran titre (les tests), la partie est déjà en route.
			if (scenes == null || !scenes.showTitle) {
				leave()
				return
			}
			// La mise en page des images attend que l'écran ait sa taille.
			fitLogo()
			releaseFlyers()
			step = Step.INTRO
			AudioManager.instance?.playMusic(if (hasMusic()) music else "")
			Logger.i("Loading title screen ...")
		}

		clock += delta
		animate(delta)
		fly(delta)

		// Seule lecture de la touche d'interaction tant que la partie n'a pas commencé.
		val interact = Input.isActionJustPressed("interact")
		when (step) {
			// Une pression abrège l'arrivée ; elle n'ouvre pas le menu dans la foulée.
			Step.INTRO -> if (interact || clock >= fadeInSeconds + logoInSeconds) {
				clock = fadeInSeconds + logoInSeconds
				blink = 0.0
				step = Step.WAITING
			}
			Step.WAITING -> if (interact) {
				AudioManager.instance?.sfx("confirm")
				slots?.open()
				step = Step.MENU
			}
			Step.MENU -> handleMenu(interact)
			// La première carte est là, sous le noir du fondu : l'écran titre s'efface.
			Step.LEAVING -> if (scenes?.hasLevel == true) leave()
			else -> {}
		}
	}

	private fun animate(delta: Double) {
		// Le noir se lève.
		veil?.color = Color(0.0, 0.0, 0.0, if (fadeInSeconds > 0.0) (1.0 - clock / fadeInSeconds).coerceIn(0.0, 1.0) else 0.0)

		// Le logo arrive en grossissant, dépasse un peu sa taille, puis flotte.
		logo?.let {
			val arrival = if (logoInSeconds > 0.0) ((clock - fadeInSeconds) / logoInSeconds).coerceIn(0.0, 1.0) else 1.0
			// Il laisse la place aux cartes tant que la sélection des parties est ouverte.
			it.visible = clock >= fadeInSeconds && step != Step.MENU
			it.modulate = Color(1.0, 1.0, 1.0, (arrival * 2.5).coerceAtMost(1.0))
			val grown = logoScale * (0.7 + 0.3 * overshoot(arrival))
			it.scale = Vector2(grown, grown)
			val drift = if (floatSeconds > 0.0) sin(clock * 2.0 * PI / floatSeconds) * floatPixels else 0.0
			it.position = Vector2(logoHome.x, logoHome.y + drift)
		}

		// « Press Enter » ne clignote que lorsqu'on l'attend.
		blink += delta
		val cycle = blinkOnSeconds + blinkOffSeconds
		prompt?.visible = step == Step.WAITING && (cycle <= 0.0 || blink % cycle < blinkOnSeconds)
	}

	/** De 0 à 1 en dépassant 1 avant d'y revenir : l'élan d'une arrivée. */
	private fun overshoot(progress: Double): Double {
		val back = 1.70158
		val rest = progress - 1.0
		return 1.0 + (back + 1.0) * rest.pow(3) + back * rest.pow(2)
	}

	private fun handleMenu(interact: Boolean) {
		val audio = AudioManager.instance
		val cards = slots ?: return

		// L'écran des options a la main tant qu'il est ouvert ; la langue a pu y
		// changer, les cartes sont donc refaites à son retour.
		val options = OptionsMenu.instance
		if (options != null && options.isOpen) {
			if (interact) audio?.sfx("confirm")
			if (Input.isActionJustPressed(PauseMenu.ACTION)) audio?.sfx("cancel")
			options.handle(interact)
			if (!options.isOpen) cards.open("Options")
			return
		}

		val choice = cards.handle(interact) ?: return
		when (choice.kind) {
			SaveSlots.Kind.CONTINUE -> launch(choice.slot, resume = true)
			SaveSlots.Kind.NEW_GAME -> launch(choice.slot, resume = false)
			SaveSlots.Kind.OPTIONS -> options?.open()
			SaveSlots.Kind.BACK -> {
				cards.close()
				blink = 0.0
				step = Step.WAITING
			}
		}
	}

	private fun launch(slot: Int, resume: Boolean) {
		val scenes = SceneManager.instance ?: return
		slots?.close()
		step = Step.LEAVING
		scenes.start(slot, resume)
	}

	/** La musique demandée est-elle là ? Elle peut être en WAV, OGG ou MP3, comme les autres. */
	private fun hasMusic(): Boolean =
		music.isNotEmpty() && listOf("wav", "ogg", "mp3").any { ResourceLoader.exists("$MUSIC$music.$it") }

	// --- les Pokémon qui traversent le ciel

	/** Un Pokémon en vol : il traverse l'écran d'un bord à l'autre, puis revient plus tard, ailleurs. */
	private class Bird(val sprite: Sprite2D, val far: Boolean) {
		var heading = 1.0
		var speed = 0.0
		var height = 0.0
		var sway = 0.0
		var phase = 0.0
		var wait = 0.0
	}

	private val birds = ArrayList<Bird>()
	private val random = Random.Default

	private fun releaseFlyers() {
		if (flyerSpecies.isEmpty()) return
		val sheet = ResourceLoader.load("$FLYERS$flyerSpecies.png") as? Texture2D
		if (sheet == null) {
			Logger.e("Pokemon volant sans image : $flyerSpecies")
			return
		}
		val width = screen?.getSize()?.x ?: return
		listOf(Triple("Control/Backdrop/FarFlyers", farFlyers, true), Triple("Control/Backdrop/NearFlyers", nearFlyers, false)).forEach { (path, count, far) ->
			val host: Node = (if (hasNode(path)) getNode(path) else null) ?: return@forEach
			repeat(count) {
				val sprite = Sprite2D()
				sprite.texture = sheet
				sprite.regionEnabled = true
				val size = if (far) farFlyerScale else PIXEL
				sprite.scale = Vector2(size, size)
				// La distance pâlit et bleuit.
				if (far) sprite.modulate = Color(0.8, 0.9, 1.0, 1.0)
				host.addChild(sprite)

				val bird = Bird(sprite, far)
				route(bird)
				// Au lancement ils sont déjà en l'air, quelque part au-dessus des nuages.
				bird.wait = 0.0
				sprite.position = Vector2(random.nextDouble() * width, bird.height)
				birds.add(bird)
			}
		}
	}

	/** Tire le prochain passage d'un oiseau : son sens, sa hauteur, son allure, et l'attente avant de repartir. */
	private fun route(bird: Bird) {
		val size = screen?.getSize() ?: return
		bird.heading = if (random.nextBoolean()) 1.0 else -1.0
		bird.speed = if (bird.far) 34.0 + random.nextDouble() * 22.0 else 70.0 + random.nextDouble() * 40.0
		// Ceux du loin volent plus haut dans l'image ; aucun ne passe sur le logo.
		val band = if (bird.far) 0.44 to 0.66 else 0.5 to 0.8
		bird.height = size.y * (band.first + random.nextDouble() * (band.second - band.first))
		bird.sway = if (bird.far) 6.0 + random.nextDouble() * 6.0 else 10.0 + random.nextDouble() * 14.0
		bird.phase = random.nextDouble() * 2.0 * PI
		bird.wait = 1.0 + random.nextDouble() * 5.0
		bird.sprite.position = Vector2(if (bird.heading > 0.0) -FLYER_MARGIN else size.x + FLYER_MARGIN, bird.height)
	}

	private fun fly(delta: Double) {
		val width = screen?.getSize()?.x ?: return
		birds.forEach { bird ->
			// Les ailes battent même pendant l'attente : l'oiseau est hors de l'écran.
			val beat = ((clock + bird.phase) * FLYER_BEATS).toInt() % 2
			// La planche : rangées bas, gauche, droite, haut ; les deux dessins sont dans les colonnes 0 et 2.
			val row = if (bird.heading < 0.0) 1 else 2
			bird.sprite.regionRect = Rect2(beat * 2 * FLYER_FRAME, row * FLYER_FRAME, FLYER_FRAME, FLYER_FRAME)

			if (bird.wait > 0.0) {
				bird.wait -= delta
				return@forEach
			}
			val x = bird.sprite.position.x + bird.heading * bird.speed * delta
			val y = bird.height + sin(clock * 0.9 + bird.phase) * bird.sway
			bird.sprite.position = Vector2(x, y)
			if (x < -FLYER_MARGIN || x > width + FLYER_MARGIN) route(bird)
		}
	}

	private fun leave() {
		step = Step.GONE
		slots?.close()
		visible = false
	}
}
