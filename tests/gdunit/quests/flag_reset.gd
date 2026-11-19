extends "res://tests/gdunit/game_suite.gd"

# Sans sauvegarde, une partie demarre sans aucun drapeau d'histoire.

func test_flag_reset() -> void:
	if game == null:
		return
	set_flag("test_flag")
	check("le drapeau est pose", flag("test_flag"))
	# On quitte sans sauvegarder : la relance ne trouve rien a reprendre.
	await relaunch()
	check("relance sans sauvegarde : il n'y a plus de drapeau", not flag("test_flag"))
	check("et l'on repart du point de depart", level() != null and player() != null)
