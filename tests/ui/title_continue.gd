extends "res://tests/lib.gd"

# Avec une sauvegarde, l'ecran titre propose Continuer en premier, et Continuer reprend la
# partie : meme carte, meme case.

func title() -> bool:
	return true

func test() -> void:
	await title_pick("Nouvelle partie")
	await title_gone()
	var saved := two_steps_from(cell())
	await walk("on se deplace avant de sauvegarder", saved, false)
	await menu_pick("Save")
	await wait_choices()
	await tap("interact")
	await secs(2.2)
	check("la partie est sauvegardee", saved_file().get_value("save", "scene", "").ends_with("start_town.tscn"))

	await relaunch()
	check("relance : l'ecran titre revient", title_shown() and level() == null)
	await title_ready()
	await tap("interact")
	check("avec une sauvegarde : Continuer vient en premier", title_entries() == ["Continuer", "Nouvelle partie", "Options", "Retour"], str(title_entries()))
	check("le curseur est sur Continuer", title_selected() == "Continuer", title_selected())
	shot("titre_continuer")
	await tap("interact")
	await title_gone()
	check("Continuer : l'ecran titre a disparu", not title_shown())
	check("on reprend sur la carte sauvegardee", level() != null and level().scene_file_path.ends_with("start_town.tscn"))
	check("sur la case sauvegardee", cell() == saved, str(cell()))
	await walk("on peut marcher", two_steps_from(saved), false)
