extends "res://tests/lib.gd"

# On accroche la cloche depuis le portique : la carte se recharge, la cloche prend la place, la Veillee commence.

func start() -> Vector2i:
	return Vector2i(31, 13)

func test() -> void:
	await receive("clear_bell", Vector2i(31, 14), "ui_down")
	set_flag("bell_ribbon")
	await interact_facing("ui_up")
	await wait_ask()
	check("avec le ruban : la question", box_text() == "Accrocher la Cloche claire ?" and ask_choices().visible, box_text())
	await tap("ui_down")
	await tap("interact")
	check("Non : rien ne change", not box().visible and not flag("bell_hung") and node("World/BellStandEmpty") != null)
	await tap("interact")
	await wait_ask()
	await tap("interact")
	await wait_text("Vous accrochez la cloche. Elle tient.")
	check("Oui : on accroche la cloche", box_text() == "Vous accrochez la cloche. Elle tient." and flag("bell_hung"), box_text())
	check("la place ne change pas tant que la boite est ouverte", node("World/BellStandEmpty") != null)
	check("la cloche sonne, musique en pause", audio().jingle_playing() and audio().last_jingle_id() == "bell" and not audio().music_audible())
	await tap("interact")
	check("on ne passe pas la boite tant qu'elle sonne", box().visible)
	await wait_jingle()
	var id := level_id()
	await tap("interact")
	var end := Time.get_ticks_msec() + 4000
	while Time.get_ticks_msec() < end and level_id() == id:
		await process_frame
	check("la boite fermee, la carte se recharge", level_id() != id)
	await secs(0.8)
	check("la cloche a pris notre place : on a recule sur la marche, toujours tourne vers elle", cell() == Vector2i(31, 14) and str(player().get_node("Sprite").animation) == "idle_up", str(cell()))
	check("la cloche est sur son socle", node("World/BellStand") != null and node("World/BellStandEmpty") == null)
	check("la cloche sonnee, la musique du village reprend, la meme", audio().music_id() == "new_bark_town" and audio().music_audible(), audio().music_id())
	check("elle barre le portique", not is_free(Vector2i(31, 13)))
	check("Meme est derriere nous, le pecheur aussi", node("World/Entities/OdileAfter") != null and node("World/Entities/FisherAfter") != null)
	check("le pecheur a quitte le bord de l'eau", node("World/Entities/Fisher") == null and is_free(Vector2i(40, 17)))
	shot("veillee")
	await examine("le socle, apres", Vector2i(31, 14), "à sa place")
	await menu_pick("Bag")
	await tap("ui_right")
	check("la Cloche claire a quitte le sac", bag_rows() == ["Retour"], str(bag_rows()))
