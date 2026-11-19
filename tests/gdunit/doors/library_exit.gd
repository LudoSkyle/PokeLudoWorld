extends "res://tests/gdunit/game_suite.gd"

# Sortir de la bibliotheque.

func scene() -> String:
	return "library"

func start() -> Vector2i:
	return Vector2i(16, 14)

func test_library_exit() -> void:
	if game == null:
		return
	await hold_until_change("Bas sur le paillasson", "ui_down")
	await arrival("village devant la bibliotheque", Vector2i(3, 30), "idle_down")
