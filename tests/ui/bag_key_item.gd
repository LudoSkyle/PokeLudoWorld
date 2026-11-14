extends "res://tests/lib.gd"

# Valider un objet rare : une seule action, Annuler.

func test() -> void:
	await fill_bag()
	await menu_pick("Bag")
	await tap("ui_right")
	await tap("interact")
	check("la boite d'actions s'ouvre", bag_choices().visible)
	check("un objet rare ne propose qu'Annuler", bag_answers() == ["Annuler"], str(bag_answers()))
	check("le bas de l'ecran dit quel objet est choisi", bag("Description").text == "Objet choisi : Vieille canne.", bag("Description").text)
	shot("sac_objet_rare_actions")
	await tap("ui_left")
	check("les poches ne bougent pas pendant le choix", bag("Title").text == "Objets rares")
	await tap("interact")
	check("Annuler referme la boite", not bag_choices().visible and bag_open())
	check("on retrouve la liste et la description", bag_line() == 0 and bag("Description").text.begins_with("Une canne"), bag("Description").text)
	check("l'objet est toujours la", bag_rows() == ["Vieille canne", "Carte du village", "Retour"], str(bag_rows()))
	await tap("interact")
	await tap("menu")
	check("la touche du menu annule aussi, sans fermer le sac", not bag_choices().visible and bag_open())
