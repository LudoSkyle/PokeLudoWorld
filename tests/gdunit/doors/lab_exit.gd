extends "res://tests/gdunit/game_suite.gd"

# Sortir du labo.

func scene() -> String:
	return "lab_house"

func start() -> Vector2i:
	return Vector2i(16, 15)

func test_lab_exit() -> void:
	if game == null:
		return
	await hold_until_change("Bas sur le paillasson", "ui_down")
	await arrival("village devant le labo", Vector2i(45, 9), "idle_down")
