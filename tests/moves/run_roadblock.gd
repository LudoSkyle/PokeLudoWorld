extends "res://tests/lib.gd"

# En courant vers le passage garde : on est repousse au pas, d'une seule case.

func start() -> Vector2i:
	return Vector2i(10, 8)

func test() -> void:
	Input.action_press("run")
	Input.action_press("ui_left")
	await secs(2.5)
	check("le garde nous arrete et parle", box().visible and box_text().to_lower().contains("passage"), box_text())
	check("on a recule d'une case, pas plus", cell() == Vector2i(6, 8), str(cell()))
	check("le recul s'est fait au pas", is_equal_approx(player().get_node("Movement").tiles_per_second, 4.0), str(player().get_node("Movement").tiles_per_second))
	Input.action_release("ui_left")
	Input.action_release("run")
	await close_box()
	await secs(1.0)
	await walk("on repart librement", Vector2i(9, 8), false)
