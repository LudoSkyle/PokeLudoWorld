extends "res://tests/lib.gd"

# Les portes de l'ile : trois batiments s'ouvrent, deux sont de simples facades.

func scene() -> String:
	return "start_island"

func start() -> Vector2i:
	return Vector2i(15, 10)

func test() -> void:
	# La maison orange : sa porte ne mene nulle part.
	var id0 := level_id()
	await hold_no_change("maison orange du nord-ouest : porte close", "ui_up")
	check("on reste devant la maison orange", cell() == Vector2i(15, 10) and level_id() == id0, str(cell()))
	# Chez Ludo.
	place(Vector2i(8, 11))
	await hold_until_change("porte de Ludo", "ui_up")
	check("on entre chez Ludo", str(level().scene_file_path).ends_with("ludo_house.tscn"), str(level().scene_file_path))
	await hold_until_change("paillasson de Ludo", "ui_down")
	await arrival("retour devant chez Ludo", Vector2i(8, 11), "idle_down")
	# La bibliotheque.
	place(Vector2i(8, 28))
	await hold_until_change("porte de la bibliotheque", "ui_up")
	check("on entre dans la bibliotheque", str(level().scene_file_path).ends_with("library.tscn"), str(level().scene_file_path))
	await hold_until_change("paillasson de la bibliotheque", "ui_down")
	await arrival("retour devant la bibliotheque", Vector2i(8, 28), "idle_down")
	# Le laboratoire.
	place(Vector2i(48, 11))
	await hold_until_change("porte du labo", "ui_up")
	check("on entre au labo", str(level().scene_file_path).ends_with("lab_house.tscn"), str(level().scene_file_path))
