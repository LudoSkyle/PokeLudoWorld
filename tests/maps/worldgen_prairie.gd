extends "res://tests/lib.gd"

# Une carte inventee par le generateur (tools/mapgen/worlds/prairie.toml), assemblee par le constructeur, se
# joue : de la sortie du nord a la porte de la cabane, puis jusqu'a la sortie de l'est — a pied.

func scene() -> String:
	return "prairie"

func start() -> Vector2i:
	return Vector2i(32, 2)

func test() -> void:
	check("la carte est chargee", level() != null and cell() == Vector2i(32, 2), str(cell()))
	await walk("par la piste jusque devant la cabane", Vector2i(34, 20), false)
	shot("prairie_cabane")
	await walk("et jusqu'a la sortie de l'est", Vector2i(61, 35), false)
	shot("prairie_est")
