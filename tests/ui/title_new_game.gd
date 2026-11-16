extends "res://tests/lib.gd"

# L'ecran titre au lancement, sans sauvegarde : « Press Enter », le menu, puis Nouvelle partie
# lance la partie sur la carte de depart.

func title() -> bool:
	return true

func test() -> void:
	check("au lancement : l'ecran titre est affiche", title_shown())
	check("au lancement : aucune carte n'est chargee", level() == null)
	check("au lancement : le menu est ferme", not title_menu().visible)
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
	check("la touche d'interaction ouvre le menu", title_menu().visible)
	check("sans sauvegarde : Nouvelle partie, Options, Retour", title_entries() == ["Nouvelle partie", "Options", "Retour"], str(title_entries()))
	check("le curseur est sur la premiere entree", title_selected() == "Nouvelle partie", title_selected())
	await secs(1.2)
	check("menu ouvert : « Press Enter » ne clignote plus", not title_prompt().visible)
	shot("titre_menu")

	await tap("interact")
	check("Nouvelle partie : le menu se ferme", not title_menu().visible)
	await title_gone()
	check("la partie est lancee : l'ecran titre a disparu", not title_shown())
	check("on est sur la carte de depart", level() != null and level().scene_file_path.ends_with("start_town.tscn"), "" if level() == null else level().scene_file_path)
	check("le joueur est la", player() != null)
	shot("titre_partie_lancee")
	var from := cell()
	var to := from
	for d in DIRS.keys():
		if can_step(from, from + d):
			to = from + d
			break
	await walk("la partie lancee : on marche", to, false)
