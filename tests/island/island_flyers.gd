extends "res://tests/lib.gd"

# Des Goelise et des Bekipan volent au-dessus de l'ile : du decor vivant, sans corps,
# chacun dans sa zone, par trajets d'une a trois cases, sans jamais rebrousser chemin.

func scene() -> String:
	return "start_island"

func start() -> Vector2i:
	return Vector2i(10, 9)

func test() -> void:
	var sky: Node2D = level().get_node("Sky")
	var birds: Array = sky.get_children()
	var wingull := 0
	var pelipper := 0
	var bodies := 0
	var shadows := 0
	for b in birds:
		if b.get("species") == "wingull":
			wingull += 1
		elif b.get("species") == "pelipper":
			pelipper += 1
		if b is CollisionObject2D or not b.find_children("*", "CollisionObject2D", true, false).is_empty():
			bodies += 1
		if b.get_node_or_null("Shadow") != null and b.get_node("Sprite").texture != null:
			shadows += 1
	check("quatre Goelise et deux Bekipan", wingull == 4 and pelipper == 2, "%d et %d" % [wingull, pelipper])
	check("ils volent au-dessus du decor, sous le voile", sky.z_index > 0 and sky.z_index < level().get_node("Haze").z_index, str(sky.z_index))
	check("aucun n'a de corps : on ne les heurte pas", bodies == 0, "%d" % bodies)
	check("chacun a son image et son ombre au sol", shadows == birds.size(), "%d" % shadows)
	var zones_ok := true
	for b in birds:
		var z: Rect2i = b.get("zone")
		if z.size != Vector2i(10, 10):
			zones_ok = false
	check("chacun a sa zone de dix cases sur dix", zones_ok)

	# On les suit quatorze secondes.
	var last := {}
	var heading := {}
	var run := {}
	var moved := {}
	var reversed := 0
	var outside := 0
	var too_long := 0
	var diagonal := 0
	for b in birds:
		last[b] = b.position
		heading[b] = Vector2.ZERO
		run[b] = 0.0
		moved[b] = false
	var end := Time.get_ticks_msec() + 14000
	while Time.get_ticks_msec() < end:
		await process_frame
		for b in birds:
			var step: Vector2 = b.position - last[b]
			last[b] = b.position
			var z: Rect2i = b.get("zone")
			var c := Vector2i(floori(b.position.x / 16.0), floori(b.position.y / 16.0))
			if not z.has_point(c):
				outside += 1
			if step.length() < 0.001:
				run[b] = 0.0          # il plane : le trajet est fini
				continue
			moved[b] = true
			if absf(step.x) > 0.001 and absf(step.y) > 0.001:
				diagonal += 1
			var way := step.sign()
			if run[b] == 0.0 and heading[b] != Vector2.ZERO and way == -heading[b]:
				reversed += 1
			heading[b] = way
			run[b] += step.length()
			if run[b] > 3.0 * 16.0 + 0.5:
				too_long += 1
	var all_moved := true
	for b in birds:
		if not moved[b]:
			all_moved = false
	check("en quatorze secondes, chacun a vole", all_moved)
	check("aucun n'est sorti de sa zone", outside == 0, "%d images hors zone" % outside)
	check("un trajet est une ligne droite de trois cases au plus", too_long == 0 and diagonal == 0, "%d trop longs, %d en biais" % [too_long, diagonal])
	check("aucun ne rebrousse chemin d'un trajet au suivant", reversed == 0, "%d demi-tours" % reversed)
	# On marche dessous sans rien heurter.
	check("un oiseau au-dessus d'une case ne la bouche pas", is_free(Vector2i(17, 16)) and not find_path(Vector2i(10, 9), Vector2i(17, 16)).is_empty())
	shot("ile_oiseaux")

	# De loin en loin, un oiseau qui passe au-dessus du joueur pousse son cri.
	var caller: Node2D = birds[0]
	var before: int = audio().cries_played()
	for b in birds:
		b.set("cry_every", Vector2(0, 0))          # les autres se taisent : on n'ecoute que celui-la
	caller.set("cry_range", 0.5)
	caller.set("cry_every", Vector2(0.2, 0.4))
	await secs(2.0)
	check("loin du joueur, un oiseau ne crie pas", audio().cries_played() == before or caller.position.distance_to(player().position) <= 8.0, "%d" % (audio().cries_played() - before))
	caller.set("cry_range", 400.0)
	before = audio().cries_played()
	await secs(2.5)
	check("au-dessus du joueur, il pousse son cri", audio().cries_played() > before and audio().last_cry_id() == str(caller.get("species")), "%d %s" % [audio().cries_played() - before, audio().last_cry_id()])
	caller.set("cry_every", Vector2(0, 0))
	before = audio().cries_played()
	await secs(1.5)
	check("regle a zero, il se tait", audio().cries_played() == before)
