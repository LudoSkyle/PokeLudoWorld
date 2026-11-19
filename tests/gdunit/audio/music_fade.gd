extends "res://tests/gdunit/game_suite.gd"

# Une musique arrive en fondu sur une seconde, et en changer est un fondu enchaine : l'ancienne
# s'eteint pendant que la nouvelle monte.

func title() -> bool:
	return true

func test_music_fade() -> void:
	if game == null:
		return
	check("au lancement : la musique du titre monte, elle n'est pas encore a plein volume", audio().music_id() == "title" and audio().music_level() < 1.0, "%.2f" % audio().music_level())
	var low: float = audio().music_level()
	await secs(0.3)
	check("elle monte", audio().music_level() > low, "%.2f -> %.2f" % [low, audio().music_level()])
	await secs(1.0)
	check("apres une seconde elle est a plein volume", is_equal_approx(audio().music_level(), 1.0), "%.2f" % audio().music_level())
	check("rien ne s'eteint : il n'y avait pas de musique avant", audio().leaving_id() == "")

	await title_pick("New")
	var end := ticks() + 5000
	while ticks() < end and audio().music_id() != "new_bark_town":
		await get_tree().process_frame
	await wait(3)
	check("la carte arrive : la musique du village monte", audio().music_id() == "new_bark_town" and audio().music_level() < 1.0, "%.2f" % audio().music_level())
	check("pendant ce temps celle du titre s'eteint", audio().leaving_id() == "title" and audio().leaving_level() > 0.0 and audio().leaving_level() < 1.0, "%s %.2f" % [audio().leaving_id(), audio().leaving_level()])
	check("les deux se croisent : l'une monte autant que l'autre descend", absf(audio().music_level() + audio().leaving_level() - 1.0) < 0.05, "%.2f + %.2f" % [audio().music_level(), audio().leaving_level()])
	await secs(1.2)
	check("une seconde plus tard : le village a plein volume", is_equal_approx(audio().music_level(), 1.0), "%.2f" % audio().music_level())
	check("celle du titre s'est tue", audio().leaving_id() == "" and is_zero_approx(audio().leaving_level()))
