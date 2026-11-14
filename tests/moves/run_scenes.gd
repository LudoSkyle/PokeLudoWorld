extends "res://tests/lib.gd"

# Courir ne casse ni les portes ni les passages gardes.

func start() -> Vector2i:
	return Vector2i(21, 16)

func test() -> void:
	# En courant vers une porte : on entre, et l'on se retrouve pose sur une case.
	var id := level_id()
	Input.action_press("run")
	Input.action_press("ui_up")
	var end := Time.get_ticks_msec() + 4000
	while Time.get_ticks_msec() < end and level_id() == id:
		await process_frame
	Input.action_release("ui_up")
	await secs(0.8)
	check("en courant vers la porte, on entre dans la bibliotheque", level_id() != id and level().get_meta("location", "") == "Bibliothèque", str(level().get_meta("location", "")))
	check("on est pose sur une case de la piece", fmod(player().position.x, 16.0) == 8.0 and fmod(player().position.y, 16.0) == 8.0 and is_free(cell()) , str(player().position))
	Input.action_release("run")
