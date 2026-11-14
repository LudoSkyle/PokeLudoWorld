extends "res://tests/lib.gd"

# La quete commencee, les archives se reconnaissent et la troisieme case donne le Registre.

func start() -> Vector2i:
	return Vector2i(21, 14)

func test() -> void:
	set_flag("bell_told")
	await walk("on entre dans la bibliotheque", Vector2i(21, 13), true)
	await examine("archives, premiere case", Vector2i(9, 9), "registres reliés")
	await examine("archives, quatrieme case", Vector2i(12, 9), "registres reliés")
	await examine("un rayonnage voisin reste ordinaire", Vector2i(13, 9), "pleine de livres")
	await walk("devant la troisieme case", Vector2i(11, 9), false)
	await interact_facing("ui_up")
	await wait_text("Des registres reliés, rangés par année.")
	check("d'abord le texte des archives", box_text() == "Des registres reliés, rangés par année.", box_text())
	await tap("interact")
	await wait_text("L'un d'eux est beaucoup plus poussiéreux que les autres.")
	check("puis l'indice, sans objet a l'ecran", box_text().begins_with("L'un d'eux") and not reveal().visible, box_text())
	await tap("interact")
	await wait_text("Vous trouvez le Registre poussiéreux !")
	await secs(0.4)
	check("le Registre est montre au centre de l'ecran", reveal().visible and box_text() == "Vous trouvez le Registre poussiéreux !", box_text())
	shot("registre")
	await wait_text("« ...la cloche a été descendue à l'abri pour l'hiver, »")
	check("il se lit quand on le prend", box_text().begins_with("« ...la cloche"), box_text())
	await tap("interact")
	await wait_text("« au frais, là où l'eau dort sous la pierre. »")
	check("l'indice de la grotte", box_text().contains("l'eau dort sous la pierre"), box_text())
	await close_box()
	check("le drapeau bell_register est pose", flag("bell_register"))
	await examine("le rayon, apres", Vector2i(11, 9), "c'est de là que venait")
	await menu_pick("Bag")
	await tap("ui_right")
	check("le Registre est dans le sac, une seule fois", bag_rows() == ["Registre poussiéreux", "Retour"], str(bag_rows()))
	check("avec sa description", bag("Description").text.begins_with("Le vieux registre"), bag("Description").text)
