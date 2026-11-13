extends "res://tests/lib.gd"

# Maison des voisins : tour de table et paillasson.

func scene() -> String:
	return "neighbor_house"

func start() -> Vector2i:
	return Vector2i(15, 13)

func test() -> void:
	await walk("tour de table", Vector2i(18, 9), false)
	await walk("2e case du paillasson", Vector2i(16, 13), false)
