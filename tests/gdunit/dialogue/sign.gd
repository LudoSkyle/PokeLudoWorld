extends "res://tests/gdunit/game_suite.gd"

# Un panneau se lit en lui faisant face.

func start() -> Vector2i:
	return Vector2i(22, 4)

func test_sign() -> void:
	if game == null:
		return
	await examine("le panneau", Vector2i(22, 4), "maison de ludo")
