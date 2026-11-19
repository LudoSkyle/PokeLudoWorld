extends "res://tests/gdunit/game_suite.gd"

# Deux Poke Balls posees au sol : une Potion au bout de la presqu'ile du sud-est,
# une Poke Ball au fond de la plage de l'ouest. Ni l'une ni l'autre n'est un objet rare.

func scene() -> String:
	return "start_island"

func start() -> Vector2i:
	return Vector2i(47, 45)

func pick(label: String, first: String, second: String, who: String, flag_name: String, key := "ui_down", to := Vector2i.DOWN) -> void:
	check(label + " : l'objet est pose au sol, et plein", level().get_node_or_null("World/" + who) != null and not is_free(cell() + to))
	await interact_facing(key)
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
	check(label + " : il a quitte la carte, sa case se foule", level().get_node_or_null("World/" + who) == null and is_free(cell() + to))

func test_island_items() -> void:
	if game == null:
		return
	await pick("la Potion", "Vous trouvez une Potion !", "Vous rangez la Potion dans la poche Objets.", "ItemPotion", "found_island_potion")
	await menu_pick("Bag")
	check("la Potion est dans le sac", bag_rows().has("Potion x1"), str(bag_rows()))
	await tap("menu")
	await tap("menu")
	await place(Vector2i(3, 41))
	await pick("la Poke Ball", "Vous trouvez une Poké Ball !", "Vous rangez la Poké Ball dans la poche Poké Balls.", "ItemBall", "found_island_ball")
	await place(Vector2i(48, 2))
	await pick("l'Eau Fraiche", "Vous trouvez une Eau Fraîche !", "Vous rangez l'Eau Fraîche dans la poche Objets.", "ItemWater", "found_island_water", "ui_up", Vector2i.UP)
	# Le Rappel attend dans le creux du flanc ouest de la place : du sable que seule l'eau touche. On n'y vient pas a pied.
	var revive := level().get_node_or_null("World/ItemRevive")
	var nook := Vector2i(19, 26)
	check("un Rappel attend dans le creux, hors d'atteinte a pied", revive != null and Vector2i(floori(revive.position.x / 16.0), floori(revive.position.y / 16.0)) == nook
		and find_path(cell(), nook + Vector2i.LEFT).is_empty() and find_path(cell(), nook + Vector2i.UP).is_empty() and find_path(cell(), nook + Vector2i.DOWN).is_empty())
	await reload_level()
	check("apres rechargement, elles ne reviennent pas", level().get_node_or_null("World/ItemPotion") == null and level().get_node_or_null("World/ItemBall") == null)
