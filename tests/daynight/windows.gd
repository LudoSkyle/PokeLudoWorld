extends "res://tests/lib.gd"

# Les fenetres des maisons s'allument la nuit : la vitre vire au jaune, le mur garde la teinte.

func start() -> Vector2i:
	return Vector2i(18, 6)

# Couleur a l'ecran d'un pixel du monde (repere de la carte).
func pixel(img: Image, world: Vector2) -> Color:
	var cam: Camera2D = player().get_node("Camera")
	var at := (level().global_position + world - cam.get_screen_center_position()) * 4.0 + Vector2(640, 480)
	return img.get_pixel(int(at.x) + 2, int(at.y) + 2)

func test() -> void:
	# La vitre de la maison : 10x7 pixels a partir de (294, 67).
	var glass := Vector2(298, 70)
	var wall := Vector2(286, 70)
	await set_hour(12.0)
	await secs(0.3)
	var day := root.get_texture().get_image()
	check("de jour : la vitre est bleue", pixel(day, glass).b > pixel(day, glass).r + 0.15, str(pixel(day, glass)))
	await set_hour(23.0)
	await secs(0.3)
	var night := root.get_texture().get_image()
	shot("fenetre_nuit")
	var lit := pixel(night, glass)
	check("de nuit : la vitre est eclairee, jaune et claire", lit.r > 0.8 and lit.g > 0.6 and lit.b < lit.r - 0.2, str(lit))
	check("elle n'est pas assombrie par la nuit", lit.get_luminance() > pixel(day, glass).get_luminance() * 0.9, "%.2f contre %.2f de jour" % [lit.get_luminance(), pixel(day, glass).get_luminance()])
	check("le mur a cote reste dans la nuit", pixel(night, wall).get_luminance() < pixel(day, wall).get_luminance(), "%s / %s" % [pixel(night, wall), pixel(day, wall)])
	var glow: PointLight2D = level().get_node("World/GlowHouse")
	check("la fenetre repand sa lueur", glow.visible and glow.energy > 0.5, str(glow.energy))
	await set_hour(19.0)
	await secs(0.3)
	var dusk := pixel(root.get_texture().get_image(), glass)
	check("au crepuscule : encore eteinte", not glow.visible and dusk.r < lit.r - 0.2, str(dusk))
	await set_hour(6.5)
	await secs(0.3)
	var dawn := pixel(root.get_texture().get_image(), glass)
	check("a l'aube : eteinte", not glow.visible and dawn.r < lit.r - 0.2 and dawn.b > dawn.r, str(dawn))
	await set_hour(12.0)
	await secs(0.3)
	check("le jour revenu : eteinte", not glow.visible and pixel(root.get_texture().get_image(), glass).b > 0.7)
