extends "res://tests/lib.gd"

# Le coureur fait un tour complet du chemin, sans le quitter.

func test() -> void:
	var route := [Vector2i(19, 12), Vector2i(22, 12), Vector2i(22, 6), Vector2i(21, 6),
		Vector2i(21, 11), Vector2i(20, 11), Vector2i(20, 6), Vector2i(19, 6)]
	var paths: TileMapLayer = level().get_node("Background/Paths")
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
		if resting("Runner") and c == route[next]:
			next += 1
			if next == route.size():
				next = 0
				laps += 1
				lap_time = (Time.get_ticks_msec() - t0) / 1000.0
		if not shot_done and Time.get_ticks_msec() - t0 > 3000:
			shot("coureur"); shot_done = true
	check("passe par tous les points, dans l'ordre", laps == 1, "%d tour(s), point %d" % [laps, next])
	check("un tour en 8 a 12 s", lap_time > 8.0 and lap_time < 12.0, "%.1f s" % lap_time)
	check("ne quitte jamais le chemin", off_path == 0, "%d images hors chemin" % off_path)
	check("ses jambes suivent son allure", str(npc("Runner").get_node("Sprite").speed_scale) == "0.75", str(npc("Runner").get_node("Sprite").speed_scale))
