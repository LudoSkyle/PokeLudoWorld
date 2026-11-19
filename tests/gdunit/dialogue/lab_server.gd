extends "res://tests/gdunit/game_suite.gd"

# Le serveur du labo.

func scene() -> String:
	return "lab_house"

func start() -> Vector2i:
	return Vector2i(9, 8)

func test_lab_server() -> void:
	if game == null:
		return
	await examine("serveur", Vector2i(9, 8), "serveur")
