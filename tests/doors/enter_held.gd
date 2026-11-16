extends "res://tests/lib.gd"

# Entrer par une porte sans relacher Haut : on continue d'avancer dans la piece.

func start() -> Vector2i:
	return Vector2i(21, 2)

func test() -> void:
	var id0 := level_id()
	Input.action_press("ui_up")
	var t0 := Time.get_ticks_msec()
	while Time.get_ticks_msec() - t0 < 4000 and level_id() == id0:
		await process_frame
	check("Haut tenu : on entre dans la cabane", level_id() != id0 and level().get_meta("location", "") == "Cabane")
	await secs(1.5)
	Input.action_release("ui_up")
	await wait(30)
	check("Haut tenu : on continue d'avancer dans la piece", cell().y < EXIT_MAT.y and cell().x == EXIT_MAT.x, str(cell()))
	shot("cabane")
