extends "res://tests/lib.gd"

# La cloche nettoyee : on la montre a Meme, elle la rend et donne son ruban.

func scene() -> String:
	return "ludo_house"

func start() -> Vector2i:
	return Vector2i(18, 11)

func test() -> void:
	set_flag("bell_told")
	set_flag("bell_clean")
	await interact_facing("ui_left")
	await wait_ask()
	check("elle attend qu'on lui montre la cloche", box_text() == "Montrer la cloche à Mémé ?" and ask_choices().visible, box_text())
	check("son nom est affiche pendant la question", speaker_name() == "Mémé Odile", speaker_name())
	await tap("ui_down")
	await tap("interact")
	check("Non : rien ne se passe", not box().visible and not flag("bell_ribbon"))
	await interact_facing("ui_left")
	await wait_ask()
	await tap("interact")
	await wait_text("Oh...")
	check("Oui : elle reconnait la cloche", box_text() == "Oh...", box_text())
	for i in 3:
		await tap("interact")
		await secs(1.6)
	await tap("interact")
	await wait_text("Vous recevez le Ruban de la Veillée !")
	await secs(0.4)
	check("le Ruban est montre au centre de l'ecran", reveal().visible and flag("bell_ribbon"), box_text())
	shot("ruban")
	await wait_text("Allez, va. Et sonne fort, que je l'entende d'ici.")
	await close_box()
	await talk("ensuite elle nous envoie sonner, sans question", Vector2i(18, 11), "ui_left", "Odile", "sonne fort", "idle_right")
	await menu_pick("Bag")
	await tap("ui_right")
	check("le Ruban est dans le sac", bag_rows() == ["Ruban de la Veillée", "Retour"], str(bag_rows()))
