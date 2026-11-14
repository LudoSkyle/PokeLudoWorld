extends "res://tests/lib.gd"

# Apres la Veillee, Alix n'est plus derriere son bureau : elle est sur la place.

func scene() -> String:
	return "library"

func start() -> Vector2i:
	return Vector2i(20, 12)

func test() -> void:
	check("avant : elle est a cote de son bureau", node("World/Entities/Alix") != null)
	set_flag("bell_hung")
	await reload_level()
	check("apres : elle n'est plus la", node("World/Entities/Alix") == null)
	await walk("on passe la ou elle se tenait", Vector2i(20, 10), false)
