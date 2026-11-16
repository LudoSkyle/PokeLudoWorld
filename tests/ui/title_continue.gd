extends "res://tests/lib.gd"

# Avec une sauvegarde, sa carte vient en premier : elle dit le lieu et le temps de jeu, et
# Continuer reprend la partie sur la meme carte, la meme case.

func title() -> bool:
	return true

func test() -> void:
	await title_pick("New")
	await title_gone()
	var saved := two_steps_from(cell())
	await walk("on se deplace avant de sauvegarder", saved, false)
	await menu_pick("Save")
	await wait_choices()
	await tap("interact")
	await secs(2.2)
	check("la partie est sauvegardee", saved_file().get_value("save", "scene", "").ends_with("field.tscn"))

	await relaunch()
	check("relance : l'ecran titre revient", title_shown() and level() == null)
	await slot_go("Save1")
	check("avec une sauvegarde : sa carte, Nouvelle partie, Options", slot_cards() == ["Save1", "New", "Options"], str(slot_cards()))
	check("la carte de la partie est choisie d'emblee", slot_selected() == "Save1", slot_selected())
	var card := slot_card("Save1")
	check("la carte porte son numero", card.get_node("Save/Title").text == "Partie 1", card.get_node("Save/Title").text)
	check("elle dit le lieu", card.get_node("Save/Location").text == "Terrain d'essai", card.get_node("Save/Location").text)
	check("elle dit le temps de jeu", card.get_node("Save/Time/Value").text == "00:00", card.get_node("Save/Time/Value").text)
	check("badges et Pokedex a zero pour l'instant", card.get_node("Save/Badges/Value").text == "0" and card.get_node("Save/Pokedex/Value").text == "0")
	check("six cases pour l'equipe", card.get_node("Save/Team").get_child_count() == 6)
	shot("titre_parties")

	await tap("interact")
	check("valider la carte propose Continuer, Effacer, Retour", slot_choices().visible and slot_answers() == ["Continuer", "Effacer", "Retour"], str(slot_answers()))
	shot("titre_parties_reponses")
	await tap("interact")
	await title_gone()
	check("Continuer : l'ecran titre a disparu", not title_shown())
	check("on reprend sur la carte sauvegardee", level() != null and level().scene_file_path.ends_with("field.tscn"))
	check("sur la case sauvegardee", cell() == saved, str(cell()))
	await walk("on peut marcher", two_steps_from(saved), false)
