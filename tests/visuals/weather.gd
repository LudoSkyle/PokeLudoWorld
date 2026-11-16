extends "res://tests/lib.gd"

# La meteo, portee de Pokemon Essentials : des gouttes comptees qui tombent le long de leur
# pente, meurent et renaissent ; rien ne defile, et tout est ancre a la carte.

func start() -> Vector2i:
	return Vector2i(11, 9)

func layer() -> Node2D:
	return level().get_node_or_null("Weather")

func sprites() -> Array:
	return layer().get_node("Particles").get_children()

# Ce qui tombe : les sprites de rang pair. Sous la pluie, les impairs sont les eclaboussures.
func drops() -> Array:
	var out := []
	var all := sprites()
	for i in all.size():
		if i % 2 == 0 and all[i].visible and all[i].modulate.a > 0.5:
			out.append(all[i])
	return out

func sheet_of(sprite: Sprite2D) -> String:
	return "" if sprite.texture == null else sprite.texture.resource_path.get_file().get_basename()

func tone() -> Vector3:
	return layer().get_node("Tone").material.get_shader_parameter("tone_shift")

# La vitesse des gouttes, en pixels de jeu par seconde, dans le repere de la CARTE. C'est la
# MEDIANE de leurs deplacements : une goutte qui renait ou reboucle saute d'un coup, parfois
# tout pres, et une moyenne s'en trouverait faussee.
func velocity(seconds: float) -> Vector2:
	var before := {}
	for d in drops():
		before[d] = d.position
	var t0 := Time.get_ticks_usec()
	await secs(seconds)
	var dt := (Time.get_ticks_usec() - t0) / 1000000.0
	var xs := []
	var ys := []
	for d in before:
		var move: Vector2 = d.position - before[d]
		xs.append(move.x)
		ys.append(move.y)
	if xs.is_empty():
		return Vector2.ZERO
	xs.sort()
	ys.sort()
	return Vector2(xs[xs.size() / 2], ys[ys.size() / 2]) / dt

# La couleur moyenne de l'ecran.
func screen() -> Color:
	var img := root.get_texture().get_image()
	var sum := Color(0, 0, 0, 0)
	var n := 0
	for y in range(100, 860, 20):
		for x in range(100, 1180, 20):
			sum += img.get_pixel(x, y)
			n += 1
	return sum / float(n)

# De combien la pluie assombrit le rouge de l'ecran, ses gouttes mises de cote.
func rain_darkening() -> float:
	var globals := root.get_node("Globals")
	globals.set_weather(0)
	await secs(0.3)
	var clear := screen()
	globals.set_weather(1)
	await secs(0.1)
	layer().get_node("Particles").visible = false
	await secs(0.2)
	var rain := screen()
	layer().get_node("Particles").visible = true
	return clear.r - rain.r

func test() -> void:
	var globals := root.get_node("Globals")
	await wait(4)
	check("dehors, la carte porte sa meteo", layer() != null)
	if layer() == null:
		return
	check("elle se dessine au-dessus du voile", layer().z_index > level().get_node("Haze").z_index)
	check("par beau temps, rien ne tombe et rien n'est teinte", sprites().is_empty() and not layer().get_node("Tone").visible)

	# --- la pluie
	globals.set_weather(1)
	await secs(1.6)
	var all := sprites()
	check("la pluie anime 60 sprites, comme Essentials", all.size() == 60, str(all.size()))
	var kinds := {}
	var splashes := 0
	for i in all.size():
		if i % 2 == 0:
			kinds[sheet_of(all[i])] = true
		elif sheet_of(all[i]) == "rain_4":
			splashes += 1
	check("un sprite sur deux est une goutte, de trois longueurs", kinds.keys().size() == 3 and kinds.has("rain_1") and kinds.has("rain_3"), str(kinds.keys()))
	check("l'autre moitie, des eclaboussures", splashes == 30, str(splashes))
	check("une trentaine de gouttes, pas des centaines", drops().size() == 30, str(drops().size()))

	var fall: Vector2 = await velocity(0.1)
	check("la pluie TOMBE : elle descend", fall.y > 200.0, str(fall))
	check("le long de sa pente, un quart vers la gauche", fall.x < 0.0 and abs(fall.x / fall.y + 0.25) < 0.06, "pente %.3f" % (fall.x / fall.y))

	# Rien ne defile : une goutte meurt et renait ailleurs. En deux secondes, plusieurs ont saute.
	var seen := {}
	for d in drops():
		seen[d] = d.position
	var jumps := 0
	for step in 24:
		await secs(0.08)
		for d in seen:
			if (d.position - seen[d]).length() > 90.0:
				jumps += 1
			seen[d] = d.position
	check("les gouttes meurent et renaissent", jumps >= 5, "%d sauts" % jumps)

	# Ancree a la carte : en marchant, la pluie garde sa vitesse dans le monde.
	Input.action_press("ui_right")
	await secs(0.35)
	var walking: Vector2 = await velocity(0.1)
	Input.action_release("ui_right")
	check("en marchant, la pluie ne suit pas la camera", abs(walking.x / walking.y + 0.25) < 0.08, "pente %.3f" % (walking.x / walking.y))
	check("la pluie retire 30 a chaque couleur", tone() == Vector3(-30, -30, -30), str(tone()))

	# --- l'averse : les images de l'orage, a 45 degres
	globals.set_weather(2)
	await secs(1.2)
	check("l'averse porte les trainees de l'orage", sheet_of(sprites()[0]) == "storm_1" and sheet_of(sprites()[1]) == "storm_4")
	var storm: Vector2 = await velocity(0.1)
	check("elle tombe a 45 degres", abs(storm.x / storm.y + 1.0) < 0.1, "pente %.3f" % (storm.x / storm.y))
	check("et assombrit davantage", tone() == Vector3(-45, -45, -45), str(tone()))

	# --- les nappes
	globals.set_weather(4)
	await secs(0.3)
	check("le blizzard pave l'ecran de sa nappe", layer().get_node("Tiles").get_child_count() == 12, str(layer().get_node("Tiles").get_child_count()))
	check("et eclaircit l'ecran", tone() == Vector3(45, 45, 45), str(tone()))
	globals.set_weather(5)
	await secs(0.3)
	check("le sable ajoute du rouge et retire du bleu", tone() == Vector3(30, 0, -30), str(tone()))
	globals.set_weather(7)
	await secs(0.3)
	check("le brouillard n'a que sa nappe", sprites().is_empty() and layer().get_node("Tiles").get_child_count() == 30)
	check("et ne teinte pas", not layer().get_node("Tone").visible)

	# --- le zenith : rien ne tombe, la teinte bat
	globals.set_weather(6)
	await secs(0.3)
	var low := 1000.0
	var high := -1000.0
	for step in 40:
		await secs(0.05)
		low = min(low, tone().x)
		high = max(high, tone().x)
	check("au zenith la teinte bat", low >= 60.0 and high <= 130.0 and high - low > 30.0, "de %.0f a %.0f" % [low, high])

	# --- la meteo et l'heure : la teinte du temps passe SOUS celle de l'heure
	var by_day: float = await rain_darkening()
	await set_hour(23.0)
	var by_night: float = await rain_darkening()
	check("de jour, la pluie retire 30 a l'ecran", abs(by_day - 0.118) < 0.02, "%.3f" % by_day)
	check("de nuit elle assombrit en proportion, sans s'empiler sur la nuit",
		by_night > 0.02 and by_night < by_day * 0.6, "%.3f la nuit, %.3f le jour" % [by_night, by_day])

	# Pas de zenith sans soleil.
	globals.set_weather(6)
	await secs(0.3)
	check("de nuit, le zenith ne teinte rien", not layer().get_node("Tone").visible, str(tone()))
	await set_hour(12.0)
	await secs(0.2)
	check("le jour revenu, il brille de nouveau", layer().get_node("Tone").visible and tone().x >= 60.0, str(tone()))

	globals.set_weather(0)
	await secs(0.2)
	check("le beau temps revenu, tout est retire", sprites().is_empty() and layer().get_node("Tiles").get_child_count() == 0)
