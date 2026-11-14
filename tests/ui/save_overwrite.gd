extends "res://tests/lib.gd"

# Une sauvegarde existe : on demande confirmation avant de l'ecraser.

func start() -> Vector2i:
	return Vector2i(6, 16)

func test() -> void:
	await menu_pick("Save")
	await wait_choices()
	await tap("interact")
	await secs(2.2)
	check("premiere sauvegarde faite", FileAccess.file_exists("user://test_save.cfg") and not menu_open())
	await walk("on se deplace", Vector2i(9, 16), false)

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
	check("Non : l'ancienne sauvegarde est intacte", saved_file().get_value("save", "x", 0.0) == 6 * 16 + 8, str(saved_file().get_value("save", "x", 0.0)))

	await menu_pick("Save")
	await wait_choices()
	await tap("interact")
	await wait_choices()
	await tap("interact")
	await secs(0.6)
	check("Oui deux fois : sauvegarde faite", box_text() == "La partie est sauvegardée.", box_text())
	check("la nouvelle place est enregistree", saved_file().get_value("save", "x", 0.0) == 9 * 16 + 8, str(saved_file().get_value("save", "x", 0.0)))
	await secs(1.6)
	check("tout est ferme", not box().visible and not menu_open())
