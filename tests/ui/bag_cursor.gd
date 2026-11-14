extends "res://tests/lib.gd"

# Le curseur du sac : la description et l'icone suivent, la liste ne boucle pas, X referme.

func test() -> void:
	await fill_bag()
	await menu_pick("Bag")
	await tap("ui_right")
	check("sur le premier objet", bag_line() == 0 and bag_icon() == "old_rod.png" and bag("Description").text.begins_with("Une canne"), bag("Description").text)
	await tap("ui_up")
	check("Haut sur le premier : butee", bag_line() == 0)
	await tap("ui_down")
	check("Bas : deuxieme objet", bag_line() == 1 and bag_icon() == "town_map.png" and bag("Description").text.begins_with("Un plan"), bag("Description").text)
	shot("sac_curseur")
	await tap("interact")
	check("valider un objet ne fait rien encore", bag_open() and bag_line() == 1 and not box().visible)
	await tap("ui_down")
	check("Bas : Retour", bag_line() == 2 and bag_icon() == "_back.png" and bag("Description").text == "Refermer le sac.")
	await tap("ui_down")
	check("Bas sur Retour : butee", bag_line() == 2)
	await tap("ui_left")
	check("changer de poche remet le curseur en haut", bag("Title").text == "Objets" and bag_line() == 0 and bag_icon() == "potion.png", bag_icon())
	var before := cell()
	Input.action_press("ui_down"); await secs(0.5); Input.action_release("ui_down"); await wait(8)
	check("le joueur ne bouge pas, sac ouvert", cell() == before, str(cell()))
	await tap("menu")
	check("X referme le sac", not bag_open() and menu_open())
	await menu_pick("Bag")
	check("rouvert : premiere poche, en haut", bag("Title").text == "Objets" and bag_line() == 0, bag("Title").text)
