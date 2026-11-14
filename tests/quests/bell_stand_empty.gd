extends "res://tests/lib.gd"

# La place avant la Veillee : un socle vide sous lequel on monte, deux statues, deux bancs.

func start() -> Vector2i:
	return Vector2i(31, 15)

func test() -> void:
	check("le socle vide est la, pas celui a la cloche", node("World/BellStandEmpty") != null and node("World/BellStand") == null)
	await walk("on monte la marche, puis sous le portique", Vector2i(31, 13), false)
	shot("place_sous_le_portique")
	await examine("le socle, depuis le portique", Vector2i(31, 13), "il manque quelque chose")
	check("aucune question tant qu'on n'a pas la cloche", not flag("bell_hung"))
	await examine("un montant se lit aussi", Vector2i(31, 13), "il manque quelque chose", "ui_left")
	check("les montants et les rochers du bas bloquent", not is_free(Vector2i(30, 13)) and not is_free(Vector2i(32, 13)) and not is_free(Vector2i(30, 14)) and not is_free(Vector2i(32, 14)))
	check("on ne traverse pas le fond du portique", not is_free(Vector2i(31, 12)))
	check("les statues et les bancs bloquent", not is_free(Vector2i(28, 12)) and not is_free(Vector2i(34, 12)) and not is_free(Vector2i(27, 14)) and not is_free(Vector2i(35, 14)))
	check("la pelouse au sud est degagee", is_free(Vector2i(27, 17)) and is_free(Vector2i(34, 17)))
	await walk("on redescend et l'on passe derriere un montant", Vector2i(30, 12), false)
	shot("place_derriere_socle")
	await walk("on traverse la place d'un banc a l'autre", Vector2i(33, 14), false)
	await walk("et l'on ressort par la pelouse", Vector2i(28, 17), false)
