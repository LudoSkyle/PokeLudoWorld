extends "res://tests/lib.gd"

# Recevoir un objet : la musique se met en pause, le jingle joue, la musique reprend.

func start() -> Vector2i:
	return Vector2i(35, 12)

func test() -> void:
	await spawn("sign", "Giver", Vector2i(35, 11), {"text": "@give:old_rod Vous recevez la Vieille canne !|@give:potion Vous recevez une Potion !|Voila."})
	var starts: int = audio().music_starts()
	await interact_facing("ui_up")
	await secs(0.5)
	check("objet rare : son jingle joue", audio().jingle_playing() and audio().last_jingle_id() == "key_item", audio().last_jingle_id())
	check("la musique est en pause", not audio().music_audible())
	await wait_text("Vous recevez une Potion !", 12.0)
	check("la boite suivante n'arrive qu'apres le jingle de l'objet rare", box_text() == "Vous recevez une Potion !", box_text())
	check("objet ordinaire : un autre jingle", audio().jingle_playing() and audio().last_jingle_id() == "item", audio().last_jingle_id())
	await tap("interact")
	check("une touche ne coupe pas le jingle", box_text() == "Vous recevez une Potion !" and audio().jingle_playing())
	await wait_jingle()
	check("le jingle fini, la musique reprend", audio().music_audible())
	check("elle reprend, elle ne redemarre pas", audio().music_starts() == starts, str(audio().music_starts()))
	await close_box()
