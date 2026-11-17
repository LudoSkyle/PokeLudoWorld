extends "res://tests/lib.gd"

# Trois volumes dans les options : la musique, les cris des Pokemon, les autres sons. Gauche/Droite,
# par crans de dix pour cent, de muet a 100 % ; applique aussitot, et garde d'un lancement a l'autre.

func start() -> Vector2i:
	return Vector2i(22, 4)

func shown(row: String) -> String:
	return str(game.get_node(VP + "/OptionsMenu/Control/Screen/Rows/" + row + "/Value").text)

func saved(key: String) -> int:
	var file := ConfigFile.new()
	file.load("user://test_settings.cfg")
	return int(file.get_value("options", key, -1))

func test() -> void:
	await menu_pick("Options")
	check("au depart, les trois volumes sont a 100 %", shown("MusicVolume") == "100 %" and shown("CriesVolume") == "100 %" and shown("SoundsVolume") == "100 %",
		"%s %s %s" % [shown("MusicVolume"), shown("CriesVolume"), shown("SoundsVolume")])
	var full_music: float = audio().music_db()
	await tap("ui_down")
	await tap("ui_down")          # vitesse du texte, langue, puis la musique
	await tap("ui_right")
	check("la musique ne depasse pas 100 %", shown("MusicVolume") == "100 %")
	for i in 5:
		await tap("ui_left")
	check("cinq crans a gauche : 50 %", shown("MusicVolume") == "50 %", shown("MusicVolume"))
	check("la musique qui joue baisse aussitot, d'environ six decibels", absf(audio().music_db() - (-6.02)) < 0.2 and audio().music_db() < full_music, "%.2f -> %.2f" % [full_music, audio().music_db()])
	check("le reglage est enregistre", saved("volume_music") == 5, str(saved("volume_music")))
	shot("options_volume")

	await tap("ui_down")
	var cries: int = audio().cries_played()
	for i in 3:
		await tap("ui_left")
	check("les cris : 70 %, et l'on entend un cri a ce volume", shown("CriesVolume") == "70 %" and audio().cries_played() > cries and absf(audio().cry_db() - (-3.1)) < 0.2,
		"%s %.2f" % [shown("CriesVolume"), audio().cry_db()])

	await tap("ui_down")
	for i in 12:
		await tap("ui_left")
	check("les autres sons : muets au bout, sans passer sous zero", shown("SoundsVolume") == "0 %" and audio().sounds_db() <= -59.0, "%s %.1f" % [shown("SoundsVolume"), audio().sounds_db()])
	check("les trois sont enregistres", saved("volume_music") == 5 and saved("volume_cries") == 7 and saved("volume_sounds") == 0,
		"%d %d %d" % [saved("volume_music"), saved("volume_cries"), saved("volume_sounds")])
	check("la musique n'a pas bouge pendant qu'on reglait les autres", shown("MusicVolume") == "50 %")

	await tap("ui_down")
	await tap("interact")
	check("Retour est toujours la derniere ligne", not options_open())

	# On les remet : les reglages des tests servent aux tests suivants.
	await menu_pick("Options")
	await tap("ui_down")
	await tap("ui_down")
	for row in 3:
		for i in 10:
			await tap("ui_right")
		await tap("ui_down")
	check("remis a 100 %", shown("MusicVolume") == "100 %" and shown("CriesVolume") == "100 %" and shown("SoundsVolume") == "100 %")
