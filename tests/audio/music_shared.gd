extends "res://tests/lib.gd"

# Deux cartes qui declarent la meme musique la partagent : elle continue, sans repartir du debut.

func start() -> Vector2i:
	return Vector2i(21, 2)

func test() -> void:
	check("sur le terrain : sa musique", audio().music_id() == "new_bark_town" and audio().music_audible(), audio().music_id())
	var starts: int = audio().music_starts()
	await walk("on entre dans la cabane", Vector2i(21, 1), true)
	check("la porte s'entend", audio().last_sfx_id() == "door", audio().last_sfx_id())
	check("dans la cabane : la meme musique", audio().music_id() == "new_bark_town" and audio().music_audible(), audio().music_id())
	check("elle n'est pas repartie du debut", audio().music_starts() == starts, str(audio().music_starts()))
	await hold_until_change("on ressort par le paillasson", "ui_down")
	check("sortir fait entendre une autre porte", audio().last_sfx_id() == "door_exit", audio().last_sfx_id())
