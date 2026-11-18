package fr.skyle.pokemonmirage.scripts.gameplay.characters

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
 * Le fichier est celui du pack de données (`tools/gamedata.py`), au format de
 * Pokémon Studio : quatre rangées — bas, gauche, droite, haut — de quatre
 * images carrées (32 pixels de côté, plus pour un gros Pokémon). Colonnes 0 et
 * 2 : les deux dessins ; colonnes 1 et 3 : les mêmes un pixel plus bas. Lues
 * dans l'ordre, elles donnent le petit saut des jeux d'origine à chaque
 * changement de dessin : le code n'ajoute rien, tout est dans l'image.
 *
 * Les noms d'animation sont ceux de [CharacterFrames], que lit
 * [CharacterAnimation] : un Pokémon s'anime comme n'importe quel personnage.
 */
object PokemonFrames {

	const val DIR = "res://src/main/kotlin/fr/skyle/pokemonmirage/assets/pokemon/overworld/"

	/** Ce qui, dans le nom d'une apparence de personnage, désigne une espèce : `pkmn_wingull`. */
	const val PREFIX = "pkmn_"

	/** Les rangées du fichier, de haut en bas. */
	private val ROWS = listOf("down", "left", "right", "up")
	private const val COLUMNS = 4

	/**
	 * L'échelle d'un Pokémon posé sur la carte ou qui suit le joueur : un peu plus petit que son dessin, pour ne pas
	 * écraser les personnages (essai, Ludovic, 18/11/2026). Ce n'est plus un multiple entier : certains pixels du
	 * dessin sont rendus plus fins que d'autres.
	 */
	private const val SCALE = 0.9

	/**
	 * Images par seconde de l'animation : chaque image dure un sixième de seconde, donc un dessin (ses deux images,
	 * haute puis basse) un tiers de seconde — la cadence mesurée sur HeartGold / SoulSilver.
	 */
	private const val WALK_FPS = 6.0

	/** Un fichier n'est découpé qu'une fois, même porté par dix Pokémon. */
	private val cache = HashMap<String, SpriteFrames>()

	/** Les animations de [species], ou null si son fichier manque. */
	fun of(species: String): SpriteFrames? {
		cache[species]?.let { return it }
		val sheet = ResourceLoader.load("$DIR$species.png") as? Texture2D ?: return null
		val side = sheet.getWidth() / COLUMNS.toDouble()

		val frames = SpriteFrames()
		if (frames.hasAnimation("default")) frames.removeAnimation("default")
		ROWS.forEachIndexed { row, name ->
			val cells = (0 until COLUMNS).map { column ->
				AtlasTexture().apply {
					atlas = sheet
					region = Rect2(column * side, row * side, side, side)
				}
			}
			add(frames, "idle_$name", 5.0, true, listOf(cells[0]))
			add(frames, "walk_$name", WALK_FPS, true, cells)
			add(frames, "turn_$name", 10.0, false, listOf(cells[2], cells[0]))
		}
		return frames.also { cache[species] = it }
	}

	/**
	 * Habille [sprite] en [species] : ses animations, le bas de l'image au bas de la case — l'ancrage de Pokémon
	 * Studio. La hauteur du Pokémon dans son image, posé ou en l'air, vient du dessin : on n'y ajoute rien. Renvoie
	 * false si le fichier manque.
	 */
	fun dress(sprite: AnimatedSprite2D, species: String, grid: Double): Boolean {
		val frames = of(species) ?: return false
		val side = frames.getFrameTexture("idle_down", 0)?.getHeight()?.toDouble() ?: return false
		sprite.spriteFrames = frames
		sprite.scale = Vector2(SCALE, SCALE)
		// Les pieds restent au bas de la case, quelle que soit l'échelle.
		sprite.position = Vector2(0.0, grid / 2.0 - side * SCALE / 2.0)
		return true
	}

	private fun add(frames: SpriteFrames, name: String, speed: Double, loop: Boolean, cells: List<AtlasTexture>) {
		frames.addAnimation(name)
		frames.setAnimationSpeed(name, speed)
		frames.setAnimationLoop(name, loop)
		cells.forEach { frames.addFrame(name, it) }
	}
}
