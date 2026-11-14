extends "res://tests/lib.gd"

# Une question ne porte que sur une etape : avant et apres, le PNJ parle sans rien demander.

func start() -> Vector2i:
	return Vector2i(35, 12)

func test() -> void:
	await spawn("npc", "Giver", Vector2i(35, 11), {
		"text": "Reviens quand tu auras quelque chose.",
		"states": PackedStringArray(["test_ready > @flag:test_shown Oh, c'est magnifique.", "test_shown > Merci de me l'avoir montré."]),
		"ask": "test_ready > Lui montrer ce que tu as ?",
	})
	await talk("avant : pas de question", Vector2i(35, 12), "ui_up", "Giver", "reviens quand", "idle_down")
	set_flag("test_ready")
	await interact_facing("ui_up")
	await wait_ask()
	check("a son etape : la question", box_text() == "Lui montrer ce que tu as ?" and ask_choices().visible, box_text())
	check("il s'est tourne vers nous pour la poser", anim("Giver") == "idle_down", anim("Giver"))
	await tap("interact")
	await wait_text("Oh, c'est magnifique.")
	check("Oui : il repond et l'histoire avance", box_text() == "Oh, c'est magnifique." and flag("test_shown"), box_text())
	await close_box()
	await talk("apres : plus de question", Vector2i(35, 12), "ui_up", "Giver", "merci de me", "idle_down")
