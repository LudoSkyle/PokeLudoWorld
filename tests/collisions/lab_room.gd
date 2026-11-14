extends "res://tests/lib.gd"

# Labo : la machine bloque, les allees et le fond se parcourent.

func scene() -> String:
	return "lab_house"

func start() -> Vector2i:
	return Vector2i(15, 15)

func test() -> void:
	await walk("devant la machine", Vector2i(15, 13), false)
	await hold_no_change("Haut contre la machine", "ui_up")
	shot("labo_machine")
	await walk("fond de la salle", Vector2i(19, 7), false)
	shot("labo_fond")
	await walk("derriere le dome de la machine", Vector2i(15, 9), false)
	shot("labo_derriere_machine")
	await hold_no_change("Bas contre la machine, depuis derriere", "ui_down")
	check("le corps de la machine bloque toujours", not is_free(Vector2i(15, 10)) and not is_free(Vector2i(16, 10)) and not is_free(Vector2i(14, 11)))
	await walk("sur les feuilles", Vector2i(11, 9), false)
	await walk("allee de gauche", Vector2i(13, 12), false)
	await walk("derriere les bibliotheques du milieu", Vector2i(10, 12), false)
	shot("labo_derriere_etageres")
	check("leur rangee du bas bloque toujours", not is_free(Vector2i(10, 13)) and not is_free(Vector2i(21, 13)))
	await walk("retour au paillasson", Vector2i(16, 15), false)
