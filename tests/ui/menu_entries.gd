extends "res://tests/lib.gd"

# Valider une entree : Sac et Options ne font rien encore, Quitter ferme le menu.

func test() -> void:
	await tap("menu")
	await tap("interact")
	check("Sac valide : le menu reste ouvert", menu_open() and menu_selected() == "Bag", menu_selected())
	check("Sac valide : pas de boite de dialogue", not box().visible)
	await tap("ui_down")
	await tap("interact")
	check("Options valide : le menu reste ouvert", menu_open() and menu_selected() == "Options", menu_selected())
	await tap("ui_down")
	await tap("interact")
	check("Quitter valide : le menu se ferme", not menu_open())
	await wait(20)
	check("la pression qui ferme n'ouvre rien d'autre", not box().visible and not menu_open())
