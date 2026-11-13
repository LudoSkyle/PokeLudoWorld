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
	await walk("sur les feuilles", Vector2i(11, 9), false)
	await walk("allee de gauche", Vector2i(13, 12), false)
	await walk("retour au paillasson", Vector2i(16, 15), false)
