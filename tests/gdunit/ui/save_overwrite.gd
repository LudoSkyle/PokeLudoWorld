extends "res://tests/gdunit/game_suite.gd"

# Une sauvegarde existe : on demande confirmation avant de l'ecraser.

func start() -> Vector2i:
	return Vector2i(22, 4)

func test_save_overwrite() -> void:
	if game == null:
		return
	await menu_pick("Save")
	await wait_choices()
	await tap("interact")
	await secs(2.2)
	check("premiere sauvegarde faite", FileAccess.file_exists("user://test_save_1.cfg") and not menu_open())
	await walk("on se deplace", Vector2i(20, 4), false)

	await menu_pick("Save")
	await wait_choices()
	await tap("interact")
	await wait_choices()
	check("seconde question : ecraser ?", box_text().begins_with("Une sauvegarde existe déjà.") and box_text().contains("écraser"), box_text())
	check("Oui/Non est revenu, sur Oui", save_choices().visible)
	shot("sauvegarde_ecraser")
	await tap("ui_down")
	await tap("interact")
	check("Non : retour au menu", menu_open() and not save_summary().visible)
	check("Non : l'ancienne sauvegarde est intacte", saved_cell().x == 22, str(saved_cell()))

	await menu_pick("Save")
	await wait_choices()
	await tap("interact")
	await wait_choices()
	await tap("interact")
	await secs(0.6)
	check("Oui deux fois : sauvegarde faite", box_text() == "La partie est sauvegardée.", box_text())
	check("la nouvelle place est enregistree", saved_cell().x == 20, str(saved_cell()))
	await secs(1.6)
	check("tout est ferme", not box().visible and not menu_open())
