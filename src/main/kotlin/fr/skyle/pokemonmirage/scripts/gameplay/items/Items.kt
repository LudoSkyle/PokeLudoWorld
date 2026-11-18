package fr.skyle.pokemonmirage.scripts.gameplay.items

import fr.skyle.pokemonmirage.scripts.ui.N

/** Poche du sac. L'ordre est celui dans lequel on les parcourt, de gauche à droite. */
enum class Pocket(val title: String, val bag: String) {
	ITEMS(N("Objets"), "items"),
	KEY_ITEMS(N("Objets rares"), "key_items"),
	BALLS(N("Poké Balls"), "balls"),
}

/**
 * Un objet du jeu. [id] est aussi sa ligne dans la sauvegarde, **et le nom de
 * son icône** : `potion` se dessine avec `assets/items/icons/potion.png`
 * (voir [ItemIcons]). [name] et [description] sont en français et se
 * traduisent à l'affichage.
 *
 * [icon] se donne quand l'icône ne porte pas le nom de l'objet : un autre
 * dessin du même objet (`old_rod-old_colors`), l'icône d'un autre objet
 * (`rule_book`), une icône faite pour le jeu (`custom/clear_bell`) ou une
 * icône sans nom (`unnamed/07_F_2_fan`). Le sac l'affiche quatre fois plus
 * grande : elle doit faire 24 × 24.
 */
data class Item(
	val id: String,
	val name: String,
	val description: String,
	val pocket: Pocket,
	val icon: String = id,
) {
	/**
	 * Un objet rare est unique et ne se jette pas : le sac n'en affiche pas la
	 * quantité, et le recevoir se fête (voir ItemReveal).
	 */
	val isKey: Boolean
		get() = pocket == Pocket.KEY_ITEMS
}

/**
 * Le catalogue. Ajouter un objet : une ligne ici, ses deux textes dans
 * `locale/en.po`, et son icône `assets/items/icons/<id>.png` — le pack de données
 * en fournit près de 1 700.
 */
object Items {

	val ALL = listOf(
		Item("potion", N("Potion"), N("Un spray qui soigne les blessures. Il rend quelques forces à qui en a besoin."), Pocket.ITEMS),
		Item("super_potion", N("Super Potion"), N("Un spray plus concentré que la Potion. Il soigne les blessures sérieuses."), Pocket.ITEMS),
		Item("hyper_potion", N("Hyper Potion"), N("Le spray des grands jours. Il remet sur pied presque n'importe qui."), Pocket.ITEMS),
		Item("antidote", N("Antidote"), N("Un spray qui chasse le poison. À garder sous la main en forêt."), Pocket.ITEMS),
		Item("revive", N("Rappel"), N("Un éclat doré qui ranime celui qui s'est évanoui."), Pocket.ITEMS),
		Item("fresh_water", N("Eau Fraîche"), N("Une eau de source très pure. Elle désaltère et requinque."), Pocket.ITEMS),
		Item("soda_pop", N("Soda Cool"), N("Une boisson pétillante et sucrée. Elle redonne du tonus."), Pocket.ITEMS),
		Item("lemonade", N("Limonade"), N("Une limonade bien fraîche. Rien de tel après une longue marche."), Pocket.ITEMS),
		Item("poke_ball", N("Poké Ball"), N("Une capsule que l'on lance pour attraper un Pokémon sauvage."), Pocket.BALLS),
		Item("old_rod", N("Vieille canne"), N("Une canne à pêche usée. Le bois est lisse à force d'avoir servi."), Pocket.KEY_ITEMS),
		Item("town_map", N("Carte du village"), N("Un plan de Bourg-Ludo et de ses environs, dessiné à la main."), Pocket.KEY_ITEMS),
		// L'icône du Livre de Règles : un vieux livre.
		Item("dusty_register", N("Registre poussiéreux"), N("Le vieux registre des Veillées. Sa dernière page parle d'une cloche mise à l'abri."), Pocket.KEY_ITEMS, icon = "rule_book"),
		Item("tarnished_bell", N("Cloche ternie"), N("Une petite cloche de bronze noircie, sortie de la vase du lac souterrain."), Pocket.KEY_ITEMS, icon = "custom/tarnished_bell"),
		// Notre cloche ; `clear_bell` tout court est le Glas Transparent officiel.
		Item("clear_bell", N("Cloche claire"), N("La cloche de Bourg-Ludo, nettoyée. Son bronze a retrouvé sa couleur."), Pocket.KEY_ITEMS, icon = "custom/clear_bell"),
		// Un dessin de fan de la planche de Kryptonlion (case 07:F:2), gardé : le pack n'a pas de ruban qui convienne.
		Item("vigil_ribbon", N("Ruban de la Veillée"), N("Le ruban que Mémé Odile portait à la dernière Veillée. Un souvenir."), Pocket.KEY_ITEMS, icon = "other/07_F_2_fan"),
	)

	private val byId = ALL.associateBy { it.id }

	fun get(id: String): Item? = byId[id]
}
