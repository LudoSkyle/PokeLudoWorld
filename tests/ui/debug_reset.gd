extends "res://tests/lib.gd"

# Debug : « Quete : debut » defait la quete de la cloche. Drapeaux retires, sac
# rendu, et la carte rechargee remet chacun a sa place d'avant.

func scene() -> String:
	return "start_island"

func start() -> Vector2i:
	return Vector2i(30, 27)

func key_items() -> Array:
	await menu_pick("Bag")
	await tap("ui_right")
	var rows := bag_rows()
	await tap("menu")
	await tap("menu")
	return rows

func test() -> void:
	# Rien a defaire tant que la quete n'a pas commence.
	await menu_pick("Debug")
	await tap("ui_down")
	await tap("interact")
	await tap("interact")
	await tap("interact")
	await secs(1.2)
	check("sans quete entamee, Debug le dit", box_text() == "« La cloche de la Veillée » : la quête n'a pas encore commencé.", box_text())
	await close_box()

	# On finit la quete : le village est sur la place, la route du nord est libre.
	await debug_tool(2)
	check("la quete est finie", flag("bell_hung") and flag("bell_told") and flag("bell_ribbon"))
	check("les gardes et Roland sont partis, Meme est sur la place",
		game.get_node_or_null(ENT + "GuardWest") == null and game.get_node_or_null(ENT + "Roland") == null and game.get_node_or_null(ENT + "OdileAfter") != null)
	check("la cloche est sur son socle", node("World/BellStand") != null and node("World/BellStandEmpty") == null)
	var rows: Array = await key_items()
	check("le sac porte ce que la quete a laisse", rows == ["Registre poussiéreux", "Ruban de la Veillée", "Retour"], str(rows))

	# La Veillee prend fin (comme si l'on avait quitte l'ile), on se tient la ou Roland reviendra, puis on repart de zero.
	set_flag("vigil_over")
	await place(Vector2i(11, 32))
	await debug_tool(3)
	var none := true
	for f in ["bell_told", "bell_register", "bell_tarnished", "bell_clean", "bell_ribbon", "bell_hung"]:
		if flag(f):
			none = false
	check("debut : plus aucun drapeau de la quete, ni l'indice de Roland, ni celui de la fin de la Veillee", none and not flag("bell_spotted") and not flag("vigil_over"))
	rows = await key_items()
	check("le sac est rendu : plus rien de la quete", rows == ["Retour"], str(rows))
	check("la carte s'est rechargee : gardes et Roland sont revenus, la place est vide",
		game.get_node_or_null(ENT + "GuardWest") != null and game.get_node_or_null(ENT + "GuardEast") != null and game.get_node_or_null(ENT + "Roland") != null
		and game.get_node_or_null(ENT + "OdileAfter") == null and game.get_node_or_null(ENT + "VisitorKalos") == null)
	check("le socle est de nouveau vide", node("World/BellStand") == null and node("World/BellStandEmpty") != null)
	check("Roland a repris sa case, et le joueur s'en est ecarte d'un pas", cell_of("Roland") == Vector2i(11, 32) and cell() != Vector2i(11, 32)
		and absi(cell().x - 11) + absi(cell().y - 32) == 1 and is_free(cell()), str(cell()))
	check("les habitants de toujours n'ont pas bouge", cell_of("BenchLady") == Vector2i(12, 13) and cell_of("Sailor") == Vector2i(53, 18))

	# La quete se rejoue : la cloche est de nouveau sous le ponton, une fois que Roland l'a dit.
	await place(Vector2i(19, 26))
	await interact_facing("ui_up")
	await secs(0.6)
	check("sans l'indice de Roland, rien sous le ponton", not box().visible)
	set_flag("bell_spotted")
	await wait(4)
	await interact_facing("ui_up")
	await wait_text("Quelque chose brille au fond de l'eau, juste sous le ponton.")
	check("la cloche est de nouveau a repecher", box_text() == "Quelque chose brille au fond de l'eau, juste sous le ponton.", box_text())
	await close_box()
	check("et on la repeche", flag("bell_tarnished") and not flag("bell_hung"))

	# Defaire une quete a moitie faite marche aussi.
	await debug_tool(3)
	check("debut, en cours de route : la cloche retourne a l'eau", not flag("bell_tarnished"))
	rows = await key_items()
	check("et quitte le sac", rows == ["Retour"], str(rows))
