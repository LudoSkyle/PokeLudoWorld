extends "res://tests/gdunit/game_suite.gd"

# Le garde sud de la sortie ouest.

func start() -> Vector2i:
	return Vector2i(2, 3)

func test_guard_south() -> void:
	if game == null:
		return
	await talk("garde sud", Vector2i(2, 3), "ui_left", "GuardSouth", "passage", "idle_right")
