extends "res://tests/gdunit/game_suite.gd"

# Un village invente par le generateur (tools/mapgen/worlds/style_village.toml, style `village`) se joue : de la
# sortie du sud a la placette, devant la porte de la mairie et de chaque maison, au bord d'un etang, puis
# jusqu'a la sortie de l'est. Les lampadaires, les massifs clotures et l'etang arretent ; la placette se foule.

func scene() -> String:
	return "style_village"

func start() -> Vector2i:
	return Vector2i(23, 39)

func test_worldgen_village() -> void:
	if game == null:
		return
	check("la carte est chargee", level() != null and cell() == Vector2i(23, 39), str(cell()))
	check("un lampadaire arrete", not is_free(Vector2i(20, 19)) and not is_free(Vector2i(28, 25)))
	check("la cloture d'un massif arrete", not is_free(Vector2i(15, 11)))
	await walk("jusque sur la placette", Vector2i(24, 22), false)
	shot("village_placette")
	await walk("devant la porte de la mairie", Vector2i(23, 13), false)
	shot("village_mairie")
	await walk("devant la maison de l'ouest", Vector2i(11, 15), false)
	await walk("au bord de l'etang", Vector2i(11, 20), false)
	shot("village_etang")
	check("l'etang arrete", not is_free(Vector2i(12, 20)) and not is_free(Vector2i(15, 20)))
	await walk("devant la maison du sud-ouest", Vector2i(11, 30), false)
	await walk("devant la maison du sud-est", Vector2i(35, 31), false)
	await walk("devant la maison de l'est", Vector2i(35, 14), false)
	await walk("et jusqu'a la sortie de l'est", Vector2i(45, 19), false)
	shot("village_est")
