extends "res://tests/gdunit/game_suite.gd"

# Une route de montagne inventee par le generateur (tools/mapgen/worlds/style_montagne.toml, style `mountain`) se
# joue : de la sortie du sud a celle du nord, en montant trois terrasses par leurs escaliers de pierre. Le bord
# d'une terrasse arrete, de part et d'autre de l'escalier ; les marches, elles, se foulent.

func scene() -> String:
	return "style_montagne"

func start() -> Vector2i:
	return Vector2i(22, 63)

func test_worldgen_montagne() -> void:
	if game == null:
		return
	check("la carte est chargee", level() != null and cell() == Vector2i(22, 63), str(cell()))
	check("le bord de la premiere terrasse arrete, a gauche de l'escalier", not is_free(Vector2i(10, 43)))
	check("et a droite", not is_free(Vector2i(18, 43)))
	check("ses marches se foulent", is_free(Vector2i(14, 43)))
	await walk("au pied du premier escalier", Vector2i(14, 45), false)
	shot("montagne_escalier_1")
	await walk("sur la premiere terrasse", Vector2i(14, 41), false)
	check("la deuxieme terrasse ne s'atteint que par son escalier", not is_free(Vector2i(22, 32)) and not is_free(Vector2i(30, 32)) and is_free(Vector2i(26, 32)))
	await walk("sur la deuxieme terrasse", Vector2i(26, 30), false)
	shot("montagne_terrasse_2")
	await walk("sur la troisieme", Vector2i(27, 19), false)
	await walk("et jusqu'a la sortie du nord", Vector2i(21, 2), false)
	shot("montagne_nord")
