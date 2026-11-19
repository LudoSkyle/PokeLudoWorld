extends "res://tests/gdunit/game_suite.gd"

# Monter a l'etage ne reannonce pas la maison : c'est le meme lieu.

func scene() -> String:
	return "ludo_house"

func start() -> Vector2i:
	return Vector2i(11, 8)

func test_banner_same_place() -> void:
	if game == null:
		return
	await secs(3.5)
	check("le bandeau de la maison est remonte", not banner().visible)
	await hold_until_change("on monte", "ui_left")
	var r: Array = await watch_banner(2.5)
	check("meme lieu, pas de bandeau", not r[0], str(r))
