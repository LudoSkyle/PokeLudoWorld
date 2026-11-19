extends "res://tests/gdunit/game_suite.gd"

# La boite de dialogue va d'un bord a l'autre de l'ecran de jeu, avec a gauche
# et a droite la meme marge qu'en bas. L'encart du nom suit son bord gauche,
# Oui / Non son bord droit — celui d'une question comme celui de la sauvegarde.

func start() -> Vector2i:
	return Vector2i(14, 8)

func right_edge(c: Control) -> float:
	return c.position.x + c.size.x

func test_message_box_width() -> void:
	if game == null:
		return
	await spawn("npc", "Named", Vector2i(14, 7), {"display_name": "Camille", "gender": "female", "ask": "On y va ?", "text": "Allons-y."})
	await interact_facing("ui_up")
	await wait_ask()
	check("la question est posee : la boite, le nom, Oui / Non", box().visible and speaker_name() == "Camille" and ask_choices().visible, speaker_name())

	var screen: Vector2 = box().get_parent().size
	var left := box().position.x
	var right := screen.x - right_edge(box())
	var bottom := screen.y - box().position.y - box().size.y
	check("l'ecran de jeu fait 1280 x 960", screen == Vector2(1280, 960), str(screen))
	check("la boite garde une marge en bas", bottom > 0.0 and bottom <= 32.0, str(bottom))
	check("a gauche, la meme marge qu'en bas", is_equal_approx(left, bottom), "%s / %s" % [left, bottom])
	check("a droite, la meme marge qu'en bas", is_equal_approx(right, bottom), "%s / %s" % [right, bottom])
	check("entre les deux, elle prend toute la largeur", is_equal_approx(box().size.x, screen.x - 2.0 * bottom), str(box().size.x))

	# Le nom est pose sur la boite, 4 pixels de jeu (16 a l'ecran) en retrait de son bord gauche.
	var tag := speaker_tag()
	check("l'encart du nom suit le bord gauche de la boite", is_equal_approx(tag.position.x - left, 16.0), str(tag.position.x - left))
	check("il est pose sur elle", tag.position.y + tag.size.y >= box().position.y and tag.position.y < box().position.y)

	check("Oui / Non est cale contre le bord droit de la boite", is_equal_approx(right_edge(ask_choices()), right_edge(box())), "%s / %s" % [right_edge(ask_choices()), right_edge(box())])
	check("et pose au-dessus d'elle", ask_choices().position.y + ask_choices().size.y <= box().position.y + 1.0)
	shot("boite_largeur")
	await tap("ui_down")
	await tap("interact")
	check("Non : tout se referme", not box().visible and not ask_choices().visible and speaker_name() == "")

	# La sauvegarde pose sa question dans la meme boite, avec son propre Oui / Non.
	await menu_pick("Save")
	await wait_choices()
	check("la sauvegarde pose sa question", box().visible and save_choices().visible)
	check("son Oui / Non est cale contre le meme bord droit", is_equal_approx(right_edge(save_choices()), right_edge(box())), "%s / %s" % [right_edge(save_choices()), right_edge(box())])
	shot("boite_largeur_sauvegarde")
	await tap("menu")
	await tap("menu")
	check("tout est referme", not box().visible and not save_choices().visible and not menu_open())
