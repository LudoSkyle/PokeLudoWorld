extends "res://tests/lib.gd"

# La machine de soin nettoie la cloche : la ternie quitte le sac, la claire y entre.

func scene() -> String:
	return "lab_house"

func start() -> Vector2i:
	return Vector2i(16, 8)

func test() -> void:
	await examine("sans la cloche : rien a soigner", Vector2i(16, 8), "machine de soin")
	check("aucune question n'a ete posee", not flag("bell_clean"))
	await receive("tarnished_bell", Vector2i(16, 9), "ui_down")
	set_flag("bell_tarnished")
	await interact_facing("ui_up")
	await wait_ask()
	check("avec la cloche : la question", box_text() == "Poser la Cloche ternie dans la machine ?" and ask_choices().visible, box_text())
	await tap("interact")
	await wait_text("La machine s'allume et chante trois notes.")
	check("Oui : la machine s'allume", box_text() == "La machine s'allume et chante trois notes.", box_text())
	check("et ses trois notes s'entendent, musique en pause", audio().jingle_playing() and audio().last_jingle_id() == "healed" and not audio().music_audible())
	await wait_jingle()
	await tap("interact")
	await wait_text("Vous récupérez la Cloche claire !")
	await secs(0.4)
	check("la Cloche claire est montree, bell_clean est pose", reveal().visible and flag("bell_clean"), box_text())
	check("avec son icone maison", reveal().get_node("Icon").texture.atlas.resource_path.ends_with("custom.png") and reveal().get_node("Icon").texture.region.position == Vector2(0, 0))
	shot("cloche_claire")
	var end := Time.get_ticks_msec() + 9000
	while Time.get_ticks_msec() < end and box().visible:
		await process_frame
	await wait(10)
	await examine("ensuite, depuis l'autre case : plus de question", Vector2i(17, 8), "une machine de soin")
	await menu_pick("Bag")
	await tap("ui_right")
	check("le sac a la Cloche claire, plus la ternie", bag_rows() == ["Cloche claire", "Retour"], str(bag_rows()))
