extends "res://tests/lib.gd"

# Les etats se lisent de bas en haut : une etape tardive atteinte seule l'emporte aussi.

func start() -> Vector2i:
	return Vector2i(35, 12)

func test() -> void:
	set_flag("test_b")
	await spawn("npc", "Teller", Vector2i(35, 11), {
		"text": "Texte par défaut.",
		"states": PackedStringArray(["test_a > Texte de l'étape A.", "test_b > Texte de l'étape B.", "test_c > Texte de l'étape C."]),
	})
	await talk("seule l'etape B est atteinte", Vector2i(35, 12), "ui_up", "Teller", "étape b", "idle_down")
	set_flag("test_a")
	await talk("A posee apres coup ne reprend pas la main", Vector2i(35, 12), "ui_up", "Teller", "étape b", "idle_down")
