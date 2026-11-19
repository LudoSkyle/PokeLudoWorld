extends "res://tests/gdunit/game_suite.gd"

# La Route 1 refaite par le generateur (tools/mapgen/plans/route_2.toml) se parcourt : du sud au nord par les
# deux ponts, la terrasse de l'est par ses escaliers de pierre, et ses rebords se sautent dans un seul sens.

func scene() -> String:
	return "route_2"

func start() -> Vector2i:
	return Vector2i(45, 47)

func press(action: String, t: float) -> void:
	Input.action_press(action)
	await secs(t)
	Input.action_release(action)
	await secs(0.6)

func test_mapgen_route_2() -> void:
	if game == null:
		return
	check("la carte est chargee", level() != null and cell() == Vector2i(45, 47), str(cell()))
	check("le bord de la terrasse arrete : on n'y monte pas a cote de l'escalier", not is_free(Vector2i(60, 33)) and not is_free(Vector2i(47, 32)))
	await walk("au pied de l'escalier de pierre", Vector2i(51, 36), false)
	await walk("on monte sur la terrasse par ses marches", Vector2i(51, 31), false)
	shot("route_2_terrasse")
	await walk("et l'on en redescend par l'autre escalier", Vector2i(57, 36), false)
	await walk("a l'ouest du rebord", Vector2i(45, 36), false)
	await press("ui_right", 0.5)
	check("le rebord se saute vers l'est : on retombe une case plus loin", cell().x >= 47 and cell().y == 36, str(cell()))
	shot("route_2_rebord")
	await walk("contre le rebord, de l'autre cote", Vector2i(47, 36), false)
	await press("ui_left", 0.5)
	check("et pas dans l'autre sens", cell() == Vector2i(47, 36), str(cell()))
	await walk("par les deux ponts jusqu'a la sortie du nord", Vector2i(15, 2), false)
