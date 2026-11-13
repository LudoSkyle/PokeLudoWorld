extends "res://tests/lib.gd"

# Grotte B2F : le lac bloque, on en fait le tour par le sud.

func scene() -> String:
	return "cave_b2f"

func start() -> Vector2i:
	return Vector2i(6, 4)

func test() -> void:
	await walk("bord du lac", Vector2i(14, 7), false)
	await hold_no_change("Bas contre le lac", "ui_down")
	shot("grotte_b2f_lac")
	await walk("tour du lac par le sud", Vector2i(15, 15), false)
