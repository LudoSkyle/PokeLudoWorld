extends "res://tests/gdunit/game_suite.gd"

# Poche de dix objets : la liste, de neuf lignes, defile avec le curseur, les fleches disent ce qui reste.

func test_bag_scroll() -> void:
	if game == null:
		return
	await fill_bag()
	await menu_pick("Bag")
	check("en haut : neuf lignes, fleche vers le bas seulement", bag_rows() == ["Potion x3", "Super Potion x4", "Hyper Potion x5", "Antidote x6", "Rappel x7", "Eau Fraîche x8", "Soda Cool x9", "Limonade x10", "Repousse x12"] and not bag("ScrollUp").visible and bag("ScrollDown").visible, str(bag_rows()))
	for i in 8:
		await tap("ui_down")
	check("8 fois Bas : derniere ligne visible, pas encore de defilement", bag_line() == 8 and bag_rows()[0] == "Potion x3" and bag("Description").text.begins_with("Un spray dont"), str(bag_rows()))
	await tap("ui_down")
	check("Bas : la liste monte d'une ligne", bag_line() == 8 and bag_rows() == ["Super Potion x4", "Hyper Potion x5", "Antidote x6", "Rappel x7", "Eau Fraîche x8", "Soda Cool x9", "Limonade x10", "Repousse x12", "Super Repousse x13"], str(bag_rows()))
	check("au milieu : les deux fleches", bag("ScrollUp").visible and bag("ScrollDown").visible)
	shot("sac_defile")
	await tap("ui_down")
	check("tout en bas : Retour est la derniere ligne", bag_line() == 8 and bag_rows() == ["Hyper Potion x5", "Antidote x6", "Rappel x7", "Eau Fraîche x8", "Soda Cool x9", "Limonade x10", "Repousse x12", "Super Repousse x13", "Retour"], str(bag_rows()))
	check("en bas : fleche vers le haut seulement", bag("ScrollUp").visible and not bag("ScrollDown").visible)
	check("la description est celle de Retour", bag("Description").text == "Refermer le sac.")
	await tap("ui_down")
	check("Bas sur Retour : butee", bag_line() == 8 and bag_rows()[8] == "Retour")
	for i in 8:
		await tap("ui_up")
	check("8 fois Haut : premiere ligne visible, sans defiler", bag_line() == 0 and bag_rows()[0] == "Hyper Potion x5", str(bag_rows()))
	await tap("ui_up")
	check("Haut : la liste redescend d'une ligne", bag_line() == 0 and bag_rows()[0] == "Super Potion x4" and bag("Description").text.begins_with("Un spray plus concentré"), str(bag_rows()))
	await tap("ui_up")
	check("retour tout en haut", bag_line() == 0 and bag_rows()[0] == "Potion x3" and not bag("ScrollUp").visible, str(bag_rows()))
