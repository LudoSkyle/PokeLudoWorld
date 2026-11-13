extends "res://tests/lib.gd"

# Panneaux du village : ouverture et fermeture de la boite.

func test() -> void:
	# --- regression : les panneaux se lisent toujours
	await walk("vers le panneau", Vector2i(6, 16), false)
	Input.action_press("ui_up"); await wait(2); Input.action_release("ui_up"); await wait(4)
	Input.action_press("interact"); await wait(2); Input.action_release("interact"); await wait(10)
	var box: Control = game.get_node(VP + "/MessageBox/Control/Box")
	check("panneau : la boite s'ouvre", box.visible)
	var n := 0
	while box.visible and n < 12:
		Input.action_press("interact"); await wait(2); Input.action_release("interact"); await wait(60)
		n += 1
	check("panneau : la boite se referme", not box.visible)
