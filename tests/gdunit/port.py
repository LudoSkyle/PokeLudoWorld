"""Porte tests/lib.gd et un dossier de tests vers gdUnit4 : tests/gdunit/game_suite.gd et tests/gdunit/<dossier>/*.gd.

    python3 tests/gdunit/port.py . moves        (depuis la racine du dépôt ; un dossier à la fois)

Il réécrit ce qu'il porte : une retouche se fait dans tests/lib.gd ou dans le test d'origine, puis on relance.
"""
import os, re, sys
ROOT = sys.argv[1]; FOLDER = sys.argv[2]
OUT = os.path.join(ROOT, 'tests', 'gdunit')
os.makedirs(os.path.join(OUT, FOLDER), exist_ok=True)

def common(s):
    s = s.replace('await process_frame', 'await get_tree().process_frame')
    s = s.replace('Time.get_ticks_msec()', 'ticks()')
    s = re.sub(r'(?<![\w.$"/])root\.', 'get_tree().root.', s)
    return s

lib = open(os.path.join(ROOT, 'tests', 'lib.gd'), encoding='utf-8').read()
head_end = lib.index('const VP :=')
body = lib[head_end:]
# ce qui tient au lanceur maison : _initialize, _run
body = re.sub(r'func _initialize\(\) -> void:\n\t_run\.call_deferred\(\)\n\n', '', body)
body = body[:body.index('func _run() -> void:')]
# attendre en SECONDES DE JEU : le temps du jeu peut aller plus vite que l'horloge
body = re.sub(r'func secs\(t: float\) -> void:\n(?:\t.*\n)+', 'func secs(t: float) -> void:\n\tvar end := ticks() + int(t * 1000.0)\n\twhile ticks() < end:\n\t\tawait get_tree().process_frame\n', body)
body = re.sub(r'func check\(label: String, ok: bool, detail: String = ""\) -> void:\n(?:\t.*\n)+',
              'func check(label: String, ok: bool, detail: String = "") -> void:\n\tif not ok:\n\t\tfailures += 1\n\t# Un contrôle raté ne coupe pas le test : les suivants se jouent, et tous sont rapportés.\n\tassert_bool(ok).override_failure_message("%s  %s" % [label, detail]).is_true()\n', body)
body = re.sub(r'func shot\(name: String\) -> void:\n(?:\t.*\n)+', 'func shot(name: String) -> void:\n\tif DisplayServer.get_name() == "headless":\n\t\treturn          # sans écran, rien n\'est dessiné\n\tget_tree().root.get_texture().get_image().save_png("user://w_%s.png" % name)\n', body)
body = common(body)
head = '''extends GdUnitTestSuite

# Outils communs aux tests joues au clavier, pour gdUnit4. Chaque test herite de ce fichier et
# ecrit une fonction test_<sujet>().
#
# C'est tests/lib.gd, porte : memes outils, memes noms. Ce qui change :
#   - c'est gdUnit4 qui lance (addons/gdUnit4), compte et rapporte ; check() est une assertion ;
#   - le jeu est monte avant chaque test (before_test) et demonte apres (after_test), dans le
#     meme Godot : on ne relance plus le moteur a chaque test ;
#   - on attend en TEMPS DE JEU (ticks(), secs()), jamais a l'horloge : lance avec --fixed-fps,
#     le jeu avance d'un soixantieme de seconde par image, aussi vite que la machine le peut.
#
# Un test est PETIT : un dialogue, une porte, une piece, un deplacement. Il demarre directement
# sur sa carte et sa case (scene() et start()). Ce placement est une mise en place ; tout ce qui
# est VERIFIE se joue avec de vraies entrees clavier.

'''
tail = '''
# Ce test lit-il l'image a l'ecran ? Sans fenetre rien n'est dessine : ceux-la se jouent a part, dans une fenetre.
func reads_screen() -> bool:
	return false

# --- le temps du jeu

var _clock := 0.0

func _process(delta: float) -> void:
	_clock += delta

# Le temps de jeu ecoule, en millisecondes : ce que comptait l'horloge quand le jeu tournait en temps reel.
func ticks() -> int:
	return int(_clock * 1000.0)

# --- monter et demonter le jeu, autour de chaque test

# Le jeu n'ecrit dans des fichiers de test que lance avec « -- --test » (GameFiles.kt). Sans cela, un
# test qui sauvegarde ecraserait la partie du joueur : on refuse de monter le jeu.
func in_test_mode() -> bool:
	return "--test" in OS.get_cmdline_user_args()

func before_test() -> void:
	failures = 0
	if not in_test_mode():
		fail("le jeu n'est pas en mode test : relancer avec « -- --test » (tests/gdunit/run.sh)")
		return
	get_tree().root.size = Vector2i(1280, 960)
	# Etat neuf a chaque test : ni reglages ni sauvegarde d'un test precedent.
	# Ce sont des fichiers de test, ceux du joueur ne sont jamais touches.
	for file in ["user://test_settings.cfg", "user://test_save.cfg", save_path(1), save_path(2), save_path(3)]:
		if FileAccess.file_exists(file):
			DirAccess.remove_absolute(file)
	for action in InputMap.get_actions():
		Input.action_release(action)
	# Un test qui lit l'image a besoin d'une fenetre que le systeme dessine vraiment : on l'attend, a l'horloge
	# (c'est le systeme qu'on attend, pas le jeu). On ne la rouvre ni ne la ramene devant : run.sh la lance une
	# fois, sans que gdUnit4 la reduise.
	if reads_screen() and DisplayServer.get_name() != "headless":
		var limit := Time.get_ticks_msec() + 8000
		while not DisplayServer.window_can_draw() and Time.get_ticks_msec() < limit:
			await get_tree().process_frame
		if not DisplayServer.window_can_draw():
			fail("la fenetre du jeu n'est pas dessinee (reduite, ou entierement cachee ?) : ce test lit l'image")
			return
		await wait(30)
	# Un lancement neuf : reglages relus, premier emplacement, ciel degage.
	get_tree().root.get_node("Globals").fresh_start()
	# Les tests se jouent en plein jour, sauf ceux qui imposent une autre heure.
	get_tree().root.get_node("Globals").set_hour(12.0)
	await boot(false)
	if start() != Vector2i(-1, -1):
		player().position = Vector2(start().x * 16 + 8, start().y * 16 + 8)
		await wait(10)

func after_test() -> void:
	if not in_test_mode():
		return
	for action in InputMap.get_actions():
		Input.action_release(action)
	if is_instance_valid(game):
		get_tree().root.remove_child(game)
		game.free()
	game = null
	await wait(5)
'''
open(os.path.join(OUT, 'game_suite.gd'), 'w', encoding='utf-8').write(head + body.rstrip('\n') + '\n' + tail)

n = 0
for name in sorted(os.listdir(os.path.join(ROOT, 'tests', FOLDER))):
    if not name.endswith('.gd'): continue
    s = open(os.path.join(ROOT, 'tests', FOLDER, name), encoding='utf-8').read()
    if s.count('extends "res://tests/lib.gd"') != 1 or s.count('func test() -> void:') != 1: print('  à la main :', FOLDER + '/' + name); continue
    s = s.replace('extends "res://tests/lib.gd"', 'extends "res://tests/gdunit/game_suite.gd"')
    s = s.replace('func test() -> void:', 'func test_%s() -> void:\n\tif game == null:\n\t\treturn' % name[:-3])
    if 'get_image()' in s: s = s.rstrip('\n') + '\n\n# Ce test lit l\'image a l\'ecran : il lui faut une fenetre (tests/gdunit/run.sh le joue a part).\nfunc reads_screen() -> bool:\n\treturn true\n'
    open(os.path.join(OUT, FOLDER, name), 'w', encoding='utf-8').write(common(s)); n += 1
print('game_suite.gd et %d tests de %s portés' % (n, FOLDER))
