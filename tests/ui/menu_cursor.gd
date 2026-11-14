extends "res://tests/lib.gd"

# Le curseur du menu suit les fleches, boucle aux deux bouts, et repart du haut a chaque ouverture.

const ENTRIES := ["Bag", "Save", "Options", "Debug", "Quit"]

func at(line: int) -> bool:
	return menu_selected() == ENTRIES[line] and menu_cursor_line() == line

func test() -> void:
	await tap("menu")
	check("ouvert sur Sac", at(0), "%s ligne %d" % [menu_selected(), menu_cursor_line()])
	for line in [1, 2, 3, 4]:
		await tap("ui_down")
		check("Bas : %s" % ENTRIES[line], at(line), "%s ligne %d" % [menu_selected(), menu_cursor_line()])
		if line == 2:
			shot("menu_options")
	await tap("ui_down")
	check("Bas sur la derniere : retour a Sac", at(0), menu_selected())
	await tap("ui_up")
	check("Haut sur la premiere : va a Quitter", at(4), menu_selected())
	await tap("ui_up")
	check("Haut : Debug", at(3), menu_selected())
	await tap("menu")
	await tap("menu")
	check("rouvert : le curseur repart de la premiere entree", at(0), menu_selected())
