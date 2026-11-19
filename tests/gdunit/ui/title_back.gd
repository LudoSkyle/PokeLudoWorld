extends "res://tests/gdunit/game_suite.gd"

# La selection des parties se referme par la touche du menu : on revient a « Press Enter », sans
# que rien ne soit lance.

func title() -> bool:
	return true

func test_title_back() -> void:
	if game == null:
		return
	await title_ready()
	await tap("interact")
	check("la selection est ouverte", slots().visible)
	await tap("ui_left")
	check("Gauche depuis la premiere carte mene a la derniere", slot_selected() == "Options", slot_selected())
	await tap("ui_right")
	check("Droite depuis la derniere ramene a la premiere", slot_selected() == "New", slot_selected())
	await tap("menu")
	check("la touche du menu referme la selection", not slots().visible)
	check("un son d'annulation s'est fait entendre", audio().last_sfx_id() == "cancel", audio().last_sfx_id())
	await title_ready()
	check("« Press Enter » est revenu", title_prompt().visible)
	check("le logo aussi", title_screen().get_node("Control/Logo").visible)
	check("rien n'est lance : pas de carte", level() == null)
	check("l'ecran titre est toujours la", title_shown())

	await tap("ui_right")
	await tap("interact")
	check("on peut rouvrir la selection", slots().visible)
	check("elle repart de la premiere carte", slot_selected() == "New", slot_selected())
	await tap("menu")
	await secs(0.8)
	check("toujours pas de carte", level() == null)
	await tap("menu")
	check("selection fermee : la touche du menu ne fait rien", not slots().visible and level() == null)
