extends "res://tests/lib.gd"

# Les rebords de roche de la route du nord se sautent, dans un seul sens : du haut vers le bas
# de leur marche. On retombe une case plus loin. Dans l'autre sens, et par les cotes, ils arretent.

func scene() -> String:
	return "route_1"

func start() -> Vector2i:
	return Vector2i(45, 48)

# Tient une touche ; si le joueur saute, la lache et attend qu'il retombe. Renvoie [hauteur maximale de l'image, a-t-il saute, hauteur a la fin].
func hop(action: String, seconds: float = 1.2) -> Array:
	var sprite: Node2D = player().get_node("Sprite")
	var rest: float = sprite.position.y
	var highest := 0.0
	var shadow: Node2D = player().get_node("JumpShadow")
	shadow_seen = false
	sounds = audio().sfx_played()
	Input.action_press(action)
	var end := Time.get_ticks_msec() + int(seconds * 1000.0)
	while Time.get_ticks_msec() < end:
		await process_frame
		highest = maxf(highest, rest - sprite.position.y)
		if shadow.visible:
			shadow_seen = true
			shadow_low = shadow_low and shadow.global_position.y > sprite.global_position.y
		if highest > 0.0:
			Input.action_release(action)          # le saut est parti : on lache, pour ne pas repartir en retombant
			if rest - sprite.position.y < 0.001:
				break
	Input.action_release(action)
	await secs(0.5)
	return [highest, highest > 0.0, rest - sprite.position.y]

# Le dernier saut : son ombre s'est-elle montree, sous l'image ? Et le compteur de bruitages avant lui.
var shadow_seen := false
var shadow_low := true
var sounds := 0

func test() -> void:
	# Le rebord de la piste du nord, (15..17, 8) : on le saute vers le sud.
	check("un rebord est plein : on ne s'y tient pas", not is_free(Vector2i(16, 8)) and not is_free(Vector2i(46, 36)) and not is_free(Vector2i(52, 44)))
	await place(Vector2i(16, 7))
	var jump: Array = await hop("ui_down")
	check("vers le bas de sa marche, on le saute et on retombe une case plus loin", cell() == Vector2i(16, 9) and jump[1], "%s %s" % [cell(), jump])
	check("le temps du saut, le joueur est en l'air, puis il retombe", jump[0] >= 6.0 and absf(jump[2]) < 0.01, str(jump))
	check("son ombre reste au sol sous lui le temps du saut, et disparait ensuite", shadow_seen and shadow_low and not player().get_node("JumpShadow").visible, "%s %s" % [shadow_seen, shadow_low])
	check("le saut s'entend, une fois", audio().sfx_played() == sounds + 1 and audio().last_sfx_id() == "jump", "%d %s" % [audio().sfx_played() - sounds, audio().last_sfx_id()])
	jump = await hop("ui_up", 0.6)
	check("dans l'autre sens il arrete : on ne remonte pas", cell() == Vector2i(16, 9) and not jump[1], "%s %s" % [cell(), jump])
	check("la, pas d'ombre, et c'est le choc qu'on entend", not shadow_seen and audio().last_sfx_id() == "bump", "%s %s" % [shadow_seen, audio().last_sfx_id()])

	# Un rebord tourne vers l'est, (46, 35..38).
	await place(Vector2i(45, 36))
	jump = await hop("ui_right")
	check("un rebord tourne vers l'est se saute vers l'est", cell() == Vector2i(47, 36) and jump[1], "%s" % cell())
	jump = await hop("ui_left", 0.6)
	check("et pas vers l'ouest", cell() == Vector2i(47, 36) and not jump[1], "%s" % cell())

	# En courant : le meme bond.
	await place(Vector2i(53, 36))
	Input.action_press("run")
	jump = await hop("ui_right")
	Input.action_release("run")
	check("en courant, le meme saut de deux cases", cell() == Vector2i(55, 36) and jump[1], "%s" % cell())

	# Par le bout : on ne saute pas un rebord en le longeant.
	await place(Vector2i(46, 34))
	jump = await hop("ui_down", 0.6)
	check("par le bout, un rebord ne se saute pas", cell() == Vector2i(46, 34) and not jump[1], "%s" % cell())

	# Le rebord du bosquet, (52, 44..45), tourne vers l'ouest : on en sort, on n'y entre pas.
	await place(Vector2i(51, 44))
	jump = await hop("ui_right", 0.6)
	check("on n'entre pas dans le bosquet de l'Antidote par son rebord", cell() == Vector2i(51, 44) and not jump[1], "%s" % cell())
	await place(Vector2i(53, 44))
	jump = await hop("ui_left")
	check("mais on en sort par la", cell() == Vector2i(51, 44) and jump[1], "%s" % cell())

	# Pas de place pour retomber : pas de saut.
	await place(Vector2i(16, 7))
	var blocker := await spawn("sign", "TestBlocker", Vector2i(16, 9), {"text": "Test."})
	jump = await hop("ui_down", 0.6)
	check("sans place pour retomber, on ne saute pas", cell() == Vector2i(16, 7) and not jump[1], "%s" % cell())
	blocker.free()
