extends "res://tests/lib.gd"

# Un meuble examinable change de texte avec l'histoire, comme un PNJ.

func start() -> Vector2i:
	return Vector2i(35, 12)

func test() -> void:
	await spawn("readable", "Shelf", Vector2i(35, 11), {
		"text": "Des registres rangés par année.",
		"states": PackedStringArray(["test_taken > Il y a un vide dans la rangée."]),
	})
	check("le meuble occupe sa case", not is_free(Vector2i(35, 11)))
	await examine("sans drapeau", Vector2i(35, 12), "registres")
	set_flag("test_taken")
	await examine("drapeau pose", Vector2i(35, 12), "un vide")
