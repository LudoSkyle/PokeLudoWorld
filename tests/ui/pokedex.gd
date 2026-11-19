extends "res://tests/lib.gd"

# Le Pokedex regional, celui du jeu : on l'ouvre depuis le menu de pause. Une espece n'y montre que
# son numero tant qu'on ne l'a pas vue ; vue, son nom et son portrait ; prise, sa fiche entiere.

func start() -> Vector2i:
	return Vector2i(22, 4)

func dex() -> Node:
	return game.get_node(VP + "/PokedexMenu")

func text_of(n: String) -> String:
	return str(dex().get_node("Control/Screen/" + n).text)

func row(n: int) -> String:
	return "%s %s%s" % [text_of("List/Numbers/Row%d" % n), text_of("List/Names/Row%d" % n), text_of("List/Marks/Row%d" % n)]

func test() -> void:
	await menu_pick("Pokedex")
	var screen: Control = dex().get_node("Control/Screen")
	check("le Pokedex s'ouvre depuis le menu de pause, sur tout l'ecran", screen.visible and screen.size == Vector2(1280, 960), str(screen.size))
	check("rien n'est inscrit encore", text_of("Counts") == "Vus 0  Pris 0", text_of("Counts"))
	check("la premiere espece n'a que son numero", row(0) == "001 -----" and text_of("Number") == "No 001" and text_of("Name") == "-----" and text_of("Status") == "Inconnu", row(0))
	check("sans portrait : un point d'interrogation", dex().get_node("Control/Screen/Portrait").texture == null and dex().get_node("Control/Screen/Unknown").visible)
	check("douze lignes, jusqu'au numero 012", text_of("List/Numbers/Row11") == "012")
	await tap("interact")
	check("on ne lit pas la fiche d'une espece inconnue", not dex().get_node("Control/Screen/Sheet").visible)

	# vue, puis prise
	dex().register("bulbasaur", false)
	await wait(4)
	check("vue : son nom et son portrait", row(0) == "001 Bulbizarre" and text_of("Status") == "Vu" and dex().get_node("Control/Screen/Portrait").texture != null and text_of("Genus") == "", row(0))
	check("le compte suit", text_of("Counts") == "Vus 1  Pris 0", text_of("Counts"))
	await tap("interact")
	check("sa fiche s'ouvre a la place de la liste, sans ce qu'on ne sait pas", dex().get_node("Control/Screen/Sheet").visible and not dex().get_node("Control/Screen/List").visible
		and text_of("Sheet/Height") == "Taille : ???" and text_of("Sheet/Text") == "Il faut l'avoir attrapé pour en savoir plus.", text_of("Sheet/Text"))
	await tap("interact")
	check("et se referme sur la liste", dex().get_node("Control/Screen/List").visible and screen.visible)
	dex().register("bulbasaur", true)
	await wait(4)
	check("prise : sa categorie, sa marque dans la liste", text_of("Genus") == "Pokémon Graine" and text_of("Status") == "Attrapé" and row(0) == "001 Bulbizarre●", row(0))
	await tap("interact")
	check("sa fiche dit sa taille, son poids et sa description", text_of("Sheet/Height") == "Taille : 0,7 m" and text_of("Sheet/Weight") == "Poids : 6,9 kg" and text_of("Sheet/Text").length() > 40, text_of("Sheet/Height"))
	shot("pokedex_sheet")
	await tap("menu")
	check("la touche du menu referme la fiche, pas le Pokedex", screen.visible and dex().get_node("Control/Screen/List").visible)

	# la liste : 151 especes, celles de la premiere generation
	await tap("ui_up")
	check("vers le haut depuis la premiere, on arrive a la derniere : la 151", dex().shown_number() == 151 and text_of("Number") == "No 151", text_of("Number"))
	dex().register("mew", true)
	await wait(4)
	check("c'est Mew", text_of("Name") == "Mew" and text_of("List/Numbers/Row11") == "151", text_of("Name"))
	await tap("ui_down")
	await tap("ui_right")
	check("Droite saute dix especes", dex().shown_number() == 11, str(dex().shown_number()))
	shot("pokedex_list")
	await tap("menu")
	check("la touche du menu referme le Pokedex et rend le menu de pause", not screen.visible and menu_open())
