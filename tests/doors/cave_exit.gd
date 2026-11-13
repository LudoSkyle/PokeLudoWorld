extends "res://tests/lib.gd"

# Sortir de la grotte par le couloir du bas.

func scene() -> String:
	return "cave_1f"

func start() -> Vector2i:
	return Vector2i(15, 19)

func test() -> void:
	await hold_until_change("Bas dans le couloir de sortie", "ui_down")
	await arrival("village devant la grotte", Vector2i(38, 3), "idle_down")
	shot("village_grotte")
