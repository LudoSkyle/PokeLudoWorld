extends "res://tests/lib.gd"

# Le menu s'ouvre avec X, se referme avec X, et fige le joueur entre les deux.

func test() -> void:
	check("ferme au depart", not menu_open())
	await tap("menu")
	check("X ouvre le menu", menu_open())
	shot("menu_ouvert")
	var before := cell()
	var facing := str(player().get_node("Sprite").animation)
	Input.action_press("ui_left"); await secs(0.6); Input.action_release("ui_left"); await wait(8)
	Input.action_press("ui_down"); await secs(0.6); Input.action_release("ui_down"); await wait(8)
	check("menu ouvert : les fleches ne deplacent pas le joueur", cell() == before, str(cell()))
	check("menu ouvert : le joueur ne se tourne pas", str(player().get_node("Sprite").animation) == facing, str(player().get_node("Sprite").animation))
	await tap("menu")
	check("X referme le menu", not menu_open())
	await walk("menu ferme : on remarche", before + Vector2i(-1, 0), false)
