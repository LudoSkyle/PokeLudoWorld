extends "res://tests/lib.gd"

# Le contenu du sac fait partie de la sauvegarde.

func test() -> void:
	await fill_bag()
	await menu_pick("Save")
	await wait_choices()
	await tap("interact")
	await secs(2.2)
	check("le sac est ecrit dans la sauvegarde", saved_file().get_value("items", "potion", 0) == 3 and saved_file().get_value("items", "old_rod", 0) == 1)
	await relaunch()
	await menu_pick("Bag")
	check("relance : la potion est toujours la", bag_rows() == ["Potion x3", "Retour"], str(bag_rows()))
	await tap("ui_right")
	check("relance : les objets rares aussi, dans le meme ordre", bag_rows() == ["Vieille canne", "Carte du village", "Retour"], str(bag_rows()))
