extends "res://tests/lib.gd"

# Une grotte inventee par le generateur (tools/mapgen/worlds/style_grotte.toml, style `cave`) se joue : du couloir
# de sortie a la salle, autour d'un massif de roche, au bord d'un bassin, de l'autre cote de l'eperon qui coupe la
# salle, et devant les objets caches au fond. Le vide, la paroi, les massifs, l'eau et les rochers arretent ; la
# grotte ne prend pas la teinte de la nuit.

func scene() -> String:
	return "style_grotte"

func start() -> Vector2i:
	return Vector2i(28, 37)

func test() -> void:
	check("la carte est chargee", level() != null and cell() == Vector2i(28, 37), str(cell()))
	set_hour(23.0)
	await wait(4)
	var tint := daylight()
	check("pas de nuit dans une grotte", tint.r > 0.98 and tint.g > 0.98 and tint.b > 0.98, str(tint))
	check("le vide arrete", not is_free(Vector2i(2, 2)) and not is_free(Vector2i(45, 36)))
	check("la paroi du couloir arrete, des deux cotes", not is_free(Vector2i(26, 36)) and not is_free(Vector2i(30, 36)))
	check("le couloir fait trois cases", is_free(Vector2i(27, 36)) and is_free(Vector2i(28, 36)) and is_free(Vector2i(29, 36)))
	await walk("du couloir jusque dans la salle", Vector2i(28, 29), false)
	shot("grotte_entree")
	check("un massif de roche arrete, par tout son tour", not is_free(Vector2i(18, 21)) and not is_free(Vector2i(15, 23)) and not is_free(Vector2i(20, 23)) and not is_free(Vector2i(18, 24)))
	check("une stalagmite arrete", not is_free(Vector2i(18, 20)))
	await walk("autour du massif", Vector2i(18, 19), false)
	shot("grotte_massif")
	await walk("jusqu'au bord d'un bassin", Vector2i(19, 12), false)
	shot("grotte_bassin")
	check("le bassin arrete", not is_free(Vector2i(20, 12)) and not is_free(Vector2i(22, 13)))
	check("l'eperon arrete, de ses flancs a son bout", not is_free(Vector2i(26, 10)) and not is_free(Vector2i(28, 10)) and not is_free(Vector2i(25, 15)) and not is_free(Vector2i(27, 17)))
	await walk("a l'ouest de l'eperon, jusque devant un objet", Vector2i(17, 8), false)
	shot("grotte_objet")
	check("l'objet est la, dans un coin de la paroi", not is_free(Vector2i(16, 8)))
	await walk("a l'est de l'eperon, en le contournant par le bas", Vector2i(30, 10), false)
	shot("grotte_eperon")
	check("un gros bloc arrete, sur ses quatre cases", not is_free(Vector2i(42, 17)) and not is_free(Vector2i(43, 17)) and not is_free(Vector2i(42, 16)) and not is_free(Vector2i(43, 16)))
	await walk("jusqu'au fond, devant le dernier objet", Vector2i(35, 6), false)
	shot("grotte_fond")
	check("il est la", not is_free(Vector2i(36, 6)))
	await walk("et retour a la sortie", Vector2i(28, 37), false)
