extends "res://tests/lib.gd"

# Une plage inventee par le generateur (tools/mapgen/worlds/style_plage.toml, style `beach`) se joue : de la
# sortie du sud au haut de l'escalier de cote, puis sur le sable en bas des marches, et retour par la sortie de l'est.

func scene() -> String:
	return "style_plage"

func start() -> Vector2i:
	return Vector2i(28, 41)

func test() -> void:
	check("la carte est chargee", level() != null and cell() == Vector2i(28, 41), str(cell()))
	await walk("par le plateau jusqu'en haut de l'escalier de cote", Vector2i(52, 22), false)
	shot("plage_escalier")
	await walk("par les marches jusque sur le sable", Vector2i(30, 24), false)
	shot("plage_sable")
	await walk("et retour, jusqu'a la sortie de l'est", Vector2i(61, 21), false)
