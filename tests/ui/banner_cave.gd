extends "res://tests/lib.gd"

# La grotte a son bandeau sombre, au texte clair.

func scene() -> String:
	return "cave_1f"

func test() -> void:
	var r: Array = await watch_banner(1.5, "bandeau_grotte")
	var name: Label = game.get_node(VP + "/LocationBanner/Control/Panel/Name")
	check("le bandeau annonce la grotte", r[0] and r[1] == "Grotte - Entrée", str(r))
	check("bandeau de grotte", banner().texture.resource_path.ends_with("cave.png"), banner().texture.resource_path)
	check("texte clair sur fond sombre", name.get_theme_color("font_color") == Color(1, 1, 1, 1), str(name.get_theme_color("font_color")))
