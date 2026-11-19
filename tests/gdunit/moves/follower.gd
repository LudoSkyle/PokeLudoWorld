extends "res://tests/gdunit/game_suite.gd"

# Un Pokemon suit le joueur : une case derriere lui, sur la case qu'il vient de quitter. Son image
# est le fichier de son espece — le meme que lit un Pokemon pose sur la carte.

func start() -> Vector2i:
	return Vector2i(2, 2)

func follower() -> Node2D:
	return game.get_node(ENT + "Follower")

func behind() -> Vector2i:
	return Vector2i(floori(follower().position.x / 16.0), floori(follower().position.y / 16.0))

func test_follower() -> void:
	if game == null:
		return
	var sprite: AnimatedSprite2D = follower().get_node("Sprite")
	await wait(5)
	check("le suiveur est la, cache sur la case du joueur tant qu'il n'a pas bouge", not follower().visible and behind() == cell(), str(behind()))
	var sheet: String = sprite.sprite_frames.get_frame_texture("idle_down", 0).atlas.resource_path
	check("son image est le fichier de son espece, celui du pack de donnees", sheet.contains("assets/pokemon/overworld/") and sheet.ends_with(".png"), sheet)
	check("le bas de son image est au bas de la case, sans rien ajouter a son dessin", is_equal_approx(sprite.position.y, 8.0 - 16.0 * sprite.scale.y) and sprite.offset == Vector2.ZERO, "%s %s" % [sprite.scale, sprite.position])

	await walk("trois cases a droite", Vector2i(5, 2), false)
	check("il apparait et se tient une case derriere, a gauche", follower().visible and behind() == cell() + Vector2i.LEFT, str(behind()))
	check("arrete, il regarde le joueur et continue de s'animer sur place", str(sprite.animation) == "walk_right" and sprite.is_playing() and sprite.speed_scale == 1.0, str(sprite.animation))
	shot("follower_right")

	await walk("deux cases en bas", Vector2i(5, 4), false)
	check("il a pris le virage : une case au-dessus du joueur", behind() == cell() + Vector2i.UP, str(behind()))
	check("et le regarde, toujours anime", str(sprite.animation) == "walk_down" and sprite.is_playing(), str(sprite.animation))
	shot("follower_down")

	# Il marche quand le joueur marche.
	var seen := {}
	Input.action_press("ui_right")
	var end := ticks() + 700
	while ticks() < end:
		seen[str(sprite.animation)] = true
		await get_tree().process_frame
	Input.action_release("ui_right")
	await secs(0.5)
	check("en chemin il est anime : il descend prendre la case, puis file a droite", seen.has("walk_down") and seen.has("walk_right"), str(seen.keys()))
	var from := cell()
	Input.action_press("ui_left")
	await secs(0.4)
	Input.action_release("ui_left")
	await secs(0.5)
	check("il ne bloque pas : le joueur rebrousse chemin a travers lui", cell().x < from.x, "%s -> %s" % [from, cell()])
	shot("follower_back")
