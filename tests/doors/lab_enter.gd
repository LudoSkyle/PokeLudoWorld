extends "res://tests/lib.gd"

# Entrer au labo.

func start() -> Vector2i:
	return Vector2i(28, 8)

func test() -> void:
	await walk("village->labo", Vector2i(28, 7), true)
	await arrival("labo", Vector2i(15, 15), "idle_up")
