extends "res://tests/gdunit/game_suite.gd"

# Les menus s'entendent : ouverture, curseur, validation, retour.

func test_sfx_menu() -> void:
	if game == null:
		return
	await tap("menu")
	check("ouvrir le menu", audio().last_sfx_id() == "menu", audio().last_sfx_id())
	await tap("ui_down")
	check("deplacer le curseur", audio().last_sfx_id() == "cursor", audio().last_sfx_id())
	# jusqu'a l'entree des options, ou qu'elle soit dans le menu
	var n := 0
	while menu_selected() != "Options" and n < 8:
		await tap("ui_down")
		n += 1
	await tap("interact")
	check("valider une entree", options_open() and audio().last_sfx_id() == "confirm", audio().last_sfx_id())
	await tap("ui_right")
	check("changer un reglage", audio().last_sfx_id() == "cursor", audio().last_sfx_id())
	await tap("menu")
	check("revenir en arriere", audio().last_sfx_id() == "cancel", audio().last_sfx_id())
	await tap("menu")
	check("la musique n'a pas ete touchee", audio().music_audible())
