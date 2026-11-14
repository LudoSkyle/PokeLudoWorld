extends "res://tests/lib.gd"

# Sauvegarder puis repondre Non : on revient au menu, rien n'est ecrit.

func test() -> void:
	await menu_pick("Save")
	check("le resume s'affiche, le menu lui laisse la place", save_summary().visible and not menu_open())
	check("le resume donne le lieu", save_summary().get_node("Location").text == "Bourg-Ludo", save_summary().get_node("Location").text)
	check("le resume donne le temps de jeu", save_summary().get_node("Time").text == "00:00", save_summary().get_node("Time").text)
	await wait_choices()
	check("la question est posee", box().visible and box_text() == "Voulez-vous sauvegarder la partie ?", box_text())
	check("Oui/Non apparait une fois la question ecrite", save_choices().visible)
	shot("sauvegarde_question")
	var before := cell()
	Input.action_press("ui_left"); await secs(0.5); Input.action_release("ui_left"); await wait(8)
	check("le joueur ne bouge pas pendant la question", cell() == before, str(cell()))
	await tap("ui_down")
	await tap("interact")
	check("Non : l'ecran de sauvegarde se ferme", not save_summary().visible and not save_choices().visible and not box().visible)
	check("Non : on revient au menu, sur Sauvegarder", menu_open() and menu_selected() == "Save", menu_selected())
	check("Non : rien n'est ecrit", not FileAccess.file_exists("user://test_save.cfg"))
	await menu_pick("Save")
	await wait_choices()
	await tap("menu")
	check("la touche du menu repond Non aussi", not save_summary().visible and menu_open())
	check("toujours rien d'ecrit", not FileAccess.file_exists("user://test_save.cfg"))
