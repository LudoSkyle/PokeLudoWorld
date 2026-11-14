extends "res://tests/lib.gd"

# Valider une entree : Sac ne fait rien encore, Options ouvre son ecran, Quitter ferme le menu.
# (Sauvegarder a ses propres tests : ui/save_*.)

func test() -> void:
	await menu_pick("Bag")
	check("Sac valide : le sac s'ouvre", bag_open())
	await tap("menu")
	check("de retour au menu, sur Sac", menu_open() and not bag_open() and menu_selected() == "Bag", menu_selected())
	await menu_pick("Options")
	check("Options valide : l'ecran des options s'ouvre", options_open())
	await tap("menu")
	check("de retour au menu, sur Options", menu_open() and not options_open() and menu_selected() == "Options", menu_selected())
	await menu_pick("Quit")
	check("Quitter valide : le menu se ferme", not menu_open())
	await wait(20)
	check("la pression qui ferme n'ouvre rien d'autre", not box().visible and not menu_open())
