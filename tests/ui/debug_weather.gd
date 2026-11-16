extends "res://tests/lib.gd"

# Debug : la ligne de la meteo fait defiler les huit temps, puis revient au beau.

func start() -> Vector2i:
	return Vector2i(11, 11)

func line(n: int) -> String:
	return debug_choices().get_node("Entries").get_child(n).text

func test() -> void:
	await menu_pick("Debug")
	check("la ligne de la meteo dit qu'il fait beau", line(3) == "Météo : normale", line(3))

	# Elle est juste sous l'heure : trois crans plus bas.
	for i in 3:
		await tap("ui_down")

	var seen := []
	for i in 8:
		await tap("interact")
		seen.append(line(3))
	check("les huit temps defilent et bouclent", seen == [
		"Météo : pluie", "Météo : averse", "Météo : neige", "Météo : blizzard",
		"Météo : tempête de sable", "Météo : zénith", "Météo : brouillard", "Météo : normale",
	], str(seen))
	check("la boite reste ouverte, le curseur sur la meme ligne", debug_choices().visible and menu_open())

	# Un temps qui teinte : la tempete de sable ajoute du rouge a l'ecran et lui retire du bleu.
	root.get_node("Globals").set_weather(5)
	await wait(4)
	var tone: Vector3 = level().get_node("Weather/Tone").material.get_shader_parameter("tone_shift")
	check("le dehors vire a l'ocre", tone.x > 0.0 and tone.z < 0.0, str(tone))
	shot("debug_meteo")

	root.get_node("Globals").set_weather(0)
	await tap("menu")
	await tap("menu")
