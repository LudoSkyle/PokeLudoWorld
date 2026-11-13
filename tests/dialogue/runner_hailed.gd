extends "res://tests/lib.gd"

# Le coureur interpelle en pleine course : il finit son pas et repond.

func start() -> Vector2i:
	return Vector2i(14, 12)

func test() -> void:
	await tap("ui_left")
	var spot := Vector2(13 * 16 + 8, 12 * 16 + 8)
	var t0 := Time.get_ticks_msec()
	var called := false
	while not called and Time.get_ticks_msec() - t0 < 6000:
		await process_frame
		var r := npc("Runner")
		# il descend la colonne 13 et arrive sur la case que nous regardons
		if r.position.x == spot.x and r.position.y < spot.y and spot.y - r.position.y < 5.0:
			Input.action_press("interact"); await wait(2); Input.action_release("interact")
			called = true
	check("on l'interpelle alors qu'il court", called)
	await secs(1.5)
	check("il s'arrete et repond", box().visible and box_text().to_lower().contains("tour du village"), box_text())
	check("arrete sur la case devant nous", cell_of("Runner") == Vector2i(13, 12) and resting("Runner"), str(npc("Runner").position))
	check("tourne vers nous", anim("Runner") == "idle_right", anim("Runner"))
	shot("dialogue_coureur_interpelle")
	await close_box()
