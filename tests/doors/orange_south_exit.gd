extends "res://tests/lib.gd"

# Sortir de la maison orange du sud par le paillasson.

# Case ou l'on arrive sur l'ile, devant la porte MaisonSud : à renseigner
# quand cette porte sera posee sur start_island. Tant qu'elle vaut (-1, -1),
# le controle d'arrivee echoue : c'est voulu.
const ISLAND_ARRIVAL := Vector2i(44, 34)

func scene() -> String:
	return "orange_house_south"

func start() -> Vector2i:
	return Vector2i(15, 14)

func test() -> void:
	await hold_until_change("Bas sur le paillasson", "ui_down")
	await arrival("ile devant la maison orange du sud", ISLAND_ARRIVAL, "idle_down")
