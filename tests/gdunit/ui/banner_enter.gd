extends "res://tests/gdunit/game_suite.gd"

# Entrer quelque part annonce le nouveau lieu.

func start() -> Vector2i:
	return Vector2i(21, 2)

func test_banner_enter() -> void:
	if game == null:
		return
	await secs(3.5)
	check("le bandeau du terrain est remonte", not banner().visible)
	await hold_until_change("on entre dans la cabane", "ui_up")
	var r: Array = await watch_banner(1.5, "bandeau_cabane")
	check("le bandeau annonce la cabane", r[0] and r[1] == "Cabane", str(r))
