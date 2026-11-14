extends "res://tests/lib.gd"

# Menu de pause : Bas ou Haut maintenu fait defiler le curseur, apres un court delai.

func test() -> void:
	await tap("menu")
	Input.action_press("ui_down")
	await secs(0.2)
	check("touche tenue : un cran tout de suite, puis un temps d'attente", menu_cursor_line() == 1, str(menu_cursor_line()))
	var seen := {}
	var moves := 0
	var last := menu_cursor_line()
	var end := Time.get_ticks_msec() + 1200
	while Time.get_ticks_msec() < end:
		await process_frame
		if menu_cursor_line() != last:
			moves += 1
			last = menu_cursor_line()
			seen[last] = true
	Input.action_release("ui_down")
	check("ensuite le curseur defile tout seul", moves >= 8, "%d crans en 1,2 s" % moves)
	check("il fait le tour des cinq entrees", seen.size() == 5, str(seen.keys()))
	var stopped := menu_cursor_line()
	await secs(0.5)
	check("touche relachee : il s'arrete", menu_cursor_line() == stopped)
	await tap("ui_up")
	check("une pression breve ne fait qu'un cran", menu_cursor_line() == (stopped + 4) % 5, "%d -> %d" % [stopped, menu_cursor_line()])
	await tap("menu")

	# une touche deja enfoncee a l'ouverture ne fait rien defiler
	Input.action_press("ui_down")
	await wait(3)
	await tap("menu")
	await secs(0.8)
	check("touche tenue avant l'ouverture : le curseur ne bouge pas", menu_open() and menu_cursor_line() == 0, str(menu_cursor_line()))
	Input.action_release("ui_down")
