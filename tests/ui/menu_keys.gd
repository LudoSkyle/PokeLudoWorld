extends "res://tests/lib.gd"

# Les vraies touches du menu : X et Echap l'ouvrent, reviennent en arriere et le ferment.

func key(code: Key) -> void:
	for pressed in [true, false]:
		var e := InputEventKey.new()
		e.physical_keycode = code
		e.pressed = pressed
		Input.parse_input_event(e)
		await wait(4)

func test() -> void:
	for code in [KEY_X, KEY_ESCAPE]:
		var name := OS.get_keycode_string(code)
		await key(code)
		check(name + " ouvre le menu", menu_open())
		await tap("ui_down")
		await tap("interact")
		check(name + " : options ouvertes", options_open())
		await key(code)
		check(name + " revient des options au menu", not options_open() and menu_open())
		await key(code)
		check(name + " ferme le menu", not menu_open())
		await tap("menu")
		await tap("ui_up")
		await tap("menu")
