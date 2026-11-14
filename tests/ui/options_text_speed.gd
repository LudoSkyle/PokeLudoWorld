extends "res://tests/lib.gd"

# Regler la vitesse du texte : Gauche/Droite, bornes, effet sur la boite, enregistrement.

func start() -> Vector2i:
	return Vector2i(6, 16)

func speed_is(node: String, seconds: float) -> bool:
	return options_speed() == node and is_equal_approx(letter_seconds(), seconds)

func test() -> void:
	await menu_pick("Options")
	for i in 5:
		await tap("ui_left")
	check("Gauche jusqu'au bout : x0.5", speed_is("Half", 0.04), "%s %.3f" % [options_speed(), letter_seconds()])
	await tap("ui_right")
	check("Droite : x1", speed_is("One", 0.02), "%s %.3f" % [options_speed(), letter_seconds()])
	shot("options_x1")
	await tap("ui_right")
	check("Droite : x2", speed_is("Two", 0.01), "%s %.3f" % [options_speed(), letter_seconds()])
	for i in 5:
		await tap("ui_right")
	check("Droite jusqu'au bout : x4", speed_is("Four", 0.005), "%s %.3f" % [options_speed(), letter_seconds()])
	var saved := ConfigFile.new()
	saved.load("user://test_settings.cfg")
	check("le reglage est enregistre", saved.get_value("options", "text_speed_factor", -1) == 3, str(saved.get_value("options", "text_speed_factor", -1)))

	# effet reel : en x4, les 15 lettres du panneau sont la en un dixieme de seconde
	await tap("menu")
	await tap("menu")
	check("menus refermes", not options_open() and not menu_open())
	await tap("ui_up")
	Input.action_press("interact"); await wait(2); Input.action_release("interact")
	await secs(0.15)
	check("x4 : le texte est deja entier", box().visible and box_text() == "Maison de Ludo.", box_text())
	await close_box()
