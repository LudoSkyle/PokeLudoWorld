extends "res://tests/lib.gd"

# Le Pokedex regional, celui du jeu : on l'ouvre depuis le menu de pause. C'est le Pokedex de
# Pokemon Essentials, porte, dans son habillage (assets/ui/pokedex). Une espece jamais vue n'a que
# son numero ; vue, son nom, son portrait et sa fiche ; prise, sa categorie, ses types, sa taille,
# son poids et sa description. La liste s'arrete a la derniere espece vue.

func start() -> Vector2i:
	return Vector2i(22, 4)

func dex() -> Node:
	return game.get_node(VP + "/PokedexMenu")

func node(path: String) -> Node:
	return dex().get_node("Control/Screen/" + path)

func text_of(path: String) -> String:
	return str(node(path).text)

func row(n: int) -> String:
	return "%s %s" % [text_of("List/Numbers/Row%d" % n), text_of("List/Names/Row%d" % n)]

func mark(n: int) -> String:
	var texture: Texture2D = node("List/Marks/Row%d" % n).texture
	return "" if texture == null else texture.resource_path.get_file()

func test() -> void:
	await menu_pick("Pokedex")
	var screen: Control = node("")
	check("le Pokedex s'ouvre depuis le menu de pause, sur tout l'ecran : 512 x 384 grossi deux fois et demie", screen.visible and screen.size * screen.scale == Vector2(1280, 960), str(screen.size * screen.scale))
	check("rien n'est inscrit : la liste est vide, sans curseur", dex().listed_count() == 0 and not node("List/Cursor").visible and text_of("List/Seen") == "0" and text_of("List/Owned") == "0" and row(0) == " ", row(0))
	await tap("interact")
	check("sans rien dans la liste, valider n'ouvre rien", not node("Entry").visible)

	# vue
	dex().register("bulbasaur", false)
	await wait(4)
	check("vue : sa ligne, son nom, sa marque d'espece vue", dex().listed_count() == 1 and row(0) == "001 Bulbizarre" and mark(0) == "icon_seen.png", "%s %s" % [row(0), mark(0)])
	check("a gauche, son nom et son portrait ; les comptes suivent", text_of("List/Name") == "Bulbizarre" and node("List/Icon").texture != null and text_of("List/Seen") == "1" and text_of("List/Owned") == "0", text_of("List/Name"))
	check("le curseur est sur sa ligne", node("List/Cursor").visible and node("List/Cursor").position == Vector2(222, 46), str(node("List/Cursor").position))
	await tap("interact")
	check("sa fiche s'ouvre a la place de la liste", node("Entry").visible and not node("List").visible and text_of("Entry/Heading") == "001  Bulbizarre", text_of("Entry/Heading"))
	check("vue seulement : ni categorie, ni types, ni mesures, ni description", text_of("Entry/Genus") == "Pokémon ?????" and text_of("Entry/Height") == "????,? m" and text_of("Entry/Weight") == "????,? kg"
		and text_of("Entry/Text") == "" and node("Entry/Type0").texture == null and not node("Entry/Own").visible, text_of("Entry/Height"))
	await tap("menu")
	check("la touche du menu referme la fiche, pas le Pokedex", screen.visible and node("List").visible and not node("Entry").visible)

	# prise
	dex().register("bulbasaur", true)
	await wait(4)
	check("prise : sa marque change dans la liste", mark(0) == "icon_own.png" and text_of("List/Owned") == "1", mark(0))
	await tap("interact")
	check("sa fiche dit sa categorie, sa taille, son poids et sa description", text_of("Entry/Genus") == "Pokémon Graine" and text_of("Entry/Height") == "0,7 m" and text_of("Entry/Weight") == "6,9 kg"
		and text_of("Entry/Text").length() > 40 and node("Entry/Own").visible, "%s %s" % [text_of("Entry/Height"), text_of("Entry/Weight")])
	check("et ses deux types, aux cases de la planche : Plante, Poison", node("Entry/Type0").texture.region == Rect2(0, 12 * 32, 96, 32) and node("Entry/Type1").texture.region == Rect2(0, 3 * 32, 96, 32), str(node("Entry/Type0").texture.region))
	shot("pokedex_fiche")
	await tap("menu")

	# la liste : celles de la premiere generation, jusqu'a la derniere vue
	dex().register("mew", true)
	await wait(4)
	check("Mew vu : la liste va jusqu'a lui, la 151", dex().listed_count() == 151 and row(1) == "002 ----------" and mark(1) == "", row(1))
	check("dix lignes, et l'ascenseur montre qu'il en reste dessous", text_of("List/Numbers/Row9") == "010" and node("List/SliderDown").visible and not node("List/SliderUp").visible and node("List/SliderBox").visible)
	shot("pokedex_liste")
	await tap("interact")
	await tap("ui_down")
	check("dans la fiche, Bas saute les especes inconnues : de Bulbizarre a Mew", text_of("Entry/Heading") == "151  Mew" and text_of("Entry/Genus") == "Pokémon Nouveau", text_of("Entry/Heading"))
	await tap("ui_up")
	check("et Haut en revient", text_of("Entry/Heading") == "001  Bulbizarre", text_of("Entry/Heading"))
	await tap("menu")
	await tap("ui_up")
	check("dans la liste, Haut depuis la premiere mene a la derniere", dex().shown_number() == 151 and text_of("List/Name") == "Mew" and text_of("List/Numbers/Row9") == "151" and node("List/SliderUp").visible and not node("List/SliderDown").visible, text_of("List/Name"))
	await tap("ui_down")
	await tap("ui_right")
	check("Droite saute dix especes ; une inconnue n'a ni nom ni portrait", dex().shown_number() == 11 and text_of("List/Name") == "" and node("List/Icon").texture == null, str(dex().shown_number()))
	await tap("interact")
	check("et sa fiche ne s'ouvre pas", not node("Entry").visible)
	await tap("menu")
	check("la touche du menu referme le Pokedex et rend le menu de pause", not screen.visible and menu_open())
