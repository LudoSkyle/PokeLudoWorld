extends "res://tests/gdunit/game_suite.gd"

# Le reflet dans l'eau : il n'apparait qu'au bord de l'eau, retourne, sous les pieds.

func start() -> Vector2i:
	return Vector2i(3, 10)          # l'herbe juste au nord de l'etang du terrain d'essai

# Le reflet du joueur : celui qui se montre sous lui, a sa verticale.
func mine() -> Node2D:
	var holder := level().get_node_or_null("Background/Reflections")
	if holder == null:
		return null
	for child in holder.get_children():
		if child.visible and abs(child.global_position.x - player().global_position.x) < 2.0:
			return child
	return null

func test_reflection() -> void:
	if game == null:
		return
	await secs(0.4)
	var glass := mine()
	check("au bord de l'eau, un reflet", glass != null)
	if glass == null:
		return

	check("il est retourne", glass.flip_v)
	check("il est sous les pieds", glass.global_position.y > player().global_position.y,
		"reflet %s, joueur %s" % [glass.global_position, player().global_position])
	check("il est a la verticale du joueur",
		abs(glass.global_position.x - player().global_position.x) < 2.0)

	var holder := level().get_node("Background/Reflections")
	var ground := level().get_node("Background/Ground")
	check("les reflets sont poses juste au-dessus de l'eau",
		holder.get_index() == ground.get_index() + 1, "index %d" % holder.get_index())

	# Un pas a l'ouest : sous cette case-la c'est la rive, du sable. Plus de reflet.
	await walk("sur la rive", Vector2i(2, 10), false)
	await secs(0.3)
	check("pas de reflet au-dessus du sable", mine() == null)

	# Et au retour, il revient.
	await walk("retour au bord", Vector2i(3, 10), false)
	await secs(0.3)
	var back := mine()
	check("le reflet revient", back != null)

	# Il ne surgit pas d'un bloc : il sort de l'eau au fil du pas. Une case plus
	# au nord, seul son sommet affleure ; en descendant, la part visible grandit.
	var full: float = back.region_rect.size.y if back != null else 0.0
	await walk("une case au nord", Vector2i(3, 9), false)
	await secs(0.3)
	var far := mine()
	check("de loin, le reflet affleure a peine", far != null and far.region_rect.size.y < full,
		"%.0f px contre %.0f au bord" % [0.0 if far == null else far.region_rect.size.y, full])
