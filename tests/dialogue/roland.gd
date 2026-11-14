extends "res://tests/lib.gd"

# Roland, devant la grotte : ce qu'il dit suit la quete.

func start() -> Vector2i:
	return Vector2i(39, 4)

func test() -> void:
	check("il ne se tient pas devant l'entree", is_free(Vector2i(38, 3)) and not is_free(Vector2i(39, 3)))
	await talk("avant la quete", Vector2i(39, 4), "ui_up", "Roland", "vingt ans", "idle_down")
	shot("dialogue_roland")
	set_flag("bell_register")
	await talk("le Registre trouve", Vector2i(39, 4), "ui_up", "Roland", "lac souterrain", "idle_down")
	set_flag("bell_tarnished")
	await talk("la cloche trouvee", Vector2i(39, 4), "ui_up", "Roland", "c'était ça qui brillait", "idle_down")
	await walk("l'entree de la grotte reste libre", Vector2i(38, 3), false)
