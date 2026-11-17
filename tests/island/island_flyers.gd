extends "res://tests/lib.gd"

# Des Goelise et des Bekipan passent au-dessus de l'ile, portes par le vent d'ouest en est :
# quatre groupes, du decor vivant, sans corps.

func scene() -> String:
	return "start_island"

func start() -> Vector2i:
	return Vector2i(10, 9)

func test() -> void:
	var sky: Node2D = level().get_node("Sky")
	var birds: Array = sky.get_children()
	var packs := {}
	var bodies := 0
	var shadows := 0
	for b in birds:
		var pack: Array = packs.get(b.get("seed"), [])
		pack.append(str(b.get("species")))
		packs[b.get("seed")] = pack
		if b is CollisionObject2D or not b.find_children("*", "CollisionObject2D", true, false).is_empty():
			bodies += 1
		if b.get_node_or_null("Shadow") != null and b.get_node("Sprite").texture != null:
			shadows += 1
	var shapes_ok := true
	for pack in packs.values():
		var gulls: int = pack.count("wingull")
		var pelipper: int = pack.count("pelipper")
		if gulls + pelipper != pack.size() or pelipper > 1 or (pelipper == 1 and gulls != 2) or (pelipper == 0 and (gulls < 1 or gulls > 2)):
			shapes_ok = false
	check("quatre groupes", packs.size() == 4, str(packs))
	check("une ou deux Goelise ; un Bekipan ne va qu'avec deux Goelise", shapes_ok, str(packs.values()))
	check("ils volent au-dessus du decor, sous le voile", sky.z_index > 0 and sky.z_index < level().get_node("Haze").z_index, str(sky.z_index))
	check("aucun n'a de corps : on ne les heurte pas", bodies == 0, "%d" % bodies)
	check("chacun a son image et son ombre au sol", shadows == birds.size(), "%d" % shadows)

	# On les suit dix secondes : toujours vers l'est, comme les Granivol de la Route 1, sauf le retour par l'autre bord.
	var last := {}
	var gap := {}
	var mate := {}
	for b in birds:
		last[b] = b.position
		for g in birds:
			if g.get("seed") == b.get("seed"):
				mate[b] = g
				break
		gap[b] = b.position.x - mate[b].position.x
	var backwards := 0
	var paused := 0
	var apart := 0
	var end := Time.get_ticks_msec() + 10000
	while Time.get_ticks_msec() < end:
		await process_frame
		for b in birds:
			var step: float = b.position.x - last[b].x
			last[b] = b.position
			if step < -200.0:
				continue          # sorti a l'est, rentre a l'ouest
			if step < -0.001:
				backwards += 1
			elif step < 0.001:
				paused += 1
			var now: float = b.position.x - mate[b].position.x
			if absf(now - gap[b]) > 2.0 and absf(absf(now - gap[b]) - 55.0 * 16.0) > 80.0:
				apart += 1
	check("le vent les porte d'ouest en est, sans demi-tour", backwards == 0, "%d reculs" % backwards)
	check("ils ne s'arretent pas en l'air", paused <= birds.size() * 3, "%d images a l'arret" % paused)
	check("un groupe reste groupe", apart == 0, "%d images ou un groupe s'ecarte" % apart)
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
	var limit := Time.get_ticks_msec() + 26000          # son premier cri est tire au sort a son arrivee, jusqu'a vingt-quatre secondes plus tard
	while audio().cries_played() == before and Time.get_ticks_msec() < limit:
		await process_frame
	check("au-dessus du joueur, il pousse son cri", audio().cries_played() > before and audio().last_cry_id() == str(caller.get("species")), "%d %s" % [audio().cries_played() - before, audio().last_cry_id()])
	caller.set("cry_every", Vector2(0, 0))
	before = audio().cries_played()
	await secs(1.5)
	check("regle a zero, il se tait", audio().cries_played() == before)
