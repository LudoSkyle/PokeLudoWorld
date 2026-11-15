extends "res://tests/lib.gd"

# L'ile de depart : ce qui porte, ce qui bloque, le decor qui ferme la carte,
# et le fait que tout se rejoint a pied.

const W := 62
const H := 49
const SEA := Vector2i(6, 32)        # la mer : pleine
const UNDER_DECK := Vector2i(9, 31) # l'eau sous un ponton : sans collision

func scene() -> String:
	return "start_island"

func start() -> Vector2i:
	return Vector2i(8, 9)

func layer(path: String) -> TileMapLayer:
	return level().get_node(path)

# Un rocher pose dans l'eau : un gros de l'atlas, ou un petit de la planche de l'ile.
func is_rock(c: Vector2i) -> bool:
	var props := layer("World/Props")
	var src := props.get_cell_source_id(c)
	var a := props.get_cell_atlas_coords(c)
	return (src == 5 and a.y >= 32 and a.y <= 33 and a.x >= 26 and a.x <= 39) or (src == 10 and a.y == 2 and a.x >= 8 and a.x <= 11)

func is_sea(c: Vector2i) -> bool:
	return c.x >= 0 and c.y >= 0 and c.x < W and c.y < H and layer("Background/Ground").get_cell_atlas_coords(c) == SEA and not is_rock(c)

# Tout ce qu'on atteint depuis le depart, a pied seulement ou en sachant nager.
func reach(from: Vector2i, swim: bool) -> Dictionary:
	var seen := {from: true}
	var todo: Array = [from]
	while not todo.is_empty():
		var c: Vector2i = todo.pop_front()
		for d in [Vector2i.LEFT, Vector2i.RIGHT, Vector2i.UP, Vector2i.DOWN]:
			var n: Vector2i = c + d
			if n.x < 0 or n.y < 0 or n.x >= W or n.y >= H or seen.has(n):
				continue
			var ok := false
			if swim and is_sea(n):
				ok = true
			elif swim and is_sea(c):
				ok = is_free(n)
			else:
				ok = can_step(c, n)
			if ok:
				seen[n] = true
				todo.append(n)
	return seen

func test() -> void:
	var ground := layer("Background/Ground")
	var relief := layer("Background/Relief")
	var bridges := layer("Background/Bridges")
	var props := layer("World/Props")
	check("la carte fait 62 cases sur 49", ground.get_used_rect() == Rect2i(0, 0, W, H), str(ground.get_used_rect()))
	check("on demarre devant la porte de Ludo", cell() == Vector2i(8, 9), str(cell()))
	check("la carte donne sa chance de rencontre et sa table", int(level().get_meta("encounter_rate", 0)) == 10 and str(level().get_meta("wild", "")).contains("mulotin"))
	# Ce qui bloque.
	check("la mer bloque", not is_free(Vector2i(24, 14)) and not is_free(Vector2i(38, 14)) and not is_free(Vector2i(48, 24)) and not is_free(Vector2i(10, 34)))
	check("le flanc et le bas d'un plateau bloquent", not is_free(Vector2i(12, 12)) and not is_free(Vector2i(6, 9)) and not is_free(Vector2i(23, 22)) and not is_free(Vector2i(43, 36)))
	check("la falaise du nord bloque", not is_free(Vector2i(13, 1)) and not is_free(Vector2i(50, 2)))
	check("le corps d'une maison bloque", not is_free(Vector2i(9, 7)) and not is_free(Vector2i(14, 7)) and not is_free(Vector2i(48, 35)))
	# Ce qui porte.
	check("on marche sur le sable jusqu'au bord de l'eau, pas plus loin", is_free(Vector2i(20, 14)) and not is_free(Vector2i(21, 14)))
	check("un ponton se traverse", is_free(Vector2i(10, 19)) and is_free(Vector2i(16, 21)) and is_free(Vector2i(45, 20)) and is_free(Vector2i(51, 19)) and is_free(Vector2i(17, 26)) and is_free(Vector2i(30, 42)))
	check("la place se parcourt, sur son plateau", is_free(Vector2i(30, 27)) and is_free(Vector2i(26, 24)) and is_free(Vector2i(34, 22)))
	# Le bord du haut d'un plateau est de l'herbe : on s'y tient, on ne le franchit pas.
	check("on se tient sur le bord du haut d'un plateau", is_free(Vector2i(34, 19)) and is_free(Vector2i(26, 20)) and is_free(Vector2i(17, 39)))
	check("mais on ne franchit pas le rebord, ni dans un sens ni dans l'autre", ledge_between(Vector2i(34, 19), Vector2i(34, 18)) and ledge_between(Vector2i(34, 18), Vector2i(34, 19))
		and not can_step(Vector2i(26, 20), Vector2i(26, 19)) and not ledge_between(Vector2i(34, 19), Vector2i(35, 19)) and can_step(Vector2i(34, 20), Vector2i(34, 19)))
	# On passe derriere une maison : la rangee du haut de son toit se franchit.
	check("on passe derriere les maisons, sous leur toit", is_free(Vector2i(48, 4)) and is_free(Vector2i(8, 23)) and is_free(Vector2i(48, 32)))
	check("chez Ludo et la maison orange du nord touchent le mur : rien ne passe derriere", not is_free(Vector2i(8, 3)) and not is_free(Vector2i(9, 4)) and not is_free(Vector2i(15, 3)) and not is_free(Vector2i(15, 4)))
	# Le mur du nord : des gradins superposes, sans agrandir la carte ; la parcelle des deux maisons porte les arbres du pied du mur.
	var mid: TileMapLayer = level().get_node("World/CliffsMid")
	var top: TileMapLayer = level().get_node("World/CliffsTop")
	var stacked := 0
	for c in top.get_used_cells():
		if mid.get_cell_source_id(c) == 5 and level().get_node("World/Cliffs").get_cell_source_id(c) == 5:
			stacked += 1
	check("le mur du nord tient dans ses quatre rangees, en trois gradins poses les uns sur les autres", stacked > 0 and mid.get_used_rect().end.y <= 3 and level().get_node("World/Cliffs").get_used_rect().size.y == 4, "%d cases a trois gradins" % stacked)
	var raised := 0
	for c in level().get_node("World/Trees").get_used_cells():
		if c.x >= 18 and c.x <= 23 and c.y <= 5 and relief.get_cell_source_id(c) != -1:
			raised += 1
	check("la parcelle des deux maisons s'allonge vers l'est et porte les arbres du pied du mur", raised >= 2 and relief.get_cell_source_id(Vector2i(22, 5)) != -1 and is_free(Vector2i(24, 8)), "%d arbres" % raised)
	check("pas de sentier de sable sur l'herbe au pied des escaliers", level().get_node("Background/Paths").get_cell_source_id(Vector2i(8, 14)) == -1 and level().get_node("Background/Paths").get_cell_source_id(Vector2i(48, 16)) == -1)
	var seats: TileMapLayer = level().get_node("World/Props")
	check("les bancs sont les bancs de bois", seats.get_cell_source_id(Vector2i(10, 13)) == 10 and seats.get_cell_atlas_coords(Vector2i(10, 13)) == Vector2i(4, 6) and seats.get_cell_atlas_coords(Vector2i(32, 19)) == Vector2i(4, 6))
	# Un ponton ne touche la terre que par une planche d'arrivee, posee sur la rive.
	var landings := 0
	var loose := 0
	for c in bridges.get_used_cells():
		if bridges.get_cell_source_id(c) != 10 or bridges.get_cell_atlas_coords(c).y >= 3:
			continue                # les pilotis ; les escaliers, dessines sur le meme calque
		var on_water := ground.get_cell_atlas_coords(c) == UNDER_DECK
		if bridges.get_cell_atlas_coords(c).y >= 1:
			landings += 1
			if on_water:
				loose += 1
			continue
		for d in [Vector2i.LEFT, Vector2i.RIGHT, Vector2i.UP, Vector2i.DOWN]:
			var a := ground.get_cell_atlas_coords(c + d)
			if a != SEA and a != UNDER_DECK and bridges.get_cell_source_id(c + d) != 10:
				loose += 1
	check("chaque ponton arrive sur la rive par ses planches de bout, jamais par le flanc", landings == 16 and loose == 0, "%d planches de bout, %d contacts sans planche" % [landings, loose])
	# Un escalier : des marches a poteaux posees sur le bord du plateau, qui garde son dessin sans sa collision.
	var steps := 0
	var steps_ok := true
	var upside_down := 0
	for c in bridges.get_used_cells():
		var a := bridges.get_cell_atlas_coords(c)
		if bridges.get_cell_source_id(c) != 10 or a.y < 3 or a.y > 4 or a.x > 7:
			continue
		if a.x == 2 or a.x == 3:
			upside_down += 1
		if relief.get_cell_alternative_tile(c) == 1:
			steps += 1
			if not is_free(c):
				steps_ok = false
	check("neuf escaliers de deux cases, tous praticables", steps == 18 and steps_ok, "%d cases" % steps)
	check("aucun escalier a l'envers", upside_down == 0, "%d" % upside_down)
	check("le labo est un etage plus haut : deux escaliers l'un au-dessus de l'autre", is_free(Vector2i(48, 11)) and is_free(Vector2i(48, 14)) and not is_free(Vector2i(47, 11)) and not is_free(Vector2i(47, 14))
		and not find_path(Vector2i(48, 16), Vector2i(48, 10)).is_empty())
	# On ne monte pas sur la place par le nord, et le nord ne touche pas l'ile du centre.
	check("la crique du nord est separee de l'ile du centre par la baie", not is_free(Vector2i(30, 13)) and not is_free(Vector2i(31, 16)))
	var by_east: Array = find_path(Vector2i(30, 5), Vector2i(30, 27))
	var through_ne_deck := false
	for c in by_east:
		if c == Vector2i(45, 20) or c == Vector2i(45, 21):
			through_ne_deck = true
	var blocked: Array = []
	for c in bridges.get_used_cells():
		if c.x >= 39 and c.y >= 18 and c.y <= 22 and bridges.get_cell_source_id(c) == 10 and bridges.get_cell_atlas_coords(c).y < 3:
			blocked.append(c)
	var by_west: Array = find_path(Vector2i(30, 5), Vector2i(30, 27), blocked)
	check("de la trouee a la place, on passe par un ponton : celui du nord-est, ou celui du nord-ouest", not by_east.is_empty() and not by_west.is_empty() and (through_ne_deck or by_east.size() <= by_west.size()),
		"%d pas par le plus court, %d sans le ponton du nord-est" % [by_east.size(), by_west.size()])
	# Le dallage de la place repose sur l'herbe du plateau.
	var paving_ok := true
	for c in layer("Background/Plaza").get_used_cells():
		if relief.get_cell_atlas_coords(c) != Vector2i(39, 25):
			paving_ok = false
	check("le dallage est tout entier sur le dessus du plateau", paving_ok and layer("Background/Plaza").get_used_cells().size() == 45)
	# Lampadaires et panneaux : sur la terre ferme, jamais sur un ponton.
	var on_land := true
	var posts := 0
	for n in level().get_node("World").get_children():
		if str(n.name).begins_with("Lamp") or str(n.name).begins_with("Sign"):
			posts += 1
			var c := Vector2i(floori(n.position.x / 16.0), floori(n.position.y / 16.0))
			var a := ground.get_cell_atlas_coords(c)
			if a == SEA or a == UNDER_DECK or bridges.get_cell_source_id(c) != -1:
				on_land = false
	check("lampadaires et panneaux sont sur la terre ferme", posts == 18 and on_land, "%d poteaux" % posts)
	# Le mobilier : de vrais bancs, pleins ; un parasol dont seul le pied arrete ; une serviette qui se foule.
	var benches := 0
	for c in props.get_used_cells():
		if props.get_cell_source_id(c) == 10 and props.get_cell_atlas_coords(c) == Vector2i(4, 6) and not is_free(c) and not is_free(c + Vector2i.RIGHT):
			benches += 1
	check("cinq bancs de bois, pleins", benches == 5, "%d" % benches)
	check("le pied d'un parasol et les caisses du quai arretent", not is_free(Vector2i(37, 37)) and not is_free(Vector2i(22, 9)) and not is_free(Vector2i(33, 41)) and not is_free(Vector2i(34, 41)))
	check("on passe sous la toile d'un parasol et sur une serviette", is_free(Vector2i(37, 36)) and is_free(Vector2i(24, 8)) and is_free(Vector2i(39, 36)))
	check("un pot de fleurs de chaque cote de la porte, jamais devant", not is_free(Vector2i(14, 8)) and not is_free(Vector2i(16, 8)) and is_free(Vector2i(15, 8)))
	check("des habitants vivent la : pres d'un banc, d'un parasol, d'un ponton, des herbes",
		cell_of("BenchLady") == Vector2i(12, 13) and cell_of("Sunbather") == Vector2i(39, 37) and cell_of("Swimmer") == Vector2i(24, 9) and cell_of("ShellKid") == Vector2i(28, 9)
		and cell_of("Sailor") == Vector2i(53, 18) and cell_of("Youngster") == Vector2i(25, 7) and cell_of("Gardener") == Vector2i(46, 41))
	# Tout se rejoint a pied, depuis le depart.
	var from := Vector2i(8, 9)
	for goal in [["la porte de la bibliotheque", Vector2i(8, 28)], ["la porte du labo", Vector2i(48, 10)], ["la maison orange du nord-ouest", Vector2i(15, 8)],
			["la maison orange du sud-est", Vector2i(48, 38)], ["la place", Vector2i(30, 27)], ["le ponton de la cloche", Vector2i(19, 26)],
			["le bout de la jetee du sud", Vector2i(30, 43)], ["les hautes herbes du sud-ouest", Vector2i(9, 41)], ["la trouee de la falaise", Vector2i(30, 4)],
			["la crique du nord", Vector2i(30, 9)], ["la plage du sud-est", Vector2i(42, 42)], ["la pointe de l'est", Vector2i(56, 28)]]:
		var path: Array = find_path(from, goal[1])
		check("on rejoint a pied " + goal[0], not path.is_empty(), "%d pas" % path.size())
	# La terre de l'ouest ne tient au reste que par ses deux pontons.
	var cut: Array = []
	for c in bridges.get_used_cells():
		if c.x <= 21 and c.y >= 18 and c.y <= 28:
			cut.append(c)
	# (la recherche de chemin deborde d'une case autour de la carte : on lui ferme ce tour)
	for x in range(-1, W + 1):
		cut.append(Vector2i(x, -1)); cut.append(Vector2i(x, H))
	for y in range(-1, H + 1):
		cut.append(Vector2i(-1, y)); cut.append(Vector2i(W, y))
	check("sans ses pontons, la bibliotheque est coupee du reste", find_path(from, Vector2i(8, 28), cut).is_empty())
	# Le decor ferme la carte, a pied comme a la nage.
	var walked := reach(from, false)
	var in_margin := 0
	var on_edge := 0
	for c in walked:
		if c.x < 4 or c.x >= W - 4 or c.y >= H - 3:
			in_margin += 1
		if c.x == 0 or c.x == W - 1 or c.y == 0 or c.y == H - 1:
			on_edge += 1
	check("a pied, aucune case de la marge n'est atteignable (4 colonnes, 3 rangees en bas)", in_margin == 0, "%d cases" % in_margin)
	check("ni aucune case du bord de la carte", on_edge == 0, "%d cases" % on_edge)
	var swum := reach(from, true)
	var escaped := 0
	for c in swum:
		if c.x == 0 or c.x == W - 1 or c.y == H - 1 or ((c.x < 4 or c.x >= W - 4 or c.y >= H - 3) and not is_sea(c)):
			escaped += 1
	check("a la nage non plus : on n'atteint ni le bord, ni la terre de la marge", escaped == 0 and swum.size() > walked.size() + 200, "%d cases hors de la carte, %d atteintes" % [escaped, swum.size()])
	var rocks := 0
	var mossy := 0
	for c in props.get_used_cells():
		if is_rock(c):
			rocks += 1
		var a := props.get_cell_atlas_coords(c)
		if props.get_cell_source_id(c) == 5 and a.y >= 30 and a.y <= 31 and a.x >= 26 and a.x <= 31:
			mossy += 1
	check("les barrieres restent discretes", rocks >= 30 and rocks <= 90, "%d cases de rocher dans l'eau" % rocks)
	check("aucun rocher moussu : ce sont des obstacles speciaux", mossy == 0, "%d" % mossy)
	var fruit := 0
	var trees := layer("World/Trees")
	for c in trees.get_used_cells():
		if trees.get_cell_atlas_coords(c) == Vector2i(24, 0):
			fruit += 1
	check("aucun arbre a fruits", fruit == 0 and trees.get_used_cells().size() > 100, "%d arbres" % trees.get_used_cells().size())
	# Les grandes fleurs se traversent ; un petit sapin, non.
	var bloom_ok := true
	var pine_ok := true
	var blooms := 0
	var pines := 0
	for c in props.get_used_cells():
		if props.get_cell_source_id(c) != 5:
			continue
		var a := props.get_cell_atlas_coords(c)
		if a.y == 4 and a.x <= 7:
			blooms += 1
			if not is_free(c):
				bloom_ok = false
		elif a.y == 1 and a.x >= 33 and a.x <= 38:
			pines += 1
			if is_free(c):
				pine_ok = false
	check("les grandes fleurs n'arretent personne", blooms > 0 and bloom_ok, "%d fleurs" % blooms)
	check("un petit sapin arrete", pines > 0 and pine_ok, "%d sapins" % pines)
