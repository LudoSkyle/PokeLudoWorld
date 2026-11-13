extends "res://tests/lib.gd"

# Outils des tests de PNJ.
const ENT := VP + "/Level/World/Entities/"

func npc(n: String) -> Node2D:
	return game.get_node(ENT + n)

func anim(n: String) -> String:
	return str(npc(n).get_node("Sprite").animation)

func box() -> Control:
	return game.get_node(VP + "/MessageBox/Control/Box")

func box_text() -> String:
	return game.get_node(VP + "/MessageBox/Control/Box/Text").text

func tap(action: String) -> void:
	Input.action_press(action); await wait(2); Input.action_release(action); await wait(8)

func close_box() -> void:
	var n := 0
	while box().visible and n < 12:
		Input.action_press("interact"); await wait(2); Input.action_release("interact"); await wait(60)
		n += 1

func talk(label: String, from: Vector2i, facing: String, who: String, expected: String, npc_anim: String) -> void:
	await walk(label + " : approche", from, false)
	await tap(facing)
	Input.action_press("interact"); await wait(2); Input.action_release("interact")
	await wait(150)
	check(label + " : la boite s'ouvre", box().visible)
	check(label + " : dit ce qu'il faut", box_text().to_lower().contains(expected), box_text())
	check(label + " : se tourne vers nous", anim(who) == npc_anim, anim(who))
	await close_box()
	check(label + " : la boite est refermee", not box().visible)
	check(label + " : on n'a pas bouge", cell() == from, str(cell()))
