extends "res://tests/lib.gd"

# Le chasseur d'insectes erre sans sortir des herbes ni nous marcher dessus.

func start() -> Vector2i:
	return Vector2i(8, 5)

func test() -> void:
	var grass: TileMapLayer = level().get_node("Background/Grass")
	# en jeu il attend 2 a 5 s entre deux gestes : on accelere pour le test
	npc("GrassWatcher").wander_pause = Vector2(0.05, 0.2)
	var seen := {}
	var outside := 0
	var turns := {}
	var closest := 999.0
	var t0 := Time.get_ticks_msec()
	var shot_done := false
	while Time.get_ticks_msec() - t0 < 15000:
		await process_frame
		var c := cell_of("GrassWatcher")
		if grass.get_cell_source_id(c) == -1:
			outside += 1
		if resting("GrassWatcher"):
			seen[c] = true
			if anim("GrassWatcher").begins_with("idle_"):
				turns[anim("GrassWatcher")] = true
		closest = minf(closest, npc("GrassWatcher").position.distance_to(player().position))
		if not shot_done and Time.get_ticks_msec() - t0 > 6000:
			shot("herbes_errance"); shot_done = true
	check("il se deplace", seen.size() >= 5, "%d cases visitees" % seen.size())
	check("il ne sort jamais des herbes", outside == 0, "%d images dehors" % outside)
	check("il regarde de tous les cotes", turns.size() == 4, str(turns.keys()))
	check("il ne nous marche pas dessus", closest >= 15.9, "%.1f px" % closest)
