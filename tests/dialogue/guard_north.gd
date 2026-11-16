extends "res://tests/lib.gd"

# Le garde nord de la sortie ouest.

func start() -> Vector2i:
	return Vector2i(2, 1)

func test() -> void:
	await talk("garde nord", Vector2i(2, 1), "ui_left", "GuardNorth", "passage", "idle_right")
	shot("dialogue_garde_nord")
