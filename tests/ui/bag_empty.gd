extends "res://tests/lib.gd"

# Sac vide : chaque poche ne propose que Retour, qui referme le sac.

func test() -> void:
	await menu_pick("Bag")
	check("le sac s'ouvre sur la poche Objets", bag_open() and bag("Title").text == "Objets", bag("Title").text)
	check("poche vide : seulement Retour", bag_rows() == ["Retour"], str(bag_rows()))
	check("le curseur est sur Retour", bag_line() == 0)
	check("description et icone de Retour", bag("Description").text == "Refermer le sac." and bag_icon() == "_back.png", bag("Description").text)
	shot("sac_vide")
	await tap("ui_down")
	await tap("ui_up")
	check("rien d'autre a parcourir", bag_line() == 0)
	await tap("ui_right")
	check("Droite : Objets rares, vide aussi", bag("Title").text == "Objets rares" and bag_rows() == ["Retour"], bag("Title").text)
	await tap("ui_right")
	check("Droite : Poke Balls, vide aussi", bag("Title").text == "Poké Balls" and bag_rows() == ["Retour"], bag("Title").text)
	await tap("interact")
	check("Retour referme le sac", not bag_open())
	check("on revient au menu, sur Sac", menu_open() and menu_selected() == "Bag", menu_selected())
