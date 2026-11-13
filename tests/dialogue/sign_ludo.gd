extends "res://tests/lib.gd"

# Le panneau de la maison de Ludo.

func start() -> Vector2i:
	return Vector2i(6, 16)

func test() -> void:
	await examine("panneau de Ludo", Vector2i(6, 16), "maison de ludo")
