package fr.skyle.pokemonmirage

import fr.skyle.pokemonmirage.scripts.gameplay.story.StoryFlags
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

/** Les drapeaux d'histoire : ce qui décide qui est sur une carte. */
class StoryFlagsTest {

	@BeforeTest
	fun none() = StoryFlags.clear()

	@Test
	fun `un nom vide ne demande rien`() {
		assertTrue(StoryFlags.allows("", ""))
		assertTrue(StoryFlags.allows("  ", "  "))
	}

	@Test
	fun `le drapeau requis doit être posé, l'interdit ne pas l'être`() {
		assertFalse(StoryFlags.allows("bell_hung", ""))
		assertTrue(StoryFlags.allows("", "bell_hung"))
		StoryFlags.set("bell_hung")
		assertTrue(StoryFlags.allows("bell_hung", "vigil_over"))
		assertFalse(StoryFlags.allows("", "bell_hung"))
		StoryFlags.set("vigil_over")
		assertFalse(StoryFlags.allows("bell_hung", "vigil_over"))
	}

	@Test
	fun `ils se reprennent d'une sauvegarde, dans l'ordre`() {
		StoryFlags.set("a"); StoryFlags.set("b")
		val saved = StoryFlags.snapshot()
		StoryFlags.clear()
		assertFalse(StoryFlags.has("a"))
		StoryFlags.restore(saved)
		assertEquals(listOf("a", "b"), StoryFlags.snapshot().toList())
	}
}
