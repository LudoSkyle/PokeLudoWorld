extends "res://tests/lib.gd"

# Regler la vitesse du texte : Gauche/Droite, bornes, effet sur une vraie boite, enregistrement.

func start() -> Vector2i:
	return Vector2i(6, 16)

func test() -> void:
	await tap("menu")
	await tap("ui_down")
	await tap("interact")
	for i in 5:
		await tap("ui_left")
	check("Gauche jusqu'au bout : Lente", options_speed() == "Slow" and is_equal_approx(letter_seconds(), 0.08), "%s %.2f" % [options_speed(), letter_seconds()])
	await tap("ui_right")
	check("Droite : Normale", options_speed() == "Normal" and is_equal_approx(letter_seconds(), 0.04), "%s %.2f" % [options_speed(), letter_seconds()])
	shot("options_normale")
	await tap("ui_right")
	check("Droite : Rapide", options_speed() == "Fast" and is_equal_approx(letter_seconds(), 0.02), "%s %.2f" % [options_speed(), letter_seconds()])
	for i in 5:
		await tap("ui_right")
	check("Droite jusqu'au bout : Instantanee", options_speed() == "Instant" and letter_seconds() == 0.0, "%s %.2f" % [options_speed(), letter_seconds()])
	var saved := ConfigFile.new()
	saved.load("user://settings.cfg")
	check("le reglage est enregistre", saved.get_value("options", "text_speed", -1) == 3, str(saved.get_value("options", "text_speed", -1)))

	# effet reel : en Instantanee, le panneau s'affiche d'un coup
	await tap("menu")
	await tap("menu")
	check("menus refermes", not options_open() and not menu_open())
	await tap("ui_up")
	Input.action_press("interact"); await wait(2); Input.action_release("interact")
	await wait(6)
	check("Instantanee : le texte est entier tout de suite", box().visible and box_text() == "Maison de Ludo.", box_text())
	await close_box()

	# on remet Rapide, la valeur par defaut
	await tap("menu")
	await tap("interact")
	await tap("ui_left")
	check("remis sur Rapide", options_speed() == "Fast", options_speed())
	await tap("menu")
	await tap("menu")
