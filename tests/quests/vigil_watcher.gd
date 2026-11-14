extends "res://tests/lib.gd"

# Le chasseur d'insectes reste dans ses herbes, et change de replique apres la Veillee.

func start() -> Vector2i:
	return Vector2i(9, 4)

func test() -> void:
	set_flag("bell_hung")
	await reload_level()
	npc("GrassWatcher").movement = "static"
	await talk("le chasseur", Vector2i(9, 4), "ui_left", "GrassWatcher", "retrouvé la cloche", "idle_right")
	await tap("interact")
	await secs(1.5)
	await tap("interact")
	await wait_text("Moi, toujours pas le moindre insecte.")
	check("toujours bredouille", box_text() == "Moi, toujours pas le moindre insecte.", box_text())
	await close_box()
