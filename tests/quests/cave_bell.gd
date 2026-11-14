extends "res://tests/lib.gd"

# La Cloche ternie, a moitie enfoncee dans la vase pres du lac du B2F.

func scene() -> String:
	return "cave_b2f"

func start() -> Vector2i:
	return Vector2i(22, 14)

func test() -> void:
	await interact_facing("ui_right")
	await wait_text("Quelque chose est à moitié enfoncé dans la vase.")
	check("on remarque quelque chose dans la vase", box_text().begins_with("Quelque chose est à moitié"), box_text())
	await tap("interact")
	await wait_text("Vous trouvez la Cloche ternie !")
	await secs(0.4)
	check("la Cloche ternie est montree, bell_tarnished est pose", reveal().visible and flag("bell_tarnished"), box_text())
	check("avec son icone maison", reveal().get_node("Icon").texture.atlas.resource_path.ends_with("custom.png") and reveal().get_node("Icon").texture.region.position == Vector2(24, 0))
	shot("cloche_ternie")
	await wait_text("Quelque chose file le long de la paroi et disparaît dans le noir.")
	check("puis la silhouette qui s'enfuit", box_text().begins_with("Quelque chose file"), box_text())
	await close_box()
	await wait(6)
	await tap("interact")
	await secs(0.3)
	check("il n'y a plus rien a prendre", not box().visible)
	check("le caillou reste un caillou", not is_free(Vector2i(23, 14)))
	await menu_pick("Bag")
	await tap("ui_right")
	check("la Cloche ternie est dans le sac, une seule fois", bag_rows() == ["Cloche ternie", "Retour"], str(bag_rows()))
