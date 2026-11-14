extends "res://tests/lib.gd"

# Debug : la ligne de l'heure fait defiler les moments de la journee, puis revient a l'heure reelle.

func start() -> Vector2i:
	return Vector2i(30, 16)

func line(n: int) -> String:
	return debug_choices().get_node("Entries").get_child(n).text

func test() -> void:
	await set_hour(-1.0)
	await menu_pick("Debug")
	check("la ligne de l'heure dit qu'on est a l'heure reelle", line(3) == "Heure : réelle", line(3))
	for i in 3:
		await tap("ui_down")
	var seen := []
	for i in 4:
		await tap("interact")
		seen.append(line(3))
	check("chaque validation passe au moment suivant", seen == ["Heure : aube", "Heure : jour", "Heure : crépuscule", "Heure : nuit"], str(seen))
	check("la boite reste ouverte, le curseur sur la meme ligne", debug_choices().visible and menu_open())
	check("et le dehors a pris la nuit", daylight().b > daylight().r, str(daylight()))
	shot("debug_heure")
	await tap("interact")
	check("apres la nuit, on revient a l'heure reelle", line(3) == "Heure : réelle", line(3))
	await tap("menu")
	await tap("menu")
	await set_hour(12.0)
