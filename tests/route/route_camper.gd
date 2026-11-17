extends "res://tests/lib.gd"

# Le campeur du pont : il dit que la riviere est en contrebas et qu'on n'y descend pas.
# Sa case vient du generateur : le test la lit sur la carte et se place a cote de lui.

func scene() -> String:
	return "route_1"

func start() -> Vector2i:
	return Vector2i(45, 48)

# Ou se tenir pour parler a ce qui est en `target` : [case, touche pour lui faire face, animation de qui se tourne vers nous].
func front_of(target: Vector2i) -> Array:
	for d in [[Vector2i.DOWN, "ui_up", "idle_down"], [Vector2i.LEFT, "ui_right", "idle_left"], [Vector2i.RIGHT, "ui_left", "idle_right"], [Vector2i.UP, "ui_down", "idle_up"]]:
		if is_free(target + d[0]):
			return [target + d[0], d[1], d[2]]
	return []

func test() -> void:
	var front := front_of(cell_of("RouteCamper"))
	check("on peut se tenir a cote du campeur", not front.is_empty(), str(cell_of("RouteCamper")))
	await place(front[0])
	await talk("le campeur", front[0], front[1], "RouteCamper", "rivière", front[2])
