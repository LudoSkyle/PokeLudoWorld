package fr.skyle.pokemonmirage

import fr.skyle.pokemonmirage.scripts.gameplay.pokemon.Pokedex
import fr.skyle.pokemonmirage.scripts.gameplay.pokemon.RegionalDex
import java.io.File
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

/** Le Pokédex : ce qu'on a vu et pris, et la liste des espèces de la région. */
class PokedexTest {

	@BeforeTest
	fun empty() = Pokedex.clear()

	@Test
	fun `une espece prise est vue, une espece vue n'est pas prise`() {
		assertTrue(Pokedex.see("pidgey"))
		assertFalse(Pokedex.see("pidgey"), "la seconde rencontre n'inscrit rien de plus")
		assertTrue(Pokedex.isSeen("pidgey"))
		assertFalse(Pokedex.isCaught("pidgey"))
		assertTrue(Pokedex.catch("mew"))
		assertTrue(Pokedex.isSeen("mew") && Pokedex.isCaught("mew"))
	}

	@Test
	fun `on ne compte que les especes de la liste qu'on donne`() {
		Pokedex.see("pidgey")
		Pokedex.catch("mew")
		Pokedex.see("mulotin")
		val region = listOf("pidgey", "rattata", "mew")
		assertEquals(2, Pokedex.seenCount(region))
		assertEquals(1, Pokedex.caughtCount(region))
	}

	@Test
	fun `ce qu'on sauvegarde se relit tel quel`() {
		Pokedex.see("pidgey")
		Pokedex.catch("mew")
		val seen = Pokedex.seenSnapshot()
		val caught = Pokedex.caughtSnapshot()
		Pokedex.clear()
		assertFalse(Pokedex.isSeen("pidgey"))
		Pokedex.restore(seen, caught)
		assertEquals(listOf("pidgey", "mew"), Pokedex.seenSnapshot())
		assertEquals(listOf("mew"), Pokedex.caughtSnapshot())
	}

	@Test
	fun `un Pokedex au format de Pokemon Studio donne ses especes dans l'ordre, sans doublon`() {
		val json = """{ "klass": "Dex", "dbSymbol": "regional", "startId": 1, "creatures": [
			{ "dbSymbol": "bulbasaur", "form": 0 }, { "dbSymbol": "ivysaur", "form": 0 }, { "dbSymbol": "ivysaur", "form": 1 } ] }"""
		assertEquals(listOf("bulbasaur", "ivysaur"), RegionalDex.parse(json))
		assertEquals(emptyList(), RegionalDex.parse("{}"))
	}

	@Test
	fun `le Pokedex regional du jeu est celui de la premiere generation`() {
		val ids = RegionalDex.parse(File("src/main/kotlin/fr/skyle/pokemonmirage/resources/pokedex/regional.json").readText())
		assertEquals(151, ids.size)
		assertEquals("bulbasaur", ids.first())
		assertEquals("pikachu", ids[24])
		assertEquals("mew", ids.last())
	}
}
