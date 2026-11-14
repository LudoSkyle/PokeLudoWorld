# Releve la grille de collisions et les portes de chaque carte fermee.
# Lu par tests/audit.py.
extends SceneTree

const BASE := "res://src/main/kotlin/fr/skyle/pokeludoworld/scenes/levels/"
const ROOMS := ["ludo_house", "ludo_bedroom", "library", "lab_house", "cave_1f", "cave_b1f", "cave_b2f"]

func _initialize() -> void:
	_run.call_deferred()

func _run() -> void:
	root.size = Vector2i(1152, 648)
	for room in ROOMS:
		var level: Node2D = load(BASE + room + ".tscn").instantiate()
		root.add_child(level)
		var cam := Camera2D.new()
		cam.position = Vector2(256, 160)
		cam.zoom = Vector2(2, 2)
		level.add_child(cam)
		cam.make_current()
		for i in 12:
			await process_frame
		await physics_frame
		await physics_frame
		print("ROOM " + room)
		var space := level.get_world_2d().direct_space_state
		for y in 20:
			var line := ""
			for x in 32:
				var q := PhysicsPointQueryParameters2D.new()
				q.collision_mask = 1
				q.position = Vector2(x * 16 + 8, y * 16 + 8)
				line += "." if space.intersect_point(q, 1).is_empty() else "#"
			print("GRID " + line)
		for d in level.get_node("Doors").get_children():
			var e: Vector2 = d.get("entry_direction")
			var x: Vector2 = d.get("exit_direction")
			print("DOOR %s %d %d %d %d %d %d" % [d.name, floori(d.position.x / 16.0),
				floori(d.position.y / 16.0), int(e.x), int(e.y), int(x.x), int(x.y)])
		root.get_texture().get_image().save_png("user://room_%s.png" % room)
		root.remove_child(level)
		level.free()
		await process_frame
	print("FIN")
	quit()
