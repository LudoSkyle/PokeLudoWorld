extends "res://tests/lib.gd"

# Un passage garde disparait avec son garde quand leur drapeau est pose : la route est ouverte.

func start() -> Vector2i:
	return Vector2i(36, 13)

func test() -> void:
	# Un garde en (35,11), sa case gardee en (36,11) : on y monte depuis le sud.
	await spawn("npc", "TestGuard", Vector2i(35, 11), {"text": "On ne passe pas.", "facing": Vector2.RIGHT, "forbidden_flag": "test_open"})
	await spawn("roadblock", "TestBlock", Vector2i(36, 11), {"guard": "TestGuard", "push_direction": Vector2.DOWN, "forbidden_flag": "test_open"})
	Input.action_press("ui_up")
	await secs(1.5)
	Input.action_release("ui_up")
	check("sans le drapeau : le garde nous arrete", box().visible and box_text().to_lower().contains("passe pas"), box_text())
	check("sans le drapeau : on est repousse", cell() == Vector2i(36, 12), str(cell()))
	await close_box()
	await secs(1.0)
	# Le drapeau pose, la carte est rechargee : ni garde ni passage.
	set_flag("test_open")
	npc("TestGuard").free()
	level().get_node("Triggers/TestBlock").free()
	var guard := await spawn("npc", "TestGuard", Vector2i(35, 11), {"text": "On ne passe pas.", "forbidden_flag": "test_open"})
	var block := await spawn("roadblock", "TestBlock", Vector2i(36, 11), {"guard": "TestGuard", "push_direction": Vector2.DOWN, "forbidden_flag": "test_open"})
	check("avec le drapeau : plus de garde ni de passage", not is_instance_valid(guard) and not is_instance_valid(block))
	Input.action_press("ui_up")
	await secs(1.5)
	Input.action_release("ui_up")
	await wait(10)
	check("avec le drapeau : on traverse sans etre arrete", cell().y < 11 and not box().visible, str(cell()))
