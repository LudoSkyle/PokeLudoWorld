extends "res://tests/lib.gd"

# Entrer dans la grotte.

func start() -> Vector2i:
	return Vector2i(38, 3)

func test() -> void:
	await walk("village->grotte", Vector2i(38, 2), true)
	await arrival("grotte 1F", Vector2i(14, 19), "idle_up")
	shot("grotte_1f_entree")
