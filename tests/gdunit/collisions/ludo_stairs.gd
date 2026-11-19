extends "res://tests/gdunit/game_suite.gd"

# Salon : les cases devant l'escalier sont libres, la rampe et le mur bloquent.

func scene() -> String:
	return "ludo_house"

func start() -> Vector2i:
	return Vector2i(11, 11)

func test_ludo_stairs() -> void:
	if game == null:
		return
	await walk("devant l'escalier, sous le tapis", Vector2i(10, 9), false)
	await walk("devant l'escalier, dans le coin", Vector2i(9, 9), false)
	await hold_no_change("Haut devant l'escalier", "ui_up")
	await hold_no_change("Gauche dans le coin", "ui_left")
	shot("devant_escalier_salon")
	await walk("tapis d'escalier atteint", STAIR_MAT, false)
	await hold_no_change("Haut sur le tapis", "ui_up")
	await hold_no_change("Droite sur le tapis", "ui_right")
	await walk("tapis d'escalier quitte vers le bas", Vector2i(11, 11), false)
