extends "res://tests/lib.gd"

# Tunnel B (B1F -> 1F).

func scene() -> String:
	return "cave_b1f"

func start() -> Vector2i:
	return Vector2i(22, 13)

func test() -> void:
	await walk("B1F -> tunnel B", Vector2i(20, 4), true)
	await arrival("grotte 1F est", Vector2i(25, 4), "idle_down")
