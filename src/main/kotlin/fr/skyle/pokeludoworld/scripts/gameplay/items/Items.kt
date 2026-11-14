package fr.skyle.pokeludoworld.scripts.gameplay.items

import fr.skyle.pokeludoworld.scripts.ui.N

/** Poche du sac. L'ordre est celui dans lequel on les parcourt, de gauche à droite. */
enum class Pocket(val title: String, val bag: String) {
	ITEMS(N("Objets"), "items"),
	KEY_ITEMS(N("Objets rares"), "key_items"),
	BALLS(N("Poké Balls"), "balls"),
}

/**
 * Un objet du jeu. [id] est aussi sa ligne dans la sauvegarde. [name] et
 * [description] sont en français et se traduisent à l'affichage. [icon] est
 * une référence d'atlas (voir [ItemIcons]).
 */
data class Item(
	val id: String,
	val name: String,
	val description: String,
	val pocket: Pocket,
	val icon: String,
) {
	/**
	 * Un objet rare est unique et ne se jette pas : le sac n'en affiche pas la
	 * quantité, et le recevoir se fête (voir ItemReveal).
	 */
	val isKey: Boolean
		get() = pocket == Pocket.KEY_ITEMS
}

/**
 * Le catalogue. Ajouter un objet : une ligne ici, et ses deux textes dans
 * `locale/en.po`.
 */
object Items {

	val ALL = listOf(
		Item("potion", N("Potion"), N("Un spray qui soigne les blessures. Il rend quelques forces à qui en a besoin."), Pocket.ITEMS, "frlg:12"),
		Item("super_potion", N("Super Potion"), N("Un spray plus concentré que la Potion. Il soigne les blessures sérieuses."), Pocket.ITEMS, "frlg:13"),
		Item("hyper_potion", N("Hyper Potion"), N("Le spray des grands jours. Il remet sur pied presque n'importe qui."), Pocket.ITEMS, "frlg:14"),
		Item("antidote", N("Antidote"), N("Un spray qui chasse le poison. À garder sous la main en forêt."), Pocket.ITEMS, "frlg:17"),
		Item("revive", N("Rappel"), N("Un éclat doré qui ranime celui qui s'est évanoui."), Pocket.ITEMS, "frlg:23"),
		Item("fresh_water", N("Eau Fraîche"), N("Une eau de source très pure. Elle désaltère et requinque."), Pocket.ITEMS, "frlg:25"),
		Item("soda_pop", N("Soda Cool"), N("Une boisson pétillante et sucrée. Elle redonne du tonus."), Pocket.ITEMS, "frlg:26"),
		Item("lemonade", N("Limonade"), N("Une limonade bien fraîche. Rien de tel après une longue marche."), Pocket.ITEMS, "frlg:27"),
		Item("poke_ball", N("Poké Ball"), N("Une capsule que l'on lance pour attraper un Pokémon sauvage."), Pocket.BALLS, "frlg:3"),
		Item("old_rod", N("Vieille canne"), N("Une canne à pêche usée. Le bois est lisse à force d'avoir servi."), Pocket.KEY_ITEMS, "frlg:216"),
		Item("town_map", N("Carte du village"), N("Un plan de Bourg-Ludo et de ses environs, dessiné à la main."), Pocket.KEY_ITEMS, "frlg:219"),
		Item("dusty_register", N("Registre poussiéreux"), N("Le vieux registre des Veillées. Sa dernière page parle d'une cloche mise à l'abri."), Pocket.KEY_ITEMS, "dex:00:A:D"),
	)

	private val byId = ALL.associateBy { it.id }

	fun get(id: String): Item? = byId[id]
}
