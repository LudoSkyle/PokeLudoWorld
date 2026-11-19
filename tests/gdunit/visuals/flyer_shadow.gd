extends "res://tests/gdunit/game_suite.gd"

# Un Pokemon volant n'a pas de reflet : trop haut, et de lui on ne voit qu'une
# ombre. Au-dessus de l'eau, c'est cette ombre qui bleuit.
# Les deux planent sur place : une zone d'une seule case.

func start() -> Vector2i:
	return Vector2i(8, 9)

func shade_of(flyer: Node2D) -> Color:
	return flyer.get_node("Shadow").color

func test_flyer_shadow() -> void:
	if game == null:
		return
	var sea: Node2D = await spawn("flyer", "SurLEau", Vector2i(4, 12), {"zone": Rect2i(4, 12, 1, 1)})
	var land: Node2D = await spawn("flyer", "SurLHerbe", Vector2i(10, 12), {"zone": Rect2i(10, 12, 1, 1)})
	await secs(0.5)

	var water_tint: Color = sea.get_node("Shade").on_water
	var land_tint: Color = sea.get_node("Shade").on_land

	check("au-dessus de l'eau, l'ombre bleuit", shade_of(sea).is_equal_approx(water_tint), str(shade_of(sea)))
	check("elle reste visible", sea.get_node("Shadow").visible)
	check("au-dessus de l'herbe, l'ombre reste noire", shade_of(land).is_equal_approx(land_tint), str(shade_of(land)))

	# Aucun reflet d'oiseau dans l'eau : seuls les personnages s'y mirent.
	var holder := level().get_node_or_null("Background/Reflections")
	var birds := 0
	if holder != null:
		for child in holder.get_children():
			if child.visible and child.texture != null and str(child.texture.resource_path).contains("overworld"):
				birds += 1
	check("pas de reflet d'oiseau", birds == 0, "%d reflets" % birds)
