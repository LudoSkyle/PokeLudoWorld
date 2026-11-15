extends "res://tests/lib.gd"

# Courir : la touche de course tenue, on va deux fois plus vite ; relachee, on remarche.

func start() -> Vector2i:
	return Vector2i(6, 8)

# Tient une direction pendant t secondes et renvoie le nombre de cases parcourues.
func travel(action: String, t: float) -> int:
	var from := cell()
	Input.action_press(action)
	await secs(t)
	Input.action_release(action)
	await secs(0.4)
	return absi(cell().x - from.x)

# Tient une direction pendant t secondes et renvoie les animations vues en chemin.
func poses_while(action: String, t: float) -> Dictionary:
	var sprite: AnimatedSprite2D = player().get_node("Sprite")
	var seen := {}
	Input.action_press(action)
	var end := Time.get_ticks_msec() + int(t * 1000.0)
	var last: Vector2 = player().position
	while Time.get_ticks_msec() < end:
		# En mouvement seulement : a l'arret, c'est la pose immobile.
		if player().position != last:
			seen[str(sprite.animation)] = true
		last = player().position
		await process_frame
	Input.action_release(action)
	await secs(0.4)
	return seen

func test() -> void:
	var sprite: AnimatedSprite2D = player().get_node("Sprite")
	var walked: int = await travel("ui_right", 1.5)
	check("en marchant : quatre cases par seconde", walked >= 5 and walked <= 7, "%d cases" % walked)
	check("les jambes vont a l'allure de la marche", is_equal_approx(sprite.speed_scale, 1.0), str(sprite.speed_scale))
	check("le joueur a une pose de course pour chaque direction", sprite.sprite_frames.has_animation("run_down") and sprite.sprite_frames.has_animation("run_left") and sprite.sprite_frames.has_animation("run_right") and sprite.sprite_frames.has_animation("run_up"))
	var poses := await poses_while("ui_right", 0.6)
	check("en marchant : la pose de marche, jamais celle de course", poses.has("walk_right") and not poses.has("run_right"), str(poses.keys()))
	check("le pas est a l'allure de la marche", is_equal_approx(player().get_node("Movement").tiles_per_second, 4.0))
	await walk("retour au depart", Vector2i(6, 8), false)
	Input.action_press("run")
	var ran: int = await travel("ui_right", 1.5)
	check("touche de course tenue : deux fois plus vite", ran >= 10 and ran <= 13, "%d cases" % ran)
	check("les jambes suivent", is_equal_approx(sprite.speed_scale, 2.0), str(sprite.speed_scale))
	poses = await poses_while("ui_left", 0.6)
	check("en courant : la pose de course, jamais celle de marche", poses.has("run_left") and not poses.has("walk_left"), str(poses.keys()))
	await secs(0.3)
	check("a l'arret : la pose immobile", str(sprite.animation) == "idle_left", str(sprite.animation))
	check("le pas est a l'allure de la course", is_equal_approx(player().get_node("Movement").tiles_per_second, 8.0))
	check("on est bien pose sur une case", fmod(player().position.x, 16.0) == 8.0, str(player().position))
	shot("course")
	Input.action_release("run")
	var after: int = await travel("ui_left", 1.5)
	check("touche relachee : on remarche", after >= 5 and after <= 7 and is_equal_approx(sprite.speed_scale, 1.0), "%d cases" % after)
	# La touche de course seule ne fait rien, et ne change pas le pivot sur place.
	var here := cell()
	Input.action_press("run")
	await secs(0.4)
	check("la touche de course seule ne deplace pas", cell() == here)
	await tap("ui_up")
	check("une pression breve fait toujours pivoter sans avancer", cell() == here and str(sprite.animation).ends_with("_up"), str(sprite.animation))
	Input.action_release("run")
