extends "res://tests/lib.gd"

# La cloche accrochee, la route de l'ouest est ouverte : plus de gardes, et la carte a un bout.

func start() -> Vector2i:
	return Vector2i(8, 8)

func test() -> void:
	set_flag("bell_hung")
	await reload_level()
	check("les deux ouvriers et leur passage ont quitte la route", node("World/Entities/GuardNorth") == null and node("World/Entities/GuardSouth") == null and node("Triggers/WestRoadblock") == null)
	check("leurs cases sont libres", is_free(Vector2i(5, 7)) and is_free(Vector2i(5, 9)))
	Input.action_press("ui_left")
	await secs(3.5)
	Input.action_release("ui_left")
	await wait(10)
	check("on passe sans etre arrete", not box().visible and cell().x < 5, str(cell()))
	check("la route s'arrete au bord de la carte", cell() == Vector2i(1, 8), str(cell()))
	await tap("interact")
	await secs(1.5)
	check("le bout de la route se lit", box().visible and box_text().to_lower().contains("s'enfonce dans la forêt"), box_text())
	await close_box()
	await walk("on revient au village", Vector2i(8, 8), false)
