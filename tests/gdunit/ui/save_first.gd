extends "res://tests/gdunit/game_suite.gd"

# Premiere sauvegarde : une seule question, le message reste une seconde, puis tout se ferme.

func start() -> Vector2i:
	return Vector2i(22, 4)

func test_save_first() -> void:
	if game == null:
		return
	await tap("ui_up")
	await menu_pick("Save")
	await wait_choices()
	await tap("interact")
	await secs(0.6)
	check("pas de seconde question sans sauvegarde existante", box_text() == "La partie est sauvegardée.", box_text())
	check("le fichier est ecrit", FileAccess.file_exists("user://test_save_1.cfg"))
	check("Oui/Non a disparu", not save_choices().visible)
	check("le message reste a l'ecran", box().visible and save_summary().visible)
	shot("sauvegarde_faite")
	await secs(1.4)
	check("une seconde plus tard tout est ferme, menu compris", not box().visible and not save_summary().visible and not menu_open())
	var file := saved_file()
	check("carte enregistree", str(file.get_value("save", "scene", "")).ends_with("field.tscn"), str(file.get_value("save", "scene", "")))
	check("case enregistree", saved_cell() == Vector2i(22, 4), str(saved_cell()))
	check("regard enregistre", file.get_value("save", "facing_y", 0.0) == -1.0, str(file.get_value("save", "facing_y", 0.0)))
	check("lieu enregistre", file.get_value("save", "location", "") == "Terrain d'essai", str(file.get_value("save", "location", "")))
	await walk("on remarche ensuite", Vector2i(21, 4), false)
