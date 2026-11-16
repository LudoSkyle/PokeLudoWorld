extends "res://tests/lib.gd"

# La nuit ne tombe que dehors : un interieur reste eclaire, et l'interface n'est pas teintee.

func start() -> Vector2i:
	return Vector2i(21, 2)

func test() -> void:
	await set_hour(23.0)
	check("dehors, la nuit est tombee", daylight().b > daylight().r, str(daylight()))
	await walk("on entre dans la cabane", Vector2i(21, 1), true)
	check("dedans : pas de teinte", level().get_node_or_null("Daylight") == null and daylight().is_equal_approx(Color.WHITE))
	shot("nuit_dedans")
	await hold_until_change("on ressort", "ui_down")
	check("dehors a nouveau : la nuit", level().get_node_or_null("Daylight") != null and daylight().b > daylight().r, str(daylight()))
	# L'interface est sur ses propres calques : la boite de dialogue garde ses couleurs.
	# On ressort devant la porte : le panneau de test se pose a droite du joueur.
	await spawn("sign", "Night", cell() + Vector2i(1, 0), {"text": "Il fait nuit."})
	await interact_facing("ui_right")
	await secs(0.8)
	var by_night: Color = root.get_texture().get_image().get_pixel(640, 912)
	shot("nuit_dialogue")
	await set_hour(12.0)
	var by_day: Color = root.get_texture().get_image().get_pixel(640, 912)
	check("la boite de dialogue a la meme couleur de nuit comme de jour", by_night.is_equal_approx(by_day), "%s / %s" % [by_night, by_day])
	await close_box()
