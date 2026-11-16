extends "res://tests/lib.gd"

# L'ecran titre au lancement, sans sauvegarde : « Press Enter », la selection des parties, puis
# Nouvelle partie lance la partie sur la carte de depart.

func title() -> bool:
	return true

func test() -> void:
	check("au lancement : l'ecran titre est affiche", title_shown())
	check("au lancement : aucune carte n'est chargee", level() == null)
	check("au lancement : la selection des parties est fermee", not slots().visible)
	await title_ready()
	check("« Press Enter » s'affiche une fois le logo arrive", title_prompt().visible)
	var logo: Sprite2D = title_screen().get_node("Control/Logo")
	var shown: Vector2 = logo.texture.get_size() * logo.scale
	check("le logo tient dans son cadre, sans deformation", logo.visible and is_equal_approx(logo.scale.x, logo.scale.y) and shown.x <= 1001.0 and shown.y <= 351.0 and (shown.x >= 999.0 or shown.y >= 349.0), str(shown))
	check("des Goelise volent, devant et derriere la tour", title_screen().get_node("Control/Backdrop/FarFlyers").get_child_count() == title_screen().far_flyers and title_screen().get_node("Control/Backdrop/NearFlyers").get_child_count() == title_screen().near_flyers and title_screen().far_flyers > 0 and title_screen().near_flyers > 0)
	shot("titre")
	# Le texte clignote : sur deux secondes on le voit affiche, et on le voit cache.
	var seen := {true: 0, false: 0}
	var end := Time.get_ticks_msec() + 2000
	while Time.get_ticks_msec() < end:
		seen[title_prompt().visible] += 1
		await process_frame
	check("« Press Enter » clignote", seen[true] > 0 and seen[false] > 0, str(seen))
	check("sans appuyer : toujours pas de carte", level() == null)

	await tap("interact")
	check("la touche d'interaction ouvre la selection des parties", slots().visible)
	check("sans sauvegarde : Nouvelle partie, Options", slot_cards() == ["New", "Options"], str(slot_cards()))
	check("la premiere carte est choisie", slot_selected() == "New", slot_selected())
	check("elle dit « Nouvelle partie »", slot_card("New").get_node("Action/Text").text == "Nouvelle partie", slot_card("New").get_node("Action/Text").text)
	await secs(1.2)
	check("selection ouverte : « Press Enter » ne clignote plus", not title_prompt().visible)
	check("selection ouverte : le logo laisse la place aux cartes", not logo.visible)
	shot("titre_parties_vide")

	await tap("interact")
	check("Nouvelle partie : la selection se ferme", not slots().visible)
	await title_gone()
	check("la partie est lancee : l'ecran titre a disparu", not title_shown())
	check("on est sur la carte de depart", level() != null and level().scene_file_path.ends_with("start_town.tscn"), "" if level() == null else level().scene_file_path)
	check("le joueur est la", player() != null)
	await walk("la partie lancee : on marche", two_steps_from(cell()), false)
	await menu_pick("Save")
	await wait_choices()
	await tap("interact")
	await secs(2.2)
	check("sauvegarder ecrit dans le premier emplacement", FileAccess.file_exists(save_path(1)) and not FileAccess.file_exists(save_path(2)))
