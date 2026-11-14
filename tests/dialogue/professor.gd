extends "res://tests/lib.gd"

# Le Professeur, dans son laboratoire : ce qu'il dit suit la quete.

func scene() -> String:
	return "lab_house"

func start() -> Vector2i:
	return Vector2i(12, 11)

func test() -> void:
	await talk("avant la quete", Vector2i(12, 11), "ui_up", "Professor", "bonjour", "idle_down")
	shot("dialogue_professeur")
	set_flag("bell_tarnished")
	await interact_facing("ui_up")
	await wait_text("Fais voir ça... Du bronze de l'ancienne mine.")
	check("la cloche trouvee : il reconnait le bronze", box_text().begins_with("Fais voir ça"), box_text())
	await tap("interact")
	await secs(1.6)
	await tap("interact")
	await wait_text("Pose-la dans la machine de soin, là-bas. Elle nettoie tout.")
	check("il envoie vers la machine de soin", box_text().contains("machine de soin"), box_text())
	await close_box()
	set_flag("bell_clean")
	await talk("la cloche nettoyee", Vector2i(12, 11), "ui_up", "Professor", "comme neuve", "idle_down")
	set_flag("bell_hung")
	await talk("la cloche accrochee : il l'a entendue", Vector2i(12, 11), "ui_up", "Professor", "entendue d'ici", "idle_down")
