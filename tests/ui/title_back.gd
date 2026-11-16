extends "res://tests/lib.gd"

# Le menu de l'ecran titre se referme par Retour ou par la touche du menu : on revient a
# « Press Enter », sans que rien ne soit lance.

func title() -> bool:
	return true

func test() -> void:
	await title_ready()
	await tap("interact")
	check("le menu est ouvert", title_menu().visible)
	await tap("ui_up")
	check("Haut depuis la premiere entree mene a la derniere", title_selected() == "Retour", title_selected())
	await tap("interact")
	check("Retour referme le menu", not title_menu().visible)
	await title_ready()
	check("« Press Enter » est revenu", title_prompt().visible)
	check("rien n'est lance : pas de carte", level() == null)
	check("l'ecran titre est toujours la", title_shown())

	await tap("interact")
	check("on peut rouvrir le menu", title_menu().visible)
	check("le curseur repart de la premiere entree", title_selected() == "Nouvelle partie", title_selected())
	await tap("menu")
	check("la touche du menu le referme aussi", not title_menu().visible)
	check("un son d'annulation s'est fait entendre", audio().last_sfx_id() == "cancel", audio().last_sfx_id())
	await secs(0.8)
	check("toujours pas de carte", level() == null)
	await tap("menu")
	check("menu ferme : la touche du menu ne fait rien", not title_menu().visible and level() == null)
