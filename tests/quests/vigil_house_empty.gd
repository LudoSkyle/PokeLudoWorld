extends "res://tests/lib.gd"

# Apres la Veillee, Meme n'est plus dans le salon : elle est sur la place.

func scene() -> String:
	return "ludo_house"

func start() -> Vector2i:
	return Vector2i(18, 11)

func test() -> void:
	check("avant : elle est sur son tabouret", node("World/Entities/Odile") != null)
	set_flag("bell_hung")
	await reload_level()
	check("apres : elle n'est plus la", node("World/Entities/Odile") == null)
	await walk("on s'assoit a sa place", Vector2i(17, 11), false)
