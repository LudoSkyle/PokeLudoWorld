extends "res://tests/lib.gd"

# Tunnel C (B1F -> B2F).

func scene() -> String:
	return "cave_b1f"

func start() -> Vector2i:
	return Vector2i(4, 4)

func test() -> void:
	await walk("B1F -> tunnel C", Vector2i(11, 10), true)
	await arrival("grotte B2F ouest", Vector2i(6, 4), "idle_down")
