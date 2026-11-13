extends "res://tests/lib.gd"

# Sortir de chez les voisins.

func scene() -> String:
	return "neighbor_house"

func start() -> Vector2i:
	return Vector2i(16, 13)

func test() -> void:
	await hold_until_change("Bas sur le paillasson", "ui_down")
	await arrival("village devant les voisins", Vector2i(21, 14), "idle_down")
