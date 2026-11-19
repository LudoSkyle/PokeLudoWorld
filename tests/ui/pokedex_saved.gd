extends "res://tests/lib.gd"

# L'outil de Debug qui remplit le Pokedex regional, et le Pokedex dans la sauvegarde : ce qu'on a vu
# et pris se retrouve apres une relance.

func dex() -> Node:
	return game.get_node(VP + "/PokedexMenu")

func counts() -> String:
	return str(dex().get_node("Control/Screen/Counts").text)

func test() -> void:
	await menu_pick("Debug")
	check("la boite de Debug a sept lignes, Retour en dernier", debug_lines().size() == 7 and debug_lines()[5] == "Remplir le Pokédex" and debug_lines()[6] == "Retour", str(debug_lines()))
	shot("debug_sept_lignes")
	for i in 5:
		await tap("ui_down")
	await tap("interact")
	await secs(1.2)
	check("l'outil dit ce qu'il a fait", box_text().begins_with("Le Pokédex régional est rempli"), box_text())
	await close_box()
	await menu_pick("Pokedex")
	check("une espece sur trois est prise, une sur trois seulement vue : 101 vues, 51 prises", counts() == "Vus 101  Pris 51", counts())
	check("la premiere est prise, la deuxieme vue, la troisieme inconnue", str(dex().get_node("Control/Screen/List/Names/Row0").text) == "Bulbizarre" and str(dex().get_node("Control/Screen/List/Marks/Row0").text) == "●"
		and str(dex().get_node("Control/Screen/List/Names/Row1").text) == "Herbizarre" and str(dex().get_node("Control/Screen/List/Marks/Row1").text) == ""
		and str(dex().get_node("Control/Screen/List/Names/Row2").text) == "-----")
	shot("pokedex_rempli")
	await tap("menu")

	await menu_pick("Save")
	await wait_choices()
	await tap("interact")
	await secs(2.2)
	var seen: PackedStringArray = str(saved_file().get_value("save", "seen", "")).split(",", false)
	var caught: PackedStringArray = str(saved_file().get_value("save", "caught", "")).split(",", false)
	check("le Pokedex est ecrit dans la sauvegarde", seen.size() == 101 and caught.size() == 51 and "bulbasaur" in caught and "ivysaur" in seen and not "ivysaur" in caught and saved_file().get_value("save", "pokedex", 0) == 101,
		"%d vues, %d prises" % [seen.size(), caught.size()])
	await relaunch()
	await menu_pick("Pokedex")
	check("relance : le Pokedex est tel qu'on l'a laisse", counts() == "Vus 101  Pris 51", counts())
