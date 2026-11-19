extends "res://tests/gdunit/game_suite.gd"

# La poubelle du labo.

func scene() -> String:
	return "lab_house"

func start() -> Vector2i:
	return Vector2i(13, 8)

func test_lab_bin() -> void:
	if game == null:
		return
	await examine("poubelle", Vector2i(13, 8), "poubelle est vide")
