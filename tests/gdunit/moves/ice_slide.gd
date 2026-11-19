extends "res://tests/gdunit/game_suite.gd"

# Le verglas (docs/player.md, « Glisser sur le verglas », porte de Pokemon SDK) : on y glisse tout
# droit sans que les touches comptent, jusqu'a buter ou jusqu'a la premiere case qui n'en est plus.
# La carte est la glaciere (tests/maps/ice.tscn, fabriquee par tests/maps/build.py) : une plaque
# de (12, 7) a (17, 9), un caillou rond dessus en (15, 8), du vide en (18, 9).

func scene() -> String:
	return "ice"

func start() -> Vector2i:
	return Vector2i(11, 8)

func follower() -> Node2D:
	return game.get_node(ENT + "Follower")

func cell_of_node(n: Node2D) -> Vector2i:
	return Vector2i(floori(n.position.x / 16.0), floori(n.position.y / 16.0))

# Une pression juste assez longue pour engager un pas, puis on lache tout et on attend l'arret.
func tap(action: String) -> void:
	Input.action_press(action)
	await secs(0.2)
	Input.action_release(action)
	await secs(1.6)

func test_ice_slide() -> void:
	if game == null:
		return
	check("la carte est chargee", level() != null and cell() == Vector2i(11, 8), str(cell()))
	check("le sol n'est pas du verglas, la plaque si", not is_ice(Vector2i(11, 8)) and is_ice(Vector2i(12, 8)) and is_ice(Vector2i(17, 9)) and not is_ice(Vector2i(18, 8)))
	var sprite: AnimatedSprite2D = player().get_node("Sprite")

	await tap("ui_right")
	check("un caillou pose sur le verglas arrete la glissade, et l'on reste dessus", cell() == Vector2i(14, 8), str(cell()))

	await tap("ui_down")
	check("on sort du verglas et l'on s'arrete sur la premiere case de sol", cell() == Vector2i(14, 10), str(cell()))

	await tap("ui_up")
	check("d'une seule pression, on traverse toute la plaque", cell() == Vector2i(14, 6), str(cell()))

	# une longue glissade : touche lachee on avance encore, sans remuer les jambes, et le suiveur fait pareil
	await walk("jusqu'au bout de la rangee du haut de la plaque", Vector2i(11, 7), false)
	var seen := {}
	var behind := {}
	Input.action_press("ui_right")
	await secs(0.2)
	Input.action_release("ui_right")
	Input.action_press("ui_down")
	var end := ticks() + 900
	while ticks() < end:
		if is_ice(cell()):
			seen[str(sprite.animation)] = true
			behind[str(follower().get_node("Sprite").animation)] = true
		await get_tree().process_frame
	Input.action_release("ui_down")
	await secs(0.9)
	check("touche lachee, on glisse jusqu'au sol d'en face", cell() == Vector2i(18, 7), str(cell()))
	check("sans remuer les jambes", seen.keys() == ["idle_right"], str(seen.keys()))
	check("une autre touche tenue ne detourne pas la glissade", cell().y == 7, str(cell()))
	check("le suiveur a glisse derriere, sans remuer non plus", cell_of_node(follower()) == Vector2i(17, 7) and not behind.is_empty() and behind.keys().all(func(k): return k.begins_with("idle")), "%s %s" % [cell_of_node(follower()), behind.keys()])
	shot("verglas")

	# contre le vide, on s'arrete sur le verglas
	await walk("jusqu'au bout de la rangee du bas", Vector2i(11, 9), false)
	await tap("ui_right")
	check("contre une paroi on s'arrete sur le verglas", cell() == Vector2i(17, 9), str(cell()))
	await tap("ui_up")
	check("et l'on repart dans un autre sens", cell() == Vector2i(17, 6), str(cell()))

	# un PNJ glisse comme le joueur
	await walk("le joueur se range", Vector2i(20, 11), false)
	var walker: Node2D = await spawn("npc", "Glisseur", Vector2i(11, 7), {"appearance": "frlg_bugcatcher", "movement": "patrol", "pace": 3.0,
		"route": PackedVector2Array([Vector2(11, 7), Vector2(20, 7)])})
	var legs := {}
	var end2 := ticks() + 4000
	while ticks() < end2 and cell_of_node(walker) != Vector2i(20, 7):
		if is_ice(cell_of_node(walker)):
			legs[str(walker.get_node("Sprite").animation)] = true
		await get_tree().process_frame
	check("un PNJ traverse la plaque et poursuit sa route", cell_of_node(walker) == Vector2i(20, 7), str(cell_of_node(walker)))
	check("il glisse sans remuer les jambes", legs.keys() == ["idle_right"], str(legs.keys()))
