extends "res://tests/lib.gd"

# Une carte qui a sa propre musique la fait demarrer ; on retrouve celle du terrain en sortant.

func start() -> Vector2i:
	return Vector2i(17, 5)

func test() -> void:
	var starts: int = audio().music_starts()
	await walk("on entre dans la salle", Vector2i(17, 4), true)
	check("la salle : sa musique", audio().music_id() == "sprout_tower" and audio().music_audible(), audio().music_id())
	check("c'est une musique qui demarre", audio().music_starts() == starts + 1, str(audio().music_starts()))
	await hold_until_change("on ressort", "ui_down")
	check("dehors : la musique du terrain revient", audio().music_id() == "new_bark_town" and audio().music_audible(), audio().music_id())
