extends "res://tests/gdunit/game_suite.gd"

# Le coureur, arrete devant nous sur sa voie : on lui parle.

func start() -> Vector2i:
	return Vector2i(19, 9)

func test_runner_stopped() -> void:
	if game == null:
		return
	var t0 := ticks()
	while ticks() - t0 < 5000 and not (cell_of("Runner") == Vector2i(19, 8) and resting("Runner")):
		await get_tree().process_frame
	await secs(0.3)
	check("il s'est arrete devant nous", cell_of("Runner") == Vector2i(19, 8), str(cell_of("Runner")))
	await talk("coureur", Vector2i(19, 9), "ui_up", "Runner", "tour du village", "idle_down")
