extends "res://tests/lib.gd"

# Meme Odile, dans le salon : elle raconte la cloche et lance la quete.

func scene() -> String:
	return "ludo_house"

func start() -> Vector2i:
	return Vector2i(18, 11)

func test() -> void:
	check("au repos elle regarde la table", anim("Odile") == "idle_left", anim("Odile"))
	check("elle occupe son tabouret", not is_free(Vector2i(17, 11)))
	await interact_facing("ui_left")
	await wait_text("Te voilà debout. J'ai gardé du pain pour toi.")
	check("elle nous accueille, tournee vers nous", box_text().begins_with("Te voilà debout") and anim("Odile") == "idle_right", anim("Odile"))
	shot("dialogue_odile")
	for i in 4:
		await tap("interact")
		await secs(1.6)
	check("la quete n'est pas lancee avant la derniere boite", box_text() == "Personne ne sait où elle est passée." and not flag("bell_told"), box_text())
	await tap("interact")
	await wait_text("Peut-être qu'Alix, la bibliothécaire, sait quelque chose.")
	check("elle pense a Alix, et la quete est lancee", box_text().contains("Alix, la bibliothécaire") and flag("bell_told"), box_text())
	await close_box()
	await secs(0.3)
	check("le dialogue fini, elle se retourne vers la table", anim("Odile") == "idle_left", anim("Odile"))
	await talk("la fois suivante", Vector2i(18, 11), "ui_left", "Odile", "alix t'a trouvé", "idle_right")
