extends "res://tests/lib.gd"

# Le panneau de la maison des voisins.

func start() -> Vector2i:
	return Vector2i(19, 14)

func test() -> void:
	await examine("panneau des voisins", Vector2i(19, 14), "voisins")
