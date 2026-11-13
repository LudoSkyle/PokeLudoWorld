extends "res://tests/lib.gd"

# Le curseur du menu suit les fleches et boucle aux deux bouts.

func test() -> void:
	await tap("menu")
	check("ouvert sur Sac", menu_selected() == "Bag" and menu_cursor_line() == 0, "%s ligne %d" % [menu_selected(), menu_cursor_line()])
	await tap("ui_down")
	check("Bas : Options", menu_selected() == "Options" and menu_cursor_line() == 1, "%s ligne %d" % [menu_selected(), menu_cursor_line()])
	shot("menu_options")
	await tap("ui_down")
	check("Bas : Quitter", menu_selected() == "Quit" and menu_cursor_line() == 2, "%s ligne %d" % [menu_selected(), menu_cursor_line()])
	await tap("ui_down")
	check("Bas sur la derniere : retour a Sac", menu_selected() == "Bag" and menu_cursor_line() == 0, menu_selected())
	await tap("ui_up")
	check("Haut sur la premiere : va a Quitter", menu_selected() == "Quit" and menu_cursor_line() == 2, menu_selected())
	await tap("ui_up")
	check("Haut : Options", menu_selected() == "Options" and menu_cursor_line() == 1, menu_selected())
	await tap("menu")
	await tap("menu")
	check("rouvert : le curseur est reste sur Options", menu_selected() == "Options" and menu_cursor_line() == 1, menu_selected())
