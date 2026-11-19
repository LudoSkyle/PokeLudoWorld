extends "res://tests/gdunit/game_suite.gd"

# Les traces de pas : le sable les garde quelques instants, l'herbe n'en garde aucune.

func start() -> Vector2i:
	return Vector2i(2, 11)          # la rive de l'etang du terrain d'essai

func traces() -> int:
	var holder := level().get_node_or_null("Background/Footprints")
	return 0 if holder == null else holder.get_child_count()

func test_footprints() -> void:
	if game == null:
		return
	# On descend la rive sans relacher la touche : une paire d'empreintes par case quittee.
	# Elles ne vivent qu'une seconde, donc on compte PENDANT la marche.
	Input.action_press("ui_down")
	await secs(0.7)
	var during := traces()
	Input.action_release("ui_down")
	check("des traces dans le sable", during >= 2, "%d traces" % during)
	check("on a bien descendu la rive", cell().x == 2 and cell().y > 11, str(cell()))

	var holder := level().get_node("Background/Footprints")
	var paths := level().get_node("Background/Paths")
	check("les traces sont posees juste au-dessus du sol",
		holder.get_index() == paths.get_index() + 1, "index %d" % holder.get_index())

	# Elles ne restent que quelques instants : une seconde et demie plus tard, plus rien.
	await secs(1.5)
	check("le sable redevient net", traces() == 0, "%d traces" % traces())

	# Sur l'herbe, aucune trace : on quitte la rive, on laisse tout s'effacer, puis on marche.
	await walk("vers l'herbe", Vector2i(8, 10), false)
	await secs(1.5)
	await walk("sur l'herbe", Vector2i(12, 10), false)
	check("l'herbe ne garde rien", traces() == 0, "%d traces" % traces())
