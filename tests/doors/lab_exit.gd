extends "res://tests/lib.gd"

# Sortir du labo.

func scene() -> String:
	return "lab_house"

func start() -> Vector2i:
	return Vector2i(16, 15)

func test() -> void:
	await hold_until_change("Bas sur le paillasson", "ui_down")
	await arrival("village devant le labo", Vector2i(28, 8), "idle_down")
