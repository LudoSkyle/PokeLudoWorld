extends "res://tests/lib.gd"

# Les portes de l'ile : les cinq batiments s'ouvrent, et l'on ressort devant chacun.

func scene() -> String:
	return "start_island"

func start() -> Vector2i:
	return Vector2i(15, 9)

func visit(label: String, front: Vector2i, inside: String) -> void:
	await place(front)
	await hold_until_change("porte de " + label, "ui_up")
	check("on entre " + label, str(level().scene_file_path).ends_with(inside + ".tscn"), str(level().scene_file_path))
	await hold_until_change("paillasson de " + label, "ui_down")
	await arrival("retour devant " + label, front, "idle_down")

func test() -> void:
	await visit("chez Anselme, la maison orange du nord-ouest", Vector2i(15, 9), "orange_house_north")
	await visit("chez Ludo", Vector2i(8, 10), "ludo_house")
	await visit("la bibliotheque", Vector2i(8, 28), "library")
	await visit("le laboratoire", Vector2i(48, 10), "lab_house")
	await visit("chez Solange, la maison orange du sud-est", Vector2i(48, 38), "orange_house_south")

	# Une porte est un decor franchissable : triee depuis le haut de sa case, sinon elle se dessine sur le joueur qui entre.
	var houses: TileMapLayer = level().get_node("World/Houses")
	var doors := level().get_node("Doors").get_children()
	var behind := 0
	for door in doors:
		var data: TileData = houses.get_cell_tile_data(Vector2i(floori(door.position.x / 16.0), floori(door.position.y / 16.0)))
		if data != null and data.y_sort_origin == -15:
			behind += 1
	check("les cinq portes passent sous le joueur qui entre", doors.size() == 5 and behind == 5, "%d sur %d" % [behind, doors.size()])
