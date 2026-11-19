extends "res://tests/gdunit/game_suite.gd"

# Le contenu du sac fait partie de la sauvegarde.

func test_bag_saved() -> void:
	if game == null:
		return
	await fill_bag()
	await menu_pick("Save")
	await wait_choices()
	await tap("interact")
	await secs(2.2)
	check("le sac est ecrit dans la sauvegarde", saved_file().get_value("items", "potion", 0) == 3 and saved_file().get_value("items", "old_rod", 0) == 1)
	await relaunch()
	await menu_pick("Bag")
	check("relance : les objets sont toujours la, dans le meme ordre", bag_rows() == ["Potion x3", "Super Potion x4", "Hyper Potion x5", "Antidote x6", "Rappel x7", "Eau Fraîche x8", "Soda Cool x9", "Limonade x10", "Repousse x12"], str(bag_rows()))
	await tap("ui_right")
	check("relance : les objets rares aussi", bag_rows() == ["Vieille canne", "Carte du village", "Retour"], str(bag_rows()))
