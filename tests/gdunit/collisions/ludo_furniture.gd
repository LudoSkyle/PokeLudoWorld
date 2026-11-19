extends "res://tests/gdunit/game_suite.gd"

# Salon : on monte sur le tabouret, on passe derriere la plante.

func scene() -> String:
	return "ludo_house"

func start() -> Vector2i:
	return Vector2i(15, 14)

func test_ludo_furniture() -> void:
	if game == null:
		return
	await walk("sur le tabouret", Vector2i(13, 11), false)
	await walk("derriere la plante", Vector2i(9, 13), false)
