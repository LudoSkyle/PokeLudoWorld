extends "res://tests/lib.gd"

# L'eau bouge : ses pixels changent d'un instant a l'autre, pas ceux du sable ni de l'herbe.

func start() -> Vector2i:
	return Vector2i(38, 17)

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
	var at := (world - cam.get_screen_center_position()) * 4.0 + Vector2(576, 324)
	return Rect2i(int(at.x), int(at.y), 64, 64)

func test() -> void:
	npc("Fisher").movement = "static"
	await secs(0.5)
	var first := root.get_texture().get_image()
	shot("eau_1")
	await secs(0.6)
	var second := root.get_texture().get_image()
	shot("eau_2")
	# La camera est bornee par la carte : on situe les cases a l'ecran d'apres elle.
	var water := on_screen(Vector2i(42, 16))
	var shallow := on_screen(Vector2i(39, 17))
	var lawn := on_screen(Vector2i(33, 17))
	check("l'eau a bouge", changed(first, second, water) > 20, str(changed(first, second, water)))
	check("l'eau claire aussi", changed(first, second, shallow) > 20, str(changed(first, second, shallow)))
	check("la pelouse, elle, n'a pas bouge", changed(first, second, lawn) == 0, str(changed(first, second, lawn)))
