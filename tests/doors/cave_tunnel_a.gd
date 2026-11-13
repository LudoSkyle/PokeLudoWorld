extends "res://tests/lib.gd"

# Tunnel A (1F -> B1F) touche tenue : on descend une fois, sans rebrousser chemin.

func scene() -> String:
	return "cave_1f"

func start() -> Vector2i:
	return Vector2i(4, 4)

func test() -> void:
	shot("grotte_1f_tunnel")
	var changes := await hold_and_count_changes("ui_up", 4.0)
	check("touche tenue : un seul changement de carte", changes == 1, "%d changement(s)" % changes)
	await arrival("grotte B1F ouest", Vector2i(4, 4), "idle_down")
	shot("grotte_b1f")
