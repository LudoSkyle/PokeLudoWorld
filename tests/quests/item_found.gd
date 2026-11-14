extends "res://tests/lib.gd"

# Une trouvaille : elle donne son objet une seule fois, pose son drapeau, puis dit autre chose.

func start() -> Vector2i:
	return Vector2i(35, 12)

func test() -> void:
	var shelf := await spawn("readable", "Shelf", Vector2i(35, 11), {
		"kind": "item",
		"flag": "test_found",
		"text": "Quelque chose dépasse de la rangée.|@give:old_rod Vous recevez la Vieille canne !|Elle était là depuis longtemps.",
		"states": PackedStringArray(["test_found > Il y a un vide dans la rangée."]),
	})
	await interact_facing("ui_up")
	await wait_text("Quelque chose dépasse de la rangée.")
	check("d'abord ce qu'on voit, sans objet a l'ecran", box_text() == "Quelque chose dépasse de la rangée." and not reveal().visible, box_text())
	await tap("interact")
	await wait_text("Vous recevez la Vieille canne !")
	await secs(0.4)
	check("l'objet rare est montre avec son annonce", reveal().visible and box_text() == "Vous recevez la Vieille canne !", box_text())
	shot("trouvaille")
	await wait_text("Elle était là depuis longtemps.")
	check("la suite arrive seule", box_text() == "Elle était là depuis longtemps.", box_text())
	await close_box()
	check("le drapeau de la trouvaille est pose", flag("test_found"))
	check("le meuble est toujours la", is_instance_valid(shelf) and not is_free(Vector2i(35, 11)))
	await examine("on reexamine", Vector2i(35, 12), "un vide")
	await menu_pick("Bag")
	await tap("ui_right")
	check("l'objet est dans le sac, une seule fois", bag_rows() == ["Vieille canne", "Retour"], str(bag_rows()))
