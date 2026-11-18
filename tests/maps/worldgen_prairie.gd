extends "res://tests/lib.gd"

# Une carte inventee par le generateur (tools/mapgen/worlds/prairie.toml), assemblee par le constructeur, se
# joue : de la sortie du nord a la porte de la cabane, au bord de l'etang — une eau a plat, qui arrete —, puis
# jusqu'a la sortie de l'est, a pied.

func scene() -> String:
	return "prairie"

func start() -> Vector2i:
	return Vector2i(25, 2)

func test() -> void:
	check("la carte est chargee", level() != null and cell() == Vector2i(25, 2), str(cell()))
	await walk("par la piste jusque devant la cabane", Vector2i(34, 20), false)
	shot("prairie_cabane")
	await walk("jusqu'a la rive de l'etang", Vector2i(46, 19), false)
	shot("prairie_etang")
	check("la berge de l'etang arrete", not is_free(Vector2i(47, 19)))
	check("son eau aussi", not is_free(Vector2i(52, 19)))
	await walk("jusqu'au pied du rebord de l'allee de cote", Vector2i(27, 32), false)
	shot("prairie_rebord")
	check("le rebord arrete a pied", not is_free(Vector2i(28, 32)))
	check("et l'on en fait le tour", not find_path(Vector2i(27, 32), Vector2i(29, 32)).is_empty())
	await walk("et jusqu'a la sortie de l'est", Vector2i(61, 29), false)
	shot("prairie_est")
