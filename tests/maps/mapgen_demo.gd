extends "res://tests/lib.gd"

# La carte d'exemple du generateur (tools/mapgen/plans/demo_cove.toml) se joue : du pas de la porte au bout
# de la jetee, par la piste, l'escalier et la plage — a pied, sans teleportation.

func scene() -> String:
	return "demo_cove"

func start() -> Vector2i:
	return Vector2i(10, 9)

func test() -> void:
	check("la carte est chargee, et l'on part devant la maison", level() != null and cell() == Vector2i(10, 9), str(cell()))
	check("la mer et la falaise arretent : le bord du plateau et l'eau sont pleins", not is_free(Vector2i(3, 10)) and not is_free(Vector2i(21, 29)))
	await walk("par la piste jusqu'en haut de l'escalier", Vector2i(21, 14), false)
	shot("mapgen_plateau")
	await walk("l'escalier se descend jusqu'a la plage", Vector2i(21, 18), false)
	await walk("et la jetee se parcourt jusqu'au bout", Vector2i(21, 27), false)
	shot("mapgen_jetee")
	check("on parle au personnage pose par le plan", game.get_node_or_null(ENT + "Pecheur") != null and game.get_node_or_null(ENT + "Coureur") != null)
