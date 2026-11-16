extends "res://tests/lib.gd"

# Les options s'ouvrent depuis l'ecran titre ; en changer la langue reecrit le menu, et l'on
# retrouve le curseur sur Options.

func title() -> bool:
	return true

func test() -> void:
	await title_pick("Options")
	check("l'ecran des options est ouvert", options_open())
	check("aucune partie n'est lancee", level() == null)
	await tap("ui_down")
	await tap("ui_right")
	shot("titre_options")
	await tap("menu")
	check("la touche du menu referme les options", not options_open())
	check("le menu de l'ecran titre est toujours la", title_menu().visible)
	check("il est passe en anglais", title_entries() == ["New game", "Options", "Back"], str(title_entries()))
	check("le curseur est reste sur Options", title_selected() == "Options", title_selected())
	await tap("ui_down")
	await tap("interact")
	check("Back referme le menu", not title_menu().visible)
	check("l'ecran titre est toujours affiche", title_shown() and level() == null)
