extends "res://tests/lib.gd"

# Une grotte de glace inventee par le generateur (tools/mapgen/worlds/style_grotte_glace.toml, style `cave`, teinte
# `ice`), batie avec le decor a plateaux `cave_ice`. Ce qu'on controle : le sol bleu-gris et le verglas se foulent,
# **toute** la paroi arrete — son dessus pale comme sa face —, le vide arrete, les deux echelles ne bloquent pas,
# l'echelle qui monte est au pied d'une paroi de trois cases, et **le verglas barre un passage d'une paroi a l'autre** :
# ce qui est derriere ne s'atteint qu'en le traversant. Les coordonnees tiennent a la graine du monde (7) : si le
# generateur change, relire le plan avant de les corriger.

func scene() -> String:
	return "style_grotte_glace"

func start() -> Vector2i:
	return Vector2i(25, 37)

func test() -> void:
	check("la carte est chargee", level() != null and cell() == Vector2i(25, 37), str(cell()))
	set_hour(23.0)
	await wait(4)
	var tint := daylight()
	check("pas de nuit dans une grotte de glace", tint.r > 0.98 and tint.g > 0.98 and tint.b > 0.98, str(tint))
	check("le vide arrete", not is_free(Vector2i(2, 9)) and not is_free(Vector2i(49, 9)))
	check("la paroi du couloir arrete, des deux cotes", not is_free(Vector2i(23, 37)) and not is_free(Vector2i(27, 37)))
	check("le couloir fait trois cases", is_free(Vector2i(24, 37)) and is_free(Vector2i(25, 37)) and is_free(Vector2i(26, 37)))
	await walk("du couloir jusque dans la salle", Vector2i(30, 14), false)
	shot("glace_salle")
	check("un massif arrete tout entier : son dessus, ses cotes, sa face", not is_free(Vector2i(29, 17)) and not is_free(Vector2i(28, 16)) and not is_free(Vector2i(32, 18)) and not is_free(Vector2i(30, 19)))
	check("l'eperon arrete, dessus compris", not is_free(Vector2i(18, 14)) and not is_free(Vector2i(19, 16)) and not is_free(Vector2i(18, 18)))
	check("un caillou fonce arrete", not is_free(Vector2i(16, 13)))
	check("un pic n'arrete que par son pied", not is_free(Vector2i(11, 22)) and is_free(Vector2i(11, 21)))
	# le verglas : une plaque en travers du bras de l'ouest, des cases (9, 15) a (16, 19)
	var ice: Array = []
	for y in range(15, 20):
		for x in range(9, 17):
			ice.append(Vector2i(x, y))
	check("le verglas va d'une paroi a l'autre", not is_free(Vector2i(8, 17)) and is_free(Vector2i(9, 17)) and is_free(Vector2i(15, 17)) and not is_free(Vector2i(16, 17)))
	check("sans traverser le verglas, on n'atteint pas ce qu'il y a derriere", find_path(cell(), Vector2i(12, 11), ice).is_empty())
	await walk("jusque sur le verglas", Vector2i(12, 17), false)
	check("on marche sur le verglas", is_free(Vector2i(12, 17)) and cell() == Vector2i(12, 17), str(cell()))
	shot("glace_plaque")
	await walk("et derriere lui, jusqu'au pied de l'echelle qui monte", Vector2i(12, 10), false)
	check("l'echelle qui monte n'arrete pas : on monte dessus", is_free(Vector2i(12, 10)) and cell() == Vector2i(12, 10), str(cell()))
	check("elle est au pied d'une paroi de trois cases : deux de face, puis son dessus", not is_free(Vector2i(12, 9)) and not is_free(Vector2i(12, 8)) and not is_free(Vector2i(12, 7)))
	shot("glace_echelle_haut")
	await walk("jusqu'au trou a echelle", Vector2i(19, 27), false)
	check("l'echelle qui descend n'arrete pas, ni ses voisines", is_free(Vector2i(19, 27)) and is_free(Vector2i(18, 27)) and is_free(Vector2i(20, 27)))
	shot("glace_echelle_bas")
	# un caillou rond sur le tour de la grotte, en (28, 31) : il est sur la paroi, pas au sol
	await walk("jusqu'au bord de la salle, sous un caillou rond du tour", Vector2i(26, 31), false)
	check("le caillou rond du tour est sur la paroi : on n'y va pas", not is_free(Vector2i(27, 31)) and not is_free(Vector2i(28, 31)) and not is_free(Vector2i(29, 31)))
	shot("glace_tour")
	await walk("et retour a la sortie", Vector2i(25, 37), false)
