package fr.skyle.pokeludoworld.scripts.gameplay.items

import fr.skyle.pokeludoworld.scripts.ui.N

/** Poche du sac. L'ordre est celui dans lequel on les parcourt, de gauche à droite. */
enum class Pocket(val title: String, val bag: String) {
	ITEMS(N("Objets"), "items"),
	KEY_ITEMS(N("Objets rares"), "key_items"),
	BALLS(N("Poké Balls"), "balls"),
}

/**
 * Un objet du jeu. [id] nomme aussi son icône (`assets/items/<id>.png`) et sa
 * ligne dans la sauvegarde. [name] et [description] sont en français et se
 * traduisent à l'affichage.
 */
data class Item(
	val id: String,
	val name: String,
	val description: String,
	val pocket: Pocket,
	/** Faux pour un objet qu'on a en un seul exemplaire : le sac n'affiche pas de quantité. */
	val counted: Boolean = true,
)

/**
 * Le catalogue. Ajouter un objet : une ligne ici, son icône de 24×24 dans
 * `assets/items`, et ses deux textes dans `locale/en.po`.
 */
object Items {

	val ALL = listOf(
		Item(
			"potion", N("Potion"),
			N("Un spray qui soigne les blessures. Il rend quelques forces à qui en a besoin."),
			Pocket.ITEMS,
		),
		Item(
			"poke_ball", N("Poké Ball"),
			N("Une capsule que l'on lance pour attraper un Pokémon sauvage."),
			Pocket.BALLS,
		),
		Item(
			"old_rod", N("Vieille canne"),
			N("Une canne à pêche usée. Le bois est lisse à force d'avoir servi."),
			Pocket.KEY_ITEMS, counted = false,
		),
		Item(
			"town_map", N("Carte du village"),
			N("Un plan de Bourg-Ludo et de ses environs, dessiné à la main."),
			Pocket.KEY_ITEMS, counted = false,
		),
	)

	private val byId = ALL.associateBy { it.id }

	fun get(id: String): Item? = byId[id]
}
