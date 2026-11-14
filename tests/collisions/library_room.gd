extends "res://tests/lib.gd"

# Bibliotheque : les allees entre les rayonnages, la table, le paillasson.

func scene() -> String:
	return "library"

func start() -> Vector2i:
	return Vector2i(15, 14)

func test() -> void:
	await walk("sous la fenetre, entre les rayonnages du fond", Vector2i(15, 8), false)
	await walk("l'allee de gauche, le long du mur", Vector2i(9, 11), false)
	await walk("derriere le feuillage de la plante", Vector2i(9, 13), false)
	await walk("sur un tabouret", Vector2i(10, 14), false)
	await walk("derriere la table de lecture", Vector2i(11, 12), false)
	await walk("devant le bureau", Vector2i(22, 12), false)
	check("un rayonnage du milieu bloque", not is_free(Vector2i(12, 11)) and not is_free(Vector2i(17, 10)))
	check("le pot de la plante bloque", not is_free(Vector2i(9, 14)) and not is_free(Vector2i(22, 14)))
	await walk("2e case du paillasson", Vector2i(16, 14), false)
