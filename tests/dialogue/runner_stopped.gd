extends "res://tests/lib.gd"

# Le coureur, arrete devant nous sur sa voie : on lui parle.

func start() -> Vector2i:
	return Vector2i(13, 12)

func test() -> void:
	var t0 := Time.get_ticks_msec()
	while Time.get_ticks_msec() - t0 < 5000 and not (cell_of("Runner") == Vector2i(13, 11) and resting("Runner")):
		await process_frame
	await secs(0.3)
	check("il s'est arrete devant nous", cell_of("Runner") == Vector2i(13, 11), str(cell_of("Runner")))
	await talk("coureur", Vector2i(13, 12), "ui_up", "Runner", "tour du village", "idle_down")
