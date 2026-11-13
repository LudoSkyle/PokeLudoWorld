extends "res://tests/lib.gd"

# L'horloge du labo donne l'heure reelle.

func scene() -> String:
	return "lab_house"

func start() -> Vector2i:
	return Vector2i(18, 7)

func test() -> void:
	var t := Time.get_time_dict_from_system()
	await examine("horloge", Vector2i(18, 7), "%d h %02d" % [t.hour, t.minute])
