extends "res://tests/lib.gd"

# Alix, la bibliothecaire : avant la quete, elle souhaite la bienvenue.

func scene() -> String:
	return "library"

func start() -> Vector2i:
	return Vector2i(20, 12)

func test() -> void:
	check("au repos elle regarde la salle", anim("Alix") == "idle_down", anim("Alix"))
	await talk("Alix", Vector2i(20, 12), "ui_up", "Alix", "bienvenue", "idle_down")
	shot("dialogue_alix")
