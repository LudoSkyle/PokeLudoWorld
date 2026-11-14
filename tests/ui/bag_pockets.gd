extends "res://tests/lib.gd"

# Les trois poches : leur titre, leur sac, leurs fleches et leur contenu.

func test() -> void:
	await fill_bag()
	await menu_pick("Bag")
	check("Objets : la potion et sa quantite", bag_rows() == ["Potion x3", "Retour"], str(bag_rows()))
	check("Objets : sac ouvert sur la bonne poche", bag("Bag").texture.resource_path.ends_with("bag_items.png"))
	check("premiere poche : pas de fleche a gauche, une a droite", not bag("PocketLeft").visible and bag("PocketRight").visible)
	shot("sac_objets")
	await tap("ui_left")
	check("Gauche sur la premiere poche : butee", bag("Title").text == "Objets", bag("Title").text)
	await tap("ui_right")
	check("Objets rares : deux objets, sans quantite", bag("Title").text == "Objets rares" and bag_rows() == ["Vieille canne", "Carte du village", "Retour"], str(bag_rows()))
	check("Objets rares : sac ouvert sur la bonne poche", bag("Bag").texture.resource_path.ends_with("bag_key_items.png"))
	check("poche du milieu : une fleche de chaque cote", bag("PocketLeft").visible and bag("PocketRight").visible)
	shot("sac_objets_rares")
	await tap("ui_right")
	check("Poke Balls : les balls et leur quantite", bag("Title").text == "Poké Balls" and bag_rows() == ["Poké Ball x5", "Retour"], str(bag_rows()))
	check("Poke Balls : sac ouvert sur la bonne poche", bag("Bag").texture.resource_path.ends_with("bag_balls.png"))
	check("derniere poche : une fleche a gauche seulement", bag("PocketLeft").visible and not bag("PocketRight").visible)
	await tap("ui_right")
	check("Droite sur la derniere poche : butee", bag("Title").text == "Poké Balls", bag("Title").text)
	check("pas de defilement pour si peu d'objets", not bag("ScrollUp").visible and not bag("ScrollDown").visible)
