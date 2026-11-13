extends "res://tests/lib.gd"

# Monter l'escalier du salon.

func scene() -> String:
	return "ludo_house"

func start() -> Vector2i:
	return Vector2i(11, 8)

func test() -> void:
	await face_left_and_shoot("pied_escalier_salon")
	await hold_until_change("Gauche sur le tapis d'escalier", "ui_left")
	await arrival("chambre", STAIR_MAT, "idle_right")
	await face_left_and_shoot("haut_escalier_chambre")
