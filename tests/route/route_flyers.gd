extends "res://tests/lib.gd"

# Au-dessus de la route du nord, pas d'oiseaux de mer : des Granivol, des Floravol et des
# Cotovol que le vent porte d'ouest en est, par groupes de deux ou trois, sans jamais se poser.

func scene() -> String:
	return "route_1"

func start() -> Vector2i:
	return Vector2i(45, 48)

func test() -> void:
	var sky: Node2D = level().get_node("Sky")
	var flyers: Array = sky.get_children()
	var kinds := {}
	var packs := {}
	var bodies := 0
	var drawn := 0
	for f in flyers:
		kinds[f.get("species")] = int(kinds.get(f.get("species"), 0)) + 1
		packs[f.get("seed")] = int(packs.get(f.get("seed"), 0)) + 1
		if f is CollisionObject2D or not f.find_children("*", "CollisionObject2D", true, false).is_empty():
			bodies += 1
		if f.get_node_or_null("Shadow") != null and f.get_node("Sprite").texture != null:
			drawn += 1
	check("des Granivol, des Floravol et des Cotovol, et aucun oiseau de mer", kinds.has("hoppip") and kinds.has("skiploom") and kinds.has("jumpluff") and not kinds.has("wingull") and not kinds.has("pelipper"), str(kinds))
	var sizes: Array = packs.values()
	check("ils vont par groupes de deux ou trois", sizes.size() >= 3 and sizes.min() >= 2 and sizes.max() <= 3, str(packs))
	check("aucun n'a de corps, chacun a son image et son ombre", bodies == 0 and drawn == flyers.size(), "%d %d" % [bodies, drawn])

	# On les suit dix secondes : toujours vers l'est, jamais a l'arret, sauf le retour par l'autre bord.
	var last := {}
	var low := {}
	var high := {}
	var gap := {}
	for f in flyers:
		last[f] = f.position
		low[f] = f.position.y
		high[f] = f.position.y
	var mate: Dictionary = {}          # pour chaque volant, le premier de son groupe
	for f in flyers:
		for g in flyers:
			if g.get("seed") == f.get("seed"):
				mate[f] = g
				break
		gap[f] = f.position - mate[f].position
	var paused := 0
	var backwards := 0
	var returns := 0
	var apart := 0
	var end := Time.get_ticks_msec() + 10000
	while Time.get_ticks_msec() < end:
		await process_frame
		for f in flyers:
			var step: float = f.position.x - last[f].x
			last[f] = f.position
			low[f] = minf(low[f], f.position.y)
			high[f] = maxf(high[f], f.position.y)
			if step < -200.0:
				returns += 1          # sorti a l'est, rentre a l'ouest
			elif step < 0.0:
				backwards += 1
			elif step < 0.0001:
				paused += 1
		for f in flyers:
			var now: Vector2 = f.position - mate[f].position
			# le groupe reste groupe : meme ecart, sauf quand l'un des deux vient de changer de bord
			if absf(now.x - gap[f].x) > 2.0 and absf(absf(now.x - gap[f].x) - 72.0 * 16.0) > 2.0:
				apart += 1
			if absf(now.y - gap[f].y) > 0.5:
				apart += 1
	check("le vent les porte vers l'est sans jamais les poser", paused == 0 and backwards == 0, "%d arrets, %d reculs" % [paused, backwards])
	check("un groupe reste groupe", apart == 0, str(apart))
	var floating := 0
	for f in flyers:
		if high[f] - low[f] > 1.0 and high[f] - low[f] <= 34.0:
			floating += 1
	check("ils montent et descendent doucement, d'une case au plus de part et d'autre", floating == flyers.size(), "%d sur %d" % [floating, flyers.size()])
	# Le retour : on en pousse un au bord est, il rentre par l'ouest.
	var one: Node2D = flyers[0]
	one.position.x = 70.0 * 16.0
	await secs(1.2)
	check("sorti par l'est, il rentre par l'ouest", one.position.x < 8.0 * 16.0, str(one.position.x))
