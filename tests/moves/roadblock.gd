extends "res://tests/lib.gd"

# Le passage garde : on s'engage entre les gardes touche tenue, on est repousse.

func start() -> Vector2i:
	return Vector2i(6, 8)

func test() -> void:
	var home: Vector2 = npc("GuardNorth").position
	var min_x := 99
	var saw_guard_in_gap := false
	Input.action_press("ui_left")
	for i in 260:
		await process_frame
		min_x = mini(min_x, cell().x)
		if npc("GuardNorth").position.distance_to(Vector2(88, 136)) < 1.0:
			saw_guard_in_gap = true
		if i == 130:
			shot("pnj_refoulement")
	check("passage : on entre bien sur la case du milieu", min_x == 5, "x min %d" % min_x)
	check("passage : on ne depasse jamais les gardes", min_x >= 5)
	check("passage : le garde prend notre place", saw_guard_in_gap)
	check("passage : le garde parle", box().visible and box_text().to_lower().contains("passage"), box_text())
	check("passage : on a recule d'une case", cell() == Vector2i(6, 8), str(cell()))
	check("passage : on regarde toujours vers l'ouest", str(player().get_node("Sprite").animation) == "idle_left", str(player().get_node("Sprite").animation))
	check("passage : le garde nous fait face", anim("GuardNorth") == "idle_right", anim("GuardNorth"))
	# Gauche est toujours enfoncee pendant qu'on ferme la boite
	await close_box()
	await wait(90)
	check("passage : le garde a repris sa place", npc("GuardNorth").position.distance_to(home) < 0.5, str(npc("GuardNorth").position))
	check("passage : touche tenue, la scene ne repart pas", cell() == Vector2i(6, 8) and not box().visible, str(cell()))
	Input.action_release("ui_left")
	await wait(20)
	shot("pnj_apres")
	# une nouvelle pression relance la scene
	Input.action_press("ui_left")
	await wait(200)
	Input.action_release("ui_left")
	check("passage : une nouvelle tentative relance la scene", box().visible and cell() == Vector2i(6, 8), str(cell()))
	await close_box()
	await wait(90)
	await walk("on repart librement", Vector2i(9, 8), false)
