extends "res://tests/lib.gd"

# Les options s'ouvrent depuis la selection des parties ; en changer la langue reecrit les
# cartes, et l'on retrouve la carte Options au milieu.

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
	check("la selection des parties est toujours la", slots().visible)
	check("la carte Options est restee choisie", slot_selected() == "Options", slot_selected())
	check("les cartes sont passees en anglais", slot_card("New").get_node("Action/Text").text == "New game", slot_card("New").get_node("Action/Text").text)
	check("l'en-tete aussi", slots().get_node("Header/Title").text == "PARTIES" and tr("PARTIES") == "SAVES", tr("PARTIES"))
	await tap("menu")
	check("la touche du menu referme la selection", not slots().visible)
	check("l'ecran titre est toujours affiche", title_shown() and level() == null)
