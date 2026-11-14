extends "res://tests/lib.gd"

# required_flag : sans son drapeau, le noeud n'est pas sur la carte.

func start() -> Vector2i:
	return Vector2i(35, 12)

func test() -> void:
	var cells := {"npc": Vector2i(35, 11), "readable": Vector2i(36, 11), "sign": Vector2i(37, 11), "roadblock": Vector2i(38, 11)}
	for kind in cells:
		var node := await spawn(kind, "Absent_" + kind, cells[kind], {"required_flag": "test_here"})
		check("sans le drapeau : pas de %s" % kind, not is_instance_valid(node))
		check("sans le drapeau : la case du %s est libre" % kind, is_free(cells[kind]))
	await walk("on marche la ou se tiendrait le PNJ", Vector2i(35, 11), false)
	await walk("on revient", Vector2i(35, 12), false)
	set_flag("test_here")
	for kind in cells:
		var node := await spawn(kind, "Present_" + kind, cells[kind], {"required_flag": "test_here", "text": "Je suis là."} if kind != "roadblock" else {"required_flag": "test_here"})
		check("avec le drapeau : le %s est la" % kind, is_instance_valid(node))
		if kind != "roadblock":
			check("avec le drapeau : le %s occupe sa case" % kind, not is_free(cells[kind]))
	await talk("et il parle", Vector2i(35, 12), "ui_up", "Present_npc", "je suis là", "idle_down")
