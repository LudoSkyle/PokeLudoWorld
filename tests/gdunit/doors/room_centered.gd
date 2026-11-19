extends "res://tests/gdunit/game_suite.gd"

# Une piece plus petite que l'ecran est centree, sans son remplissage noir, et
# la camera ne bouge plus quand on s'y promene.

func scene() -> String:
	return "ludo_house"

func start() -> Vector2i:
	return Vector2i(15, 13)

func test_room_centered() -> void:
	if game == null:
		return
	var cam: Camera2D = player().get_node("Camera")
	check("l'ecran montre 20 cases sur 15", get_tree().root.size == Vector2i(1280, 960) and cam.zoom == Vector2(4, 4), "%s zoom %s" % [get_tree().root.size, cam.zoom])
	var walls: TileMapLayer = level().get_node("Background/Walls")
	var ground: TileMapLayer = level().get_node("Background/Ground")
	# La piece : du haut des murs au bas du sol clair.
	var room := Rect2i()
	for c in ground.get_used_cells():
		if ground.get_cell_atlas_coords(c) != Vector2i(65, 49):
			room = Rect2i(c, Vector2i.ONE) if room.size == Vector2i.ZERO else room.expand(c).expand(c + Vector2i.ONE)
	for c in walls.get_used_cells():
		room = room.expand(c).expand(c + Vector2i.ONE)
	var middle: Vector2 = ground.global_position + Vector2(room.position * 16) + Vector2(room.size * 16) / 2.0
	check("la piece est plus petite que l'ecran", room.size.x < 20 and room.size.y < 15, str(room))
	var before := cam.get_screen_center_position()
	check("elle est au milieu de l'ecran", before.distance_to(middle) < 1.0, "%s contre %s" % [before, middle])
	await walk("vers le coin", Vector2i(10, 11), false)
	check("la camera ne bouge pas quand on s'y promene", cam.get_screen_center_position().distance_to(before) < 0.5, str(cam.get_screen_center_position()))
