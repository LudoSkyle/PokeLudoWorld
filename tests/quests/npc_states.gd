extends "res://tests/lib.gd"

# Un PNJ dit le texte de la derniere etape atteinte ; sans drapeau, son texte par defaut.

func start() -> Vector2i:
	return Vector2i(35, 12)

func test() -> void:
	await spawn("npc", "Teller", Vector2i(35, 11), {
		"text": "Texte par défaut.",
		"states": PackedStringArray(["test_a > Texte de l'étape A.|Seconde boîte de A.", "test_b > Texte de l'étape B."]),
	})
	await talk("sans drapeau", Vector2i(35, 12), "ui_up", "Teller", "texte par défaut", "idle_down")
	set_flag("test_a")
	await tap("interact")
	await secs(1.5)
	check("premier drapeau : le texte de son etape", box_text() == "Texte de l'étape A.", box_text())
	await tap("interact")
	await secs(1.5)
	check("la barre separe toujours deux boites", box_text() == "Seconde boîte de A.", box_text())
	await close_box()
	set_flag("test_b")
	await talk("deux drapeaux : la derniere etape gagne", Vector2i(35, 12), "ui_up", "Teller", "étape b", "idle_down")
