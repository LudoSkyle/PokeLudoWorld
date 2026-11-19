extends "res://tests/gdunit/game_suite.gd"

# L'unique sauvegarde d'avant les emplacements n'est pas perdue : au lancement elle devient
# celle du premier emplacement.

func title() -> bool:
	return true

func test_slots_old_save() -> void:
	if game == null:
		return
	plant_save(1, "Maison de Ludo", 4000.0)
	DirAccess.rename_absolute(save_path(1), "user://test_save.cfg")
	check("mise en place : seule l'ancienne sauvegarde existe", FileAccess.file_exists("user://test_save.cfg") and not FileAccess.file_exists(save_path(1)))
	await relaunch()
	check("elle a pris le premier emplacement", FileAccess.file_exists(save_path(1)) and not FileAccess.file_exists("user://test_save.cfg"))
	await slot_go("Save1")
	check("sa carte est la", slot_cards() == ["Save1", "New", "Options"], str(slot_cards()))
	check("avec son lieu et son temps de jeu", slot_card("Save1").get_node("Save/Location").text == "Maison de Ludo" and slot_card("Save1").get_node("Save/Time/Value").text == "01:06", slot_card("Save1").get_node("Save/Time/Value").text)
