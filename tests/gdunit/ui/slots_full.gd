extends "res://tests/gdunit/game_suite.gd"

# Trois parties : les trois emplacements sont pris, il n'y a plus de carte Nouvelle partie. En
# effacer une la fait revenir.

func title() -> bool:
	return true

func test_slots_full() -> void:
	if game == null:
		return
	plant_save(1)
	plant_save(2, "Maison de Ludo")
	plant_save(3, "Laboratoire")
	await relaunch()
	await slot_go("Save3")
	check("trois parties, pas de Nouvelle partie", slot_cards() == ["Save1", "Save2", "Save3", "Options"], str(slot_cards()))
	shot("titre_parties_pleines")
	await tap("interact")
	await tap("ui_down")
	await tap("interact")
	await tap("ui_up")
	await tap("interact")
	check("la troisieme effacee, Nouvelle partie revient", slot_cards() == ["Save1", "Save2", "New", "Options"], str(slot_cards()))
	await slot_go("New")
	await tap("interact")
	await title_gone()
	await menu_pick("Save")
	await wait_choices()
	await tap("interact")
	await secs(2.2)
	check("la nouvelle partie prend l'emplacement libere", FileAccess.file_exists(save_path(3)))
