extends "res://tests/lib.gd"

# Maison des voisins : entree, tour de piece, sortie.

func test() -> void:
	# --- maison des voisins (au centre)
	await walk("village->voisins", Vector2i(21, 13), true)
	await arrival("voisins", Vector2i(15, 13), "idle_up")
	await walk("voisins : tour de table", Vector2i(18, 9), false)
	await walk("voisins : 2e case du paillasson", Vector2i(16, 13), false)
	await hold_until_change("voisins : Bas sur le paillasson", "ui_down")
	await arrival("village devant les voisins", Vector2i(21, 14), "idle_down")
