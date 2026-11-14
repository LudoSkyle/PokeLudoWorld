extends "res://tests/lib.gd"

# Entrer dans la bibliotheque.

func start() -> Vector2i:
	return Vector2i(21, 14)

func test() -> void:
	await walk("village->bibliotheque", Vector2i(21, 13), true)
	await arrival("bibliotheque", Vector2i(15, 14), "idle_up")
