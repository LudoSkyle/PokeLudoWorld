extends "res://tests/gdunit/game_suite.gd"

# Les icones d'objets (docs/bag.md, « La reserve d'icones ») : un fichier par icone, en 32 x 32.
# A la racine, celles du pack de donnees, sous l'identifiant de l'objet ; dans custom/ celles
# faites pour ce jeu ; dans other/ les trois venues d'ailleurs. Chaque objet du catalogue a la sienne.

const ICONS := "res://src/main/kotlin/fr/skyle/pokemonmirage/assets/items/icons/"

func start() -> Vector2i:
	return Vector2i(11, 11)

func test_bag_icons() -> void:
	if game == null:
		return
	var missing: String = get_tree().root.get_node("Globals").items_without_icon()
	check("chaque objet du catalogue a son icone", missing == "", missing)

	for path in ["potion", "poke_ball", "master_ball", "super_repel", "old_rod", "town_map", "rule_book",
			"custom/clear_bell", "custom/tarnished_bell", "other/07_F_2_fan", "other/00_F_F_special", "other/frlg_227"]:
		var texture: Texture2D = load(ICONS + path + ".png")
		check("%s.png fait 32 x 32" % path, texture != null and texture.get_size() == Vector2(32, 32),
			"introuvable" if texture == null else str(texture.get_size()))

	# Nos icones sont a part : la racine ne contient que celles du pack.
	var project := ProjectSettings.globalize_path(ICONS)
	var pngs := func(folder: String) -> Array: return Array(DirAccess.get_files_at(project + folder)).filter(func(f): return f.ends_with(".png"))
	check("custom/ ne contient que nos deux cloches", pngs.call("custom") == ["clear_bell.png", "tarnished_bell.png"], str(pngs.call("custom")))
	check("other/ ne contient que le ruban, la fleche Retour et le point d'interrogation", pngs.call("other") == ["00_F_F_special.png", "07_F_2_fan.png", "frlg_227.png"], str(pngs.call("other")))
	check("la cloche du pack n'est pas la notre", ResourceLoader.exists(ICONS + "clear_bell.png")
		and (load(ICONS + "clear_bell.png") as Texture2D).get_image().get_data() != (load(ICONS + "custom/clear_bell.png") as Texture2D).get_image().get_data())

	await menu_pick("Bag")
	check("sac vide : la ligne Retour montre sa fleche", bag("Icon").texture.resource_path.ends_with("icons/other/00_F_F_special.png"), bag("Icon").texture.resource_path)
	await tap("menu")
	await tap("menu")

# Ce test lit l'image a l'ecran : il lui faut une fenetre (tests/gdunit/run.sh le joue a part).
func reads_screen() -> bool:
	return true
