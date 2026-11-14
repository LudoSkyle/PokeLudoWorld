extends "res://tests/lib.gd"

# Une question avant d'agir : Oui enchaine sur le texte, qui agit.

func start() -> Vector2i:
	return Vector2i(35, 12)

func test() -> void:
	await spawn("readable", "Machine", Vector2i(35, 11), {
		"ask": "Appuyer sur le bouton ?",
		"text": "@flag:test_pressed La machine s'allume.|Elle chante trois notes.",
	})
	await interact_facing("ui_up")
	await secs(0.15)
	check("la question s'ecrit d'abord, sans Oui / Non", box().visible and not ask_choices().visible)
	await wait_ask()
	check("la question est posee", box_text() == "Appuyer sur le bouton ?", box_text())
	check("Oui / Non apparait, le curseur sur Oui", ask_choices().visible and ask_line() == 0, str(ask_line()))
	check("au-dessus de la boite de dialogue", ask_choices().position.y + ask_choices().size.y <= box().position.y + 1.0)
	check("rien n'est fait tant qu'on n'a pas repondu", not flag("test_pressed"))
	shot("question")
	await tap("interact")
	await wait_text("La machine s'allume.")
	check("Oui : le texte suit", box_text() == "La machine s'allume." and not ask_choices().visible, box_text())
	check("Oui : l'action est faite", flag("test_pressed"))
	await tap("interact")
	await wait_text("Elle chante trois notes.")
	check("la suite se lit comme un dialogue", box_text() == "Elle chante trois notes.", box_text())
	await close_box()
	check("la boite est refermee", not box().visible)
	await walk("on reprend la main", Vector2i(36, 12), false)
