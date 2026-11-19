extends "res://tests/gdunit/game_suite.gd"

# L'eau bouge : ses pixels changent d'un instant a l'autre, pas ceux du sable ni de l'herbe.

func start() -> Vector2i:
	return Vector2i(2, 13)

# Nombre de pixels qui different entre deux captures, dans un rectangle de l'ecran.
func changed(a: Image, b: Image, r: Rect2i) -> int:
	var n := 0
	for y in range(r.position.y, r.end.y, 2):
		for x in range(r.position.x, r.end.x, 2):
			if a.get_pixel(x, y) != b.get_pixel(x, y):
				n += 1
	return n

# Le carre d'ecran (64 px de cote) ou se dessine une case de la carte.
func on_screen(c: Vector2i) -> Rect2i:
	var cam: Camera2D = player().get_node("Camera")
	var world := level().global_position + Vector2(c.x * 16, c.y * 16)
	var at := (world - cam.get_screen_center_position()) * 4.0 + Vector2(640, 480)
	return Rect2i(int(at.x), int(at.y), 64, 64)

func test_water_moves() -> void:
	if game == null:
		return
	npc("Fisher").movement = "static"
	# Le voile du dehors derive lentement : on le retire, pour ne juger que l'eau.
	var haze := level().get_node_or_null("Haze")
	if haze != null:
		haze.visible = false
	await secs(0.5)
	var first := get_tree().root.get_texture().get_image()
	shot("eau_1")
	await secs(0.6)
	var second := get_tree().root.get_texture().get_image()
	shot("eau_2")
	# La camera est bornee par la carte : on situe les cases a l'ecran d'apres elle.
	var water := on_screen(Vector2i(6, 12))
	var shallow := on_screen(Vector2i(3, 13))
	var lawn := on_screen(Vector2i(10, 13))
	check("l'eau a bouge", changed(first, second, water) > 20, str(changed(first, second, water)))
	check("l'eau claire aussi", changed(first, second, shallow) > 20, str(changed(first, second, shallow)))
	check("la pelouse, elle, n'a pas bouge", changed(first, second, lawn) == 0, str(changed(first, second, lawn)))

# Ce test lit l'image a l'ecran : il lui faut une fenetre (tests/gdunit/run.sh le joue a part).
func reads_screen() -> bool:
	return true
