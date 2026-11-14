extends "res://tests/lib.gd"

# forbidden_flag : une fois son drapeau pose, le noeud n'est plus sur la carte.

func start() -> Vector2i:
	return Vector2i(35, 12)

func test() -> void:
	var cells := {"npc": Vector2i(35, 11), "readable": Vector2i(36, 11), "sign": Vector2i(37, 11), "roadblock": Vector2i(38, 11)}
	var before := {}
	for kind in cells:
		before[kind] = await spawn(kind, "Before_" + kind, cells[kind], {"forbidden_flag": "test_gone", "text": "Encore là."} if kind != "roadblock" else {"forbidden_flag": "test_gone"})
		check("sans le drapeau : le %s est la" % kind, is_instance_valid(before[kind]))
	await talk("il parle", Vector2i(35, 12), "ui_up", "Before_npc", "encore là", "idle_down")
	set_flag("test_gone")
	# La presence se decide au chargement de la carte : ceux qui y sont deja
	# restent jusqu'a ce qu'on la quitte.
	check("le drapeau pose ne retire pas un noeud deja charge", is_instance_valid(before["npc"]))
	for kind in cells:
		before[kind].free()
	await wait(4)
	for kind in cells:
		var node := await spawn(kind, "After_" + kind, cells[kind], {"forbidden_flag": "test_gone"})
		check("avec le drapeau : plus de %s" % kind, not is_instance_valid(node))
		check("avec le drapeau : la case du %s est libre" % kind, is_free(cells[kind]))
	await walk("on passe la ou il se tenait", Vector2i(35, 10), false)
