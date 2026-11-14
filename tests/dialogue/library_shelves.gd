extends "res://tests/lib.gd"

# Bibliotheque : rayonnages ordinaires, et archives tant que la quete n'a pas commence.

func scene() -> String:
	return "library"

func start() -> Vector2i:
	return Vector2i(13, 9)

func test() -> void:
	await examine("rayonnage du fond", Vector2i(13, 9), "pleine de livres")
	await examine("rayonnage du milieu, depuis derriere lui", Vector2i(13, 10), "pleine de livres", "ui_down")
	await examine("archives, premiere case", Vector2i(9, 9), "pleine de livres")
	await examine("archives, troisieme case : rien a prendre", Vector2i(11, 9), "pleine de livres")
	check("aucun drapeau n'est pose", not flag("bell_register"))
	await menu_pick("Bag")
	await tap("ui_right")
	check("le sac ne contient pas de registre", bag_rows() == ["Retour"], str(bag_rows()))
