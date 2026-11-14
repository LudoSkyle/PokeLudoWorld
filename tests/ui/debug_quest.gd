extends "res://tests/lib.gd"

# L'entree Debug du menu fait avancer la quete de la cloche, etape par etape ou d'un coup.

func start() -> Vector2i:
	return Vector2i(31, 15)

func test() -> void:
	await menu_pick("Debug")
	var answers := []
	for label in debug_choices().get_node("Entries").get_children():
		if label.visible: answers.append(label.text)
	check("Debug ouvre ses outils", debug_choices().visible and answers == ["Remplir le sac", "Quête : suite", "Quête : fin", "Retour"], str(answers))
	shot("debug_outils")
	await tap("menu")
	check("la touche du menu referme les outils, pas le menu", not debug_choices().visible and menu_open())
	await tap("menu")
	check("puis le menu", not menu_open())
	await debug_tool(1)
	check("suite : la premiere etape est posee, elle seule", flag("bell_told") and not flag("bell_register"))
	await debug_tool(1)
	await debug_tool(1)
	check("deux de plus : on a trouve la cloche ternie", flag("bell_register") and flag("bell_tarnished") and not flag("bell_clean"))
	await menu_pick("Bag")
	await tap("ui_right")
	check("le sac suit : le Registre et la Cloche ternie", bag_rows() == ["Registre poussiéreux", "Cloche ternie", "Retour"], str(bag_rows()))
	await tap("menu")
	await tap("menu")
	await debug_tool(2)
	check("fin : tous les drapeaux sont poses", flag("bell_clean") and flag("bell_ribbon") and flag("bell_hung"))
	check("la carte s'est rechargee : la cloche est sur son socle, Meme est la", node("World/BellStand") != null and node("World/Entities/OdileAfter") != null)
	await menu_pick("Bag")
	await tap("ui_right")
	check("le sac suit : plus de cloche, le Ruban en plus", bag_rows() == ["Registre poussiéreux", "Ruban de la Veillée", "Retour"], str(bag_rows()))
	await tap("menu")
	await tap("menu")
	await menu_pick("Debug")
	await tap("ui_down")
	await tap("interact")
	await secs(1.5)
	check("une fois finie, Debug le dit", box_text() == "La quête de la cloche est déjà terminée.", box_text())
	await close_box()
