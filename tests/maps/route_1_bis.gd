extends "res://tests/lib.gd"

# La Route 1 refaite par le constructeur a partir de son plan (tools/mapgen/plans/route_1_bis.toml) se joue comme
# l'originale : les ponts, la terrasse et ses escaliers, les rebords.

func scene() -> String:
	return "route_1_bis"

func start() -> Vector2i:
	return Vector2i(45, 47)

func test() -> void:
	check("la carte est chargee", level() != null and cell() == Vector2i(45, 47), str(cell()))
	await walk("par le pont du milieu", Vector2i(22, 36), false)
	await walk("et le pont du nord jusqu'a la sortie du nord", Vector2i(15, 2), false)
	await walk("retour, puis la terrasse de l'est par son escalier", Vector2i(51, 31), false)
	shot("route_1_bis_terrasse")
	await walk("jusqu'a la sortie de l'est", Vector2i(66, 36), false)
