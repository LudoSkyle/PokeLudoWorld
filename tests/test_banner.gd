extends "res://tests/lib.gd"

# Bandeau de lieu : il s'annonce quand le lieu change, et seulement la.

func panel() -> Control:
	return game.get_node(VP + "/LocationBanner/Control/Panel")

func label() -> String:
	return game.get_node(VP + "/LocationBanner/Control/Panel/Name").text

# Regarde le bandeau pendant n images : [est apparu, texte, hauteur la plus basse]
func watch(t: float, name: String = "") -> Array:
	var shown := false
	var text := ""
	var lowest := -999.0
	var end := Time.get_ticks_msec() + int(t * 1000.0)
	while Time.get_ticks_msec() < end:
		await process_frame
		if panel().visible:
			shown = true
			text = label()
			if panel().position.y > lowest:
				lowest = panel().position.y
				if name != "" and lowest >= 24.0:
					shot(name); name = ""
	return [shown, text, lowest]

func test() -> void:
	var r: Array = await watch(1.5, "bandeau_village")
	check("depart : le bandeau annonce le village", r[0] and r[1] == "Bourg-Ludo", str(r))
	check("depart : il descend a sa place, en haut a gauche", is_equal_approx(r[2], 24.0) and is_equal_approx(panel().position.x, 24.0), str(r[2]))
	check("depart : le cadre contient le nom", panel().size.x >= game.get_node(VP + "/LocationBanner/Control/Panel/Name").get_minimum_size().x + 48.0, str(panel().size))
	check("depart : bandeau de bois, au pixel du jeu", panel().texture.resource_path.ends_with("wood.png") and panel().size == Vector2(524, 108), str(panel().size))
	await secs(2.5)
	check("depart : il est remonte apres quelques secondes", not panel().visible)

	await enter("maison de Ludo", Vector2i(8, 15))
	r = await watch(1.5, "bandeau_maison")
	check("maison : le bandeau annonce la maison", r[0] and r[1] == "Maison de Ludo", str(r))
	await secs(2.5)
	check("maison : il est remonte", not panel().visible)

	await walk("escalier", STAIR_MAT, false)
	await hold_until_change("etage", "ui_left")
	r = await watch(2.5)
	check("etage : meme lieu, pas de bandeau", not r[0], str(r))
