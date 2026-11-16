extends "res://tests/lib.gd"

# Les lampadaires : eteints le jour, allumes la nuit, et ils percent la teinte autour d'eux.

func start() -> Vector2i:
	return Vector2i(12, 12)

# Le carre d'ecran (64 px de cote) ou se dessine une case de la carte.
func on_screen(c: Vector2i) -> Rect2i:
	var cam: Camera2D = player().get_node("Camera")
	var world := level().global_position + Vector2(c.x * 16, c.y * 16)
	var at := (world - cam.get_screen_center_position()) * 4.0 + Vector2(640, 480)
	return Rect2i(int(at.x), int(at.y), 64, 64)

# Luminosite moyenne d'un carre de l'ecran.
func brightness(img: Image, r: Rect2i) -> float:
	var sum := 0.0
	var n := 0
	for y in range(r.position.y, r.end.y, 4):
		for x in range(r.position.x, r.end.x, 4):
			sum += img.get_pixel(x, y).get_luminance()
			n += 1
	return sum / n

func test() -> void:
	var lamp := level().get_node("World/LampWest")
	var light: PointLight2D = lamp.get_node("Light")
	check("un lampadaire est un obstacle, sur sa case", not is_free(Vector2i(9, 11)) and not is_free(Vector2i(15, 11)))
	await set_hour(12.0)
	check("en plein jour : eteint", not light.visible and is_zero_approx(light.energy), str(light.energy))
	await set_hour(23.0)
	await secs(0.3)
	check("la nuit : allume, a pleine force", light.visible and light.energy > 1.0, str(light.energy))
	var img := root.get_texture().get_image()
	shot("lampadaires_nuit")
	var near := brightness(img, on_screen(Vector2i(10, 12)))
	var far := brightness(img, on_screen(Vector2i(12, 14)))
	check("la pelouse est plus claire pres du lampadaire que loin de lui", near > far * 1.25, "%.3f pres, %.3f loin" % [near, far])
	# Le halo part du PIED du lampadaire, pas de son ampoule, qui est une case et demie plus
	# haut a l'ecran : trois cases derriere lui, la pelouse est eclairee comme trois cases devant.
	var behind := brightness(img, on_screen(Vector2i(15, 8)))
	var front := brightness(img, on_screen(Vector2i(15, 14)))
	check("le halo est centre sur le pied : autant devant que derriere",
		abs(front - behind) < 0.25 * max(front, behind), "%.3f derriere, %.3f devant" % [behind, front])
	await set_hour(19.0)
	check("au crepuscule : encore eteint", not light.visible and is_zero_approx(light.energy), str(light.energy))
	await set_hour(19.75)
	var falling: float = light.energy
	check("quand la nuit tombe : il s'allume peu a peu", light.visible and falling > 0.3 and falling < 1.0, str(falling))
	await set_hour(6.5)
	check("a l'aube : eteint", not light.visible and is_zero_approx(light.energy), str(light.energy))
	await set_hour(8.0)
	check("le jour leve : eteint", not light.visible)
	var count := 0
	for n in level().get_node("World").get_children():
		if str(n.name).begins_with("Lamp"):
			count += 1
	check("le terrain a ses deux lampadaires", count == 2, str(count))
	await set_hour(12.0)
