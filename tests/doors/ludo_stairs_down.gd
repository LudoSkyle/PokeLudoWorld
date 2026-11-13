extends "res://tests/lib.gd"

# Descendre l'escalier touche tenue : on ne remonte pas aussitot.

func scene() -> String:
	return "ludo_bedroom"

func start() -> Vector2i:
	return Vector2i(11, 8)

func test() -> void:
	var changes := await hold_and_count_changes("ui_left", 4.0)
	check("touche tenue : un seul changement de carte", changes == 1, "%d changement(s)" % changes)
	await arrival("salon par l'escalier", Vector2i(11, 8), "idle_right")
