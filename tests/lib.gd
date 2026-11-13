extends SceneTree

# Outils communs aux tests. Chaque test herite de ce fichier et ecrit test().
# Tout se joue avec de VRAIES entrees clavier : aucun teleport.

const VP := "Control/SubViewportContainer/SubViewport"
const DIRS := {Vector2i(0, -1): "ui_up", Vector2i(0, 1): "ui_down",
	Vector2i(-1, 0): "ui_left", Vector2i(1, 0): "ui_right"}
const STAIR_MAT := Vector2i(11, 8)
const EXIT_MAT := Vector2i(15, 14)

var game: Node
var failures := 0

func _initialize() -> void:
	_run.call_deferred()

func wait(n: int) -> void:
	for i in n:
		await process_frame

func level() -> Node2D:
	return game.get_node_or_null(VP + "/Level")

func level_id() -> int:
	return -1 if level() == null else level().get_instance_id()

func player() -> Node2D:
	var l := level()
	return null if l == null else l.get_node_or_null("World/Entities/Player")

func cell() -> Vector2i:
	var p := player().position
	return Vector2i(floori(p.x / 16.0), floori(p.y / 16.0))

func is_free(c: Vector2i) -> bool:
	var q := PhysicsPointQueryParameters2D.new()
	q.collide_with_bodies = true
	q.collide_with_areas = false
	q.collision_mask = 1
	q.position = level().global_position + Vector2(c.x * 16 + 8, c.y * 16 + 8)
	return level().get_world_2d().direct_space_state.intersect_point(q, 1).is_empty()

func find_path(from: Vector2i, to: Vector2i, avoid: Array = []) -> Array:
	var prev := {from: from}
	var todo: Array = [from]
	while not todo.is_empty():
		var c: Vector2i = todo.pop_front()
		if c == to:
			break
		for d in DIRS.keys():
			var n: Vector2i = c + d
			if n.x < -1 or n.y < -1 or n.x > 45 or n.y > 25 or prev.has(n) or (n in avoid and n != to):
				continue
			if is_free(n):
				prev[n] = c
				todo.append(n)
	if not prev.has(to):
		return []
	var path: Array = []
	var c: Vector2i = to
	while c != from:
		path.push_front(c)
		c = prev[c]
	return path

func check(label: String, ok: bool, detail: String = "") -> void:
	if not ok:
		failures += 1
	print("%s  %-54s %s" % ["OK  " if ok else "FAIL", label, detail])

func shot(name: String) -> void:
	root.get_texture().get_image().save_png("user://w_%s.png" % name)

func walk(label: String, to: Vector2i, expect_change: bool, avoid: Array = []) -> void:
	var path := find_path(cell(), to, avoid)
	check(label + " : chemin trouve", not path.is_empty(), "%d pas" % path.size())
	if path.is_empty():
		return
	var id := level_id()
	for target in path:
		var d: Vector2i = target - cell()
		Input.action_press(DIRS[d])
		var guard := 0
		while guard < 240 and level_id() == id and cell() != target:
			await process_frame
			guard += 1
		Input.action_release(DIRS[d])
		await wait(3)
		if level_id() != id:
			break
	if expect_change:
		var guard2 := 0
		while guard2 < 300 and level_id() == id:
			await process_frame
			guard2 += 1
		check(label + " : la carte a change", level_id() != id)
		await wait(90)
	else:
		await wait(45)
		check(label + " : arrive sur la case", cell() == to, str(cell()))
		check(label + " : PAS de changement de carte", level_id() == id)

func hold_until_change(label: String, action: String) -> void:
	var id := level_id()
	Input.action_press(action)
	var guard := 0
	while guard < 300 and level_id() == id:
		await process_frame
		guard += 1
	Input.action_release(action)
	check(label + " : la carte a change", level_id() != id)
	await wait(90)

func hold_no_change(label: String, action: String) -> void:
	var id := level_id()
	var c := cell()
	Input.action_press(action)
	await wait(70)
	Input.action_release(action)
	await wait(20)
	check(label + " : PAS de changement de carte", level_id() == id)
	check(label + " : reste sur place", cell() == c, str(cell()))

func face_left_and_shoot(name: String) -> void:
	Input.action_press("ui_left"); await wait(2); Input.action_release("ui_left"); await wait(12)
	shot(name)

func examine(label: String, from: Vector2i, expected: String) -> void:
	# marche jusqu'a la case, se tourne vers le haut d'une pression breve, examine
	await walk(label + " : approche", from, false)
	Input.action_press("ui_up"); await wait(2); Input.action_release("ui_up"); await wait(6)
	Input.action_press("interact"); await wait(2); Input.action_release("interact")
	await wait(150)
	var box: Control = game.get_node(VP + "/MessageBox/Control/Box")
	var text: String = game.get_node(VP + "/MessageBox/Control/Box/Text").text
	if expected == "":
		check(label + " : rien a lire", not box.visible, text)
	else:
		check(label + " : la boite s'ouvre", box.visible)
		check(label + " : dit ce qu'il faut", text.to_lower().contains(expected), text)
		print("     > " + text)
	var n := 0
	while box.visible and n < 12:
		Input.action_press("interact"); await wait(2); Input.action_release("interact"); await wait(60)
		n += 1
	check(label + " : la boite est refermee", not box.visible)
	check(label + " : on n'a pas bouge", cell() == from, str(cell()))

func arrival(label: String, expected: Vector2i, anim: String) -> void:
	var p0 := player().position
	await wait(80)
	var p1 := player().position
	var sprite: AnimatedSprite2D = player().get_node("Sprite")
	check(label + " : arrive en %s" % str(expected), cell() == expected, "case %s" % str(cell()))
	check(label + " : immobile apres l'arrivee", p0 == p1, "%s -> %s" % [p0, p1])
	check(label + " : regarde du bon cote", str(sprite.animation) == anim, str(sprite.animation))
	check(label + " : case d'arrivee libre", is_free(cell()))
	shot(label.replace(" ", "_").replace("'", ""))

func hold_and_count_changes(action: String, frames: int) -> int:
	# maintient une touche sans la relacher et compte les changements de carte
	var last := level_id()
	var changes := 0
	Input.action_press(action)
	for i in frames:
		await process_frame
		if level_id() != last and level_id() != -1:
			changes += 1
			last = level_id()
	Input.action_release(action)
	await wait(20)
	return changes

func enter(label: String, door: Vector2i) -> void:
	await walk(label, door, true)

func test() -> void:
	pass

func _run() -> void:
	root.size = Vector2i(1152, 648)
	var packed: PackedScene = load("res://src/main/kotlin/fr/skyle/pokeludoworld/scenes/core/game_manager.tscn")
	game = packed.instantiate()
	root.add_child(game)
	await wait(20)
	await test()
	print("RESULTAT : %s" % ("TOUT PASSE" if failures == 0 else "%d ECHEC(S)" % failures))
	quit()
