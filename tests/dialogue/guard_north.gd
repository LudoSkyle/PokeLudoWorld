extends "res://tests/lib.gd"

# Le garde nord de la sortie ouest.

func start() -> Vector2i:
	return Vector2i(6, 7)

func test() -> void:
	await talk("garde nord", Vector2i(6, 7), "ui_left", "GuardNorth", "passage", "idle_right")
	shot("dialogue_garde_nord")
