extends "res://tests/lib.gd"

# Le garde sud de la sortie ouest.

func start() -> Vector2i:
	return Vector2i(2, 3)

func test() -> void:
	await talk("garde sud", Vector2i(2, 3), "ui_left", "GuardSouth", "passage", "idle_right")
