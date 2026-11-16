extends "res://tests/lib.gd"

# Un panneau se lit en lui faisant face.

func start() -> Vector2i:
	return Vector2i(22, 4)

func test() -> void:
	await examine("le panneau", Vector2i(22, 4), "maison de ludo")
