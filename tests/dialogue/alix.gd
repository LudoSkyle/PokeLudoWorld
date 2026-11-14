extends "res://tests/lib.gd"

# Alix, la bibliothecaire : avant la quete, elle souhaite la bienvenue.

func scene() -> String:
	return "library"

func start() -> Vector2i:
	return Vector2i(20, 12)

func test() -> void:
	check("au repos elle regarde la salle", anim("Alix") == "idle_down", anim("Alix"))
	await interact_facing("ui_up")
	await wait_text("Bienvenue à la bibliothèque.")
	check("son nom est affiche, en rouge", speaker_name() == "Alix" and speaker_color() == "red", speaker_name() + " " + speaker_color())
	shot("nom_alix")
	await close_box()
	await talk("Alix", Vector2i(20, 12), "ui_up", "Alix", "bienvenue", "idle_down")
	shot("dialogue_alix")
