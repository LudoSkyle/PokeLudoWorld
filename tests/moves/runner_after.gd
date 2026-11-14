extends "res://tests/lib.gd"

# Apres la Veillee, le coureur tourne dans l'autre sens et passe par la place.

func start() -> Vector2i:
	return Vector2i(22, 17)

func test() -> void:
	set_flag("bell_hung")
	await reload_level()
	check("l'ancien coureur a laisse la place au nouveau", node("World/Entities/Runner") == null and node("World/Entities/RunnerAfter") != null)
	# Ses passages, dans l'ordre : il descend le chemin de l'ouest, longe le sud,
	# remonte, traverse le haut de la place, revient par le chemin, redescend.
	var marks := [Vector2i(14, 12), Vector2i(20, 15), Vector2i(31, 11), Vector2i(30, 10), Vector2i(26, 13), Vector2i(20, 16)]
	var seen := []
	var end := Time.get_ticks_msec() + 30000
	while Time.get_ticks_msec() < end and seen.size() < marks.size():
		await process_frame
		var c := cell_of("RunnerAfter")
		if c == marks[seen.size()]:
			seen.append(c)
			if c == Vector2i(31, 11):
				shot("coureur_place")
	check("il fait sa nouvelle boucle dans l'ordre", seen.size() == marks.size(), str(seen))
	check("en passant par le haut de la place", Vector2i(31, 11) in seen)
