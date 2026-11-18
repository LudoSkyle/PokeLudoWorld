extends "res://tests/lib.gd"

# Les icones d'objets : un fichier par icone, en quatre dossiers. named/ pour les objets
# officiels qu'on sait nommer, unnamed/ pour ceux qu'on ne sait pas nommer, custom/ pour
# celles du jeu, invented/ pour les objets de Kryptonlion, que le jeu ne lit pas.
# Chaque objet du catalogue a la sienne, en 24 x 24.

const ICONS := "res://src/main/kotlin/fr/skyle/pokemonmirage/assets/items/icons/"

func start() -> Vector2i:
	return Vector2i(11, 11)

func test() -> void:
	var missing: String = root.get_node("Globals").items_without_icon()
	check("chaque objet du catalogue a son icone, en 24 x 24", missing == "", missing)

	for path in ["named/potion", "named/poke_ball", "named/master_ball", "named/razz_berry", "named/machine_fire", "named/rule_book", "named/tri_pass",
			"custom/clear_bell", "custom/tarnished_bell", "unnamed/07_F_2_fan", "unnamed/00_F_F_special", "unnamed/frlg_227"]:
		var texture: Texture2D = load(ICONS + path + ".png")
		check("%s.png fait 24 x 24" % path, texture != null and texture.get_size() == Vector2(24, 24),
			"introuvable" if texture == null else str(texture.get_size()))

	# Deux dessins du meme objet : le second porte le nom de son origine.
	var recent: Texture2D = load(ICONS + "named/old_rod.png")
	var first: Texture2D = load(ICONS + "named/old_rod-old_colors.png")
	check("la canne a ses deux dessins : le recent en 32 x 32, celui d'origine en 24 x 24",
		recent != null and first != null and recent.get_size() == Vector2(32, 32) and first.get_size() == Vector2(24, 24))

	# Nos icones sont a part : named/ ne contient que des objets officiels.
	var project := ProjectSettings.globalize_path(ICONS)
	check("custom/ ne contient que nos deux cloches", Array(DirAccess.get_files_at(project + "custom")).filter(func(f): return f.ends_with(".png")) == ["clear_bell.png", "tarnished_bell.png"])
	check("la cloche de named/ est le Glas officiel, pas la notre",
		(load(ICONS + "named/clear_bell.png") as Texture2D).get_image().get_data() != (load(ICONS + "custom/clear_bell.png") as Texture2D).get_image().get_data())
	# Une icone sans nom dont le jeu se sert garde le nom de sa case.
	check("le ruban et la fleche n'ont pas ete renommes", not ResourceLoader.exists(ICONS + "named/vigil_ribbon.png") and not ResourceLoader.exists(ICONS + "named/back.png"))
	check("les objets inventes sont sur le disque, mais le jeu ne les importe pas",
		DirAccess.get_files_at(project + "invented").size() > 20 and FileAccess.file_exists(project + "invented/.gdignore"))

	await menu_pick("Bag")
	check("sac vide : la ligne Retour montre sa fleche", bag("Icon").texture.resource_path.ends_with("icons/unnamed/00_F_F_special.png"), bag("Icon").texture.resource_path)
	await tap("menu")
	await tap("menu")
