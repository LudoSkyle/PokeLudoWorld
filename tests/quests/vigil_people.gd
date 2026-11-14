extends "res://tests/lib.gd"

# La Veillee : chacun est sur la place et dit sa replique d'apres.

func start() -> Vector2i:
	return Vector2i(31, 15)

func test() -> void:
	set_flag("bell_hung")
	await reload_level()
	await talk("Meme, au pied du socle", Vector2i(31, 15), "ui_left", "OdileAfter", "fait le déplacement", "idle_right")
	await tap("interact")
	for i in 2:
		await secs(1.6)
		await tap("interact")
	await wait_text("*Kraak* ...MON DOS !!!")
	check("et son dos le lui fait payer", box_text() == "*Kraak* ...MON DOS !!!", box_text())
	shot("meme_dos")
	await close_box()
	await talk("le pecheur, face au socle", Vector2i(31, 15), "ui_right", "FisherAfter", "ma canne", "idle_left")
	await secs(0.3)
	check("le dialogue fini, le pecheur regarde de nouveau la cloche", anim("FisherAfter") == "idle_up", anim("FisherAfter"))
	await place(Vector2i(29, 14))
	await talk("Alix", Vector2i(29, 14), "ui_up", "AlixAfter", "fermé la bibliothèque", "idle_down")
	await place(Vector2i(33, 12))
	await talk("Roland", Vector2i(33, 12), "ui_down", "RolandAfter", "sans la voir", "idle_up")
	await place(Vector2i(37, 14))
	await talk("l'ouvrier", Vector2i(37, 14), "ui_left", "WorkerAfter", "route de l'ouest est ouverte", "idle_right")
	await place(Vector2i(35, 17))
	await talk("le second ouvrier", Vector2i(35, 17), "ui_up", "WorkerAfter2", "outils sont rangés", "idle_down")
	await place(Vector2i(31, 17))
	await talk("un enfant venu d'ailleurs", Vector2i(31, 17), "ui_left", "VisitorChild", "toute petite", "idle_right")
	await walk("on quitte la place par le sud puis le chemin", Vector2i(26, 16), false)
