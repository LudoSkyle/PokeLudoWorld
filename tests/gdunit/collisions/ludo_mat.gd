extends "res://tests/gdunit/game_suite.gd"

# Le paillasson du salon se traverse et s'atteint de tous les cotes.

func scene() -> String:
	return "ludo_house"

func start() -> Vector2i:
	return Vector2i(15, 14)

func test_ludo_mat() -> void:
	if game == null:
		return
	await walk("traverse vers la droite", Vector2i(17, 14), false)
	await walk("traverse vers la gauche", Vector2i(13, 14), false)
	await walk("atteint par le haut", EXIT_MAT, false, [Vector2i(14, 14), Vector2i(16, 14)])
