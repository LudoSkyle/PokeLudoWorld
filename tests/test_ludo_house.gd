extends "res://tests/lib.gd"

# Maison de Ludo : entree touche tenue, paillasson, tele, escalier, chambre, sortie.

func test() -> void:
	# --- maison de Ludo (en bas a gauche) : on entre SANS relacher Haut,
	#     et le personnage doit continuer d'avancer dans la piece
	await walk("vers la porte de Ludo", Vector2i(8, 16), false)
	var id0 := level_id()
	Input.action_press("ui_up")
	var g := 0
	while g < 400 and level_id() == id0:
		await process_frame
		g += 1
	check("Haut tenu : on entre chez Ludo", level_id() != id0)
	await wait(120)
	Input.action_release("ui_up")
	await wait(30)
	check("Haut tenu : on continue d'avancer dans la piece", cell().y < EXIT_MAT.y and cell().x == EXIT_MAT.x, str(cell()))
	await walk("retour sur le paillasson", EXIT_MAT, false, [Vector2i(14, 14), Vector2i(16, 14)])
	shot("salon")

	# --- la tele : une emission au hasard, jamais la meme liste vide
	await examine("tele du salon", Vector2i(17, 9), " ")
	await examine("tele du salon, 2e fois", Vector2i(18, 9), " ")

	await walk("paillasson traverse vers la droite", Vector2i(17, 14), false)
	await walk("paillasson traverse vers la gauche", Vector2i(13, 14), false)
	await walk("paillasson atteint par le haut", EXIT_MAT, false, [Vector2i(14, 14), Vector2i(16, 14)])

	await walk("sur le tabouret", Vector2i(13, 11), false)
	await walk("derriere la plante", Vector2i(9, 13), false)

	# --- escalier qui monte
	await walk("devant l'escalier, sous le tapis", Vector2i(10, 9), false)
	await walk("devant l'escalier, dans le coin", Vector2i(9, 9), false)
	await hold_no_change("Haut devant l'escalier (salon)", "ui_up")
	await hold_no_change("Gauche dans le coin (salon)", "ui_left")
	shot("devant_escalier_salon")
	await walk("tapis d'escalier atteint", STAIR_MAT, false)
	await hold_no_change("Haut sur le tapis (salon)", "ui_up")
	await hold_no_change("Droite sur le tapis (salon)", "ui_right")
	await walk("tapis d'escalier quitte vers le bas", Vector2i(11, 11), false)
	await walk("tapis d'escalier de nouveau", STAIR_MAT, false)
	await face_left_and_shoot("pied_escalier_salon")
	await hold_until_change("Gauche sur le tapis d'escalier", "ui_left")
	await arrival("chambre", STAIR_MAT, "idle_right")
	await face_left_and_shoot("haut_escalier_chambre")

	# --- escalier qui descend
	await walk("sur le coussin", Vector2i(13, 11), false)
	await walk("devant la cage, sous le tapis", Vector2i(10, 9), false)
	await walk("devant la cage, dans le coin", Vector2i(9, 9), false)
	await hold_no_change("Haut devant la cage (chambre)", "ui_up")
	await hold_no_change("Gauche dans le coin (chambre)", "ui_left")
	shot("devant_cage_chambre")

	await walk("retour au tapis d'escalier", STAIR_MAT, false)
	var last := level_id()
	var changes := 0
	Input.action_press("ui_left")
	for i in 600:
		await process_frame
		if level_id() != last and level_id() != -1:
			changes += 1
			last = level_id()
	Input.action_release("ui_left")
	await wait(20)
	check("Gauche maintenu dans l'escalier : un seul changement", changes == 1, "%d changement(s)" % changes)
	await arrival("salon par l'escalier", STAIR_MAT, "idle_right")

	await walk("vers le paillasson", EXIT_MAT, false)
	await hold_until_change("Bas sur le paillasson", "ui_down")
	await arrival("village devant chez Ludo", Vector2i(8, 16), "idle_down")
