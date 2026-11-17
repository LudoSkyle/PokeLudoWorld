extends "res://tests/lib.gd"

# L'ile de depart : la geographie de sa carte d'exemple, posee avec les tuiles de la Route 1.
# Ce qui porte, ce qui bloque, le decor qui ferme la carte, et le fait que tout se rejoint a pied.
# Les cases des maisons, des personnages et des objets viennent du generateur : on les lit sur la carte.

const W := 55
const H := 50
const ROUTE := 11          # la planche de la Route 1 (route.png)
const VILLAGE := 14        # les maisons (village.png)
const ROAD := [23, 24, 25, 26, 27]

func scene() -> String:
	return "start_island"

func start() -> Vector2i:
	return Vector2i(6, 9)

func layer(path: String) -> TileMapLayer:
	return level().get_node(path)

func at(path: String) -> Vector2i:
	var n: Node2D = level().get_node(path)
	return Vector2i(floori(n.position.x / 16.0), floori(n.position.y / 16.0))

# Le tablier d'un ponton : la rangee 12 de route.png, colonnes 0 a 8.
func on_deck(c: Vector2i) -> bool:
	var bridges := layer("Background/Bridges")
	return bridges.get_cell_source_id(c) == ROUTE and bridges.get_cell_atlas_coords(c).y == 12 and bridges.get_cell_atlas_coords(c).x <= 8

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
	check("la mer est pleine, liseré compris", not is_free(Vector2i(2, 20)) and not is_free(Vector2i(25, 15)) and not is_free(Vector2i(45, 20)) and is_sea(Vector2i(2, 20)))
	check("on marche sur le sable de la plage", is_free(Vector2i(28, 35)) and is_free(Vector2i(22, 13)) and is_free(Vector2i(5, 40)) and ground.get_cell_atlas_coords(Vector2i(28, 35)) == Vector2i(1, 1))
	check("on marche sur l'herbe des plateaux", is_free(Vector2i(28, 29)) and is_free(Vector2i(8, 15)) and is_free(Vector2i(45, 14)))
	check("la falaise d'un plateau est pleine", not is_free(Vector2i(21, 25)) and not is_free(Vector2i(21, 27)) and not is_free(Vector2i(22, 31)) and layer("Background/Cliffs1").get_cell_source_id(Vector2i(21, 25)) == ROUTE)
	check("on ne passe pas de la plage au plateau par le pied de sa falaise", is_free(Vector2i(22, 32)) and not can_step(Vector2i(22, 32), Vector2i(22, 31)))
	check("le bord du haut d'un plateau est de l'herbe : on s'y tient, et l'on passe de la a la plage de derriere", is_free(Vector2i(24, 41)) and can_step(Vector2i(24, 40), Vector2i(24, 41)) and can_step(Vector2i(24, 41), Vector2i(23, 41)),
		"%s %s %s" % [is_free(Vector2i(24, 41)), can_step(Vector2i(24, 40), Vector2i(24, 41)), can_step(Vector2i(24, 41), Vector2i(23, 41))])

	# Les cinq escaliers : trois marches entre deux poteaux, face au sud.
	var stairs := {"du nord-ouest": Vector2i(14, 13), "du nord-est": Vector2i(31, 13), "de la place": Vector2i(26, 31), "de la bibliotheque": Vector2i(2, 33), "du sud-est": Vector2i(36, 37)}
	var climbed := 0
	for name in stairs:
		var s: Vector2i = stairs[name]
		var ok := not is_free(s) and not is_free(s + Vector2i(4, 0))
		for i in [1, 2, 3]:
			ok = ok and can_step(s + Vector2i(i, 1), s + Vector2i(i, 0)) and can_step(s + Vector2i(i, 0), s + Vector2i(i, -1))
		if ok:
			climbed += 1
	check("cinq escaliers de pierre, trois marches entre deux poteaux pleins", climbed == 5, "%d" % climbed)

	# Les pontons : du dessus d'un plateau a l'autre, larges de trois cases.
	check("les pontons sont les planches de la Route 1, et l'on y marche", on_deck(Vector2i(9, 19)) and on_deck(Vector2i(14, 23)) and on_deck(Vector2i(16, 30)) and on_deck(Vector2i(41, 20)) and on_deck(Vector2i(42, 23)) and on_deck(Vector2i(33, 46))
		and is_free(Vector2i(9, 19)) and is_free(Vector2i(14, 23)) and is_free(Vector2i(16, 30)) and is_free(Vector2i(42, 23)) and is_free(Vector2i(33, 46)))
	check("on y entre par les bouts, pas par le flanc", can_step(Vector2i(9, 16), Vector2i(9, 17)) and can_step(Vector2i(20, 23), Vector2i(22, 23) - Vector2i(1, 0)) and not can_step(Vector2i(8, 19), Vector2i(7, 19)) and not can_step(Vector2i(14, 22), Vector2i(14, 21)))
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
	check("le dallage de la place : neuf cases sur six, sur le plateau du centre", plaza.get_used_rect() == Rect2i(24, 22, 9, 6) and plaza.get_cell_source_id(Vector2i(28, 25)) == ROUTE, str(plaza.get_used_rect()))
	check("le socle et les statues arretent, on se tient devant", not is_free(Vector2i(28, 23)) and not is_free(Vector2i(27, 24)) and not is_free(Vector2i(25, 23)) and not is_free(Vector2i(31, 23)) and is_free(Vector2i(28, 26)))
	var ring_free := true
	for x in range(23, 34):
		for y in [21, 28]:
			if not is_free(Vector2i(x, y)) and cell_of("Runner") != Vector2i(x, y):
				ring_free = false
	for y in range(21, 29):
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
			if is_sea(c) or on_deck(c) or is_free(c):
				on_land = false
	check("huit lampadaires et cinq panneaux, pleins, sur la terre ferme", posts == 13 and on_land, "%d poteaux" % posts)
	var props := layer("World/Props")
	var benches := 0
	for c in props.get_used_cells():
		if props.get_cell_source_id(c) == 10 and props.get_cell_atlas_coords(c) == Vector2i(4, 6) and not is_free(c) and not is_free(c + Vector2i.RIGHT):
			benches += 1
	check("trois bancs de bois, pleins", benches == 3, "%d" % benches)
	check("des habitants vivent la : pres d'un banc, sur une serviette, pres des herbes", cell_of("BenchLady") == Vector2i(11, 14) and cell_of("Sunbather") == Vector2i(28, 36) and cell_of("Swimmer") == Vector2i(25, 11)
		and cell_of("ShellKid") == Vector2i(28, 11) and cell_of("Sailor") == Vector2i(43, 16) and cell_of("Youngster") == Vector2i(48, 13) and cell_of("Gardener") == Vector2i(48, 31))
	check("on marche sur une serviette, et l'on passe sous un parasol, derriere son mat", is_free(Vector2i(28, 35)) and is_free(Vector2i(25, 36)) and is_free(Vector2i(26, 36)) and is_free(Vector2i(22, 11)) and props.get_cell_source_id(Vector2i(25, 36)) == 10)

	# Tout se rejoint a pied, depuis le depart.
	var seen := reach(cell())
	var places := {"la place": Vector2i(28, 29), "le ponton de la cloche": Vector2i(14, 22), "le bout de la jetee du sud": Vector2i(33, 47), "les hautes herbes du sud-ouest": Vector2i(12, 42),
		"la trouee de la falaise": Vector2i(25, 4), "la crique du nord": Vector2i(22, 13), "la plage du sud": Vector2i(28, 35), "la plage de l'ouest": Vector2i(5, 40), "la presqu'ile du sud-est": Vector2i(45, 45)}
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

	# La place : par ses deux pontons, par son escalier du sud, ou par son bord du nord depuis la crique.
	var decks: Array = []
	for c in bridges.get_used_cells():
		if on_deck(c):
			decks.append(c)
	var stair_of_plaza := [Vector2i(27, 31), Vector2i(28, 31), Vector2i(29, 31)]
	check("la place se rejoint par ses pontons, par son escalier, et par son bord du nord depuis la crique", reach(cell(), decks + stair_of_plaza).has(Vector2i(28, 29)) and reach(Vector2i(28, 35), decks).has(Vector2i(28, 29)) and reach(cell(), stair_of_plaza).has(Vector2i(28, 29)))
	check("le jardin du sud-ouest se rejoint par son ponton, ou par son bord du haut depuis la plage du sud", reach(cell(), decks).has(Vector2i(12, 42)))
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
	check("la trouee du nord : cinq cases, entre deux falaises, jusqu'au bord", is_free(Vector2i(23, 1)) and is_free(Vector2i(27, 1)) and not is_free(Vector2i(22, 1)) and not is_free(Vector2i(28, 1)) and at("Doors/Nord0") == Vector2i(23, 0) and at("Doors/Nord4") == Vector2i(27, 0))
	var trees := layer("World/Trees")
	check("la foret est celle de la Route 1", trees.get_used_cells().size() > 60 and trees.get_cell_source_id(trees.get_used_cells()[0]) == ROUTE, "%d arbres" % trees.get_used_cells().size())
	var grass := layer("Background/Grass")
	check("les hautes herbes sont celles de la Route 1, et se traversent", grass.get_used_cells().size() > 30 and grass.get_cell_source_id(grass.get_used_cells()[0]) == 12 and is_free(Vector2i(12, 42)), "%d" % grass.get_used_cells().size())
