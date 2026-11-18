extends "res://tests/lib.gd"

# Quand la fenetre change de forme, l'image garde son rapport 4:3 : elle reste centree, et des
# bandes noires remplissent ce qui depasse.

func frame() -> Control:
	return game.get_node("Control/Frame/SubViewportContainer")

func ratio_kept(label: String) -> void:
	var size := frame().size
	check(label + " : l'image reste en 4:3", absf(size.x / size.y - 4.0 / 3.0) < 0.001, str(size))

func test() -> void:
	# Avant sa premiere mise en page le cadre doit deja avoir une taille : a zero, la vue du jeu
	# n'a pas d'echelle et le moteur signale une erreur au premier mouvement de souris.
	var fresh: Node = load("res://src/main/kotlin/fr/skyle/pokemonmirage/scenes/core/game_manager.tscn").instantiate()
	var first: Vector2 = fresh.get_node("Control/Frame/SubViewportContainer").size
	fresh.free()
	check("des le chargement, le cadre de jeu a sa taille", first.is_equal_approx(Vector2(1280, 960)), str(first))
	await ratio_kept("fenetre d'origine")
	check("fenetre d'origine : l'image la remplit", frame().size.distance_to(Vector2(1280, 960)) < 0.01, str(frame().size))

	root.size = Vector2i(1700, 960)
	await wait(6)
	await ratio_kept("fenetre plus large")
	check("fenetre plus large : toute la hauteur est prise", is_equal_approx(frame().size.y, 960.0), str(frame().size))
	check("fenetre plus large : l'image est centree, une bande de chaque cote", absf(frame().global_position.x - 210.0) < 0.01, str(frame().global_position))
	check("les bandes sont noires", game.get_node("Control/Bars").color == Color.BLACK and root.get_texture().get_image().get_pixel(40, 480).is_equal_approx(Color.BLACK), str(root.get_texture().get_image().get_pixel(40, 480)))
	shot("rapport_large")

	root.size = Vector2i(1000, 960)
	await wait(6)
	await ratio_kept("fenetre plus etroite")
	check("fenetre plus etroite : toute la largeur est prise", is_equal_approx(frame().size.x, 1000.0), str(frame().size))
	check("fenetre plus etroite : une bande en haut, une en bas", absf(frame().global_position.y - 105.0) < 0.01, str(frame().global_position))
	await walk("fenetre redimensionnee : on marche toujours", two_steps_from(cell()), false)
