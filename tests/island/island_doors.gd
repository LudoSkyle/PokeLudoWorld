extends "res://tests/lib.gd"

# Les portes de l'ile : les cinq batiments s'ouvrent, et l'on ressort devant chacun.

func scene() -> String:
	return "start_island"

func start() -> Vector2i:
	return Vector2i(13, 10)

func visit(label: String, front: Vector2i, inside: String) -> void:
	await place(front)
	await hold_until_change("porte de " + label, "ui_up")
	check("on entre " + label, str(level().scene_file_path).ends_with(inside + ".tscn"), str(level().scene_file_path))
	await hold_until_change("paillasson de " + label, "ui_down")
	await arrival("retour devant " + label, front, "idle_down")

func test() -> void:
	await visit("chez Anselme, la maison du nord-ouest", Vector2i(13, 10), "orange_house_north")
	await visit("chez Ludo", Vector2i(6, 9), "ludo_house")
	await visit("la bibliotheque", Vector2i(3, 30), "library")
	await visit("le laboratoire", Vector2i(45, 9), "lab_house")
	await visit("chez Solange, la maison du sud-est", Vector2i(43, 34), "orange_house_south")

	# Chaque maison est une seule tuile, triee juste derriere la rangee de son pied : le joueur qui entre passe devant elle, celui qui la contourne passe derriere son toit.
	var houses: TileMapLayer = level().get_node("World/Houses")
	var doors := level().get_node("Doors").get_children().filter(func(d): return not str(d.name).begins_with("Nord"))   # les cinq cases de la trouee du nord menent a la route, pas a une maison
	var behind := 0
	for door in doors:
		var data: TileData = houses.get_cell_tile_data(Vector2i(floori(door.position.x / 16.0), floori(door.position.y / 16.0)))
		if data == null and not is_free(Vector2i(floori(door.position.x / 16.0) - 1, floori(door.position.y / 16.0))) and is_free(Vector2i(floori(door.position.x / 16.0), floori(door.position.y / 16.0))):
			behind += 1
	check("les cinq portes sont des cases libres dans un mur plein", doors.size() == 5 and behind == 5, "%d sur %d" % [behind, doors.size()])
	var sorted_behind := 0
	for c in houses.get_used_cells():
		if houses.get_cell_tile_data(c).y_sort_origin == -1:
			sorted_behind += 1
	check("cinq maisons, chacune d'une seule tuile triee derriere qui se tient a sa porte", houses.get_used_cells().size() == 5 and sorted_behind == 5, "%d" % sorted_behind)
