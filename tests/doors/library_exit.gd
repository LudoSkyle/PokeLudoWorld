extends "res://tests/lib.gd"

# Sortir de la bibliotheque.

func scene() -> String:
	return "library"

func start() -> Vector2i:
	return Vector2i(16, 14)

func test() -> void:
	await hold_until_change("Bas sur le paillasson", "ui_down")
	await arrival("village devant la bibliotheque", Vector2i(21, 14), "idle_down")
