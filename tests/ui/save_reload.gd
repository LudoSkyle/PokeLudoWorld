extends "res://tests/lib.gd"

# Relancer le jeu reprend la partie : meme carte, meme case, meme regard, temps de jeu conserve.

func scene() -> String:
	return "ludo_house"

func start() -> Vector2i:
	return Vector2i(17, 10)

func test() -> void:
	await tap("ui_right")
	await secs(1.0)
	await menu_pick("Save")
	check("le resume donne le lieu de la maison", save_summary().get_node("Location").text == "Maison de Ludo", save_summary().get_node("Location").text)
	await wait_choices()
	await tap("interact")
	await secs(2.2)
	var seconds: float = saved_file().get_value("save", "seconds", 0.0)
	check("temps de jeu enregistre", seconds > 1.0, "%.1f s" % seconds)
	await walk("on s'eloigne apres la sauvegarde", Vector2i(15, 12), false)

	await relaunch()
	check("relance : on est dans la maison de Ludo", level().scene_file_path.ends_with("ludo_house.tscn"), level().scene_file_path)
	check("relance : sur la case sauvegardee", cell() == Vector2i(17, 10), str(cell()))
	check("relance : on regarde du meme cote", str(player().get_node("Sprite").animation) == "idle_right", str(player().get_node("Sprite").animation))
	var scenes := game.get_node(VP + "/SceneManager")
	shot("sauvegarde_reprise")
	await walk("relance : on peut marcher", Vector2i(16, 10), false)
	await menu_pick("Save")
	var shown: String = save_summary().get_node("Time").text
	check("relance : le temps de jeu repart de la sauvegarde", shown == "00:00" and box().visible, shown)
	await wait_choices()
	await tap("interact")
	await wait_choices()
	await tap("interact")
	await secs(0.6)
	check("le temps de jeu a continue", saved_file().get_value("save", "seconds", 0.0) > seconds, "%.1f > %.1f" % [saved_file().get_value("save", "seconds", 0.0), seconds])
