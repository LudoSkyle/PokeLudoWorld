extends "res://tests/lib.gd"

# Entrer chez les voisins.

func start() -> Vector2i:
	return Vector2i(21, 14)

func test() -> void:
	await walk("village->voisins", Vector2i(21, 13), true)
	await arrival("voisins", Vector2i(15, 13), "idle_up")
