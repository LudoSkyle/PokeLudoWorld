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

func test() -> void:
	var sprite: AnimatedSprite2D = player().get_node("Sprite")
	var walked: int = await travel("ui_right", 1.5)
	check("en marchant : quatre cases par seconde", walked >= 5 and walked <= 7, "%d cases" % walked)
	check("les jambes vont a l'allure de la marche", is_equal_approx(sprite.speed_scale, 1.0), str(sprite.speed_scale))
	check("le pas est a l'allure de la marche", is_equal_approx(player().get_node("Movement").tiles_per_second, 4.0))
	await walk("retour au depart", Vector2i(6, 8), false)
	Input.action_press("run")
	var ran: int = await travel("ui_right", 1.5)
	check("touche de course tenue : deux fois plus vite", ran >= 10 and ran <= 13, "%d cases" % ran)
	check("les jambes suivent", is_equal_approx(sprite.speed_scale, 2.0), str(sprite.speed_scale))
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
