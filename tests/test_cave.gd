extends "res://tests/lib.gd"

# Grotte : 1er niveau, deux sous-sols par les tunnels, retour et sortie.

func test() -> void:
	# --- la grotte : 1er niveau, deux sous-sols, et retour par l'autre tunnel
	await walk("village->grotte", Vector2i(38, 2), true)
	await arrival("grotte 1F", Vector2i(14, 19), "idle_up")
	shot("grotte_1f_entree")
	await walk("1F : derriere une crete", Vector2i(8, 9), false)
	await walk("1F : sur le sol sombre", Vector2i(4, 14), false)
	await walk("1F : au pied du tunnel A", Vector2i(4, 4), false)
	shot("grotte_1f_tunnel")
	# Haut maintenu dans le tunnel : on descend UNE fois, sans rebrousser chemin
	var last2 := level_id()
	var changes2 := 0
	Input.action_press("ui_up")
	for i in 600:
		await process_frame
		if level_id() != last2 and level_id() != -1:
			changes2 += 1
			last2 = level_id()
	Input.action_release("ui_up")
	await wait(20)
	check("Haut maintenu dans le tunnel : un seul changement", changes2 == 1, "%d changement(s)" % changes2)
	await arrival("grotte B1F ouest", Vector2i(4, 4), "idle_down")
	shot("grotte_b1f")
	await walk("B1F -> tunnel C", Vector2i(11, 10), true)
	await arrival("grotte B2F ouest", Vector2i(6, 4), "idle_down")
	await walk("B2F : bord du lac", Vector2i(14, 7), false)
	await hold_no_change("B2F : Bas contre le lac", "ui_down")
	shot("grotte_b2f_lac")
	await walk("B2F : tour du lac par le sud", Vector2i(15, 15), false)
	await walk("B2F -> tunnel D", Vector2i(23, 3), true)
	await arrival("grotte B1F est", Vector2i(22, 13), "idle_down")
	await walk("B1F -> tunnel B", Vector2i(20, 4), true)
	await arrival("grotte 1F est", Vector2i(25, 4), "idle_down")
	await walk("1F : vers la sortie", Vector2i(15, 19), false)
	await hold_until_change("1F : Bas dans le couloir de sortie", "ui_down")
	await arrival("village devant la grotte", Vector2i(38, 3), "idle_down")
	shot("village_grotte")
