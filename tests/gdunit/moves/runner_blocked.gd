extends "res://tests/gdunit/game_suite.gd"

# On se plante sur la voie du coureur : il attend, puis repart.

func start() -> Vector2i:
	return Vector2i(19, 9)

func test_runner_blocked() -> void:
	if game == null:
		return
	var closest := 999.0
	var t0 := ticks()
	while ticks() - t0 < 3000:
		await get_tree().process_frame
		closest = minf(closest, npc("Runner").position.distance_to(player().position))
	check("s'arrete devant nous", cell_of("Runner") == Vector2i(19, 8) and resting("Runner"), str(cell_of("Runner")))
	check("ne nous traverse pas", closest >= 15.9, "%.1f px" % closest)
	check("a l'arret il ne court plus sur place", anim("Runner") == "idle_down", anim("Runner"))
	shot("coureur_bloque")
	await walk("on libere la voie", Vector2i(20, 9), false)
	await secs(0.8)
	check("il repart", cell_of("Runner") != Vector2i(19, 8), str(cell_of("Runner")))
