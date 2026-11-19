extends "res://tests/gdunit/game_suite.gd"

# L'ecran titre a sa musique ; elle laisse la place a celle du lieu quand la partie commence.

func title() -> bool:
	return true

func test_music_title() -> void:
	if game == null:
		return
	await title_ready()
	check("l'ecran titre demande sa musique", audio().music_id() == "title", audio().music_id())
	check("elle s'entend", audio().music_audible())
	var starts: int = audio().music_starts()
	await tap("interact")
	await secs(0.5)
	check("ouvrir le menu ne la relance pas", audio().music_starts() == starts and audio().music_id() == "title")
	await tap("interact")
	await title_gone()
	await secs(0.6)
	check("la partie lancee : c'est la musique du village", audio().music_id() == "new_bark_town", audio().music_id())
	check("elle s'entend", audio().music_audible())
	check("une seule musique de plus a demarre", audio().music_starts() == starts + 1, "%d -> %d" % [starts, audio().music_starts()])
