extends "res://tests/lib.gd"

# Deux directions tenues : la derniere pressee commande, et la premiere reprend
# la main quand on relache la seconde. Dans les deux sens, sans priorite.

func start() -> Vector2i:
	return Vector2i(29, 19)

# Tient `first`, puis presse `second` par-dessus, puis relache `second`.
# Renvoie les trois deplacements observes : avant, pendant, apres.
func overlap(first: String, second: String) -> Array:
	var moves: Array = []
	var from := cell()
	Input.action_press(first)
	await secs(0.55)
	moves.append(cell() - from)
	from = cell()
	Input.action_press(second)
	await secs(0.6)
	Input.action_release(second)
	await secs(0.3)
	moves.append(cell() - from)
	from = cell()
	await secs(0.55)
	moves.append(cell() - from)
	Input.action_release(first)
	await secs(0.4)
	return moves

func test() -> void:
	var m: Array = await overlap("ui_up", "ui_right")
	check("Haut tenu : on monte", m[0].y < 0 and m[0].x == 0, str(m[0]))
	check("Droite pressee par-dessus : on va a droite", m[1].x >= 1, str(m[1]))
	check("Droite relachee : Haut reprend la main", m[2].y < 0 and m[2].x == 0, str(m[2]))
	await place(Vector2i(34, 17))
	m = await overlap("ui_down", "ui_left")
	check("Bas tenu : on descend", m[0].y > 0 and m[0].x == 0, str(m[0]))
	check("Gauche pressee par-dessus : on va a gauche", m[1].x <= -1, str(m[1]))
	await place(Vector2i(29, 18))
	m = await overlap("ui_right", "ui_up")
	check("Droite tenue : on va a droite", m[0].x > 0 and m[0].y == 0, str(m[0]))
	check("Haut presse par-dessus : on monte, comme avant", m[1].y <= -1, str(m[1]))
	check("Haut relache : Droite reprend la main", m[2].x > 0 and m[2].y == 0, str(m[2]))
	await place(Vector2i(29, 18))
	# Deux directions opposees : la derniere pressee commande aussi.
	m = await overlap("ui_right", "ui_left")
	check("Droite puis Gauche : on repart a gauche", m[1].x < 0, str(m[1]))
