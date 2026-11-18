package fr.skyle.pokemonmirage.scripts.core

import godot.annotation.Register
import godot.annotation.Script
import godot.api.ColorRect
import godot.api.Node2D
import godot.api.ResourceLoader
import godot.api.ShaderMaterial
import godot.api.Sprite2D
import godot.api.Texture2D
import godot.core.Color
import godot.core.Vector2
import godot.core.Vector3
import kotlin.math.abs
import kotlin.math.ceil
import kotlin.math.round
import kotlin.random.Random

/**
 * La météo à l'écran : **le portage, méthode pour méthode, de `RPG::Weather`**
 * de Pokémon Essentials (`001_Overworld_Weather.rb`). Les noms des fonctions
 * sont les siens, pour qu'on puisse relire les deux côte à côte.
 *
 * Ce qu'il faut en retenir, parce que c'est ce qui fait le rendu :
 *
 * - **Rien ne défile.** Chaque goutte est un sprite à part. Elle naît à un
 *   endroit tiré au sort, avance le long de sa propre pente, **meurt** quand
 *   elle a parcouru une distance tirée au sort elle aussi, et renaît ailleurs.
 *   Il n'y a ni grille ni champ qui glisse d'un bloc.
 * - **Tout est ancré à la carte**, pas à l'écran : les positions sont celles du
 *   monde, et l'on ne regarde l'écran que pour faire naître une particule ou la
 *   faire reboucler. Quand on marche, la pluie reste où elle tombe.
 * - Sous la pluie, **un sprite sur deux est une éclaboussure** : posée au
 *   hasard, elle ne se montre que les deux derniers dixièmes de sa vie.
 * - La nappe du blizzard, du sable et du brouillard est un pavage de tuiles qui
 *   glisse et se replie sur lui-même.
 * - La teinte d'écran est celle de RPG Maker : on **ajoute** une couleur.
 *
 * Deux choses seulement ne sont pas portées : les fondus d'un temps à l'autre
 * (on change d'un coup, comme Essentials quand la durée vaut zéro, ce qui est
 * son cas à l'entrée d'une carte) et les éclairs de l'orage, que l'averse n'a pas.
 *
 * Les valeurs — images, vitesses, teintes — sont dans [Weather].
 */
@Script
class WeatherLayer : Node2D() {

	private var type: Weather.Sky = Weather.Sky.CLEAR
	private var max: Int = 0

	/** Le coin haut-gauche de l'écran dans la carte, et la taille de l'écran, en pixels de jeu. */
	private var ox: Double = 0.0
	private var oy: Double = 0.0
	private var width: Double = 320.0
	private var height: Double = 240.0

	private var particleSheets: List<Texture2D> = emptyList()
	private var tileSheets: List<Texture2D> = emptyList()

	private val sprites = ArrayList<Sprite2D>()
	private val spriteX = DoubleArray(Weather.MAX_SPRITES)
	private val spriteY = DoubleArray(Weather.MAX_SPRITES)
	private val spriteOpacity = DoubleArray(Weather.MAX_SPRITES)
	private val spriteLifetimes = DoubleArray(Weather.MAX_SPRITES)

	private val tiles = ArrayList<Sprite2D>()
	private var tilesWide: Int = 0
	private var tilesTall: Int = 0
	private var tileX: Double = 0.0
	private var tileY: Double = 0.0

	/** Le battement du zénith : ce que la teinte gagne au plus, et où elle en est. */
	private var sunMagnitude: Double = 0.0
	private var sunStrength: Double = 0.0

	private var random: Random = Random.Default
	private val sheets = HashMap<String, Texture2D?>()

	private var particleHost: Node2D? = null
	private var tileHost: Node2D? = null
	private var toneRect: ColorRect? = null
	private var toneMaterial: ShaderMaterial? = null

	@Register
	override fun _ready() {
		particleHost = getNode(PARTICLES) as? Node2D
		tileHost = getNode(TILES) as? Node2D
		toneRect = getNode(TONE) as? ColorRect
		toneMaterial = toneRect?.material as? ShaderMaterial
	}

	/** Donne une graine au hasard : les mêmes tirages à chaque fois, pour les tests. */
	@Register
	fun seed(value: Int) {
		random = Random(value)
	}

	// --- def update

	@Register
	override fun _process(delta: Double) {
		locate()
		if (Weather.sky != type) fadeIn(Weather.sky)

		updateScreenTone(delta)

		// Update weather particles (raindrops, snowflakes, etc.)
		if (particleSheets.isNotEmpty()) {
			ensureSprites()
			for (i in 0 until Weather.MAX_SPRITES) updateSpritePosition(i, delta)
		} else if (sprites.isNotEmpty()) {
			sprites.forEach { it.queueFree() }
			sprites.clear()
		}

		// Update weather tiles (sandstorm/blizzard/fog tiled overlay)
		if (tilesWide > 0 && tilesTall > 0) {
			ensureTiles()
			recalculateTilePositions(delta)
			for (i in tiles.indices) updateTilePosition(i)
		} else if (tiles.isNotEmpty()) {
			tiles.forEach { it.queueFree() }
			tiles.clear()
		}

		draw()
	}

	/**
	 * `@weather.ox = $game_map.display_x` : où est l'écran dans la carte. Chez
	 * nous c'est la caméra qui le dit ; sa vue fait 320 × 240 pixels de jeu.
	 */
	private fun locate() {
		val camera = getViewport()?.getCamera2d() ?: return
		val view = getViewportRect().size
		width = view.x / camera.zoom.x
		height = view.y / camera.zoom.y

		val corner = toLocal(camera.getScreenCenterPosition() - Vector2(width / 2.0, height / 2.0))
		ox = round(corner.x)
		oy = round(corner.y)
	}

	// --- def fade_in, avec une durée nulle : self.type = new_type ; self.max = new_max

	private fun fadeIn(newType: Weather.Sky) {
		val newMax = if (newType == Weather.Sky.CLEAR) 0 else Weather.MAP_SPRITES

		// def type=
		type = newType
		prepareBitmaps()
		if (tileSheets.isNotEmpty()) {
			tilesWide = ceil(width / tileSheets[0].getWidth()).toInt() + 1
			tilesTall = ceil(height / tileSheets[0].getHeight()).toInt() + 1
		} else {
			tilesWide = 0
			tilesTall = 0
		}
		ensureSprites()
		for (i in sprites.indices) setSpriteBitmap(i)
		ensureTiles()
		for (i in tiles.indices) setTileBitmap(i)

		// def max=
		if (max == newMax) return
		max = newMax.coerceIn(0, Weather.MAX_SPRITES)
		ensureSprites()
		for (i in sprites.indices) sprites[i].visible = i < max
	}

	// --- def prepare_bitmaps

	private fun prepareBitmaps() {
		particleSheets = type.particles.mapNotNull { sheet(it) }
		tileSheets = type.tiles.mapNotNull { sheet(it) }
	}

	private fun sheet(name: String): Texture2D? =
		sheets.getOrPut(name) { ResourceLoader.load("$SHEETS$name.png") as? Texture2D }

	// --- def ensureSprites

	private fun ensureSprites() {
		if (sprites.size >= Weather.MAX_SPRITES || particleSheets.isEmpty()) return
		val host = particleHost ?: return

		for (i in 0 until Weather.MAX_SPRITES) {
			if (i >= sprites.size) {
				val sprite = Sprite2D()
				sprite.centered = false
				host.addChild(sprite)
				sprites.add(sprite)
				spriteOpacity[i] = 0.0
				setSpriteBitmap(i)
			}
			sprites[i].visible = i < max
			spriteLifetimes[i] = 0.0
		}
	}

	// --- def ensureTiles

	private fun ensureTiles() {
		val wanted = tilesWide * tilesTall
		// Les tuiles en trop d'un temps précédent ne feraient que doubler celles-ci.
		while (tiles.size > wanted) tiles.removeAt(tiles.size - 1).queueFree()
		val host = tileHost ?: return

		while (tiles.size < wanted) {
			val sprite = Sprite2D()
			sprite.centered = false
			sprite.modulate = Color(1.0, 1.0, 1.0, 0.0)
			host.addChild(sprite)
			tiles.add(sprite)
			setTileBitmap(tiles.size - 1)
		}
		tiles.forEach { it.visible = true }
	}

	// --- def set_sprite_bitmap

	private fun setSpriteBitmap(index: Int) {
		val sprite = sprites.getOrNull(index) ?: return
		if (particleSheets.isEmpty()) {
			sprite.texture = null
			return
		}
		if (type.category == Weather.Category.RAIN) {
			val lastIndex = particleSheets.size - 1   // Last sprite is a splash
			sprite.texture = if (index % 2 == 0) particleSheets[index % lastIndex] else particleSheets[lastIndex]
		} else {
			sprite.texture = particleSheets[index % particleSheets.size]
		}
	}

	// --- def set_tile_bitmap

	private fun setTileBitmap(index: Int) {
		val sprite = tiles.getOrNull(index) ?: return
		sprite.texture = if (tileSheets.isEmpty()) null else tileSheets[index % tileSheets.size]
	}

	// --- def reset_sprite_position

	private fun resetSpritePosition(index: Int) {
		val sprite = sprites[index]
		if (index < max) {
			sprite.visible = true
		} else {
			sprite.visible = false
			spriteLifetimes[index] = 0.0
			return
		}

		val bitmap = sprite.texture ?: return
		val bitmapWidth = bitmap.getWidth().toDouble()
		val bitmapHeight = bitmap.getHeight().toDouble()

		if (isSplash(index)) {
			spriteX[index] = ox - bitmapWidth + rand(width + bitmapWidth * 2)
			spriteY[index] = oy - bitmapHeight + rand(height + bitmapHeight * 2)
			spriteLifetimes[index] = (30 + random.nextInt(20)) * 0.01   // 0.3-0.5 seconds
			// Essentials la laisse voir une image avant de la cacher : c'est un
			// accroc de leur côté. Elle ne se montre ici que quand elle doit.
			spriteOpacity[index] = 0.0
			return
		}

		val xSpeed = type.particleDrift.x
		val ySpeed = type.particleDrift.y
		val gradient = xSpeed / ySpeed
		if (abs(gradient) >= 1) {
			// Position sprite to the right of the screen
			spriteX[index] = ox + width + rand(width)
			spriteY[index] = oy + height - rand(height + bitmapHeight - (width / gradient))
			val distanceToCover = spriteX[index] - ox - (width / 2) + bitmapWidth + rand(width * 8 / 5)
			spriteLifetimes[index] = abs(distanceToCover / xSpeed)
		} else {
			// Position sprite to the top of the screen
			spriteX[index] = ox - bitmapWidth + rand(width + bitmapWidth - (gradient * height))
			spriteY[index] = oy - bitmapHeight - rand(height)
			val distanceToCover = oy - spriteY[index] + (height / 2) + rand(height * 8 / 5)
			spriteLifetimes[index] = abs(distanceToCover / ySpeed)
		}
		spriteOpacity[index] = 255.0
	}

	// --- def update_sprite_position

	private fun updateSpritePosition(index: Int, deltaT: Double) {
		val sprite = sprites.getOrNull(index) ?: return
		val bitmap = sprite.texture ?: return
		if (!sprite.visible) return

		if (spriteLifetimes[index] >= 0) {
			spriteLifetimes[index] -= deltaT
			if (spriteLifetimes[index] <= 0) {
				resetSpritePosition(index)
				return
			}
		}

		// Update visibility/position/opacity of sprite
		if (isSplash(index)) {
			spriteOpacity[index] = if (spriteLifetimes[index] < 0.2) 255.0 else 0.0   // 0.2 seconds
			return
		}

		val distX = type.particleDrift.x * deltaT
		val distY = type.particleDrift.y * deltaT
		spriteX[index] += distX
		spriteY[index] += distY
		if (type == Weather.Sky.SNOW) {
			spriteX[index] += distX * (spriteY[index] - oy) / (height * 3)   // Faster when further down screen
			spriteX[index] += SNOW_SWAY[random.nextInt(4)] * distX / 8   // Random movement
			spriteY[index] += SNOW_VARIETY[index % 6] * distY / 10   // Variety
		}

		val spriteWidth = bitmap.getWidth().toDouble()
		val spriteHeight = bitmap.getHeight().toDouble()
		if (spriteX[index] - ox > width) spriteX[index] -= width
		if (spriteX[index] - ox < -spriteWidth) spriteX[index] += width
		if (spriteY[index] - oy > height) spriteY[index] -= height
		if (spriteY[index] - oy < -spriteHeight) spriteY[index] += height

		val x = spriteX[index] - ox
		val y = spriteY[index] - oy
		// Check if sprite is off-screen; if so, reset it
		if (spriteOpacity[index] < 64 || x < -spriteWidth || y > height) resetSpritePosition(index)
	}

	/** Sous la pluie, les sprites de rang impair sont les éclaboussures. */
	private fun isSplash(index: Int): Boolean = type.category == Weather.Category.RAIN && index % 2 == 1

	// --- def recalculate_tile_positions

	private fun recalculateTilePositions(deltaT: Double) {
		val tileWidth = tileSheets[0].getWidth().toDouble()
		val tileHeight = tileSheets[0].getHeight().toDouble()
		tileX += type.tileDrift.x * deltaT
		tileY += type.tileDrift.y * deltaT
		while (tileX < ox - tileWidth) tileX += tileWidth
		while (tileX > ox) tileX -= tileWidth
		while (tileY < oy - tileHeight) tileY += tileHeight
		while (tileY > oy) tileY -= tileHeight
	}

	// --- def update_tile_position

	private fun updateTilePosition(index: Int) {
		val sprite = tiles[index]
		val bitmap = sprite.texture ?: return
		val tileWidth = bitmap.getWidth().toDouble()
		val tileHeight = bitmap.getHeight().toDouble()

		var x = round(tileX) + (index % tilesWide) * tileWidth
		var y = round(tileY) + (index / tilesWide) * tileHeight
		if (x - ox < -tileWidth) x += tilesWide * tileWidth
		if (y - oy > height) y -= tilesTall * tileHeight

		sprite.position = Vector2(x, y)
		sprite.visible = true
		sprite.modulate = Color(1.0, 1.0, 1.0, if (max > 0) 1.0 else 0.0)
	}

	// --- def update_screen_tone

	private fun updateScreenTone(deltaT: Double) {
		val base = type.tone(max.toDouble())
		var red = base.red
		var green = base.green
		var blue = base.blue
		val gray = base.gray

		// Modify base tone
		if (type.category == Weather.Category.SUN) {
			val weatherMax = max.toDouble()
			if (sunMagnitude != weatherMax && sunMagnitude != -weatherMax) sunMagnitude = weatherMax
			if ((sunMagnitude > 0 && sunStrength > sunMagnitude) || (sunMagnitude < 0 && sunStrength < 0)) sunMagnitude *= -1
			sunStrength += sunMagnitude * deltaT / 0.8   // 0.8 seconds per half flash
			red += sunStrength
			green += sunStrength
			blue += sunStrength / 2

			// Hors d'Essentials : le zénith est la lumière du soleil, et il n'y
			// a pas de soleil la nuit. Sa teinte se retire à mesure que la nuit
			// tombe — au rythme où les lampes s'allument — et revient avec le jour.
			val sun = 1.0 - DayNight.light()
			red *= sun
			green *= sun
			blue *= sun
		}

		// Apply screen tone
		val rect = toneRect ?: return
		toneMaterial?.setShaderParameter(TONE_SHIFT, Vector3(red, green, blue))
		toneMaterial?.setShaderParameter(TONE_GRAY, gray)
		rect.visible = red != 0.0 || green != 0.0 || blue != 0.0 || gray != 0.0
		// Il déborde de l'écran : la caméra peut avoir bougé depuis qu'on l'a lue.
		rect.setPosition(Vector2(ox - MARGIN, oy - MARGIN))
		rect.setSize(Vector2(width + MARGIN * 2, height + MARGIN * 2))
	}

	/** Pose chaque sprite là où le calcul l'a mis, au pixel près. */
	private fun draw() {
		for (i in sprites.indices) {
			val sprite = sprites[i]
			sprite.position = Vector2(round(spriteX[i]), round(spriteY[i]))
			sprite.modulate = Color(1.0, 1.0, 1.0, spriteOpacity[i] / 255.0)
		}
	}

	/** `rand(n)` de Ruby : un entier de 0 à n exclu. */
	private fun rand(limit: Double): Double {
		val bound = limit.toInt()
		return if (bound <= 0) 0.0 else random.nextInt(bound).toDouble()
	}

	companion object {
		private const val PARTICLES = "Particles"
		private const val TILES = "Tiles"
		private const val TONE = "Tone"
		private const val TONE_SHIFT = "tone_shift"
		private const val TONE_GRAY = "tone_gray"
		private const val SHEETS = "res://src/main/kotlin/fr/skyle/pokemonmirage/assets/weather/"

		/** De combien le rectangle de teinte dépasse de l'écran, en pixels de jeu. */
		private const val MARGIN = 32.0

		/** Les écarts que la neige ajoute à sa chute. */
		private val SNOW_SWAY = intArrayOf(2, 1, 0, -1)
		private val SNOW_VARIETY = intArrayOf(2, 1, 1, 0, 0, -1)
	}
}
