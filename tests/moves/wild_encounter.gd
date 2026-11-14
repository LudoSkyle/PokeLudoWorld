extends "res://tests/lib.gd"

# Les rencontres sauvages : un pas dans l'herbe d'une carte peuplee peut faire
# surgir un Pokemon. Le sort est impose, un test ne compte pas sur la chance.

func start() -> Vector2i:
	return Vector2i(12, 5)

func in_grass(c: Vector2i) -> bool:
	return level().get_node("Background/Grass").get_cell_source_id(c) != -1

func test() -> void:
	npc("GrassWatcher").movement = "static"
	check("la carte donne sa chance de rencontre", int(level().get_meta("encounter_rate", 0)) == 10, str(level().get_meta("encounter_rate", 0)))
	check("le depart est hors de l'herbe, la case de gauche dedans", not in_grass(Vector2i(12, 5)) and in_grass(Vector2i(11, 5)) and in_grass(Vector2i(10, 5)))

	# Sort contraire : on traverse l'herbe sans rien croiser.
	await walk("sans chance", Vector2i(11, 5), false)
	check("sort contraire : pas de rencontre", encounters() == 0 and not box().visible, str(encounters()))

	# Sort favorable : le pas suivant dans l'herbe donne une rencontre.
	force_encounters(1)
	Input.action_press("ui_left")
	var end := Time.get_ticks_msec() + 2500
	while Time.get_ticks_msec() < end and not box().visible:
		await process_frame
	check("sort favorable : la rencontre s'annonce", box().visible and encounters() == 1, str(encounters()))
	var at: Vector2 = player().position
	await wait(6)
	check("elle arrive une fois pose sur la case, et l'y arrete", cell() == Vector2i(10, 5) and player().position == at, str(player().position))
	await wait_text("Un Pokémon sauvage apparaît !")
	check("l'annonce est dite", box_text() == "Un Pokémon sauvage apparaît !", box_text())
	# La touche est restee enfoncee : le joueur ne repart pas tant que la boite est la.
	await secs(0.5)
	check("le joueur ne bouge plus pendant l'annonce", cell() == Vector2i(10, 5), str(cell()))
	Input.action_release("ui_left")
	await close_box()
	check("la boite fermee, une seule rencontre comptee", not box().visible and encounters() == 1, str(encounters()))

	# Hors de l'herbe, meme avec le sort favorable, rien.
	await walk("retour", Vector2i(11, 5), false)
	await close_box()
	var before := encounters()
	await walk("sortie de l'herbe", Vector2i(12, 5), false)
	check("hors de l'herbe : pas de rencontre", encounters() == before and not box().visible, "%d -> %d" % [before, encounters()])

	# Une carte sans chance de rencontre a des herbes vides.
	level().set_meta("encounter_rate", 0)
	await walk("herbes vides", Vector2i(11, 5), false)
	check("carte a 0 : pas de rencontre", encounters() == before and not box().visible, str(encounters()))
	force_encounters(0)
