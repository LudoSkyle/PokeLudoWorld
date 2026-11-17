extends "res://tests/lib.gd"

# La route du nord : des terres en hauteur au-dessus d'une riviere, relevees tuile par tuile
# sur la carte d'exemple. Ce qui porte, ce qui bloque, l'eau qu'on n'atteint jamais, et le
# fait que tout se rejoint depuis l'entree du sud. Les cases citees sont celles de l'exemple.

const W := 69
const H := 50
const SOUTH := [Vector2i(44, 49), Vector2i(45, 49), Vector2i(46, 49)]
const ROUTE := 11          # la source du TileSet decoupee dans la planche de l'exemple (route.png)

func scene() -> String:
	return "north_route"

func start() -> Vector2i:
	return Vector2i(45, 48)

func layer(path: String) -> TileMapLayer:
	return level().get_node(path)

# Le tablier d'un pont : la rangee 12 de route.png, colonnes 0 a 8.
func on_deck(c: Vector2i) -> bool:
	var bridges := layer("Background/Bridges")
	return bridges.get_cell_source_id(c) == ROUTE and bridges.get_cell_atlas_coords(c).y == 12 and bridges.get_cell_atlas_coords(c).x <= 8

# De l'eau, ou le sable du pied des falaises : les trois premieres rangees de route.png, sauf la pelouse.
func is_wet(c: Vector2i) -> bool:
	if c.x < 0 or c.y < 0 or c.x >= W or c.y >= H or on_deck(c):
		return false
	var a := layer("Background/Ground").get_cell_atlas_coords(c)
	return a.y <= 2 and a.x <= 7 and a != Vector2i(4, 2)

func reach(from: Vector2i) -> Dictionary:
	var seen := {from: true}
	var todo: Array = [from]
	while not todo.is_empty():
		var c: Vector2i = todo.pop_front()
		for d in [Vector2i.LEFT, Vector2i.RIGHT, Vector2i.UP, Vector2i.DOWN]:
			var n: Vector2i = c + d
			if n.x < 0 or n.y < 0 or n.x >= W or n.y >= H or seen.has(n):
				continue
			if can_step(c, n):
				seen[n] = true
				todo.append(n)
	return seen

func test() -> void:
	var ground := layer("Background/Ground")
	check("la carte fait 69 cases sur 50, comme l'exemple", ground.get_used_rect() == Rect2i(0, 0, W, H), str(ground.get_used_rect()))
	check("on demarre dans la trouee du sud", cell() == Vector2i(45, 48), str(cell()))
	check("la carte donne sa chance de rencontre et sa table", int(level().get_meta("encounter_rate", 0)) == 3 and int(level().get_meta("encounter_rate_run", 0)) == 5 and str(level().get_meta("wild", "")).contains("mulotin"))
	check("c'est une carte d'exterieur, et elle a son nom", level().get_meta("daylight", false) == true and str(level().get_meta("location", "")) == "Route du nord")
	check("tout le sol vient de la planche de la route", ground.get_cell_source_id(Vector2i(30, 24)) == ROUTE and ground.get_cell_source_id(Vector2i(45, 44)) == ROUTE)

	# Ce qui bloque, ce qui porte.
	var deep := ground.get_cell_atlas_coords(Vector2i(30, 24))
	var foot := ground.get_cell_atlas_coords(Vector2i(25, 12))
	check("la riviere est pleine, et profonde au milieu de son lit", not is_free(Vector2i(30, 24)) and deep.x >= 5 and deep.x <= 7 and deep.y <= 2, str(deep))
	check("au pied des falaises court un lisere de sable, plein lui aussi", foot.x <= 4 and foot.y <= 2 and foot != Vector2i(3, 2) and not is_free(Vector2i(25, 12)), str(foot))
	check("la falaise a deux etages : la roche, puis l'herbe", layer("Background/Cliffs1").get_cell_source_id(Vector2i(23, 12)) == ROUTE and not is_free(Vector2i(23, 12)) and not is_free(Vector2i(22, 12)))
	check("on marche sur les deux ponts, larges de trois cases", is_free(Vector2i(14, 22)) and is_free(Vector2i(15, 22)) and is_free(Vector2i(16, 22)) and is_free(Vector2i(29, 35)) and is_free(Vector2i(29, 36)) and is_free(Vector2i(29, 37)))
	check("les ponts sont les planches de l'exemple", on_deck(Vector2i(15, 22)) and on_deck(Vector2i(29, 36)))
	check("on entre sur un pont et on en sort par ses bouts", can_step(Vector2i(15, 17), Vector2i(15, 18)) and can_step(Vector2i(15, 29), Vector2i(15, 30)) and can_step(Vector2i(23, 36), Vector2i(24, 36)) and can_step(Vector2i(35, 36), Vector2i(36, 36)),
		"%s %s %s %s" % [can_step(Vector2i(15, 17), Vector2i(15, 18)), can_step(Vector2i(15, 29), Vector2i(15, 30)), can_step(Vector2i(23, 36), Vector2i(24, 36)), can_step(Vector2i(35, 36), Vector2i(36, 36))])
	check("on ne descend pas d'un pont par le flanc", not can_step(Vector2i(14, 22), Vector2i(13, 22)) and not can_step(Vector2i(16, 22), Vector2i(17, 22)) and not can_step(Vector2i(29, 35), Vector2i(29, 34)) and not can_step(Vector2i(29, 37), Vector2i(29, 38)))
	check("la montagne de l'est est pleine", not is_free(Vector2i(63, 16)) and not is_free(Vector2i(60, 13)))
	check("un bord de plateau ne se franchit pas", is_free(Vector2i(36, 34)) and not can_step(Vector2i(36, 34), Vector2i(35, 34)))
	check("on monte aux hautes terres par les marches des deux escaliers", can_step(Vector2i(51, 35), Vector2i(51, 34)) and can_step(Vector2i(51, 34), Vector2i(51, 33)) and can_step(Vector2i(57, 34), Vector2i(57, 33)) and can_step(Vector2i(57, 33), Vector2i(57, 32)),
		"%s %s %s %s" % [can_step(Vector2i(51, 35), Vector2i(51, 34)), can_step(Vector2i(51, 34), Vector2i(51, 33)), can_step(Vector2i(57, 34), Vector2i(57, 33)), can_step(Vector2i(57, 33), Vector2i(57, 32))])
	check("mais pas par leurs poteaux", not is_free(Vector2i(49, 34)) and not is_free(Vector2i(53, 34)) and not is_free(Vector2i(55, 33)) and not is_free(Vector2i(59, 33)))
	check("un rebord de roche arrete le pas, dans les deux sens", not is_free(Vector2i(15, 8)) and not is_free(Vector2i(16, 8)) and not is_free(Vector2i(17, 8)) and not is_free(Vector2i(46, 36)) and not is_free(Vector2i(52, 44)))
	# L'arbre du bout du pont : pied en (37..39, 34). Ses deux rangees du bas sont pleines sur ses trois cases, pas le haut de sa cime.
	var tree_low := [Vector2i(37, 34), Vector2i(38, 34), Vector2i(39, 34), Vector2i(37, 33), Vector2i(38, 33), Vector2i(39, 33)]
	var tree_solid := true
	for c in tree_low:
		tree_solid = tree_solid and not is_free(c)
	check("un arbre bloque ses deux rangees du bas sur toute sa largeur", tree_solid)
	check("mais pas le haut de sa cime : on passe derriere", not is_free(Vector2i(38, 46)) and not is_free(Vector2i(40, 45)) and is_free(Vector2i(39, 44)), "%s %s %s" % [is_free(Vector2i(38, 46)), is_free(Vector2i(40, 45)), is_free(Vector2i(39, 44))])
	check("le coin rentrant du plateau est de la pelouse : on s'y tient, sans en tomber", can_step(Vector2i(36, 34), Vector2i(36, 33)) and not can_step(Vector2i(36, 33), Vector2i(36, 32)) and not can_step(Vector2i(36, 33), Vector2i(35, 33)),
		"%s %s %s" % [can_step(Vector2i(36, 34), Vector2i(36, 33)), can_step(Vector2i(36, 33), Vector2i(36, 32)), can_step(Vector2i(36, 33), Vector2i(35, 33))])
	var ledges := layer("Background/Ledges")
	check("un rebord tourne vers l'est a son bout du bas, meme la ou l'exemple le cache sous un arbre", ledges.get_cell_atlas_coords(Vector2i(46, 38)) == Vector2i(15, 2) and ledges.get_cell_atlas_coords(Vector2i(18, 33)) == Vector2i(15, 2) and not is_free(Vector2i(46, 38)),
		"%s %s" % [ledges.get_cell_atlas_coords(Vector2i(46, 38)), ledges.get_cell_atlas_coords(Vector2i(18, 33))])
	check("la piste passe sous l'ombre du sapin", layer("Background/Paths").get_cell_source_id(Vector2i(52, 31)) == ROUTE)
	var props := layer("World/Props")
	var conifer := props.tile_set.get_source(ROUTE) as TileSetAtlasSource
	check("le sapin et l'arbuste ont leur ombre entiere : une rangee sous le pied", conifer.get_tile_size_in_atlas(props.get_cell_atlas_coords(Vector2i(52, 30))) == Vector2i(1, 3) and conifer.get_tile_size_in_atlas(props.get_cell_atlas_coords(Vector2i(61, 41))) == Vector2i(1, 3),
		"%s" % conifer.get_tile_size_in_atlas(props.get_cell_atlas_coords(Vector2i(52, 30))))
	var grass := layer("Background/Grass")
	var tufts := grass.get_used_cells()
	var crossed := 0
	for c in tufts:
		if is_free(c):
			crossed += 1
	check("les hautes herbes se traversent", tufts.size() > 100 and crossed >= tufts.size() - 6, "%d sur %d" % [crossed, tufts.size()])
	var front: TileMapLayer = level().get_node_or_null("World/GrassFront")
	check("elles ont leur moitie de devant, prise a la meme planche", grass.get_cell_source_id(tufts[0]) == 12 and front != null and front.get_cell_source_id(tufts[0]) == 13,
		"%d %s" % [grass.get_cell_source_id(tufts[0]), front])
	check("les bouts de route du nord et de l'est sont fermes", not is_free(Vector2i(15, 0)) and is_free(Vector2i(15, 1)) and not is_free(Vector2i(68, 36)) and is_free(Vector2i(67, 36)))

	# Tout se rejoint.
	var seen := reach(cell())
	var places := {"la sortie du nord": Vector2i(15, 1), "la sortie de l'est": Vector2i(67, 36), "les hautes terres": Vector2i(50, 25), "la porte du sud": Vector2i(45, 49), "le nord du rebord, par le detour des hautes herbes": Vector2i(16, 7)}
	# Les objets et les personnages : leur case vient du generateur, on la lit sur la carte.
	for who in ["World/ItemRoutePotion", "World/ItemRouteBall", "World/ItemRouteSuper", "World/Entities/RouteCamper", "World/Entities/RouteLass", "World/Entities/RoutePicnicker", "World/Entities/RouteYoungster", "World/SignSouth", "World/SignEast", "World/SignNorth"]:
		var node: Node2D = level().get_node(who)
		var at := Vector2i(floori(node.position.x / 16.0), floori(node.position.y / 16.0))
		var beside := Vector2i(-1, -1)
		for d in [Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT, Vector2i.UP]:
			if seen.has(at + d):
				beside = at + d
		places["a cote de " + who.get_file()] = beside
	var lost: Array = []
	for name in places:
		if not seen.has(places[name]):
			lost.append(name)
	check("chaque lieu est atteignable a pied depuis l'entree", lost.is_empty(), str(lost))
	check("le bosquet derriere l'arbuste reste ferme : ni Coupe ni saut de rebord", not seen.has(Vector2i(59, 45)) and not is_free(Vector2i(61, 41)))
	# L'Antidote est la Poke Ball que l'exemple cache dans ce bosquet : il faudra couper l'arbuste pour l'avoir.
	var antidote: Node2D = level().get_node("World/ItemRouteAntidote")
	var hidden_at := Vector2i(floori(antidote.position.x / 16.0), floori(antidote.position.y / 16.0))
	var touched := false
	for d in [Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT, Vector2i.UP]:
		touched = touched or seen.has(hidden_at + d)
	var grove := reach(Vector2i(61, 42))
	var from_grove := false
	for d in [Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT, Vector2i.UP]:
		from_grove = from_grove or grove.has(hidden_at + d)
	check("l'Antidote attend derriere l'arbuste a couper : hors d'atteinte, mais a portee depuis le bosquet", not touched and from_grove, "%s %s %s" % [hidden_at, touched, from_grove])
	var people: Array = []
	for who in level().get_node("World/Entities").get_children():
		people.append(str(who.get("appearance")))
	check("dans la foret, ni pecheur ni montagnard", not people.has("hgss_fisherman") and not people.has("hgss_hiker") and people.has("hgss_camper") and people.has("hgss_lass"), str(people))
	check("un arbre n'a qu'une essence : ceux que l'exemple fait de deux teintes ont celle de leur cime", layer("World/Trees").get_cell_atlas_coords(Vector2i(44, 43)).y == 9 and layer("World/Trees").get_cell_atlas_coords(Vector2i(3, 13)).y == 9,
		"%s %s" % [layer("World/Trees").get_cell_atlas_coords(Vector2i(44, 43)), layer("World/Trees").get_cell_atlas_coords(Vector2i(3, 13))])
	check("l'escalier a le pied de ses poteaux, sur la case du dessous", layer("Background/Bridges").get_cell_source_id(Vector2i(49, 35)) == ROUTE and layer("Background/Bridges").get_cell_source_id(Vector2i(53, 35)) == ROUTE and is_free(Vector2i(49, 35)))

	# Les terres sont en hauteur : on n'atteint jamais l'eau, et le decor ferme la carte.
	var wet: Array = []
	var border: Array = []
	for c in seen:
		if not on_deck(c):
			for d in [Vector2i.LEFT, Vector2i.RIGHT, Vector2i.UP, Vector2i.DOWN]:
				if is_wet(c + d):
					wet.append(c)
		if (c.x == 0 or c.x == W - 1 or c.y == 0 or c.y == H - 1) and not SOUTH.has(c):
			border.append(c)
	check("aucune case ou l'on marche ne touche l'eau ni le sable, hors des ponts", wet.is_empty(), str(wet.slice(0, 6)))
	check("aucune case du bord n'est atteignable, hors de la trouee du sud", border.is_empty(), str(border.slice(0, 6)))
	check("la carte se parcourt : plus de 550 cases atteignables", seen.size() > 550, str(seen.size()))
