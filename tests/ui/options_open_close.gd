extends "res://tests/lib.gd"

# L'ecran des options s'ouvre depuis le menu et y ramene, par Retour ou par X.

func test() -> void:
	await tap("menu")
	await tap("ui_down")
	await tap("interact")
	check("Options valide : l'ecran s'ouvre", options_open())
	shot("options")
	var before := cell()
	Input.action_press("ui_left"); await secs(0.5); Input.action_release("ui_left"); await wait(8)
	check("options ouvertes : le joueur ne bouge pas", cell() == before, str(cell()))
	await tap("menu")
	check("X ferme les options", not options_open())
	check("X ne ferme pas le menu derriere", menu_open() and menu_selected() == "Options", menu_selected())
	await tap("interact")
	check("on rouvre les options", options_open())
	# Haut depuis la premiere ligne boucle sur la derniere : Retour
	await tap("ui_up")
	await tap("interact")
	check("Retour ferme les options", not options_open())
	check("Retour ramene au menu", menu_open())
	await tap("menu")
	check("X ferme ensuite le menu", not menu_open())
