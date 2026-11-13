extends "res://tests/lib.gd"

# Menu ouvert : le coureur s'arrete sur sa case, et repart a la fermeture.

func test() -> void:
	await secs(1.0)
	await tap("menu")
	await secs(0.5)
	var stopped := cell_of("Runner")
	var p0: Vector2 = npc("Runner").position
	await secs(1.5)
	check("menu ouvert : le coureur ne bouge plus", npc("Runner").position == p0, "%s -> %s" % [p0, npc("Runner").position])
	check("menu ouvert : il s'est arrete sur une case entiere", resting("Runner"), str(p0))
	check("menu ouvert : il ne court pas sur place", anim("Runner").begins_with("idle_"), anim("Runner"))
	await tap("menu")
	await secs(1.0)
	check("menu ferme : le coureur repart", cell_of("Runner") != stopped, str(cell_of("Runner")))
