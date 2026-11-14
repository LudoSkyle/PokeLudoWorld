extends "res://tests/lib.gd"

# Un drapeau d'histoire fait partie de la sauvegarde.

func test() -> void:
	check("partie neuve : le drapeau n'est pas pose", not flag("test_flag"))
	set_flag("test_flag")
	check("pose, il l'est", flag("test_flag"))
	check("et lui seul", not flag("test_other"))
	await menu_pick("Save")
	await wait_choices()
	await tap("interact")
	await secs(2.2)
	check("il est ecrit dans la sauvegarde", saved_file().get_value("flags", "test_flag", false) == true)
	await relaunch()
	check("relance : il est toujours pose", flag("test_flag"))
	check("relance : toujours lui seul", not flag("test_other"))
