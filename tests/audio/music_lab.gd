extends "res://tests/lib.gd"

# Le laboratoire a sa propre musique.

func scene() -> String:
	return "lab_house"

func test() -> void:
	check("le labo : sa musique", audio().music_id() == "elm_lab" and audio().music_audible(), audio().music_id())
