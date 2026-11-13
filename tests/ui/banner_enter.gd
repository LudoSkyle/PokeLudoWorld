extends "res://tests/lib.gd"

# Entrer dans une maison annonce le nouveau lieu.

func start() -> Vector2i:
	return Vector2i(8, 16)

func test() -> void:
	await secs(3.5)
	check("le bandeau du village est remonte", not banner().visible)
	await hold_until_change("on entre chez Ludo", "ui_up")
	var r: Array = await watch_banner(1.5, "bandeau_maison")
	check("le bandeau annonce la maison", r[0] and r[1] == "Maison de Ludo", str(r))
