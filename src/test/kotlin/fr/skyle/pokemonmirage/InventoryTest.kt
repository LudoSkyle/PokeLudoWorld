package fr.skyle.pokemonmirage

import fr.skyle.pokemonmirage.scripts.gameplay.items.Inventory
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

/** Le contenu du sac. */
class InventoryTest {

	@BeforeTest
	fun empty() = Inventory.clear()

	@Test
	fun `on ajoute, on compte, on retire`() {
		Inventory.add("potion", 3)
		Inventory.add("potion")
		assertEquals(4, Inventory.count("potion"))
		assertTrue(Inventory.remove("potion", 4))
		assertFalse(Inventory.has("potion"))
	}

	@Test
	fun `on ne retire pas plus qu'on n'a, et rien ne bouge`() {
		Inventory.add("potion", 2)
		assertFalse(Inventory.remove("potion", 3))
		assertFalse(Inventory.remove("potion", 0))
		assertEquals(2, Inventory.count("potion"))
	}

	@Test
	fun `les objets restent dans l'ordre où on les a reçus, et se reprennent d'une sauvegarde`() {
		Inventory.add("revive")
		Inventory.add("potion", 2)
		val saved = Inventory.snapshot()
		assertEquals(listOf("revive", "potion"), saved.keys.toList())
		Inventory.clear()
		Inventory.restore(saved)
		assertEquals(2, Inventory.count("potion"))
		assertEquals(1, Inventory.count("revive"))
	}
}
