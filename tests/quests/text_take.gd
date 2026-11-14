extends "res://tests/lib.gd"

# Une boite qui commence par @take: retire un objet du sac au moment ou elle s'affiche.

func start() -> Vector2i:
	return Vector2i(35, 12)

func test() -> void:
	await receive("potion*3", Vector2i(36, 12), "ui_right")
	await receive("old_rod", Vector2i(36, 12), "ui_right")
	await spawn("npc", "Taker", Vector2i(35, 11), {"text": "Montre-moi ça.|@take:potion*2 @take:old_rod Merci, je garde tout."})
	await interact_facing("ui_up")
	await wait_text("Montre-moi ça.")
	await tap("interact")
	await wait_text("Merci, je garde tout.")
	check("la consigne ne s'affiche pas", box_text() == "Merci, je garde tout.", box_text())
	await close_box()
	await menu_pick("Bag")
	check("deux potions sur trois sont reprises", bag_rows() == ["Potion x1", "Retour"], str(bag_rows()))
	await tap("ui_right")
	check("l'objet rare a quitte le sac", bag_rows() == ["Retour"], str(bag_rows()))
