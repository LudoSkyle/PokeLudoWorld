extends "res://tests/gdunit/game_suite.gd"

# Des champs inventes par le generateur (tools/mapgen/worlds/style_champs.toml, style `fields`) se jouent : de la
# sortie du sud au portillon d'un champ, dans ses allees jusqu'au fond de la derniere, devant l'objet qu'elle
# garde, puis dans un second champ, et jusqu'a la sortie du nord. Le ble et la cloture arretent.

func scene() -> String:
	return "style_champs"

func start() -> Vector2i:
	return Vector2i(29, 55)

func test_worldgen_champs() -> void:
	if game == null:
		return
	check("la carte est chargee", level() != null and cell() == Vector2i(29, 55), str(cell()))
	check("la cloture d'un champ arrete", not is_free(Vector2i(10, 34)) and not is_free(Vector2i(22, 45)))
	check("son portillon se franchit", is_free(Vector2i(15, 34)) and is_free(Vector2i(16, 34)))
	check("le ble arrete", not is_free(Vector2i(16, 39)))
	await walk("jusque devant le portillon du champ du sud-ouest", Vector2i(15, 33), false)
	shot("champs_portillon")
	await walk("dans le champ, par ses allees, jusqu'au fond de la derniere", Vector2i(20, 44), false)
	shot("champs_fond")
	check("l'objet est la, au bout de l'allee", not is_free(Vector2i(21, 44)))
	await walk("dans le champ du nord-ouest, jusque devant son objet", Vector2i(13, 11), false)
	shot("champs_nord_ouest")
	await walk("et jusqu'a la sortie du nord", Vector2i(28, 2), false)
