extends "res://tests/gdunit/game_suite.gd"

# Effacer une partie demande confirmation, le curseur sur Non ; Oui efface le fichier et retire
# la carte.

func title() -> bool:
	return true

func test_slots_delete() -> void:
	if game == null:
		return
	plant_save(1)
	plant_save(2, "Maison de Ludo", 600.0)
	await relaunch()
	await slot_go("Save1")
	await tap("interact")
	await tap("ui_down")
	await tap("interact")
	check("Effacer pose la question", slots().get_node("Footer/Hint").text == "Effacer la partie 1 ?", slots().get_node("Footer/Hint").text)
	check("Oui ou Non", slot_answers() == ["Oui", "Non"], str(slot_answers()))
	shot("titre_parties_effacer")
	await tap("interact")
	check("le curseur attendait sur Non : rien n'est efface", FileAccess.file_exists(save_path(1)))
	check("on revient aux cartes", not slot_choices().visible and slot_cards() == ["Save1", "Save2", "New", "Options"], str(slot_cards()))
	check("la question a disparu", slots().get_node("Footer/Hint").text == "")

	await tap("interact")
	await tap("ui_down")
	await tap("interact")
	await tap("menu")
	check("la touche du menu repond Non", FileAccess.file_exists(save_path(1)) and not slot_choices().visible)

	await tap("interact")
	await tap("ui_down")
	await tap("interact")
	await tap("ui_up")
	await tap("interact")
	check("Oui : le fichier est efface", not FileAccess.file_exists(save_path(1)))
	check("l'autre partie est toujours la", FileAccess.file_exists(save_path(2)))
	check("sa carte a disparu", slot_cards() == ["Save2", "New", "Options"], str(slot_cards()))
	check("la carte qui prend sa place est choisie", slot_selected() == "Save2", slot_selected())
	check("aucune partie n'a ete lancee", level() == null)
