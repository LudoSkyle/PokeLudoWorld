extends "res://tests/lib.gd"

# Une boite qui commence par @flag: pose un drapeau au moment ou elle s'affiche.

func start() -> Vector2i:
	return Vector2i(35, 12)

func test() -> void:
	await spawn("npc", "Teller", Vector2i(35, 11), {
		"text": "Écoute bien.|@flag:test_told Voilà, tu sais tout.",
		"states": PackedStringArray(["test_told > Je te l'ai déjà dit."]),
	})
	await interact_facing("ui_up")
	await wait_text("Écoute bien.")
	check("premiere boite : le drapeau n'est pas encore pose", box_text() == "Écoute bien." and not flag("test_told"), box_text())
	await tap("interact")
	await wait_text("Voilà, tu sais tout.")
	check("la consigne ne s'affiche pas", box_text() == "Voilà, tu sais tout.", box_text())
	check("le drapeau est pose quand sa boite s'affiche", flag("test_told"))
	await close_box()
	await talk("la fois suivante", Vector2i(35, 12), "ui_up", "Teller", "déjà dit", "idle_down")
