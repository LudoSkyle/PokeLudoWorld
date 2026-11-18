extends "res://tests/lib.gd"

# Une nouvelle partie commence dans la chambre de Ludo, au milieu du tapis bleu, tourne vers le
# bas ; de la on rejoint l'escalier et l'on descend dans la maison.

func title() -> bool:
	return true

func scene() -> String:
	return "ludo_bedroom"

func test() -> void:
	check("la carte de depart du jeu est la chambre de Ludo", load("res://src/main/kotlin/fr/skyle/pokemonmirage/scenes/core/game_manager.tscn").instantiate().get_node(VP + "/SceneManager").start_scene.ends_with("ludo_bedroom.tscn"))
	await title_pick("New")
	await title_gone()
	check("on est dans la chambre de Ludo", level().scene_file_path.ends_with("ludo_bedroom.tscn"), level().scene_file_path)
	check("au milieu du tapis", cell() == Vector2i(15, 11), str(cell()))
	check("tourne vers le bas", str(player().get_node("Sprite").animation) == "idle_down", str(player().get_node("Sprite").animation))
	shot("nouvelle_partie")
	for d in DIRS.keys():
		check("on peut faire un pas vers %s" % DIRS[d], can_step(cell(), cell() + d))
	await walk("on rejoint le palier de l'escalier", Vector2i(11, 8), false)
	await hold_until_change("on descend l'escalier", "ui_left")
	check("l'escalier mene dans la maison de Ludo", level().scene_file_path.ends_with("ludo_house.tscn"), level().scene_file_path)
