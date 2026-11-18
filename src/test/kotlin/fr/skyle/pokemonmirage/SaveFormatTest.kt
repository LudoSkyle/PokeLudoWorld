package fr.skyle.pokemonmirage

import fr.skyle.pokemonmirage.scripts.core.SaveGame
import kotlin.test.Test
import kotlin.test.assertEquals

/** Ce qu'une sauvegarde retient d'une carte : son nom, pas son chemin. */
class SaveFormatTest {

	@Test
	fun `une carte se désigne par son nom, où que soit rangée sa scène`() {
		assertEquals("start_island", SaveGame.mapOf("res://src/main/kotlin/fr/skyle/pokemonmirage/scenes/levels/start_island.tscn"))
		assertEquals("start_island", SaveGame.mapOf("res://src/main/kotlin/fr/skyle/pokeludoworld/scenes/levels/start_island.tscn"))
		assertEquals("route_1", SaveGame.mapOf("res://ailleurs/route_1.tscn"))
	}

	@Test
	fun `et son nom redonne sa scène`() {
		val scene = SaveGame.sceneOf("ludo_bedroom")
		assertEquals("ludo_bedroom", SaveGame.mapOf(scene))
		assertEquals(true, scene.startsWith("res://") && scene.endsWith("/scenes/levels/ludo_bedroom.tscn"))
	}
}
