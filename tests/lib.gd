extends SceneTree

# Outils communs aux tests. Chaque test herite de ce fichier et ecrit test().
#
# Un test est PETIT : un dialogue, une porte, une piece, un deplacement. Il
# demarre directement sur sa carte et sa case (scene() et start()) pour ne pas
# rejouer le trajet depuis le village. Ce placement est une mise en place ;
# tout ce qui est VERIFIE se joue avec de vraies entrees clavier.

const VP := "Control/SubViewportContainer/SubViewport"
const LEVELS := "res://src/main/kotlin/fr/skyle/pokeludoworld/scenes/levels/"
const DIRS := {Vector2i(0, -1): "ui_up", Vector2i(0, 1): "ui_down",
	Vector2i(-1, 0): "ui_left", Vector2i(1, 0): "ui_right"}
const STAIR_MAT := Vector2i(11, 8)
const EXIT_MAT := Vector2i(15, 14)

var game: Node
var failures := 0

# Carte de depart : nom d'un fichier de scenes/levels, sans extension.
func scene() -> String:
	return "start_town"

# Case de depart. (-1, -1) = la ou la carte fait apparaitre le joueur.
func start() -> Vector2i:
	return Vector2i(-1, -1)

func _initialize() -> void:
	_run.call_deferred()

func wait(n: int) -> void:
	for i in n:
		await process_frame

# Attend en SECONDES : les images ne durent pas pareil sur tous les ecrans.
func secs(t: float) -> void:
	var end := Time.get_ticks_msec() + int(t * 1000.0)
	while Time.get_ticks_msec() < end:
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
	check(label + " : chemin trouve", cell() == to or not path.is_empty(), "%d pas" % path.size())
	if path.is_empty() and cell() != to:
		return
	var id := level_id()
	var replans := 0
	while not path.is_empty():
		var target: Vector2i = path.pop_front()
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
		# Un PNJ qui bouge a pu se mettre en travers : on recalcule la route.
		if cell() != target and replans < 20:
			replans += 1
			await wait(20)
			path = find_path(cell(), to, avoid)
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

func examine(label: String, from: Vector2i, expected: String, facing: String = "ui_up") -> void:
	# marche jusqu'a la case, se tourne d'une pression breve, examine
	await walk(label + " : approche", from, false)
	Input.action_press(facing); await wait(2); Input.action_release(facing); await wait(6)
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

func hold_and_count_changes(action: String, seconds: float) -> int:
	# maintient une touche sans la relacher et compte les changements de carte
	var last := level_id()
	var changes := 0
	Input.action_press(action)
	var end := Time.get_ticks_msec() + int(seconds * 1000.0)
	while Time.get_ticks_msec() < end:
		await process_frame
		if level_id() != last and level_id() != -1:
			changes += 1
			last = level_id()
	Input.action_release(action)
	await wait(20)
	return changes

func enter(label: String, door: Vector2i) -> void:
	await walk(label, door, true)

# --- PNJ

const ENT := VP + "/Level/World/Entities/"

func npc(n: String) -> Node2D:
	return game.get_node(ENT + n)

func anim(n: String) -> String:
	return str(npc(n).get_node("Sprite").animation)

func box() -> Control:
	return game.get_node(VP + "/MessageBox/Control/Box")

func box_text() -> String:
	return game.get_node(VP + "/MessageBox/Control/Box/Text").text

func tap(action: String) -> void:
	Input.action_press(action); await wait(2); Input.action_release(action); await wait(8)

func close_box() -> void:
	var n := 0
	while box().visible and n < 12:
		Input.action_press("interact"); await wait(2); Input.action_release("interact"); await wait(60)
		n += 1

func talk(label: String, from: Vector2i, facing: String, who: String, expected: String, npc_anim: String) -> void:
	await walk(label + " : approche", from, false)
	await tap(facing)
	Input.action_press("interact"); await wait(2); Input.action_release("interact")
	await wait(150)
	check(label + " : la boite s'ouvre", box().visible)
	check(label + " : dit ce qu'il faut", box_text().to_lower().contains(expected), box_text())
	check(label + " : se tourne vers nous", anim(who) == npc_anim, anim(who))
	await close_box()
	check(label + " : la boite est refermee", not box().visible)
	check(label + " : on n'a pas bouge", cell() == from, str(cell()))

func cell_of(n: String) -> Vector2i:
	var p := npc(n).position
	return Vector2i(floori(p.x / 16.0), floori(p.y / 16.0))

# Vrai quand le PNJ est pose sur un centre de case (pas au milieu d'un pas).
func resting(n: String) -> bool:
	var p := npc(n).position
	return is_equal_approx(fmod(p.x, 16.0), 8.0) and is_equal_approx(fmod(p.y, 16.0), 8.0)

# --- menu de pause

func menu() -> Node:
	return game.get_node(VP + "/PauseMenu")

func menu_open() -> bool:
	return game.get_node(VP + "/PauseMenu/Control/Menu").visible

# Ligne (0, 1, 2...) en face de laquelle le curseur est dessine.
func menu_cursor_line() -> int:
	var cursor: Control = game.get_node(VP + "/PauseMenu/Control/Menu/Cursor")
	var list: Control = game.get_node(VP + "/PauseMenu/Control/Menu/Entries")
	var middle := cursor.position.y + cursor.size.y / 2.0 - list.position.y
	return floori(middle / 64.0)

# Nom du noeud de l'entree en face du curseur : Bag, Options, Quit.
func menu_selected() -> String:
	var list: Control = game.get_node(VP + "/PauseMenu/Control/Menu/Entries")
	var line := menu_cursor_line()
	return "" if line < 0 or line >= list.get_child_count() else str(list.get_child(line).name)

# Ouvre le menu s'il est ferme, descend jusqu'a l'entree nommee (Bag, Save,
# Options, Quit) et la valide.
func menu_pick(entry: String) -> void:
	if not menu_open():
		await tap("menu")
	var n := 0
	while menu_selected() != entry and n < 8:
		await tap("ui_down")
		n += 1
	await tap("interact")

func options_open() -> bool:
	return game.get_node(VP + "/OptionsMenu/Control/Screen").visible

# Nom du choix de vitesse affiche en rouge : Half, One, Two, Four.
func options_speed() -> String:
	var red := ""
	for label in game.get_node(VP + "/OptionsMenu/Control/Screen/Rows/TextSpeed/Choices").get_children():
		if label.get_theme_color("font_color").r > 0.8:
			red += str(label.name)
	return red

# Nom du choix de langue affiche en rouge : French, English.
func options_language() -> String:
	var red := ""
	for label in game.get_node(VP + "/OptionsMenu/Control/Screen/Rows/Language/Choices").get_children():
		if not str(label.name).begins_with("PixelShadow") and label.get_theme_color("font_color").r > 0.8:
			red += str(label.name)
	return red

func letter_seconds() -> float:
	return game.get_node(VP + "/MessageBox").seconds_per_letter

# --- bandeau de lieu

func banner() -> Control:
	return game.get_node(VP + "/LocationBanner/Control/Panel")

func banner_text() -> String:
	return game.get_node(VP + "/LocationBanner/Control/Panel/Name").text

# Regarde le bandeau pendant t secondes : [est apparu, texte, hauteur la plus basse]
func watch_banner(t: float, name: String = "") -> Array:
	var shown := false
	var text := ""
	var lowest := -999.0
	var end := Time.get_ticks_msec() + int(t * 1000.0)
	while Time.get_ticks_msec() < end:
		await process_frame
		if banner().visible:
			shown = true
			text = banner_text()
			if banner().position.y > lowest:
				lowest = banner().position.y
				if name != "" and lowest >= 24.0:
					shot(name); name = ""
	return [shown, text, lowest]

func test() -> void:
	pass

# Lance le jeu. load_save = reprendre la sauvegarde de test, comme au vrai
# lancement ; sinon on part de scene() et start().
func boot(load_save: bool) -> void:
	var packed: PackedScene = load("res://src/main/kotlin/fr/skyle/pokeludoworld/scenes/core/game_manager.tscn")
	game = packed.instantiate()
	var scenes := game.get_node(VP + "/SceneManager")
	scenes.start_scene = LEVELS + scene() + ".tscn"
	scenes.load_save = load_save
	root.add_child(game)
	await wait(20)

# Quitte le jeu et le relance en reprenant la sauvegarde.
func relaunch() -> void:
	root.remove_child(game)
	game.free()
	await wait(5)
	await boot(true)

# --- sac

func bag(path: String) -> Node:
	return game.get_node(VP + "/BagMenu/Control/Screen/" + path)

func bag_open() -> bool:
	return game.get_node(VP + "/BagMenu/Control/Screen").visible

# Les lignes non vides de la liste, avec leur quantite : ["Potion x3", "Retour"]
func bag_rows() -> Array:
	var rows: Array = []
	for i in 6:
		var name: String = bag("Names/Row%d" % i).text
		var amount: String = bag("Amounts/Row%d" % i).text
		if name != "":
			rows.append(name if amount == "" else name + " " + amount)
	return rows

# Ligne (0..5) en face de laquelle le curseur du sac est dessine.
func bag_line() -> int:
	var cursor: Control = bag("Cursor")
	return floori((cursor.position.y + cursor.size.y / 2.0 - bag("Names").position.y) / 64.0)

# Remplit le sac par l'entree Debug du menu, comme le ferait le joueur :
# huit objets (x3 a x10), des Poke Balls (x11) et deux objets rares.
func fill_bag() -> void:
	await menu_pick("Debug")
	# Le premier message se passe a la touche ; les deux objets rares
	# s'annoncent ensuite et passent tout seuls, sans tenir compte des touches.
	var end := Time.get_ticks_msec() + 15000
	while Time.get_ticks_msec() < end and box().visible:
		await tap("interact")
		await secs(0.2)
	await wait(10)

func bag_choices() -> Control:
	return bag("Choices")

# Les reponses proposees par la boite de choix du sac : ["Jeter", "Annuler"]
func bag_answers() -> Array:
	var answers: Array = []
	for label in bag("Choices/Entries").get_children():
		if label.visible:
			answers.append(label.text)
	return answers

func reveal() -> Control:
	return game.get_node(VP + "/ItemReveal/Control/Panel")

# --- sauvegarde

func save_summary() -> Control:
	return game.get_node(VP + "/SaveMenu/Control/Summary")

func save_choices() -> Control:
	return game.get_node(VP + "/SaveMenu/Control/Choices")

func saved_file() -> ConfigFile:
	var file := ConfigFile.new()
	file.load("user://test_save.cfg")
	return file

# Attend que la question soit ecrite et que Oui/Non apparaisse.
func wait_choices() -> void:
	var end := Time.get_ticks_msec() + 4000
	while Time.get_ticks_msec() < end and not save_choices().visible:
		await process_frame
	await wait(4)

# --- drapeaux d'histoire

func flag(name: String) -> bool:
	return root.get_node("Globals").has_flag(name)

func set_flag(name: String) -> void:
	root.get_node("Globals").set_flag(name)

# --- noeuds de test
#
# Les briques de quete se verifient sans scenario : le test pose lui-meme un
# PNJ, un meuble, un panneau ou un passage sur la carte, avec ses reglages.

const SCENES := "res://src/main/kotlin/fr/skyle/pokeludoworld/scenes/"
const SPAWNABLE := {
	"npc": [SCENES + "characters/npc.tscn", "World/Entities"],
	"readable": [SCENES + "levels/readable.tscn", "World"],
	"sign": [SCENES + "levels/sign.tscn", "World"],
	"roadblock": [SCENES + "levels/roadblock.tscn", "Triggers"],
}

# Pose un noeud sur une case. props : ses proprietes telles qu'un .tscn les
# ecrit (snake_case). Renvoie le noeud ; s'il a quitte la carte de lui-meme,
# is_instance_valid(noeud) est faux.
func spawn(kind: String, name: String, at: Vector2i, props: Dictionary = {}) -> Node:
	var node: Node2D = load(SPAWNABLE[kind][0]).instantiate()
	node.name = name
	for key in props:
		if not key in node:
			check("%s : la propriete %s existe" % [name, key], false)
		node.set(key, props[key])
	node.position = Vector2(at.x * 16 + 8, at.y * 16 + 8)
	level().get_node(SPAWNABLE[kind][1]).add_child(node)
	await wait(4)
	return node

# --- question dans un dialogue

func ask_choices() -> Control:
	return game.get_node(VP + "/MessageBox/Control/Choices")

# Attend que la question soit ecrite et que Oui/Non apparaisse.
func wait_ask() -> void:
	var end := Time.get_ticks_msec() + 4000
	while Time.get_ticks_msec() < end and not ask_choices().visible:
		await process_frame
	await wait(4)

# Ligne (0 = Oui, 1 = Non) en face de laquelle le curseur de la question est dessine.
func ask_line() -> int:
	var cursor: Control = ask_choices().get_node("Cursor")
	return floori((cursor.position.y + cursor.size.y / 2.0 - ask_choices().get_node("Entries").position.y) / 64.0)

# Se tourne vers la case voisine et l'examine, sans rien verifier.
func interact_facing(facing: String) -> void:
	await tap(facing)
	await tap("interact")

# Attend qu'un texte soit entierement ecrit dans la boite (au plus t secondes).
func wait_text(expected: String, t: float = 4.0) -> void:
	var end := Time.get_ticks_msec() + int(t * 1000.0)
	while Time.get_ticks_msec() < end and box_text() != expected:
		await process_frame
	await wait(2)

func _run() -> void:
	root.size = Vector2i(1152, 648)
	# Etat neuf a chaque test : ni reglages ni sauvegarde d'un test precedent.
	# Ce sont des fichiers de test, ceux du joueur ne sont jamais touches.
	for file in ["user://test_settings.cfg", "user://test_save.cfg"]:
		if FileAccess.file_exists(file):
			DirAccess.remove_absolute(file)
	await boot(false)
	if start() != Vector2i(-1, -1):
		player().position = Vector2(start().x * 16 + 8, start().y * 16 + 8)
		await wait(10)
	await test()
	print("RESULTAT : %s" % ("TOUT PASSE" if failures == 0 else "%d ECHEC(S)" % failures))
	quit()
