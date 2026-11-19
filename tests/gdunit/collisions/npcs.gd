extends "res://tests/gdunit/game_suite.gd"

# Les PNJ sont solides, la case entre les gardes est libre.

func start() -> Vector2i:
	return Vector2i(8, 9)

func test_npcs() -> void:
	if game == null:
		return
	check("gardes : cases solides", not is_free(Vector2i(1, 1)) and not is_free(Vector2i(1, 3)))
	check("gardes : le milieu est libre", is_free(Vector2i(1, 2)))
	check("pecheur : case solide", not is_free(Vector2i(4, 13)))
	npc("GrassWatcher").movement = "static"
	check("chasseur : case solide", not is_free(Vector2i(8, 7)))
	await walk("on contourne le chasseur sans le traverser", Vector2i(8, 5), false)
	check("on est passe de l'autre cote", cell() == Vector2i(8, 5))
