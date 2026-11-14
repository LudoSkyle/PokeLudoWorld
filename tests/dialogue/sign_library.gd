extends "res://tests/lib.gd"

# Le panneau de la bibliotheque.

func start() -> Vector2i:
	return Vector2i(19, 14)

func test() -> void:
	await examine("panneau de la bibliotheque", Vector2i(19, 14), "bibliothèque")
