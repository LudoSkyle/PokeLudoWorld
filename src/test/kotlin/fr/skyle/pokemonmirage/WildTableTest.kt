package fr.skyle.pokemonmirage

import fr.skyle.pokemonmirage.scripts.gameplay.wild.WildTable
import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull
import kotlin.test.assertTrue

/** La table de rencontres d'une carte : sa lecture et son tirage. */
class WildTableTest {

	@Test
	fun `une table bien écrite garde toutes ses lignes`() {
		val table = WildTable.parse("mulotin:2-4*50 | piafeuille:2-5*35 | chenibulle:3*15")
		assertEquals(emptyList(), table.errors)
		assertEquals(listOf("mulotin", "piafeuille", "chenibulle"), table.slots.map { it.species.id })
		assertEquals(listOf(2..4, 2..5, 3..3), table.slots.map { it.levels })
		assertEquals(listOf(50, 35, 15), table.slots.map { it.weight })
	}

	@Test
	fun `sans poids une ligne vaut un`() {
		assertEquals(1, WildTable.parse("mulotin:3").slots.single().weight)
	}

	@Test
	fun `une ligne mal écrite est écartée et signalée, les autres restent`() {
		val table = WildTable.parse("mulotin:2-4 | inconnu:3 | piafeuille:9-2 | chenibulle:0 | n'importe quoi")
		assertEquals(listOf("mulotin"), table.slots.map { it.species.id })
		assertEquals(4, table.errors.size)
	}

	@Test
	fun `une table vide ne tire rien`() {
		val table = WildTable.parse("")
		assertTrue(table.isEmpty)
		assertNull(table.pick(Random(1)))
	}

	@Test
	fun `le tirage suit les poids et reste dans les niveaux`() {
		val table = WildTable.parse("mulotin:2-4*90 | chenibulle:7*10")
		val random = Random(42)
		val drawn = List(2000) { table.pick(random)!! }
		val common = drawn.count { it.species.id == "mulotin" }
		assertTrue(common in 1700..1900, "mulotin tiré $common fois sur 2000")
		assertTrue(drawn.all { if (it.species.id == "mulotin") it.level in 2..4 else it.level == 7 })
	}
}
