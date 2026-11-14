extends "res://tests/lib.gd"

# Choisir la langue : les menus et les dialogues changent aussitot, le reglage est enregistre.

func start() -> Vector2i:
	return Vector2i(6, 16)

func read_sign() -> String:
	await tap("ui_up")
	Input.action_press("interact"); await wait(2); Input.action_release("interact")
	await secs(1.0)
	var text := box_text()
	await close_box()
	return text

func test() -> void:
	check("francais au depart", TranslationServer.get_locale() == "fr", TranslationServer.get_locale())
	check("le panneau est en francais", await read_sign() == "Maison de Ludo.")

	await tap("menu")
	await tap("ui_down")
	await tap("interact")
	await tap("ui_down")
	check("Francais est le choix en rouge", options_language() == "French", options_language())
	await tap("ui_left")
	check("Gauche sur le premier choix : butee", options_language() == "French", options_language())
	await tap("ui_right")
	check("Droite : English", options_language() == "English" and TranslationServer.get_locale() == "en", TranslationServer.get_locale())
	shot("options_english")
	check("les libelles des menus sont traduits", game.tr("Vitesse du texte") == "Text speed" and game.tr("Sac") == "Bag" and game.tr("Bourg-Ludo") == "Ludo Town")
	var saved := ConfigFile.new()
	saved.load("user://test_settings.cfg")
	check("le reglage est enregistre", saved.get_value("options", "language", "") == "en", str(saved.get_value("options", "language", "")))
	await tap("menu")
	shot("menu_english")
	await tap("menu")
	check("le panneau est en anglais", await read_sign() == "Ludo's house.")

	await tap("menu")
	await tap("ui_down")
	await tap("interact")
	await tap("ui_down")
	await tap("ui_right")
	check("Droite sur le dernier choix : butee", options_language() == "English", options_language())
	await tap("ui_left")
	check("Gauche : retour au francais", options_language() == "French" and TranslationServer.get_locale() == "fr", TranslationServer.get_locale())
	await tap("menu")
	await tap("menu")
	check("le panneau est de nouveau en francais", await read_sign() == "Maison de Ludo.")
