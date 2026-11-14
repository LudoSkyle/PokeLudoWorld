extends "res://tests/lib.gd"

# Recevoir un objet rare : il s'affiche au centre, une seconde, puis le dialogue continue seul.

func test() -> void:
	await menu_pick("Debug")
	await tap("interact")
	await secs(1.2)
	check("d'abord un message ordinaire, sans objet a l'ecran", box().visible and not reveal().visible, box_text())
	await tap("interact")
	await secs(0.9)
	check("l'objet rare apparait au centre, avec son annonce", reveal().visible and box_text() == "Vous recevez la Vieille canne !", box_text())
	check("il est pleinement visible apres le fondu", is_equal_approx(reveal().modulate.a, 1.0), str(reveal().modulate.a))
	check("au centre de l'ecran, au-dessus de la boite de dialogue", is_equal_approx(reveal().position.x + reveal().size.x / 2.0, 576.0) and reveal().position.y + reveal().size.y < 464.0)
	var first: Rect2 = reveal().get_node("Icon").texture.region
	shot("objet_rare")
	await tap("interact")
	check("une touche ne le fait pas passer", reveal().visible and box_text() == "Vous recevez la Vieille canne !", box_text())
	var t0 := Time.get_ticks_msec()
	while Time.get_ticks_msec() - t0 < 9000 and box_text() != "Vous recevez la Carte du village !":
		await process_frame
	check("la suite arrive toute seule", box_text().begins_with("Vous recevez la Carte"), box_text())
	await secs(0.8)
	check("le second objet a sa propre icone", reveal().visible and reveal().get_node("Icon").texture.region != first)
	t0 = Time.get_ticks_msec()
	while Time.get_ticks_msec() - t0 < 9000 and box().visible:
		await process_frame
	check("apres le dernier, le dialogue se ferme seul", not box().visible)
	await secs(0.4)
	check("et l'objet a disparu", not reveal().visible)
	await walk("on reprend la main", cell() + Vector2i(-1, 0), false)
	await menu_pick("Bag")
	await tap("ui_right")
	check("les deux objets sont dans le sac", bag_rows() == ["Vieille canne", "Carte du village", "Retour"], str(bag_rows()))
