extends "res://tests/lib.gd"

# Deux outils de Debug : aller sur le terrain d'essai depuis n'importe quelle carte, et regler la
# vitesse du jeu.

func scene() -> String:
	return "start_island"

func start() -> Vector2i:
	return Vector2i(30, 13)

func test() -> void:
	await menu_pick("Debug")
	for i in 7:
		await tap("ui_down")
	check("la vitesse est x1 au depart", debug_lines()[7] == "Vitesse : x1" and is_equal_approx(Engine.time_scale, 1.0), debug_lines()[7])
	await tap("interact")
	check("valider passe a x2, sans fermer la boite", debug_lines()[7] == "Vitesse : x2" and is_equal_approx(Engine.time_scale, 2.0) and debug_choices().visible, debug_lines()[7])
	await tap("interact")
	await tap("interact")
	check("puis x4, puis x8", debug_lines()[7] == "Vitesse : x8" and is_equal_approx(Engine.time_scale, 8.0), debug_lines()[7])
	await tap("interact")
	check("et de nouveau x1", debug_lines()[7] == "Vitesse : x1" and is_equal_approx(Engine.time_scale, 1.0), debug_lines()[7])
	await tap("ui_up")
	check("au-dessus : le terrain d'essai", debug_lines()[6] == "Terrain d'essai")
	var id := level_id()
	await tap("interact")
	var n := 0
	while level_id() == id and n < 400:
		await wait(1)
		n += 1
	await wait(90)
	check("on arrive sur le terrain d'essai, menu ferme", level_id() != id and str(level().get_meta("location", "")) == "Terrain d'essai" and not menu_open(), str(level().get_meta("location", "")))
	check("a son point d'apparition", cell() == Vector2i(12, 9), str(cell()))
