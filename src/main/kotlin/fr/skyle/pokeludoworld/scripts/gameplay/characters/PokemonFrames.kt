package fr.skyle.pokeludoworld.scripts.gameplay.characters

import godot.api.AnimatedSprite2D
import godot.api.AtlasTexture
import godot.api.ResourceLoader
import godot.api.SpriteFrames
import godot.api.Texture2D
import godot.core.Rect2
import godot.core.Vector2

/**
 * Le sprite d'un Pokémon sur la carte, **lu dans le fichier de son espèce** :
 * `assets/pokemon/overworld/<espèce>.png`, et nulle part ailleurs. Un Pokémon
 * posé, un Pokémon qui suit le joueur, un Pokémon qui vole : c'est le même
 * fichier et les mêmes animations — il n'y a pas de planche par usage.
 *
 * Le fichier a deux colonnes de quatre images carrées (32 pixels de côté, 64
 * pour un gros Pokémon) : dos, dos, face, face ; gauche, gauche, droite,
 * droite. La première image d'une direction est celle posée au sol : c'est la
 * pose immobile. La marche alterne les deux.
 *
 * Les noms d'animation sont ceux de [CharacterFrames], que lit
 * [CharacterAnimation] : un Pokémon s'anime comme n'importe quel personnage.
 */
object PokemonFrames {

	const val DIR = "res://src/main/kotlin/fr/skyle/pokeludoworld/assets/pokemon/overworld/"

	/** Ce qui, dans le nom d'une apparence de personnage, désigne une espèce : `pkmn_wingull`. */
	const val PREFIX = "pkmn_"

	/** (colonne, rangée de la première image) de chaque direction dans le fichier. */
	private val PLACES = mapOf("up" to (0 to 0), "down" to (0 to 2), "left" to (1 to 0), "right" to (1 to 2))

	/**
	 * Les espèces qui volent, et de combien de pixels chacune se tient au-dessus
	 * de la ligne du sol. Voler n'est que cela : la même image, plus haut.
	 */
	private val LIFT = mapOf("wingull" to 3.0, "pelipper" to 2.0, "hoppip" to 4.0, "skiploom" to 4.0, "jumpluff" to 3.0)

	/** Un fichier n'est découpé qu'une fois, même porté par dix Pokémon. */
	private val cache = HashMap<String, SpriteFrames>()

	/** La hauteur de vol de [species], en pixels ; 0 pour une espèce qui marche. */
	fun liftOf(species: String): Double = LIFT[species] ?: 0.0

	/** Les animations de [species], ou null si son fichier manque. */
	fun of(species: String): SpriteFrames? {
		cache[species]?.let { return it }
		val sheet = ResourceLoader.load("$DIR$species.png") as? Texture2D ?: return null
		val side = sheet.getWidth() / 2.0

		val frames = SpriteFrames()
		if (frames.hasAnimation("default")) frames.removeAnimation("default")
		PLACES.forEach { (name, place) ->
			val (grounded, raised) = (0..1).map { beat ->
				AtlasTexture().apply {
					atlas = sheet
					region = Rect2(place.first * side, (place.second + beat) * side, side, side)
				}
			}
			add(frames, "idle_$name", 5.0, true, listOf(grounded))
			add(frames, "walk_$name", 8.0, true, listOf(raised, grounded))
			add(frames, "turn_$name", 10.0, false, listOf(raised, grounded))
		}
		return frames.also { cache[species] = it }
	}

	/**
	 * Habille [sprite] en [species] : ses animations, à l'échelle 1 (le fichier
	 * est au pixel du jeu), le bas de l'image au bas de la case — relevé de sa
	 * hauteur de vol si l'espèce vole. Renvoie false si le fichier manque.
	 */
	fun dress(sprite: AnimatedSprite2D, species: String, grid: Double): Boolean {
		val frames = of(species) ?: return false
		val side = frames.getFrameTexture("idle_down", 0)?.getHeight()?.toDouble() ?: return false
		sprite.spriteFrames = frames
		sprite.scale = Vector2(1.0, 1.0)
		sprite.position = Vector2(0.0, grid / 2.0 - side / 2.0 - liftOf(species))
		return true
	}

	private fun add(frames: SpriteFrames, name: String, speed: Double, loop: Boolean, cells: List<AtlasTexture>) {
		frames.addAnimation(name)
		frames.setAnimationSpeed(name, speed)
		frames.setAnimationLoop(name, loop)
		cells.forEach { frames.addFrame(name, it) }
	}
}
