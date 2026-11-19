extends "res://tests/gdunit/game_suite.gd"

# Entrer par une porte : on arrive sur le paillasson de la piece, tourne vers l'interieur.

func start() -> Vector2i:
	return Vector2i(17, 5)

func test_enter() -> void:
	if game == null:
		return
	await walk("terrain->salle", Vector2i(17, 4), true)
	await arrival("salle", Vector2i(15, 14), "idle_up")
