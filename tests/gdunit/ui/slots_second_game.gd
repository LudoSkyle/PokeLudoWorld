extends "res://tests/gdunit/game_suite.gd"

# Une nouvelle partie alors qu'il y en a deja une prend l'emplacement libre suivant : elle part
# du point d'apparition, et sauvegarder n'ecrase pas la premiere.

func title() -> bool:
	return true

func test_slots_second_game() -> void:
	if game == null:
		return
	plant_save(1, "Terrain d'essai", 3725.0)
	await relaunch()
	await slot_go("New")
	check("une partie existe : sa carte, puis Nouvelle partie", slot_cards() == ["Save1", "New", "Options"], str(slot_cards()))
	check("sa carte dit une heure et deux minutes", slot_card("Save1").get_node("Save/Time/Value").text == "01:02", slot_card("Save1").get_node("Save/Time/Value").text)
	await tap("interact")
	await title_gone()
	var spawn: Vector2 = level().get_node("SpawnPoint").position
	check("la nouvelle partie part du point d'apparition, pas de la case sauvegardee", cell() == Vector2i(floori(spawn.x / 16.0), floori(spawn.y / 16.0)) and cell() != SAVE_CELL, str(cell()))
	await walk("on s'eloigne", two_steps_from(cell()), false)
	var here := cell()
	await menu_pick("Save")
	await wait_choices()
	await tap("interact")
	await secs(2.2)
	check("elle s'ecrit dans le deuxieme emplacement", FileAccess.file_exists(save_path(2)))
	check("a la case ou l'on est", saved_cell(2) == here, str(saved_cell(2)))
	check("la premiere partie n'a pas bouge", is_equal_approx(saved_file(1).get_value("save", "seconds", 0.0), 3725.0) and saved_cell(1) == SAVE_CELL)

	await relaunch()
	await slot_go("Save2")
	check("les deux parties ont leur carte", slot_cards() == ["Save1", "Save2", "New", "Options"], str(slot_cards()))
	check("la deuxieme porte son numero", slot_card("Save2").get_node("Save/Title").text == "Partie 2", slot_card("Save2").get_node("Save/Title").text)
	shot("titre_parties_deux")
