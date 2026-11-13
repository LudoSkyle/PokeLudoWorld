extends "res://tests/lib.gd"

# Grotte 1F : derriere une crete, sur le sol sombre, jusqu'au tunnel A.

func scene() -> String:
	return "cave_1f"

func start() -> Vector2i:
	return Vector2i(14, 19)

func test() -> void:
	await walk("derriere une crete", Vector2i(8, 9), false)
	await walk("sur le sol sombre", Vector2i(4, 14), false)
	await walk("au pied du tunnel A", Vector2i(4, 4), false)
