extends "res://tests/gdunit/game_suite.gd"

# Les rencontres sauvages : un pas dans l'herbe d'une carte peuplee peut faire
# surgir un Pokemon. Le sort est impose, un test ne compte pas sur la chance.

func start() -> Vector2i:
	return Vector2i(12, 8)

# Les especes de la table du terrain d'essai, et leur nom.
const NAMES := {"mulotin": "Mulotin", "piafeuille": "Piafeuille", "chenibulle": "Chenibulle"}

func in_grass(c: Vector2i) -> bool:
	return level().get_node("Background/Grass").get_cell_source_id(c) != -1

func test_wild_encounter() -> void:
	if game == null:
		return
	npc("GrassWatcher").movement = "static"
	check("la carte donne sa chance de rencontre", int(level().get_meta("encounter_rate", 0)) == 10, str(level().get_meta("encounter_rate", 0)))
	check("le depart est hors de l'herbe, la case de gauche dedans", not in_grass(Vector2i(12, 8)) and in_grass(Vector2i(11, 8)) and in_grass(Vector2i(10, 8)))

	# Sort contraire : on traverse l'herbe sans rien croiser.
	await walk("sans chance", Vector2i(11, 8), false)
	check("sort contraire : pas de rencontre", encounters() == 0 and not box().visible, str(encounters()))

	# Sort favorable : le pas suivant dans l'herbe donne une rencontre.
	force_encounters(1)
	Input.action_press("ui_left")
	var end := ticks() + 2500
	while ticks() < end and not box().visible:
		await get_tree().process_frame
	check("sort favorable : la rencontre s'annonce", box().visible and encounters() == 1, str(encounters()))
	var at: Vector2 = player().position
	await wait(6)
	check("elle arrive une fois pose sur la case, et l'y arrete", cell() == Vector2i(10, 8) and player().position == at, str(player().position))
	var met := last_encounter().split(":")
	check("le Pokemon rencontre vient de la table de la carte", met.size() == 2 and NAMES.has(met[0]) and int(met[1]) >= 2 and int(met[1]) <= 5, last_encounter())
	var announce: String = "Un %s sauvage apparaît !" % NAMES.get(met[0], "?")
	await wait_text(announce)
	check("l'annonce le nomme", box_text() == announce, box_text())
	# La touche est restee enfoncee : le joueur ne repart pas tant que la boite est la.
	await secs(0.5)
	check("le joueur ne bouge plus pendant l'annonce", cell() == Vector2i(10, 8), str(cell()))
	Input.action_release("ui_left")
	await close_box()
	check("la boite fermee, une seule rencontre comptee", not box().visible and encounters() == 1, str(encounters()))

	# Hors de l'herbe, meme avec le sort favorable, rien.
	await walk("retour", Vector2i(11, 8), false)
	await close_box()
	var before := encounters()
	await walk("sortie de l'herbe", Vector2i(12, 8), false)
	check("hors de l'herbe : pas de rencontre", encounters() == before and not box().visible, "%d -> %d" % [before, encounters()])

	# Une carte sans chance de rencontre a des herbes vides.
	level().set_meta("encounter_rate", 0)
	await walk("herbes vides", Vector2i(11, 8), false)
	check("carte a 0 : pas de rencontre", encounters() == before and not box().visible, str(encounters()))

	# Une carte qui a une chance mais pas de table n'a personne a montrer.
	level().set_meta("encounter_rate", 100)
	level().set_meta("wild", "")
	await walk("retour hors de l'herbe", Vector2i(12, 8), false)
	await walk("herbes sans table", Vector2i(11, 8), false)
	check("carte sans table : pas de rencontre", encounters() == before and not box().visible, str(encounters()))
	force_encounters(0)

	# Courir dans l'herbe derange davantage : un pas couru tire sur encounter_rate_run, un pas marche sur encounter_rate.
	# Le hasard decide (ni sort favorable ni contraire) : a 0 il ne donne jamais rien, a 100 toujours.
	force_encounters(-1)
	level().set_meta("wild", "mulotin:2-4*50 | piafeuille:2-5*35 | chenibulle:3*15")
	level().set_meta("encounter_rate", 0)
	level().set_meta("encounter_rate_run", 100)
	await walk("sortie", Vector2i(12, 8), false)
	before = encounters()
	await walk("au pas, chance du pas", Vector2i(11, 8), false)
	check("au pas : c'est la chance du pas marche qui compte", encounters() == before and not box().visible, str(encounters()))
	await walk("sortie", Vector2i(12, 8), false)
	Input.action_press("run")
	Input.action_press("ui_left")
	var until := ticks() + 2500
	while ticks() < until and not box().visible:
		await get_tree().process_frame
	Input.action_release("ui_left")
	Input.action_release("run")
	check("en courant : c'est la chance du pas couru", box().visible and encounters() == before + 1 and cell() == Vector2i(11, 8), "%d %s" % [encounters(), cell()])
	await close_box()
	level().set_meta("encounter_rate", 100)
	level().set_meta("encounter_rate_run", 0)
	await place(Vector2i(12, 8))
	before = encounters()
	Input.action_press("run")
	await walk("en courant, chance nulle", Vector2i(11, 8), false)
	Input.action_release("run")
	check("et a l'inverse : en courant, la chance du pas marche ne compte pas", encounters() == before and not box().visible, str(encounters()))
	level().remove_meta("encounter_rate_run")
	await place(Vector2i(12, 8))
	Input.action_press("run")
	Input.action_press("ui_left")
	until = ticks() + 2500
	while ticks() < until and not box().visible:
		await get_tree().process_frame
	Input.action_release("ui_left")
	Input.action_release("run")
	check("sans reglage pour la course : courir ou marcher revient au meme", box().visible and encounters() == before + 1, str(encounters()))
	await close_box()
	force_encounters(0)
