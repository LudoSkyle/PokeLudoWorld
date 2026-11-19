extends "res://tests/gdunit/game_suite.gd"

# Le laboratoire a sa propre musique.

func scene() -> String:
	return "lab_house"

func test_music_lab() -> void:
	if game == null:
		return
	check("le labo : sa musique", audio().music_id() == "elm_lab" and audio().music_audible(), audio().music_id())
