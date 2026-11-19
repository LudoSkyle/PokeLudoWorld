extends "res://tests/gdunit/game_suite.gd"

# La table de rencontres d'une carte : qui vit dans ses herbes, a quel niveau,
# en quelle proportion. Verifiee par tirages, sans marcher.

const LEVELS_DIR := "res://src/main/kotlin/fr/skyle/pokemonmirage/scenes/levels/"

func start() -> Vector2i:
	return Vector2i(12, 8)

func counts(draws: Array) -> Dictionary:
	var seen := {}
	for d in draws:
		var id: String = d.split(":")[0]
		seen[id] = seen.get(id, 0) + 1
	return seen

func test_wild_table() -> void:
	if game == null:
		return
	# Les poids : 80 / 20 sur 1000 tirages.
	var draws := wild_draws("mulotin:2-4*80 | chenibulle:7*20", 1000)
	var seen := counts(draws)
	check("mille tirages demandes, mille rendus", draws.size() == 1000, str(draws.size()))
	check("seules les especes de la table sortent", seen.keys().size() == 2 and seen.has("mulotin") and seen.has("chenibulle"), str(seen))
	check("les poids font les proportions (80 / 20)", absi(seen.get("mulotin", 0) - 800) < 60, str(seen))

	# Les niveaux : toute la fourchette, rien en dehors.
	var levels := {}
	var fixed := true
	for d in draws:
		var parts: PackedStringArray = d.split(":")
		if parts[0] == "mulotin":
			levels[int(parts[1])] = true
		elif int(parts[1]) != 7:
			fixed = false
	var sorted := levels.keys()
	sorted.sort()
	check("une fourchette 2-4 donne 2, 3 et 4, rien d'autre", sorted == [2, 3, 4], str(sorted))
	check("un niveau seul donne toujours ce niveau", fixed)

	# Sans poids, les especes se valent.
	seen = counts(wild_draws("mulotin:3 | piafeuille:3", 1000))
	check("sans poids, parts egales", absi(seen.get("mulotin", 0) - 500) < 70, str(seen))

	# La meme graine rejoue les memes tirages ; une autre en donne d'autres.
	var table := "mulotin:2-4*50 | piafeuille:2-5*35 | chenibulle:3*15"
	check("meme graine, memes tirages", wild_draws(table, 40, 7) == wild_draws(table, 40, 7))
	check("autre graine, autres tirages", wild_draws(table, 40, 7) != wild_draws(table, 40, 8))

	# Les entrees mal ecrites sont ecartees et signalees ; les autres restent.
	check("une table juste n'a pas d'erreur", wild_errors(table) == "", wild_errors(table))
	check("espece inconnue : signalee", wild_errors("licorne:3").contains("licorne"), wild_errors("licorne:3"))
	check("niveaux a l'envers : signales", wild_errors("mulotin:5-2") != "")
	check("niveau 0 ou au-dela de 100 : signales", wild_errors("mulotin:0") != "" and wild_errors("mulotin:2-101") != "")
	check("poids nul : signale", wild_errors("mulotin:3*0") != "")
	check("entree illisible : signalee", wild_errors("mulotin") != "")
	seen = counts(wild_draws("licorne:3 | mulotin:3", 50))
	check("l'entree fausse est ecartee, la bonne reste", seen.keys() == ["mulotin"], str(seen))
	check("une table vide ne tire personne", wild_draws("", 10).is_empty())

	# Chaque carte du jeu : une table sans erreur, et pas de chance sans table.
	var bad := []
	var peopled := 0
	for file in DirAccess.get_files_at(LEVELS_DIR):
		if not file.ends_with(".tscn"):
			continue
		var packed: PackedScene = load(LEVELS_DIR + file)
		var state := packed.get_state()
		var rate := 0
		var wild := ""
		for i in state.get_node_property_count(0):
			var prop := str(state.get_node_property_name(0, i))
			if prop == "metadata/encounter_rate":
				rate = int(state.get_node_property_value(0, i))
			elif prop == "metadata/wild":
				wild = str(state.get_node_property_value(0, i))
		if wild_errors(wild) != "":
			bad.append("%s : %s" % [file, wild_errors(wild)])
		if rate > 0 and wild_draws(wild, 1).is_empty():
			bad.append("%s : une chance de rencontre mais personne dans la table" % file)
		if rate > 0:
			peopled += 1
	check("toutes les cartes ont une table juste", bad.is_empty(), "\n".join(bad))
	check("au moins une carte du jeu est peuplee", peopled >= 1, str(peopled))
