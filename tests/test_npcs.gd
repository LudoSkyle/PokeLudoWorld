extends "res://tests/lib.gd"

# PNJ du village : leur parler, et le passage garde a l'ouest.

const ENT := VP + "/Level/World/Entities/"

func npc(n: String) -> Node2D:
	return game.get_node(ENT + n)

func anim(n: String) -> String:
	return str(npc(n).get_node("Sprite").animation)

func box() -> Control:
	return game.get_node(VP + "/MessageBox/Control/Box")

func box_text() -> String:
	return game.get_node(VP + "/MessageBox/Control/Box/Text").text

func tap(action: String) -> void:
	Input.action_press(action); await wait(2); Input.action_release(action); await wait(8)

func close_box() -> void:
	var n := 0
	while box().visible and n < 12:
		Input.action_press("interact"); await wait(2); Input.action_release("interact"); await wait(60)
		n += 1

func talk(label: String, from: Vector2i, facing: String, who: String, expected: String, npc_anim: String) -> void:
	await walk(label + " : approche", from, false)
	await tap(facing)
	Input.action_press("interact"); await wait(2); Input.action_release("interact")
	await wait(150)
	check(label + " : la boite s'ouvre", box().visible)
	check(label + " : dit ce qu'il faut", box_text().to_lower().contains(expected), box_text())
	check(label + " : se tourne vers nous", anim(who) == npc_anim, anim(who))
	await close_box()
	check(label + " : la boite est refermee", not box().visible)
	check(label + " : on n'a pas bouge", cell() == from, str(cell()))

func test() -> void:
	shot("pnj_depart")
	# --- le chasseur d'insectes dans les hautes herbes
	check("herbes : le PNJ regarde vers le bas au repos", anim("GrassWatcher") == "idle_down", anim("GrassWatcher"))
	await talk("herbes, par le bas", Vector2i(8, 5), "ui_up", "GrassWatcher", "herbes", "idle_down")
	shot("pnj_herbes")
	await talk("herbes, par la gauche", Vector2i(7, 4), "ui_right", "GrassWatcher", "herbes", "idle_left")
	await walk("herbes : on ne traverse pas le PNJ", Vector2i(9, 4), false)
	check("herbes : sa case est solide", not is_free(Vector2i(8, 4)))

	# --- les deux gardes de la sortie ouest
	check("gardes : cases solides", not is_free(Vector2i(5, 7)) and not is_free(Vector2i(5, 9)))
	check("gardes : le milieu est libre", is_free(Vector2i(5, 8)))
	await talk("garde nord", Vector2i(6, 7), "ui_left", "GuardNorth", "passage", "idle_right")
	shot("pnj_gardes")
	await talk("garde sud", Vector2i(6, 9), "ui_left", "GuardSouth", "passage", "idle_right")

	# --- on tente de passer au milieu, touche maintenue
	await walk("devant le passage", Vector2i(6, 8), false)
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
