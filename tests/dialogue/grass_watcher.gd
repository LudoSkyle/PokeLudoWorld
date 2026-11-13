extends "res://tests/lib.gd"

# Le chasseur d'insectes : il se tourne vers nous de chaque cote.

func start() -> Vector2i:
	return Vector2i(8, 5)

func test() -> void:
	# il erre : on le fige sur sa case de depart pour lui parler
	npc("GrassWatcher").movement = "static"
	check("au repos il regarde vers le bas", anim("GrassWatcher") == "idle_down", anim("GrassWatcher"))
	await talk("par le bas", Vector2i(8, 5), "ui_up", "GrassWatcher", "herbes", "idle_down")
	shot("dialogue_chasseur")
	await talk("par la gauche", Vector2i(7, 4), "ui_right", "GrassWatcher", "herbes", "idle_left")
