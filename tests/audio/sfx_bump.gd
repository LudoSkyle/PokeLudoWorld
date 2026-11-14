extends "res://tests/lib.gd"

# Buter contre un obstacle s'entend, a la cadence des pas, sans toucher a la musique.

func start() -> Vector2i:
	return Vector2i(27, 15)

func test() -> void:
	var before: int = audio().sfx_played()
	Input.action_press("ui_up")
	await secs(1.3)
	Input.action_release("ui_up")
	var bumps: int = audio().sfx_played() - before
	check("on bute contre le banc : le choc s'entend", audio().last_sfx_id() == "bump", audio().last_sfx_id())
	check("a la cadence des pas, pas a chaque image", bumps >= 2 and bumps <= 5, str(bumps))
	check("la musique continue", audio().music_audible() and not audio().jingle_playing())
	check("on n'a pas bouge", cell() == Vector2i(27, 15), str(cell()))
