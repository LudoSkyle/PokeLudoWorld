package fr.skyle.pokeludoworld.scripts.gameplay.characters

import godot.api.AtlasTexture
import godot.api.SpriteFrames
import godot.api.Texture2D
import godot.core.Rect2

/**
 * Fabrique les animations d'un personnage à partir de sa planche, pour ne pas
 * tenir un `.tres` par personnage. Toutes les planches ont le même découpage :
 * 4 colonnes × 4 rangées, rangées bas, gauche, droite, haut ; la première
 * image d'une rangée est la pose immobile.
 *
 * Les noms et les vitesses sont ceux de `player.tres`, que lit
 * [CharacterAnimation].
 */
object CharacterFrames {

	private const val COLUMNS = 4
	private val ROWS = listOf("down", "left", "right", "up")

	fun build(sheet: Texture2D): SpriteFrames {
		val width = sheet.getWidth() / COLUMNS.toDouble()
		val height = sheet.getHeight() / ROWS.size.toDouble()

		val frames = SpriteFrames()
		if (frames.hasAnimation("default")) frames.removeAnimation("default")

		ROWS.forEachIndexed { row, name ->
			val cells = (0 until COLUMNS).map { column ->
				AtlasTexture().apply {
					atlas = sheet
					region = Rect2(column * width, row * height, width, height)
				}
			}

			add(frames, "idle_$name", 5.0, true, listOf(cells[0]))
			add(frames, "walk_$name", 8.0, true, listOf(cells[1], cells[2], cells[3], cells[0]))
			add(frames, "turn_$name", 10.0, false, listOf(cells[1], cells[0]))
		}

		return frames
	}

	private fun add(frames: SpriteFrames, name: String, speed: Double, loop: Boolean, cells: List<AtlasTexture>) {
		frames.addAnimation(name)
		frames.setAnimationSpeed(name, speed)
		frames.setAnimationLoop(name, loop)
		cells.forEach { frames.addFrame(name, it) }
	}
}
