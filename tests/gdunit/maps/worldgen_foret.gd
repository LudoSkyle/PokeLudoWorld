extends "res://tests/gdunit/game_suite.gd"

# Une foret profonde inventee par le generateur (tools/mapgen/worlds/style_foret.toml, style `forest`) se joue :
# de la sortie du nord a une plaque de terre nue, au bord d'une mare, puis a la sortie du sud. La carte est
# dans la penombre : sa teinte est plus sombre que le plein jour.

func scene() -> String:
	return "style_foret"

func start() -> Vector2i:
	return Vector2i(35, 2)

func test_worldgen_foret() -> void:
	if game == null:
		return
	check("la carte est chargee", level() != null and cell() == Vector2i(35, 2), str(cell()))
	set_hour(12.0)
	await wait(4)
	var tint := daylight()
	check("la foret est dans la penombre, en plein midi", tint.r < 0.8 and tint.g < 0.9 and tint.g > tint.r, str(tint))
	await walk("jusque sur une plaque de terre nue", Vector2i(28, 15), false)
	shot("foret_terre")
	check("la terre nue se foule", is_free(Vector2i(28, 15)))
	await walk("jusqu'a la rive d'une mare", Vector2i(27, 24), false)
	shot("foret_mare")
	check("la mare arrete", not is_free(Vector2i(28, 24)) and not is_free(Vector2i(30, 24)))
	await walk("et jusqu'a la sortie du sud", Vector2i(35, 47), false)
	shot("foret_sud")
