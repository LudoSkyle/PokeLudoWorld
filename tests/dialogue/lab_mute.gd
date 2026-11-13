extends "res://tests/lib.gd"

# Ce qui ne dit rien dans le labo : l'etagere a fioles et la machine.

func scene() -> String:
	return "lab_house"

func start() -> Vector2i:
	return Vector2i(14, 8)

func test() -> void:
	await examine("etagere a fioles (muette)", Vector2i(14, 8), "")
	await examine("la machine (muette)", Vector2i(15, 13), "")
