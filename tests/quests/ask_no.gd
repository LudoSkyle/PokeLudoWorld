extends "res://tests/lib.gd"

# Une question avant d'agir : Non, ou la touche du menu, referme sans rien faire.

func start() -> Vector2i:
	return Vector2i(35, 12)

func test() -> void:
	await spawn("readable", "Machine", Vector2i(35, 11), {
		"ask": "Appuyer sur le bouton ?",
		"text": "@flag:test_pressed La machine s'allume.",
	})
	await interact_facing("ui_up")
	await wait_ask()
	await tap("ui_down")
	check("Bas mene a Non", ask_line() == 1, str(ask_line()))
	await tap("interact")
	check("Non : tout se referme", not box().visible and not ask_choices().visible)
	check("Non : rien n'est fait", not flag("test_pressed"))
	await tap("interact")
	check("on repose la question : elle s'ecrit lettre par lettre", box().visible and box_text() != "Appuyer sur le bouton ?", box_text())
	await tap("interact")
	check("une pression finit de l'ecrire, sans repondre", box_text() == "Appuyer sur le bouton ?" and box().visible, box_text())
	await wait_ask()
	check("la question revient, le curseur de nouveau sur Oui", ask_choices().visible and ask_line() == 0)
	await tap("menu")
	check("la touche du menu repond Non", not box().visible and not flag("test_pressed"))
	check("et n'ouvre pas le menu", not menu_open())
	await walk("on reprend la main", Vector2i(36, 12), false)
