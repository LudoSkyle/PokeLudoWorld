extends "res://tests/npc_lib.gd"

# PNJ qui bougent seuls : le chasseur d'insectes erre dans les herbes, le
# coureur boucle sur le chemin. Et le pecheur, immobile au bord de l'eau.

const ROUTE := [Vector2i(13, 16), Vector2i(26, 16), Vector2i(26, 9), Vector2i(25, 9),
	Vector2i(25, 15), Vector2i(14, 15), Vector2i(14, 9), Vector2i(13, 9)]

func cell_of(n: String) -> Vector2i:
	var p := npc(n).position
	return Vector2i(floori(p.x / 16.0), floori(p.y / 16.0))

func resting(n: String) -> bool:
	var p := npc(n).position
	return is_equal_approx(fmod(p.x, 16.0), 8.0) and is_equal_approx(fmod(p.y, 16.0), 8.0)

func test() -> void:
	var paths: TileMapLayer = level().get_node("Background/Paths")
	var grass: TileMapLayer = level().get_node("Background/Grass")

	# --- le coureur : un tour complet, le joueur reste au point de depart
	var next := 0
	var laps := 0
	var off_path := 0
	var lap_time := 0.0
	var t0 := Time.get_ticks_msec()
	var shot_done := false
	while laps == 0 and Time.get_ticks_msec() - t0 < 30000:
		await process_frame
		var c := cell_of("Runner")
		if paths.get_cell_source_id(c) == -1:
			off_path += 1
		if resting("Runner") and c == ROUTE[next]:
			next += 1
			if next == ROUTE.size():
				next = 0
				laps += 1
				lap_time = (Time.get_ticks_msec() - t0) / 1000.0
		if not shot_done and Time.get_ticks_msec() - t0 > 3000:
			shot("coureur"); shot_done = true
	check("coureur : passe par tous les points, dans l'ordre", laps == 1, "%d tour(s), point %d" % [laps, next])
	check("coureur : un tour en 16 a 20 s", lap_time > 16.0 and lap_time < 20.0, "%.1f s" % lap_time)
	check("coureur : ne quitte jamais le chemin", off_path == 0, "%d images hors chemin" % off_path)
	check("coureur : ses jambes suivent son allure", str(npc("Runner").get_node("Sprite").speed_scale) == "0.75", str(npc("Runner").get_node("Sprite").speed_scale))

	# --- on se met en travers : il attend, sans nous traverser
	await walk("coureur : on se plante sur sa voie", Vector2i(13, 12), false, [Vector2i(13, 9), Vector2i(13, 10), Vector2i(13, 11)])
	var closest := 999.0
	var guard := 0
	while guard < 6000 and not (cell_of("Runner") == Vector2i(13, 11) and resting("Runner")):
		await process_frame
		closest = minf(closest, npc("Runner").position.distance_to(player().position))
		guard += 1
	var t2 := Time.get_ticks_msec()
	while Time.get_ticks_msec() - t2 < 1500:
		await process_frame
		closest = minf(closest, npc("Runner").position.distance_to(player().position))
	check("coureur : s'arrete devant nous", cell_of("Runner") == Vector2i(13, 11), str(cell_of("Runner")))
	check("coureur : ne nous traverse pas", closest >= 15.9, "%.1f px" % closest)
	check("coureur : a l'arret il ne court plus sur place", anim("Runner") == "idle_down", anim("Runner"))
	shot("coureur_bloque")
	await tap("ui_up")
	Input.action_press("interact"); await wait(2); Input.action_release("interact")
	await wait(150)
	check("coureur : il nous parle", box().visible and box_text().to_lower().contains("tour du village"), box_text())
	check("coureur : il nous regarde", anim("Runner") == "idle_down", anim("Runner"))
	await close_box()
	await walk("coureur : on libere la voie", Vector2i(15, 12), false)
	await secs(0.5)
	check("coureur : il repart", cell_of("Runner") != Vector2i(13, 11), str(cell_of("Runner")))

	# --- on l'interpelle en pleine course : il finit son pas et repond
	await tap("ui_left")
	var spot := Vector2(14 * 16 + 8, 12 * 16 + 8)
	var t1 := Time.get_ticks_msec()
	var called := false
	while not called and Time.get_ticks_msec() - t1 < 40000:
		await process_frame
		var r := npc("Runner")
		# il remonte la colonne 14 et arrive sur la case que nous regardons
		if r.position.x == spot.x and r.position.y > spot.y and r.position.y - spot.y < 5.0:
			Input.action_press("interact"); await wait(2); Input.action_release("interact")
			called = true
	check("coureur : on l'interpelle alors qu'il court", called)
	await secs(1.5)
	check("coureur : il s'arrete et repond", box().visible and box_text().to_lower().contains("tour du village"), box_text())
	check("coureur : arrete sur la case devant nous", cell_of("Runner") == Vector2i(14, 12) and resting("Runner"), str(npc("Runner").position))
	check("coureur : tourne vers nous", anim("Runner") == "idle_right", anim("Runner"))
	shot("coureur_interpelle")
	await close_box()

	# --- le chasseur d'insectes : il erre, sans sortir des herbes
	# en jeu il attend 2 a 5 s entre deux gestes : on accelere pour le test
	npc("GrassWatcher").wander_pause = Vector2(0.05, 0.2)
	await walk("herbes : on s'y installe", Vector2i(8, 5), false)
	var seen := {}
	var outside := 0
	var turns := {}
	closest = 999.0
	var t3 := Time.get_ticks_msec()
	var shot2 := false
	while Time.get_ticks_msec() - t3 < 20000:
		await process_frame
		var c := cell_of("GrassWatcher")
		if grass.get_cell_source_id(c) == -1:
			outside += 1
		if resting("GrassWatcher"):
			seen[c] = true
			if anim("GrassWatcher").begins_with("idle_"):
				turns[anim("GrassWatcher")] = true
		closest = minf(closest, npc("GrassWatcher").position.distance_to(player().position))
		if not shot2 and Time.get_ticks_msec() - t3 > 8000:
			shot("herbes_errance"); shot2 = true
	check("herbes : il se deplace", seen.size() >= 6, "%d cases visitees" % seen.size())
	check("herbes : il ne sort jamais des herbes", outside == 0, "%d images dehors" % outside)
	check("herbes : il regarde de tous les cotes", turns.size() == 4, str(turns.keys()))
	check("herbes : il ne nous marche pas dessus", closest >= 15.9, "%.1f px" % closest)
	check("herbes : sa case est solide", not is_free(cell_of("GrassWatcher")) or not resting("GrassWatcher"))

	# --- le pecheur
	check("pecheur : regarde l'eau au repos", anim("Fisher") == "idle_right", anim("Fisher"))
	await talk("pecheur", Vector2i(40, 16), "ui_down", "Fisher", "mord", "idle_up")
	shot("pecheur")
	await secs(0.3)
	check("pecheur : le dialogue fini, il se retourne vers l'eau", anim("Fisher") == "idle_right", anim("Fisher"))
