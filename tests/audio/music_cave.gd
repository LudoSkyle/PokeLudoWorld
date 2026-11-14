extends "res://tests/lib.gd"

# La grotte a sa musique, la meme d'un niveau a l'autre.

func scene() -> String:
	return "cave_b2f"

func start() -> Vector2i:
	return Vector2i(23, 5)

func test() -> void:
	check("la grotte : sa musique", audio().music_id() == "union_cave" and audio().music_audible(), audio().music_id())
	var starts: int = audio().music_starts()
	await walk("on monte d'un niveau", Vector2i(23, 3), true)
	check("au niveau du dessus : la meme, sans repartir", audio().music_id() == "union_cave" and audio().music_starts() == starts, str(audio().music_starts()))
