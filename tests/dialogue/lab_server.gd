extends "res://tests/lib.gd"

# Le serveur du labo.

func scene() -> String:
	return "lab_house"

func start() -> Vector2i:
	return Vector2i(9, 8)

func test() -> void:
	await examine("serveur", Vector2i(9, 8), "serveur")
