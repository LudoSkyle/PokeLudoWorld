extends "res://tests/lib.gd"

# L'ile de depart : la geographie de sa carte d'exemple, posee avec les tuiles de la Route 1.
# Ce qui porte, ce qui bloque, le decor qui ferme la carte, et le fait que tout se rejoint a pied.
# Les cases des maisons, des personnages et des objets viennent du generateur : on les lit sur la carte.

const W := 55
const H := 50
const ROUTE := 11          # la planche de la Route 1 (route.png)
const VILLAGE := 14        # les maisons (village.png)
const ROAD := [3, 4, 5]

func scene() -> String:
	return "start_island"

func start() -> Vector2i:
	return Vector2i(10, 9)

func layer(path: String) -> TileMapLayer:
	return level().get_node(path)

func at(path: String) -> Vector2i:
	var n: Node2D = level().get_node(path)
	return Vector2i(floori(n.position.x / 16.0), floori(n.position.y / 16.0))

# Le tablier d'un ponton : la rangee 12 de route.png, colonnes 0 a 8.
func on_deck(c: Vector2i) -> bool:
	var bridges := layer("Background/Bridges")
	var a := bridges.get_cell_atlas_coords(c)
	return bridges.get_cell_source_id(c) == ROUTE and (a.y == 12 and a.x >= 12 or a.x == 15 and a.y >= 13 and a.y <= 14 or a in [Vector2i(13, 13), Vector2i(14, 13), Vector2i(13, 14), Vector2i(14, 14), Vector2i(13, 15), Vector2i(14, 15)])          # les planches de la jetee

# La mer, liseré de sable compris : les trois premieres rangees de route.png, sauf le sable plein et la pelouse.
func is_sea(c: Vector2i) -> bool:
	if c.x < 0 or c.y < 0 or c.x >= W or c.y >= H:
		return false
	var a := layer("Background/Ground").get_cell_atlas_coords(c)
	return a.y <= 2 and a.x <= 7 and a != Vector2i(4, 2) and a != Vector2i(1, 1)

func reach(from: Vector2i, cut: Array = []) -> Dictionary:
	var seen := {from: true}
	var todo: Array = [from]
	while not todo.is_empty():
		var c: Vector2i = todo.pop_front()
		for d in [Vector2i.LEFT, Vector2i.RIGHT, Vector2i.UP, Vector2i.DOWN]:
			var n: Vector2i = c + d
			if n.x < 0 or n.y < 0 or n.x >= W or n.y >= H or seen.has(n) or cut.has(n):
				continue
			if can_step(c, n):
				seen[n] = true
				todo.append(n)
	return seen

func test() -> void:
	var ground := layer("Background/Ground")
	var bridges := layer("Background/Bridges")
	check("la carte fait 55 cases sur 50, comme son exemple", ground.get_used_rect() == Rect2i(0, 0, W, H), str(ground.get_used_rect()))
	check("on demarre devant la porte de Ludo", cell() == at("Doors/MaisonLudo") + Vector2i.DOWN, str(cell()))
	check("la carte donne sa chance de rencontre et sa table", int(level().get_meta("encounter_rate", 0)) == 3 and int(level().get_meta("encounter_rate_run", 0)) == 5 and str(level().get_meta("wild", "")).contains("mulotin"))
	check("tout le sol vient de la planche de la Route 1", ground.get_cell_source_id(Vector2i(28, 25)) == ROUTE and ground.get_cell_source_id(Vector2i(2, 20)) == ROUTE and ground.get_cell_source_id(Vector2i(28, 35)) == ROUTE)

	# Trois niveaux : la mer, la plage, les plateaux.
	check("la mer est pleine, liseré compris", not is_free(Vector2i(2, 20)) and not is_free(Vector2i(47, 22)) and not is_free(Vector2i(51, 21)) and is_sea(Vector2i(2, 20)))
	check("on marche sur le sable de la plage", is_free(Vector2i(28, 35)) and is_free(Vector2i(17, 16)) and is_free(Vector2i(5, 43)) and ground.get_cell_atlas_coords(Vector2i(28, 35)) == Vector2i(1, 1))
	check("on marche sur l'herbe des plateaux", is_free(Vector2i(28, 29)) and is_free(Vector2i(8, 15)) and is_free(Vector2i(45, 14)))
	var cliffs := layer("Background/Cliffs1")
	check("la falaise d'un plateau est pleine", not is_free(Vector2i(34, 25)) and not is_free(Vector2i(34, 27)) and not is_free(Vector2i(25, 31)) and not is_free(Vector2i(35, 25)) and not is_free(Vector2i(25, 32)))
	# Deux etages, comme sur la Route 1 : l'anneau d'herbe (route.png, colonnes 5 a 9 des rangees 3 a 5), cerne de l'anneau de roche (colonnes 0 a 4).
	var grass_ring := cliffs.get_cell_atlas_coords(Vector2i(34, 25))
	var rock_ring := cliffs.get_cell_atlas_coords(Vector2i(35, 25))
	check("elle a deux etages, l'herbe puis la roche : deux niveaux au-dessus de l'eau, comme la Route 1", cliffs.get_cell_source_id(Vector2i(34, 25)) == ROUTE and grass_ring.y >= 3 and grass_ring.y <= 5 and grass_ring.x >= 5 and grass_ring.x <= 9
		and rock_ring.y >= 3 and rock_ring.y <= 5 and rock_ring.x <= 4 and ground.get_cell_atlas_coords(Vector2i(34, 25)) == Vector2i(1, 4), "%s %s" % [grass_ring, rock_ring])
	check("on ne passe pas de la plage au plateau par le pied de sa falaise", is_free(Vector2i(36, 25)) and not can_step(Vector2i(36, 25), Vector2i(35, 25)))

	# Les cinq escaliers : trois marches entre deux poteaux, face au sud.
	var stairs := {"du nord-ouest": Vector2i(14, 13), "du nord-est": Vector2i(39, 18), "de la place": Vector2i(26, 31), "de la bibliotheque": Vector2i(2, 33), "du sud-est": Vector2i(36, 37)}
	var climbed := 0
	for name in stairs:
		var s: Vector2i = stairs[name]
		var ok := not is_free(s) and not is_free(s + Vector2i(4, 0))
		for i in [1, 2, 3]:
			ok = ok and can_step(s + Vector2i(i, 2), s + Vector2i(i, 1)) and can_step(s + Vector2i(i, 1), s + Vector2i(i, 0)) and can_step(s + Vector2i(i, 0), s + Vector2i(i, -1))
		if ok:
			climbed += 1
	check("cinq escaliers de pierre, deux rangees de trois marches entre deux poteaux pleins : une par etage", climbed == 5, "%d" % climbed)

	# Un seul ponton : la jetee du sud. On passe d'une terre a l'autre par les plages et leurs escaliers.
	var decks_now := 0
	for c in bridges.get_used_cells():
		if on_deck(c):
			decks_now += 1
			if c.x < 32 or c.x > 34 or c.y < 43:
				decks_now += 1000
	check("il ne reste qu'un ponton, la jetee du sud, large de trois cases", decks_now == 18 and on_deck(Vector2i(33, 46)) and is_free(Vector2i(33, 46)), "%d" % decks_now)
	check("on ne descend pas de la jetee dans l'eau", not can_step(Vector2i(34, 47), Vector2i(35, 47)) and not can_step(Vector2i(32, 47), Vector2i(31, 47)))
	# Trois escaliers de cote, la ou l'on passait par un ponton : trois rangees de marches sur les deux etages de la falaise.
	var side := 0
	for s in [[Vector2i(18, 19), Vector2i.RIGHT], [Vector2i(23, 37), Vector2i.LEFT]]:
		var ok := true
		for j in 3:
			var foot: Vector2i = s[0] + Vector2i(0, j)
			ok = ok and can_step(foot, foot + s[1]) and can_step(foot + s[1], foot + s[1] * 2) and can_step(foot + s[1] * 2, foot + s[1] * 3)
		ok = ok and not is_free(s[0] + s[1] + Vector2i(0, -1)) and not is_free(s[0] + s[1] + Vector2i(0, 3))
		if ok:
			side += 1
	check("deux escaliers de cote : de la crique a la place, du jardin a la plage du sud", side == 2, "%d" % side)
	var wide := true
	for c in bridges.get_used_cells():
		if on_deck(c) and not (on_deck(c + Vector2i.LEFT) or on_deck(c + Vector2i.RIGHT)):
			wide = false
	check("aucun ponton d'une seule case de large", wide)

	# Les maisons : cinq, de chaume, d'une seule tuile ; on passe derriere le haut du toit.
	var houses := layer("World/Houses")
	var huts := 0
	for c in houses.get_used_cells():
		if houses.get_cell_source_id(c) == VILLAGE:
			huts += 1
	check("cinq maisons de chaume", huts == 5, "%d" % huts)
	var ludo := at("Doors/MaisonLudo")
	check("le corps d'une maison bloque, sa porte s'ouvre, on passe derriere son toit", not is_free(ludo + Vector2i.LEFT) and not is_free(ludo + Vector2i(1, -2)) and is_free(ludo) and is_free(ludo + Vector2i(0, -4)),
		"%s %s %s %s" % [is_free(ludo + Vector2i.LEFT), is_free(ludo + Vector2i(1, -2)), is_free(ludo), is_free(ludo + Vector2i(0, -4))])

	# La place : son dallage, le socle, les deux statues, le tour du coureur.
	var plaza := layer("Background/Plaza")
	check("le dallage de la place : un ovale de neuf cases sur six, coins coupes, sur le plateau du centre", plaza.get_used_rect() == Rect2i(24, 20, 9, 6) and plaza.get_cell_source_id(Vector2i(28, 23)) == ROUTE and plaza.get_cell_source_id(Vector2i(24, 20)) == -1 and plaza.get_cell_source_id(Vector2i(32, 25)) == -1, str(plaza.get_used_rect()))
	check("le socle et les statues arretent, on se tient devant", not is_free(Vector2i(28, 21)) and not is_free(Vector2i(27, 22)) and not is_free(Vector2i(25, 21)) and not is_free(Vector2i(31, 21)) and is_free(Vector2i(28, 24)))
	var ring_free := true
	for x in range(23, 34):
		for y in [19, 26]:
			if not is_free(Vector2i(x, y)) and cell_of("Runner") != Vector2i(x, y):
				ring_free = false
	for y in range(19, 27):
		for x in [23, 33]:
			if not is_free(Vector2i(x, y)) and cell_of("Runner") != Vector2i(x, y):
				ring_free = false
	check("le tour de la place est libre pour le coureur", ring_free)

	# Lampadaires, panneaux, mobilier.
	var on_land := true
	var posts := 0
	for n in level().get_node("World").get_children():
		if str(n.name).begins_with("Lamp") or str(n.name).begins_with("Sign"):
			posts += 1
			var c := Vector2i(floori(n.position.x / 16.0), floori(n.position.y / 16.0))
			if str(n.name) == "LampPier":          # celui-la est sur la jetee, contre son bord : on passe a cote
				if not on_deck(c) or is_free(c) or not is_free(c + Vector2i.RIGHT) or not is_free(c + Vector2i(2, 0)):
					on_land = false
			elif is_sea(c) or on_deck(c) or is_free(c):
				on_land = false
	check("neuf lampadaires et cinq panneaux, pleins : sur la terre ferme, sauf celui de la jetee", posts == 14 and on_land, "%d poteaux" % posts)
	var props := layer("World/Props")
	var benches := 0
	for c in props.get_used_cells():
		if props.get_cell_source_id(c) == 10 and props.get_cell_atlas_coords(c) == Vector2i(4, 6) and not is_free(c) and not is_free(c + Vector2i.RIGHT):
			benches += 1
	check("deux bancs de face et un de profil, pleins", benches == 2 and props.get_cell_atlas_coords(Vector2i(49, 31)) == Vector2i(9, 5) and not is_free(Vector2i(49, 31)) and not is_free(Vector2i(49, 30)), "%d" % benches)
	# Rien ne se pose sur une piste : ni banc, ni lampadaire, ni panneau, ni habitant immobile.
	var paths := layer("Background/Paths")
	var on_path: Array = []
	for n in level().get_node("World").get_children() + level().get_node("World/Entities").get_children():
		if n is Node2D and not (n is TileMapLayer) and str(n.name) != "Entities" and str(n.name) != "Player" and not str(n.name).begins_with("Runner") and not str(n.name).begins_with("Glow") and not str(n.name).begins_with("Guard"):          # les gardes, eux, barrent la piste expres
			var c := Vector2i(floori(n.position.x / 16.0), floori(n.position.y / 16.0))
			if paths.get_cell_source_id(c) != -1 or ground.get_cell_atlas_coords(c) == Vector2i(8, 1):
				on_path.append(str(n.name))
	for c in props.get_used_cells():
		if props.get_cell_source_id(c) == 10 and (paths.get_cell_source_id(c) != -1 or ground.get_cell_atlas_coords(c) == Vector2i(8, 1)):
			on_path.append("mobilier en %s" % c)
	check("rien n'est pose sur une piste", on_path.is_empty(), str(on_path))
	check("des habitants vivent la : pres d'un banc, sur une serviette, pres des herbes", cell_of("BenchLady") == Vector2i(11, 14) and cell_of("Sunbather") == Vector2i(28, 36) and cell_of("Swimmer") == Vector2i(25, 15)
		and cell_of("ShellKid") == Vector2i(29, 13) and cell_of("Sailor") == Vector2i(45, 17) and cell_of("Gardener") == Vector2i(49, 32))
	check("on marche sur une serviette, et l'on passe sous un parasol, derriere son mat", is_free(Vector2i(28, 35)) and is_free(Vector2i(25, 36)) and is_free(Vector2i(26, 36)) and is_free(Vector2i(22, 15)) and props.get_cell_source_id(Vector2i(25, 36)) == 10)

	# Tout se rejoint a pied, depuis le depart.
	var seen := reach(cell())
	var places := {"la place": Vector2i(28, 29), "la jetee, devant la cloche": Vector2i(34, 47), "le bout de la jetee du sud": Vector2i(33, 47), "les hautes herbes du sud-ouest": Vector2i(12, 42),
		"la sortie du nord": Vector2i(4, 4), "la crique du nord": Vector2i(17, 16), "la plage du sud": Vector2i(28, 35), "la plage de l'ouest": Vector2i(5, 43), "la presqu'ile du sud-est": Vector2i(45, 45)}
	for door in ["MaisonLudo", "MaisonNord", "Bibliotheque", "Laboratoire", "MaisonSud"]:
		places["devant " + door] = at("Doors/" + door) + Vector2i.DOWN
	for who in ["World/ItemPotion", "World/ItemBall", "World/ItemWater", "World/SignLudo", "World/SignLibrary", "World/SignLab", "World/SignNorth", "World/SignPier"]:
		var beside := Vector2i(-1, -1)
		for d in [Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT, Vector2i.UP]:
			if seen.has(at(who) + d):
				beside = at(who) + d
		places["a cote de " + who.get_file()] = beside
	var lost: Array = []
	for name in places:
		if not seen.has(places[name]):
			lost.append(name)
	check("chaque lieu est atteignable a pied depuis chez Ludo", lost.is_empty(), str(lost))
	check("la carte se parcourt : plus de 1000 cases atteignables", seen.size() > 1000, str(seen.size()))

	# La place : par son escalier de cote depuis la crique, ou par son escalier du sud. Son bord du nord est une falaise.
	var decks: Array = []
	for x in [19, 20]:
		for y in [19, 20, 21]:
			decks.append(Vector2i(x, y))
	var stair_of_plaza := [Vector2i(27, 31), Vector2i(28, 31), Vector2i(29, 31), Vector2i(27, 32), Vector2i(28, 32), Vector2i(29, 32)]
	# Le bord du haut d'un plateau est de l'herbe : on y marche, sur toute sa longueur. C'est le gradin de roche, derriere, qui arrete.
	var top_ok := true
	for x in range(22, 32):          # (plus a l'est, la place rejoint le plateau du parc a fleurs)
		top_ok = top_ok and is_free(Vector2i(x, 18)) and can_step(Vector2i(x, 19), Vector2i(x, 18)) and not is_free(Vector2i(x, 17))
	check("on monte sur la rangee du haut de la place, d'un bout a l'autre, sans en sortir", top_ok)
	check("on marche aussi sur le bord du haut des autres plateaux", is_free(Vector2i(45, 26)) and is_free(Vector2i(15, 36)) and not is_free(Vector2i(45, 25)))
	check("la place et le plateau du laboratoire ne font qu'un : on passe de l'une a l'autre sans escalier", reach(Vector2i(28, 29), decks + stair_of_plaza).has(at("Doors/Laboratoire") + Vector2i.DOWN))
	check("la place ne se rejoint que par ses deux escaliers", not reach(cell(), decks + stair_of_plaza).has(Vector2i(28, 29)) and reach(Vector2i(28, 35), decks).has(Vector2i(28, 29)) and reach(cell(), stair_of_plaza).has(Vector2i(28, 29)))
	var garden_stair := [Vector2i(21, 37), Vector2i(21, 38), Vector2i(21, 39), Vector2i(22, 37), Vector2i(22, 38), Vector2i(22, 39)]
	check("le jardin du sud-ouest et la bibliotheque ne se rejoignent que par l'escalier de cote du jardin", not reach(cell(), garden_stair).has(Vector2i(12, 42)) and not reach(cell(), garden_stair).has(at("Doors/Bibliotheque") + Vector2i.DOWN)
		and reach(cell()).has(Vector2i(12, 42)))
	# Les rochers de la mer : ceux de l'exemple, et quelques-uns de plus dans les cinq groupes que Ludovic a entoures. De
	# l'eau qu'on touche d'une plage, on n'atteint pas le bord de la carte (la mer du sud-est, non entouree, reste ouverte).
	var sea_rocks := layer("World/Props")
	var surfed := {}
	var surf_todo: Array = []
	for y in H:
		for x in W:
			var c := Vector2i(x, y)
			if is_sea(c) and sea_rocks.get_cell_source_id(c) != ROUTE and not bridges.get_cell_source_id(c) != -1:
				for d in [Vector2i.UP, Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT]:
					if Rect2i(0, 0, W, H).has_point(c + d) and is_free(c + d) and bridges.get_cell_source_id(c + d) == -1:
						surf_todo.append(c)
	var surf_out: Array = []
	while not surf_todo.is_empty():
		var c: Vector2i = surf_todo.pop_back()
		if surfed.has(c) or c.x < 0 or c.y < 0 or c.x >= W or c.y >= H or not is_sea(c) or sea_rocks.get_cell_source_id(c) == ROUTE or bridges.get_cell_source_id(c) != -1:
			continue
		surfed[c] = true
		if (c.x == 0 or c.y == H - 1 or c.x == W - 1) and not (c.x >= 49 and c.y >= 36) and not (c.x >= 50 and c.y >= 15 and c.y <= 25):          # (a l'est, Ludovic a choisi ses cinq rochers : la passe y reste ouverte)
			surf_out.append(c)
		for d in [Vector2i.UP, Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT]:
			surf_todo.append(c + d)
	check("en surfant depuis une plage, on ne sort pas de la carte", surf_out.is_empty() and surfed.size() > 100, "%d cases, %s" % [surfed.size(), str(surf_out.slice(0, 8))])
	var line := 0
	for y in H:
		var run := 0
		for x in W:
			run = run + 1 if sea_rocks.get_cell_source_id(Vector2i(x, y)) == ROUTE and is_sea(Vector2i(x, y)) else 0
			line = maxi(line, run)
	check("les rochers ne font pas de ligne droite", line <= 3, "%d" % line)
	check("de l'eau, on s'y reflete : la mer porte la donnee water, liseré compris ; le sable de la plage garde les traces", ground.get_cell_tile_data(Vector2i(2, 20)).get_custom_data("water") == true
		and ground.get_cell_tile_data(Vector2i(28, 35)).get_custom_data("sand") == true and ground.get_cell_tile_data(Vector2i(28, 29)).get_custom_data("water") == false)

	# Le decor ferme la carte : on n'atteint ni l'eau, ni le bord, hors de la trouee du nord.
	var wet := 0
	var border: Array = []
	for c in seen:
		if is_sea(c) and not on_deck(c):
			wet += 1
		if (c.x == 0 or c.x == W - 1 or c.y == 0 or c.y == H - 1) and not (c.y == 0 and ROAD.has(c.x)):
			border.append(c)
	check("on ne marche jamais dans l'eau", wet == 0, "%d cases" % wet)
	check("aucune case du bord n'est atteignable, hors de la trouee du nord", border.is_empty(), str(border.slice(0, 6)))
	# La sortie du nord ressemble a ce qui la suit : sur l'herbe, en hauteur, une piste de trois cases — comme la Route 1 commence.
	check("la sortie du nord : une piste de trois cases dans la foret, jusqu'au bord", is_free(Vector2i(3, 1)) and is_free(Vector2i(5, 1)) and not is_free(Vector2i(2, 1)) and not is_free(Vector2i(6, 1))
		and at("Doors/Nord0") == Vector2i(3, 0) and at("Doors/Nord2") == Vector2i(5, 0) and level().get_node_or_null("Doors/Nord3") == null)
	check("elle est sur l'herbe du plateau, a la hauteur de la Route 1 : aucun escalier entre chez Ludo et elle", ground.get_cell_atlas_coords(Vector2i(4, 2)) == Vector2i(8, 1) and layer("Background/Paths").get_cell_source_id(Vector2i(3, 2)) == ROUTE
		and not find_path(cell(), Vector2i(4, 5)).is_empty() and find_path(cell(), Vector2i(4, 5)).size() < 20)
	check("on ne contourne pas les gardes par l'herbe", not is_free(Vector2i(2, 3)) and not is_free(Vector2i(6, 3)) and not is_free(Vector2i(1, 3)) and not is_free(Vector2i(7, 3)))
	# La couture : la colonne x de l'ile est la colonne x + 41 de la Route 1. Les arbres que le bord coupe en deux ont ici leur pied.
	var seam := layer("World/Trees")
	check("les arbres du bas de la Route 1 ont leur pied ici : de part et d'autre de la piste, et tout le long du bord", seam.get_cell_source_id(Vector2i(0, 0)) == ROUTE and seam.get_cell_source_id(Vector2i(6, 0)) == ROUTE
		and seam.get_cell_source_id(Vector2i(7, 1)) == ROUTE and seam.get_cell_source_id(Vector2i(25, 0)) == ROUTE and seam.get_cell_source_id(Vector2i(27, 1)) == ROUTE)
	var kid: Node2D = npc("Youngster")
	check("le gamin se promene autour de ses herbes, dans un rectangle qui les deborde", kid.get("movement") == "wander" and kid.get("wander_zone") == Rect2i(47, 11, 7, 6) and Rect2i(47, 11, 7, 6).has_point(cell_of("Youngster")), str(kid.get("wander_zone")))
	var trees := layer("World/Trees")
	check("la foret est celle de la Route 1", trees.get_used_cells().size() > 60 and trees.get_cell_source_id(trees.get_used_cells()[0]) == ROUTE, "%d arbres" % trees.get_used_cells().size())
	var grass := layer("Background/Grass")
	check("les hautes herbes sont celles de la Route 1, et se traversent", grass.get_used_cells().size() > 30 and grass.get_cell_source_id(grass.get_used_cells()[0]) == 12 and is_free(Vector2i(12, 42)), "%d" % grass.get_used_cells().size())
