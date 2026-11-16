extends "res://tests/lib.gd"

# La cloche repose sous le ponton de l'ouest ; la trouee de la falaise est gardee jusqu'a la
# Veillee ; la Veillee rassemble le village, puis prend fin des qu'on quitte l'ile.

func scene() -> String:
	return "start_island"

func start() -> Vector2i:
	return Vector2i(19, 26)

func there(n: String) -> bool:
	return game.get_node_or_null(ENT + n) != null

# Les personnages immobiles sur le plateau de la place (le coureur n'en est pas).
func crowd() -> int:
	var n := 0
	for who in game.get_node(ENT.trim_suffix("/")).get_children():
		var c := Vector2i(floori(who.position.x / 16.0), floori(who.position.y / 16.0))
		if str(who.name) != "Player" and not str(who.name).begins_with("Runner") and Rect2i(24, 19, 13, 10).has_point(c):
			n += 1
	return n

func test() -> void:
	# Sous le ponton : on repeche la cloche en regardant l'eau, vers le nord. Roland a dit ou
	# chercher (island_bell_hint joue cet echange) : ici son indice est pose d'office.
	set_flag("bell_spotted")
	await wait(4)
	check("la cloche n'est pas encore trouvee", not flag("bell_tarnished"))
	await interact_facing("ui_up")
	await wait_text("Quelque chose brille au fond de l'eau, juste sous le ponton.")
	check("depuis le ponton, on voit briller quelque chose", box_text() == "Quelque chose brille au fond de l'eau, juste sous le ponton.", box_text())
	await close_box()
	check("on a repeche la cloche", flag("bell_tarnished"))
	check("on n'a pas bouge du ponton", cell() == Vector2i(19, 26), str(cell()))
	await interact_facing("ui_up")
	await secs(0.6)
	check("une fois repechee, il n'y a plus rien a voir", not box().visible, box_text())

	# AVANT. La trouee de la falaise : deux ouvriers la tiennent et renvoient le joueur.
	check("avant : la place est vide", crowd() == 0, "%d" % crowd())
	check("les deux gardes tiennent la trouee, un contre chaque paroi", cell_of("GuardWest") == Vector2i(28, 3) and cell_of("GuardEast") == Vector2i(33, 3),
		"%s %s" % [str(cell_of("GuardWest")), str(cell_of("GuardEast"))])
	place(Vector2i(30, 7))
	Input.action_press("ui_up")
	await secs(2.5)
	Input.action_release("ui_up")
	await secs(0.5)
	check("un garde interpelle le joueur", box().visible and box_text().contains("passage est fermé"), box_text())
	await close_box()
	await secs(1.0)
	check("le joueur est renvoye en arriere", cell().y >= 4, str(cell()))

	# PENDANT. La cloche accrochee, le village est sur la place ; recharger la carte n'y met pas fin.
	set_flag("bell_hung")
	await reload_level()
	check("recharger la carte ne met pas fin a la Veillee", not flag("vigil_over"))
	check("les gardes sont partis", not there("GuardWest") and not there("GuardEast"))
	check("le village est sur la place", there("OdileAfter") and there("AlixAfter") and there("VisitorPainter") and there("RolandAfter"))
	check("dix personnes autour de la cloche, pas plus", crowd() == 10, "%d" % crowd())
	check("trois visiteurs sont ailleurs : sur la route du nord, vers la jetee, sur la plage de la crique — bien en vue",
		cell_of("VisitorKalos") == Vector2i(31, 7) and cell_of("VisitorFestival") == Vector2i(32, 39) and cell_of("VisitorBlackBelt") == Vector2i(29, 9),
		"%s %s %s" % [str(cell_of("VisitorKalos")), str(cell_of("VisitorFestival")), str(cell_of("VisitorBlackBelt"))])
	check("ceux de toujours n'ont pas bouge", cell_of("BenchLady") == Vector2i(12, 13) and cell_of("Sailor") == Vector2i(53, 18))
	# Personne ne gene : ni sur le tour de la place ou court le coureur, ni devant le socle, ni devant un escalier.
	var ring_free := true
	for x in range(25, 36):
		for y in [21, 27]:
			if not is_free(Vector2i(x, y)) and cell_of("RunnerAfter") != Vector2i(x, y):
				ring_free = false
	for y in range(21, 28):
		for x in [25, 35]:
			if not is_free(Vector2i(x, y)) and cell_of("RunnerAfter") != Vector2i(x, y):
				ring_free = false
	check("le tour de la place reste libre pour le coureur", ring_free)
	check("on peut encore se tenir devant le socle", is_free(Vector2i(30, 26)))
	check("les escaliers de la place restent degages", is_free(Vector2i(31, 28)) and is_free(Vector2i(24, 23)) and is_free(Vector2i(36, 24)))

	# APRES. On entre chez Ludo : quitter l'ile met fin a la Veillee. Meme Odile est rentree.
	place(Vector2i(8, 9))
	await hold_until_change("porte de Ludo", "ui_up")
	check("quitter l'ile met fin a la Veillee", flag("vigil_over"))
	check("Meme Odile est rentree chez Ludo", there("OdileBack") and not there("Odile"))
	await hold_until_change("paillasson de Ludo", "ui_down")
	await arrival("retour sur l'ile", Vector2i(8, 9), "idle_down")
	check("la place s'est videe : il ne reste que Roland et le peintre", crowd() == 2 and there("RolandAfter") and there("VisitorPainter"), "%d" % crowd())
	check("les visiteurs sont repartis, Meme et Alix sont rentrees", not there("VisitorKalos") and not there("VisitorHiker") and not there("VisitorBlackBelt") and not there("OdileAfter") and not there("AlixAfter"))
	check("le pecheur a repris sa place au bout de la jetee", cell_of("FisherLater") == Vector2i(31, 43) and not there("Fisher") and not there("FisherAfter"))
	check("les ouvriers ont quitte la place : l'un surveille la trouee, l'autre range le quai",
		cell_of("WorkerLater") == Vector2i(27, 5) and cell_of("WorkerLater2") == Vector2i(33, 39) and not there("WorkerAfter"))
	check("le coureur court toujours", there("RunnerAfter"))
	await talk("Roland, apres", Vector2i(33, 24), "ui_left", "RolandAfter", "je reste encore un peu.", "idle_right")
	await walk("route du nord", Vector2i(30, 1), false)
	await examine("bout de la route", Vector2i(30, 1), "route du nord", "ui_up")
