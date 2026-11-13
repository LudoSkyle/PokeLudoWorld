extends "res://tests/lib.gd"

# Les PNJ sont solides, la case entre les gardes est libre.

func start() -> Vector2i:
	return Vector2i(9, 8)

func test() -> void:
	check("gardes : cases solides", not is_free(Vector2i(5, 7)) and not is_free(Vector2i(5, 9)))
	check("gardes : le milieu est libre", is_free(Vector2i(5, 8)))
	check("pecheur : case solide", not is_free(Vector2i(40, 17)))
	npc("GrassWatcher").movement = "static"
	check("chasseur : case solide", not is_free(Vector2i(8, 4)))
	await walk("on contourne le chasseur sans le traverser", Vector2i(9, 4), false)
	check("on n'est pas passe par sa case", cell() == Vector2i(9, 4))
