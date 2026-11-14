extends "res://tests/lib.gd"

# Une trouvaille sans suite quitte la carte une fois prise, et n'y revient pas.

func start() -> Vector2i:
	return Vector2i(35, 12)

func test() -> void:
	var props := {"kind": "item", "flag": "test_picked", "text": "@give:potion*2 Vous trouvez deux Potions !"}
	var item := await spawn("readable", "Pickup", Vector2i(35, 11), props)
	check("avant : elle occupe sa case", is_instance_valid(item) and not is_free(Vector2i(35, 11)))
	await interact_facing("ui_up")
	await wait_text("Vous trouvez deux Potions !")
	check("elle s'annonce, sans sa consigne", box_text() == "Vous trouvez deux Potions !", box_text())
	await close_box()
	await wait(4)
	check("prise : elle n'est plus sur la carte", not is_instance_valid(item) and flag("test_picked"))
	await walk("on marche sur sa case", Vector2i(35, 11), false)
	await tap("interact")
	check("il n'y a plus rien a examiner", not box().visible)
	item = await spawn("readable", "Pickup", Vector2i(36, 11), props)
	check("carte rechargee : elle n'y revient pas", not is_instance_valid(item))
	await menu_pick("Bag")
	check("le sac en a deux, pas plus", bag_rows() == ["Potion x2", "Retour"], str(bag_rows()))
