extends "res://tests/lib.gd"

# Les objets de la route du nord : la Potion et l'Antidote sont les deux Poke Balls de la
# carte d'exemple. Leur case vient du generateur : le test la lit sur la carte.

func scene() -> String:
	return "route_1"

func start() -> Vector2i:
	return Vector2i(45, 48)

func cell_at(node: Node2D) -> Vector2i:
	return Vector2i(floori(node.position.x / 16.0), floori(node.position.y / 16.0))

# Ou se tenir pour ramasser ce qui est en `target` : [case, touche pour lui faire face].
func front_of(target: Vector2i) -> Array:
	for d in [[Vector2i.DOWN, "ui_up"], [Vector2i.LEFT, "ui_right"], [Vector2i.RIGHT, "ui_left"], [Vector2i.UP, "ui_down"]]:
		if is_free(target + d[0]):
			return [target + d[0], d[1]]
	return []

func pick(label: String, first: String, second: String, who: String, flag_name: String) -> void:
	var node: Node2D = level().get_node_or_null("World/" + who)
	check(label + " : l'objet est pose au sol, et plein", node != null and not is_free(cell_at(node)))
	var target := cell_at(node)
	var front := front_of(target)
	check(label + " : on peut se tenir a cote", not front.is_empty(), str(target))
	await place(front[0])
	await interact_facing(front[1])
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
	check(label + " : il a quitte la carte, sa case se foule", level().get_node_or_null("World/" + who) == null and is_free(target))

# L'arbuste de l'exemple se coupe, dans les jeux d'origine. Le notre ne sait pas encore : il le dit, et reste plein.
func cut_tree() -> void:
	var tree: Node2D = level().get_node_or_null("Readables/CutTree0")
	check("l'arbuste a coupe a de quoi se lire", tree != null)
	var target := cell_at(tree)
	var front := front_of(target)
	check("l'arbuste : on peut se tenir devant", not front.is_empty(), str(target))
	await place(front[0])
	await interact_facing(front[1])
	var said := "Cet arbre semble pouvoir être coupé !"
	await wait_text(said)
	check("l'arbuste dit qu'il se coupe", box_text() == said, box_text())
	await close_box()
	await secs(0.3)
	check("et il reste plein", not is_free(target))

func test() -> void:
	await pick("la Potion", "Vous trouvez une Potion !", "Vous rangez la Potion dans la poche Objets.", "ItemRoutePotion", "found_route_potion")
	await pick("l'Antidote", "Vous trouvez un Antidote !", "Vous rangez l'Antidote dans la poche Objets.", "ItemRouteAntidote", "found_route_antidote")
	await cut_tree()
