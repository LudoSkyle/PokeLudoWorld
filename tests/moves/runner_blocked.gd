extends "res://tests/lib.gd"

# On se plante sur la voie du coureur : il attend, puis repart.

func start() -> Vector2i:
	return Vector2i(13, 12)

func test() -> void:
	var closest := 999.0
	var t0 := Time.get_ticks_msec()
	while Time.get_ticks_msec() - t0 < 3000:
		await process_frame
		closest = minf(closest, npc("Runner").position.distance_to(player().position))
	check("s'arrete devant nous", cell_of("Runner") == Vector2i(13, 11) and resting("Runner"), str(cell_of("Runner")))
	check("ne nous traverse pas", closest >= 15.9, "%.1f px" % closest)
	check("a l'arret il ne court plus sur place", anim("Runner") == "idle_down", anim("Runner"))
	shot("coureur_bloque")
	await walk("on libere la voie", Vector2i(14, 12), false)
	await secs(0.8)
	check("il repart", cell_of("Runner") != Vector2i(13, 11), str(cell_of("Runner")))
