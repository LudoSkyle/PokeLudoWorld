extends "res://tests/lib.gd"

# La poubelle du labo.

func scene() -> String:
	return "lab_house"

func start() -> Vector2i:
	return Vector2i(13, 8)

func test() -> void:
	await examine("poubelle", Vector2i(13, 8), "poubelle est vide")
