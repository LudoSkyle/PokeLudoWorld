extends "res://tests/lib.gd"

# Tunnel D (B2F -> B1F).

func scene() -> String:
	return "cave_b2f"

func start() -> Vector2i:
	return Vector2i(15, 15)

func test() -> void:
	await walk("B2F -> tunnel D", Vector2i(23, 3), true)
	await arrival("grotte B1F est", Vector2i(22, 13), "idle_down")
