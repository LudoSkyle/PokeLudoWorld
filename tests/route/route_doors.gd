extends "res://tests/lib.gd"

# La trouee du nord de l'ile mene a la route du nord, et l'on en revient.

func scene() -> String:
	return "start_island"

func start() -> Vector2i:
	return Vector2i(30, 2)

func test() -> void:
	await hold_until_change("la trouee du nord de l'ile", "ui_up")
	check("on arrive sur la route du nord", str(level().scene_file_path).ends_with("route_1.tscn"), str(level().scene_file_path))
	await arrival("au bas de la route, tourne vers le nord", Vector2i(45, 48), "idle_up")
	await hold_until_change("la sortie du sud de la route", "ui_down")
	check("on revient sur l'ile", str(level().scene_file_path).ends_with("start_island.tscn"), str(level().scene_file_path))
	await arrival("dans la trouee, tourne vers le sud", Vector2i(31, 1), "idle_down")
