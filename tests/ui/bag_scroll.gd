extends "res://tests/lib.gd"

# Poche de huit objets : la liste defile avec le curseur, les fleches disent ce qui reste.

func test() -> void:
	await fill_bag()
	await menu_pick("Bag")
	check("en haut : six lignes, fleche vers le bas seulement", bag_rows() == ["Potion x3", "Super Potion x4", "Hyper Potion x5", "Antidote x6", "Rappel x7", "Eau Fraîche x8"] and not bag("ScrollUp").visible and bag("ScrollDown").visible, str(bag_rows()))
	for i in 5:
		await tap("ui_down")
	check("5 fois Bas : derniere ligne visible, pas encore de defilement", bag_line() == 5 and bag_rows()[0] == "Potion x3" and bag("Description").text.begins_with("Une eau"), str(bag_rows()))
	await tap("ui_down")
	check("Bas : la liste monte d'une ligne", bag_line() == 5 and bag_rows() == ["Super Potion x4", "Hyper Potion x5", "Antidote x6", "Rappel x7", "Eau Fraîche x8", "Soda Cool x9"], str(bag_rows()))
	check("au milieu : les deux fleches", bag("ScrollUp").visible and bag("ScrollDown").visible)
	shot("sac_defile")
	await tap("ui_down")
	await tap("ui_down")
	check("tout en bas : Retour est la derniere ligne", bag_line() == 5 and bag_rows() == ["Antidote x6", "Rappel x7", "Eau Fraîche x8", "Soda Cool x9", "Limonade x10", "Retour"], str(bag_rows()))
	check("en bas : fleche vers le haut seulement", bag("ScrollUp").visible and not bag("ScrollDown").visible)
	check("la description est celle de Retour", bag("Description").text == "Refermer le sac.")
	await tap("ui_down")
	check("Bas sur Retour : butee", bag_line() == 5 and bag_rows()[5] == "Retour")
	for i in 5:
		await tap("ui_up")
	check("5 fois Haut : premiere ligne visible, sans defiler", bag_line() == 0 and bag_rows()[0] == "Antidote x6", str(bag_rows()))
	await tap("ui_up")
	check("Haut : la liste redescend d'une ligne", bag_line() == 0 and bag_rows()[0] == "Hyper Potion x5" and bag("Description").text.begins_with("Le spray"), str(bag_rows()))
	for i in 4:
		await tap("ui_up")
	check("retour tout en haut", bag_line() == 0 and bag_rows()[0] == "Potion x3" and not bag("ScrollUp").visible, str(bag_rows()))
	await tap("ui_right")
	await tap("ui_left")
	check("changer de poche puis revenir : la liste repart du haut", bag_rows()[0] == "Potion x3" and bag_line() == 0)
