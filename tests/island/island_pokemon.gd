extends "res://tests/lib.gd"

# Trois Pokemon sont poses sur l'ile : on leur parle, ils disent leur cri — en texte, et en son —
# et ne crient pas autrement. Deux enfants font la course sur la plage du sud, cote a cote.

func scene() -> String:
	return "start_island"

func start() -> Vector2i:
	return Vector2i(30, 13)

func hear(label: String, who: String, species: String, said: String, key: String) -> void:
	var before: int = audio().cries_played()
	await interact_facing(key)
	await wait_text(said)
	check(label + " : il dit son cri", box().visible and box_text() == said, box_text())
	check(label + " : et on l'entend", audio().cries_played() == before + 1 and audio().last_cry_id() == species, "%d %s" % [audio().cries_played() - before, audio().last_cry_id()])
	await close_box()
	check(label + " : il n'a pas bouge", cell_of(who) != Vector2i(-1, -1) and not is_free(cell_of(who)))

func test() -> void:
	# Un Pokemon pose sur la carte lit le fichier de son espece : il n'y a pas de planche a part pour les PNJ.
	var posed: AnimatedSprite2D = game.get_node(ENT + "Corphish/Sprite")
	var his: String = posed.sprite_frames.get_frame_texture("idle_down", 0).atlas.resource_path
	check("Ecrapince lit le fichier de son espece, au pixel du jeu, pose au bas de sa case", his.ends_with("assets/pokemon/overworld/corphish.png") and posed.scale == Vector2(1, 1) and posed.position == Vector2(0, -8), "%s %s" % [his, posed.position])
	shot("island_corphish")
	check("Ecrapince est en haut a droite du gamin aux coquillages", cell_of("Corphish") == cell_of("ShellKid") + Vector2i(1, -1), str(cell_of("Corphish")))
	var quiet: int = audio().cries_played()
	await secs(3.0)
	check("tant qu'on ne lui parle pas, il se tait", audio().last_cry_id() != "corphish")
	await hear("Ecrapince", "Corphish", "corphish", "Krr... Krapince !", "ui_up")
	check("Kokiyas est dans le creux de sable, sous la lagune de l'est", cell_of("Shellder") == Vector2i(48, 25) and not is_free(Vector2i(47, 25)) and not is_free(Vector2i(49, 25)), str(cell_of("Shellder")))
	await place(cell_of("Shellder") + Vector2i.UP)
	await hear("Kokiyas", "Shellder", "shellder", "Koki... yas !", "ui_down")
	check("Joliflor est pres de la dame aux fleurs", (cell_of("Bellossom") - cell_of("Gardener")).length() <= 2.0, str(cell_of("Bellossom")))
	await place(cell_of("Bellossom") + Vector2i.DOWN)
	await hear("Joliflor", "Bellossom", "bellossom", "Joli ! Joliflor !", "ui_up")

	# Les deux enfants : chacun sa rangee, ils courent ensemble.
	var a: Node2D = game.get_node(ENT + "KidRunnerA")
	var b: Node2D = game.get_node(ENT + "KidRunnerB")
	var from_a := a.position
	var apart := 0.0
	var ran := 0.0
	var end := Time.get_ticks_msec() + 4000
	while Time.get_ticks_msec() < end:
		await process_frame
		apart = maxf(apart, absf(a.position.x - b.position.x))
		ran = maxf(ran, a.position.distance_to(from_a))
	check("les deux enfants courent", ran > 32.0, "%.1f" % ran)
	check("cote a cote : jamais plus de deux cases d'ecart, chacun sur sa rangee", apart <= 32.0 and absf(a.position.y - b.position.y) == 16.0, "%.1f" % apart)
	check("la mamie est assise sur son banc", cell_of("BenchLady") == Vector2i(11, 14))
	await place(Vector2i(11, 15))
	await interact_facing("ui_up")
	await wait_text("Je viens m'asseoir ici tous les matins.")
	check("et elle repond quand on lui parle : c'est elle qu'on vise, pas le banc", box().visible and box_text() == "Je viens m'asseoir ici tous les matins.", box_text())
	await close_box()
