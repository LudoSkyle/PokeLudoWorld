extends "res://tests/gdunit/game_suite.gd"

# Le pecheur : il repond, puis se retourne vers l'eau.

func start() -> Vector2i:
	return Vector2i(4, 12)

func test_fisher() -> void:
	if game == null:
		return
	check("au repos il regarde l'eau", anim("Fisher") == "idle_right", anim("Fisher"))
	await talk("pecheur", Vector2i(4, 12), "ui_down", "Fisher", "mord", "idle_up")
	shot("dialogue_pecheur")
	await secs(0.3)
	check("le dialogue fini, il se retourne vers l'eau", anim("Fisher") == "idle_right", anim("Fisher"))
