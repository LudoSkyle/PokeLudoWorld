extends "res://tests/lib.gd"

# La bibliotheque a sa propre musique ; on retrouve celle du village en sortant.

func start() -> Vector2i:
	return Vector2i(21, 14)

func test() -> void:
	var starts: int = audio().music_starts()
	await walk("on entre dans la bibliotheque", Vector2i(21, 13), true)
	check("la bibliotheque : sa musique", audio().music_id() == "sprout_tower" and audio().music_audible(), audio().music_id())
	check("c'est une musique qui demarre", audio().music_starts() == starts + 1, str(audio().music_starts()))
	await hold_until_change("on ressort", "ui_down")
	check("dehors : la musique du village revient", audio().music_id() == "new_bark_town" and audio().music_audible(), audio().music_id())
