extends "res://tests/gdunit/game_suite.gd"

# Courir ne casse ni les portes ni les passages gardes.

func start() -> Vector2i:
	return Vector2i(17, 7)

func test_run_scenes() -> void:
	if game == null:
		return
	# En courant vers une porte : on entre, et l'on se retrouve pose sur une case.
	var id := level_id()
	Input.action_press("run")
	Input.action_press("ui_up")
	var end := ticks() + 4000
	while ticks() < end and level_id() == id:
		await get_tree().process_frame
	Input.action_release("ui_up")
	await secs(0.8)
	check("en courant vers la porte, on entre dans la salle", level_id() != id and level().get_meta("location", "") == "Salle", str(level().get_meta("location", "")))
	check("on est pose sur une case de la piece", fmod(player().position.x, 16.0) == 8.0 and fmod(player().position.y, 16.0) == 8.0 and is_free(cell()) , str(player().position))
	Input.action_release("run")
