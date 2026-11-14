extends "res://tests/lib.gd"

# Les hautes herbes : le bas de chaque touffe passe devant qui s'y tient, fixe a
# sa case, et la touffe bruisse sur place quand on y entre.

func start() -> Vector2i:
	return Vector2i(12, 5)

func state(layer: TileMapLayer, c: Vector2i) -> int:
	return layer.get_cell_atlas_coords(c).x

func test() -> void:
	var grass: TileMapLayer = level().get_node("Background/Grass")
	npc("GrassWatcher").movement = "static"
	await wait(20)
	var front: TileMapLayer = level().get_node_or_null("World/GrassFront")
	check("le calque de devant existe, parmi le decor trie", front != null and front.y_sort_enabled)
	if front == null:
		return
	var same := front.get_used_cells().size() == grass.get_used_cells().size()
	for c in grass.get_used_cells():
		if front.get_cell_source_id(c) != 9:
			same = false
	check("il porte le bas d'une touffe sur chaque case d'herbe", same, str(front.get_used_cells().size()))
	check("il est cale sur l'herbe", front.global_position == grass.global_position, str(front.global_position))
	# Le bas d'herbe ne passe devant un personnage qu'a 2 px de l'arrivee sur sa case.
	# Plus tot, il lui barrerait le corps : en montant, la bande est encore a hauteur
	# de taille a mi-pas.
	var sort_at: int = front.tile_set.get_source(9).get_tile_data(Vector2i(6, 0), 0).y_sort_origin
	check("il ne passe devant qu'en fin de pas, au niveau des pieds", sort_at >= 1 and sort_at <= 3, str(sort_at))
	check("rien n'est attache au personnage", player().get_node("Grass").get_child_count() == 0)
	var seen := {}
	var seen_front := {}
	Input.action_press("ui_left")
	var end := Time.get_ticks_msec() + 900
	while Time.get_ticks_msec() < end and cell() != Vector2i(11, 5):
		seen[state(grass, Vector2i(11, 5))] = true
		await process_frame
	Input.action_release("ui_left")
	end = Time.get_ticks_msec() + 600
	while Time.get_ticks_msec() < end:
		seen[state(grass, Vector2i(11, 5))] = true
		seen_front[state(front, Vector2i(11, 5))] = true
		await process_frame
	check("on est entre dans l'herbe", cell() == Vector2i(11, 5), str(cell()))
	check("la touffe a bruisse sous nos pas", seen.has(7) and seen.has(8), str(seen.keys()))
	check("son bas, devant nous, a bruisse avec elle", seen_front.has(7) or seen_front.has(8), str(seen_front.keys()))
	check("puis elle s'est redressee, a l'arret l'herbe est normale", state(grass, Vector2i(11, 5)) == 6 and state(front, Vector2i(11, 5)) == 6)
	# Touche tenue : le bruissement reste sur les cases traversees, derriere nous.
	var trail := 0
	Input.action_press("ui_left")
	end = Time.get_ticks_msec() + 700
	while Time.get_ticks_msec() < end:
		for x in range(5, 12):
			if state(grass, Vector2i(x, 5)) != 6 and Vector2i(x, 5) != cell():
				trail += 1
		await process_frame
	Input.action_release("ui_left")
	# En secondes et non en images : le bruissement dure un temps, pas un nombre d'images.
	await secs(1.0)
	check("touche tenue : les cases quittees bruissent encore derriere nous", trail > 0, str(trail))
	var parted := []
	for c in grass.get_used_cells():
		if state(grass, c) != 6 or state(front, c) != 6:
			parted.append("%s herbe=%d devant=%d" % [c, state(grass, c), state(front, c)])
	check("tout s'est redresse", parted.is_empty(), str(parted))
	await place(Vector2i(10, 4))
	await secs(0.6)
	shot("herbe_dedans")
