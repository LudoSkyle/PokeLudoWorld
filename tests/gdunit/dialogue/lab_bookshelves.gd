extends "res://tests/gdunit/game_suite.gd"

# Les bibliotheques du labo, au fond et au milieu.

func scene() -> String:
	return "lab_house"

func start() -> Vector2i:
	return Vector2i(21, 8)

func test_lab_bookshelves() -> void:
	if game == null:
		return
	await examine("bibliotheque du fond", Vector2i(21, 8), "bibliothèque")
	await examine("bibliotheque du milieu", Vector2i(11, 14), "bibliothèque")
