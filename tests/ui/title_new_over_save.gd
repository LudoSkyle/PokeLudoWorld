extends "res://tests/lib.gd"

# Nouvelle partie alors qu'une sauvegarde existe : on repart du point d'apparition de la carte
# de depart, et la sauvegarde reste en place tant qu'on ne sauvegarde pas par-dessus.

func title() -> bool:
	return true

func test() -> void:
	await title_pick("Nouvelle partie")
	await title_gone()
	var spawn := cell()
	var saved := two_steps_from(spawn)
	await walk("on s'eloigne du point d'apparition", saved, false)
	check("la case de sauvegarde n'est pas le point d'apparition", cell() != spawn, str(spawn))
	await menu_pick("Save")
	await wait_choices()
	await tap("interact")
	await secs(2.2)

	await relaunch()
	await title_pick("Nouvelle partie")
	await title_gone()
	check("Nouvelle partie : on repart du point d'apparition", cell() == spawn, "%s, attendu %s" % [cell(), spawn])
	check("la sauvegarde est toujours la", int(saved_file().get_value("save", "x", 0.0)) == saved.x * 16 + 8 and int(saved_file().get_value("save", "y", 0.0)) == saved.y * 16 + 8, str(saved_file().get_value("save", "x", 0.0)))
