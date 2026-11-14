extends "res://tests/lib.gd"

# Sac : Bas maintenu descend toute la liste, Haut maintenu la remonte, et la quantite a jeter defile aussi.

func test() -> void:
	await fill_bag()
	await menu_pick("Bag")
	Input.action_press("ui_down")
	await secs(1.6)
	Input.action_release("ui_down")
	check("Bas tenu : on arrive tout en bas, sur Retour", bag_rows()[5] == "Retour" and bag_line() == 5 and bag("Description").text == "Refermer le sac.", str(bag_rows()))
	check("la liste ne boucle pas : on y reste", not bag("ScrollDown").visible)
	shot("sac_bas_tenu")
	Input.action_press("ui_up")
	await secs(1.6)
	Input.action_release("ui_up")
	check("Haut tenu : on remonte tout en haut", bag_rows()[0] == "Potion x3" and bag_line() == 0, str(bag_rows()))

	# la quantite : 10 Limonades
	for i in 7:
		await tap("ui_down")
	check("sur la Limonade", bag_rows()[bag_line()] == "Limonade x10", str(bag_rows()))
	await tap("interact")
	await tap("interact")
	check("quantite a 1", bag("Amount/Value").text == "x1")
	Input.action_press("ui_up")
	await secs(0.2)
	check("Haut tenu : un cran, puis l'attente", bag("Amount/Value").text == "x2", bag("Amount/Value").text)
	var values := {}
	var end := Time.get_ticks_msec() + 1600
	while Time.get_ticks_msec() < end:
		await process_frame
		values[bag("Amount/Value").text] = true
	Input.action_release("ui_up")
	check("puis la quantite defile et boucle par toutes les valeurs", values.size() == 10, str(values.keys()))
	var kept: String = bag("Amount/Value").text
	await secs(0.5)
	check("touche relachee : la quantite ne bouge plus", bag("Amount/Value").text == kept, kept)
