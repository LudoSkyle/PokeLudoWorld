extends "res://tests/lib.gd"

# La vue de debug du Pokedex national : toutes les especes, vues ou non, avec ce qui leur manque.
# Elle s'ouvre depuis les outils de Debug ; ce n'est pas le Pokedex du jeu.

func start() -> Vector2i:
	return Vector2i(22, 4)

func dex() -> Node:
	return game.get_node(VP + "/PokedexDebug")

func text_of(n: String) -> String:
	return str(dex().get_node("Control/Screen/" + n).text)

func test() -> void:
	await menu_pick("Debug")
	for i in 4:
		await tap("ui_down")
	check("le cinquieme outil est le Pokedex national", debug_lines()[4] == "Pokédex national", str(debug_lines()))
	await tap("interact")
	var screen: Control = dex().get_node("Control/Screen")
	check("la vue s'ouvre, la boite d'outils se referme", screen.visible and not debug_choices().visible)
	check("elle annonce les 1025 especes", text_of("Title").begins_with("Pokédex national — 1025 espèces"), text_of("Title"))
	check("la premiere est Bulbizarre, avec ses deux noms", dex().shown_number() == 1 and text_of("Names") == "Bulbizarre / Bulbasaur", text_of("Names"))
	check("sa taille, son poids, sa categorie", text_of("Facts").contains("0,7 m") and text_of("Facts").contains("6,9 kg") and text_of("Facts").contains("Pokémon Graine"), text_of("Facts"))
	check("ses deux descriptions", text_of("French").length() > 40 and text_of("English").length() > 40)
	check("son icone est la ; son sprite de marche manque, et c'est dit", dex().get_node("Control/Screen/Icon").texture != null and dex().get_node("Control/Screen/Walker").texture == null
		and text_of("Lacks") == "Manque : sprite", text_of("Lacks"))
	check("la liste montre quatorze especes, le curseur sur la premiere", text_of("List").split("\n").size() == 14 and text_of("List").begins_with("> 0001 Bulbizarre"), text_of("List").split("\n")[0])
	shot("pokedex_debug")

	await tap("ui_down")
	check("Bas : l'espece suivante", dex().shown_number() == 2 and text_of("Names").begins_with("Herbizarre"))
	await tap("ui_right")
	check("Droite : dix d'un coup", dex().shown_number() == 12)
	await tap("ui_up")
	await tap("ui_left")
	await tap("ui_left")
	check("Gauche s'arrete au debut", dex().shown_number() == 1)
	await tap("ui_up")
	check("Haut depuis la premiere mene a la derniere", dex().shown_number() == 1025 and text_of("Names") == "Pêchaminus / Pecharunt", text_of("Names"))
	check("la derniere n'a ni texte francais, ni icone, ni sprite : la vue le dit", text_of("Lacks") == "Manque : texte FR, icône, sprite" and text_of("French").begins_with("("), text_of("Lacks"))
	check("la liste a suivi : la derniere ligne porte le curseur et l'etoile de ce qui manque", text_of("List").split("\n")[-1] == "> 1025 Pêchaminus *", text_of("List").split("\n")[-1])

	# Une espece qui a tout : Joliflor, dont on a le sprite de marche.
	await tap("ui_down")
	for i in 18:
		await tap("ui_right")
	await tap("ui_down")
	check("Joliflor a tout, sprite compris", dex().shown_number() == 182 and text_of("Lacks") == "" and dex().get_node("Control/Screen/Walker").texture != null, "%d %s" % [dex().shown_number(), text_of("Lacks")])
	shot("pokedex_debug_complet")

	await tap("menu")
	check("la touche du menu referme la vue, pas le menu", not screen.visible and menu_open())
