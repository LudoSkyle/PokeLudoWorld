extends "res://tests/lib.gd"

# Laboratoire : entree, machine, objets a examiner, sortie.

func test() -> void:
	# --- laboratoire (en haut a droite)
	await walk("village->labo", Vector2i(28, 7), true)
	await arrival("labo", Vector2i(15, 15), "idle_up")
	await walk("labo : devant la machine", Vector2i(15, 13), false)
	await hold_no_change("labo : Haut contre la machine", "ui_up")
	shot("labo_machine")
	var t := Time.get_time_dict_from_system()
	await examine("labo : horloge", Vector2i(18, 7), "%d h %02d" % [t.hour, t.minute])
	await examine("labo : poubelle", Vector2i(13, 8), "poubelle est vide")
	await examine("labo : serveur", Vector2i(9, 8), "serveur")
	await examine("labo : bibliotheque du fond", Vector2i(21, 8), "bibliotheque")
	await examine("labo : bibliotheque du milieu", Vector2i(11, 14), "bibliotheque")
	await examine("labo : etagere a fioles (muette)", Vector2i(14, 8), "")
	await examine("labo : la machine (muette)", Vector2i(15, 13), "")
	await walk("labo : fond de la salle", Vector2i(19, 7), false)
	shot("labo_fond")
	await walk("labo : sur les feuilles", Vector2i(11, 9), false)
	await walk("labo : allee de gauche", Vector2i(13, 12), false)
	await walk("labo : retour au paillasson", Vector2i(16, 15), false)
	await hold_until_change("labo : Bas sur le paillasson", "ui_down")
	await arrival("village devant le labo", Vector2i(28, 8), "idle_down")
