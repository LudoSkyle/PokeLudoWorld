extends "res://tests/lib.gd"

# La cloche n'est sous le ponton qu'une fois que Roland a dit ou chercher : avant, on n'y trouve
# rien ; des qu'il a parle, elle brille, sans que la carte se recharge.

func scene() -> String:
	return "start_island"

func start() -> Vector2i:
	return Vector2i(14, 22)

func bell() -> Node2D:
	return node("Readables/Bell")

func nothing_there(label: String) -> void:
	await interact_facing("ui_up")
	await secs(0.6)
	check(label + " : on ne trouve rien sous le ponton", not box().visible and not flag("bell_tarnished"), box_text())
	check(label + " : rien ne brille", bell() != null and not bell().visible)

func test() -> void:
	await nothing_there("avant la quete")

	# Sans le Registre, Roland ne sait rien : il ne dit pas ou chercher.
	await place(Vector2i(8, 37))
	await interact_facing("ui_left")
	await wait_text("Ces eaux, j'y ai plongé vingt ans.")
	check("sans le Registre, Roland parle de ses plongees", box_text() == "Ces eaux, j'y ai plongé vingt ans.", box_text())
	await close_box()
	check("il n'a rien indique", not flag("bell_spotted"))
	await place(Vector2i(14, 22))
	await nothing_there("apres ce premier echange")

	# Le Registre trouve, il dit ou chercher — et la cloche apparait aussitot.
	set_flag("bell_register")
	await place(Vector2i(8, 37))
	var id := level_id()
	await interact_facing("ui_left")
	await wait_text("Sous le ponton de l'ouest, là où l'eau est profonde...")
	check("avec le Registre, Roland dit ou chercher", box_text() == "Sous le ponton de l'ouest, là où l'eau est profonde...", box_text())
	await close_box()
	check("son indice est retenu", flag("bell_spotted"))
	check("la carte ne s'est pas rechargee", level_id() == id)
	check("quelque chose brille maintenant sous le ponton", bell().visible)

	await place(Vector2i(14, 22))
	await interact_facing("ui_up")
	await wait_text("Quelque chose brille au fond de l'eau, juste sous le ponton.")
	check("on la voit depuis le ponton", box_text() == "Quelque chose brille au fond de l'eau, juste sous le ponton.", box_text())
	await close_box()
	check("on a repeche la cloche", flag("bell_tarnished"))

	# Roland peut le redire : l'indice ne fait pas revenir la cloche.
	await secs(0.3)
	check("une fois repechee, elle a quitte la carte", bell() == null)
