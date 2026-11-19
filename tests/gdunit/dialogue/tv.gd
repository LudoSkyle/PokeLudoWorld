extends "res://tests/gdunit/game_suite.gd"

# La tele du salon : une emission au hasard, depuis ses deux cases.

func scene() -> String:
	return "ludo_house"

func start() -> Vector2i:
	return Vector2i(17, 9)

func test_tv() -> void:
	if game == null:
		return
	await examine("tele, case de gauche", Vector2i(17, 9), " ")
	await examine("tele, case de droite", Vector2i(18, 9), " ")
