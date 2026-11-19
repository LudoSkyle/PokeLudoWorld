extends "res://tests/gdunit/game_suite.gd"

# Sortir de chez Ludo par le paillasson.

func scene() -> String:
	return "ludo_house"

func start() -> Vector2i:
	return Vector2i(15, 14)

func test_ludo_exit() -> void:
	if game == null:
		return
	await hold_until_change("Bas sur le paillasson", "ui_down")
	await arrival("village devant chez Ludo", Vector2i(10, 9), "idle_down")
