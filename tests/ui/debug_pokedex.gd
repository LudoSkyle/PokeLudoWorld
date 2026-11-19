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
	check("son icone et son sprite de marche sont la : il ne lui manque rien", dex().get_node("Control/Screen/Icon").texture != null and dex().get_node("Control/Screen/Walker").texture != null
		and text_of("Lacks") == "", text_of("Lacks"))
	check("la liste montre quatorze especes, le curseur sur la premiere, sans etoile", text_of("List").split("\n").size() == 14 and text_of("List").split("\n")[0] == "> 0001 Bulbizarre", text_of("List").split("\n")[0])
	shot("pokedex_debug")

	# Le sprite de marche se montre de face, puis tourne sur lui-meme : un quart de tour par seconde.
	var walker: TextureRect = dex().get_node("Control/Screen/Walker")
	var front: Rect2 = walker.texture.region
	var grid: TextureRect = dex().get_node("Control/Screen/WalkerGrid")
	check("il est a quatre pixels d'ecran par pixel, sur un damier au pixel avec les axes de sa case", walker.size == Vector2(128, 128) and grid.visible and grid.size == Vector2(128, 128) and grid.texture.get_size() == Vector2(8, 8)
		and dex().get_node("Control/Screen/WalkerAxisV").position.x == grid.position.x + 63, "%s %s" % [walker.size, grid.size])
	check("il se montre d'abord de face", dex().shown_facing() == 0 and front.position == Vector2(0, 0) and front.size == Vector2(32, 32), str(front))
	var sides := {}
	var end := Time.get_ticks_msec() + 4300
	while Time.get_ticks_msec() < end:
		await process_frame
		sides[dex().shown_facing()] = walker.texture.region.position
	check("en quatre secondes il a montre ses quatre cotes : face, gauche, dos, droite", sides.size() == 4 and sides[0] == Vector2(0, 0) and sides[1] == Vector2(0, 32) and sides[2] == Vector2(0, 96) and sides[3] == Vector2(0, 64), str(sides))

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
	check("la derniere est complete elle aussi : rien ne lui manque", text_of("Lacks") == "" and text_of("French").length() > 40, text_of("Lacks"))
	check("la liste a suivi : la derniere ligne porte le curseur, sans etoile", text_of("List").split("\n")[-1] == "> 1025 Pêchaminus", text_of("List").split("\n")[-1])

	# Un gros Pokemon a son propre fichier, pas une case de la planche : Lugia.
	await tap("ui_down")
	for i in 24:
		await tap("ui_right")
	for i in 8:
		await tap("ui_down")
	var big_walker: TextureRect = dex().get_node("Control/Screen/Walker")
	check("un gros Pokemon est montre a la meme echelle que les autres, donc deux fois plus grand : 64 pixels sur 256", big_walker.texture.region.size == Vector2(64, 64) and big_walker.size == Vector2(256, 256)
		and dex().get_node("Control/Screen/WalkerGrid").size == Vector2(256, 256), "%s %s" % [big_walker.texture.region.size, big_walker.size])
	check("Lugia, gros Pokemon, a son sprite dans son propre fichier", dex().shown_number() == 249 and dex().get_node("Control/Screen/Walker").texture != null and text_of("Lacks") == "", "%d %s" % [dex().shown_number(), text_of("Lacks")])
	await tap("ui_up")
	for i in 30:
		await tap("ui_left")
	await tap("ui_up")

	# Une espece qui a tout : Joliflor.
	await tap("ui_down")
	for i in 18:
		await tap("ui_right")
	await tap("ui_down")
	check("Joliflor a tout, sprite compris", dex().shown_number() == 182 and text_of("Lacks") == "" and dex().get_node("Control/Screen/Walker").texture != null, "%d %s" % [dex().shown_number(), text_of("Lacks")])
	var shown: String = dex().get_node("Control/Screen/Walker").texture.atlas.resource_path
	check("chaque espece a son fichier : celui de Joliflor", shown.ends_with("pokemon/overworld/bellossom.png"), shown)
	shot("pokedex_debug_complet")

	await tap("menu")
	check("la touche du menu referme la vue, pas le menu", not screen.visible and menu_open())
