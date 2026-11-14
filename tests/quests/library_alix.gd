extends "res://tests/lib.gd"

# Alix suit la quete : elle oriente vers les archives, puis reconnait le Registre.

func scene() -> String:
	return "library"

func start() -> Vector2i:
	return Vector2i(20, 12)

func test() -> void:
	set_flag("bell_told")
	await interact_facing("ui_up")
	await wait_text("La cloche ? Ta grand-mère en parle encore ?")
	check("la quete commencee : elle parle de la cloche", box_text() == "La cloche ? Ta grand-mère en parle encore ?", box_text())
	await tap("interact")
	await wait_text("Le registre des Veillées doit être quelque part dans ces rayons.")
	await tap("interact")
	await wait_text("Cherche au fond, à gauche : c'est là que dorment les vieux papiers.")
	check("elle montre le fond, a gauche", box_text().begins_with("Cherche au fond, à gauche"), box_text())
	await close_box()
	set_flag("bell_register")
	await talk("le Registre trouve", Vector2i(20, 12), "ui_up", "Alix", "tu l'as trouvé", "idle_down")
