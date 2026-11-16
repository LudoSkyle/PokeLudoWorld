extends "res://tests/lib.gd"

# Dehors, la teinte suit l'heure : quatre moments, et des passages progressifs.

func start() -> Vector2i:
	return Vector2i(11, 11)

func test() -> void:
	check("une carte d'exterieur porte la teinte du jour", level().get_node_or_null("Daylight") != null)
	await set_hour(12.0)
	check("en plein jour : le decor est tel qu'il est dessine", daylight().is_equal_approx(Color.WHITE), str(daylight()))
	shot("heure_jour")
	await set_hour(23.0)
	var night := daylight()
	check("la nuit : sombre et bleue", night.b > night.r and night.r < 0.5 and night.b < 0.9, str(night))
	shot("heure_nuit")
	await set_hour(3.0)
	check("a 3 h c'est toujours la nuit, la meme", daylight().is_equal_approx(night), str(daylight()))
	await set_hour(6.5)
	var dawn := daylight()
	check("l'aube : claire et rosee", dawn.r > dawn.g and dawn.g > 0.7 and dawn.b > 0.7, str(dawn))
	shot("heure_aube")
	await set_hour(19.0)
	var dusk := daylight()
	check("le crepuscule : orange", dusk.r > dusk.g and dusk.g > dusk.b and dusk.b < 0.6, str(dusk))
	shot("heure_crepuscule")
	await set_hour(19.75)
	var between := daylight()
	check("entre crepuscule et nuit : une teinte intermediaire", between.r < dusk.r and between.r > night.r and between.b > dusk.b, str(between))
	await set_hour(18.25)
	check("avant le crepuscule, le jour commence a tomber", daylight().g < 1.0 and daylight().g > dusk.g, str(daylight()))
	await set_hour(-1.0)
	var real: float = root.get_node("Globals").hour()
	check("heure rendue a l'horloge : entre 0 et 24", real >= 0.0 and real < 24.0, str(real))
	await set_hour(12.0)
