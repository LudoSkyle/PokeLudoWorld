extends "res://tests/lib.gd"

# Un texte trop long pour les deux lignes de la boite se lit page par page :
# deux lignes s'ecrivent, la touche amene les suivantes, et le message d'apres
# ne vient qu'une fois la derniere page lue. Jamais de barre de defilement.

# Trois lignes dans la boite : deux pour la premiere page, une pour la seconde.
const LONG := "Les anciens ont gravé sur ce panneau toute la longue chronique du village : chaque maison construite, chaque tempête traversée, chaque bateau rentré au port."

func start() -> Vector2i:
	return Vector2i(35, 12)

func text_label() -> RichTextLabel:
	return game.get_node(VP + "/MessageBox/Control/Box/Text")

# Nombre de lignes que le texte demande a la largeur de la boite.
func lines_needed(text: String) -> int:
	var probe := TextParagraph.new()
	probe.width = text_label().size.x
	probe.add_string(text, text_label().get_theme_font("normal_font"), text_label().get_theme_font_size("normal_font_size"))
	return probe.get_line_count()

# Vrai si ce qui est ecrit tient dans la boite : deux lignes au plus, rien qui
# depasse en bas, et aucune barre de defilement — ni au texte, ni a ses ombres.
func fits() -> bool:
	var texts: Array = [text_label()]
	for child in text_label().get_children():
		if child is RichTextLabel:
			texts.append(child)
	for t in texts:
		if t.get_v_scroll_bar().visible or t.get_line_count() > 2 or t.get_content_height() > t.size.y:
			return false
	return true

func test() -> void:
	await spawn("sign", "Chatty", Vector2i(35, 11), {"text": LONG + "|Fin."})
	check("le texte de test demande trois lignes", lines_needed(LONG) == 3, str(lines_needed(LONG)))

	await interact_facing("ui_up")
	check("la boite s'ouvre et ecrit lettre a lettre", box().visible and LONG.begins_with(box_text()) and box_text().length() * 2 < LONG.length(), box_text())
	await tap("interact")
	var page1 := box_text()
	check("une pression finit d'ecrire la page : le debut du texte, pas tout", page1 != "" and LONG.begins_with(page1) and page1.length() < LONG.length(), page1)
	check("la premiere page remplit les deux lignes", text_label().get_line_count() == 2, str(text_label().get_line_count()))
	check("rien ne depasse, pas de barre de defilement", fits())
	shot("pages_1")
	await secs(0.5)
	check("la page attend la touche", box_text() == page1, box_text())

	var rest := LONG.substr(page1.length()).strip_edges()
	await tap("interact")
	check("la touche tourne la page : la suite s'ecrit lettre a lettre", box().visible and box_text() != page1 and rest.begins_with(box_text()) and box_text().length() < rest.length(), box_text())
	await wait_text(rest)
	check("la seconde page finit le texte, sans rien perdre", box_text() == rest and page1 + " " + rest == LONG, box_text())
	check("la, rien ne depasse non plus", fits())
	shot("pages_2")

	await tap("interact")
	await wait_text("Fin.")
	check("le message suivant ne vient qu'apres la derniere page", box().visible and box_text() == "Fin.", box_text())
	check("un texte court tient en une page", fits())
	await close_box()
	check("la boite est refermee", not box().visible)
