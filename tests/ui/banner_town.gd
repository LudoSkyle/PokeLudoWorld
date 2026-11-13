extends "res://tests/lib.gd"

# Bandeau de lieu a l'arrivee dans le village.

func test() -> void:
	var r: Array = await watch_banner(1.5, "bandeau_village")
	check("le bandeau annonce le village", r[0] and r[1] == "Bourg-Ludo", str(r))
	check("il descend a sa place, en haut a gauche", is_equal_approx(r[2], 24.0) and is_equal_approx(banner().position.x, 24.0), str(r[2]))
	check("le cadre contient le nom", banner().size.x >= game.get_node(VP + "/LocationBanner/Control/Panel/Name").get_minimum_size().x + 48.0, str(banner().size))
	check("bandeau de bois, au pixel du jeu", banner().texture.resource_path.ends_with("wood.png") and banner().size == Vector2(524, 108), str(banner().size))
	await secs(2.5)
	check("il est remonte apres quelques secondes", not banner().visible)
