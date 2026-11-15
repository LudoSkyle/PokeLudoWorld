extends "res://tests/lib.gd"

# Deux Poke Balls posees au sol : une Potion au fond du recoin de la pointe de l'est,
# une Poke Ball au bord des hautes herbes. Ni l'une ni l'autre n'est un objet rare.

func scene() -> String:
	return "start_island"

func start() -> Vector2i:
	return Vector2i(55, 31)

func pick(label: String, first: String, second: String, who: String, flag_name: String) -> void:
	check(label + " : l'objet est pose au sol, et plein", level().get_node_or_null("World/" + who) != null and not is_free(cell() + Vector2i.DOWN))
	await interact_facing("ui_down")
	await wait_text(first)
	check(label + " : on le trouve", box_text() == first, box_text())
	var presses := 0
	while box().visible and box_text() != second and presses < 12:
		await tap("interact")
		await secs(0.5)
		presses += 1
	await wait_text(second)
	check(label + " : on le range", box_text() == second, box_text())
	await close_box()
	await secs(0.3)
	check(label + " : son drapeau est pose", flag(flag_name))
	check(label + " : il a quitte la carte, sa case se foule", level().get_node_or_null("World/" + who) == null and is_free(cell() + Vector2i.DOWN))

func test() -> void:
	await pick("la Potion", "Vous trouvez une Potion !", "Vous rangez la Potion dans la poche Objets.", "ItemPotion", "found_island_potion")
	await menu_pick("Bag")
	check("la Potion est dans le sac", bag_rows().has("Potion x1"), str(bag_rows()))
	await tap("menu")
	await tap("menu")
	await place(Vector2i(5, 39))
	await pick("la Poke Ball", "Vous trouvez une Poké Ball !", "Vous rangez la Poké Ball dans la poche Poké Balls.", "ItemBall", "found_island_ball")
	await reload_level()
	check("apres rechargement, elles ne reviennent pas", level().get_node_or_null("World/ItemPotion") == null and level().get_node_or_null("World/ItemBall") == null)
