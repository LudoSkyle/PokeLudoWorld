extends "res://tests/lib.gd"

# Chambre : le coussin, et les cases devant la cage d'escalier.

func scene() -> String:
	return "ludo_bedroom"

func start() -> Vector2i:
	return Vector2i(11, 8)

func test() -> void:
	await walk("sur le coussin", Vector2i(13, 11), false)
	await walk("devant la cage, sous le tapis", Vector2i(10, 9), false)
	await walk("devant la cage, dans le coin", Vector2i(9, 9), false)
	await hold_no_change("Haut devant la cage", "ui_up")
	await hold_no_change("Gauche dans le coin", "ui_left")
	shot("devant_cage_chambre")
	await walk("retour au tapis d'escalier", STAIR_MAT, false)
