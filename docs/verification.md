# Vérifier sans ouvrir l'éditeur

Godot n'est pas dans `/Applications` sur la machine de dev. Pose-le une fois :

```bash
GODOT=/Users/godart/Downloads/Godot.app/Contents/MacOS/Godot
```

> Lancé depuis `~/Downloads`, macOS l'exécute via AppTranslocation, depuis un
> chemin temporaire en lecture seule : les réglages d'éditeur ne persistent pas.
> Le déplacer dans `/Applications` règle le problème.

## Le projet compile-t-il, la scène charge-t-elle ?

```bash
"$GODOT" --headless --path "$PWD" --import && "$GODOT" --headless --path "$PWD" --quit-after 30
```

Aucune sortie en dehors des logs de `Globals` = aucune erreur.

## Rendre une image

Le mode headless ne rend rien. Il faut une fenêtre, et un script GDScript
temporaire — qui cohabite sans problème avec le Kotlin :

```gdscript
extends SceneTree
func _initialize() -> void: _run.call_deferred()
func _run() -> void:
    root.size = Vector2i(768, 448)
    var level := load("res://.../start_island.tscn").instantiate()
    root.add_child(level)
    await process_frame
    root.get_texture().get_image().save_png("user://shot.png")
    quit()
```

```bash
"$GODOT" --path "$PWD" --script res://.probe_tmp/shot.gd
```

L'image sort dans `~/Library/Application Support/Godot/app_userdata/PokeLudoWorld/`.
**Supprimer le dossier de sonde après usage.**

## Tester les collisions

Headless suffit : instancier la map, attendre trois `physics_frame`, puis
`intersect_point` sur le centre de chaque case et imprimer une carte ASCII.
C'est ce qui a permis de voir que la bouche de grotte était le seul trou de la
falaise, et que la sortie ouest était ouverte.

## Tester le tri Y

Ajouter des `Polygon2D` magenta dans `World/Entities`, origine aux pieds :

```gdscript
p.polygon = PackedVector2Array([Vector2(-6,-22), Vector2(6,-22), Vector2(6,0), Vector2(-6,0)])
p.position = Vector2(case.x * 16 + 8, case.y * 16 + 16)
```

Au-dessus d'un arbre on doit passer derrière, en dessous devant.

## Une capture qui ne montre pas le joueur n'est pas un résultat

La caméra est bornée à l'étendue de la map : près d'un bord, le joueur n'est
plus au centre de l'image, et un recadrage fixe sur le centre peut ne pas le
montrer du tout. Ça s'est produit sur la zone d'eau, la capture est passée pour
bonne, et le défaut est remonté par le joueur.

Dans une sonde, lever les limites avant de capturer :

```gdscript
cam.limit_left = -10000 ; cam.limit_top = -10000
cam.limit_right = 10000 ; cam.limit_bottom = 10000
```

Le joueur est alors exactement au centre, et `cam.get_screen_center_position()`
doit valoir sa position — à imprimer, c'est l'assertion qui empêche de valider
une image vide.

## Tester en jouant, pas en téléportant

Poser le joueur sur une case par `position = ...` court-circuite tout ce qui
peut mal tourner : le chemin pour y arriver, le pas en cours, la touche encore
enfoncée. Trois défauts sont passés ainsi sur les changements de carte.

Une sonde peut jouer pour de vrai : `Input.action_press("ui_up")`, attendre que
la case change, relâcher. Avec un parcours en largeur sur les collisions du
jeu, elle suit n'importe quel trajet. Les contrôles à faire à chaque arrivée
sont listés dans [levels.md](levels.md).

## Les tests : un sujet par fichier

Un test vérifie **une seule chose** — un dialogue, une porte, une pièce, un
déplacement — et dure de 5 à 20 secondes. Il démarre directement sur sa carte
et sa case, sans rejouer de trajet.

```bash
tests/run.sh dialogue/fisher     # un test
tests/run.sh fisher lab_clock    # pareil, par leur nom seul
tests/run.sh doors               # tout un dossier
tests/run.sh doors/ludo          # ceux dont le chemin commence ainsi
tests/run.sh audit               # accessibilité des cartes fermées
tests/run.sh --list              # la liste
tests/run.sh                     # tout : 6 minutes, à éviter
```

| Dossier | Un fichier par… | Exemples |
|---|---|---|
| `dialogue/` | personnage ou objet à qui l'on parle | `fisher`, `guard_north`, `runner_hailed`, `sign`, `tv`, `lab_clock` |
| `moves/` | déplacement qu'on veut voir | `runner_loop`, `runner_blocked`, `grass_wander`, `roadblock` |
| `doors/` | porte, dans un sens | `enter`, `enter_held`, `ludo_stairs_up`, `lab_exit` |
| `collisions/` | pièce ou obstacle | `ludo_stairs`, `lab_room`, `npcs` |
| `ui/` | comportement d'interface | `banner_arrival`, `banner_same_place`, `title_new_game` |
| `quests/` | brique du moteur de quêtes, sur des nœuds posés par le test (`spawn`) | `flag_saved`, `npc_states`, `item_found`, `ask_yes`, `library_register` |
| `audio/` | ce qu'on entend : musique d'un lieu, jingle, bruitage | `music_shared`, `music_change`, `jingle_item`, `sfx_bump` |
| `daynight/` | la teinte du dehors selon l'heure, les lampadaires, les fenêtres | `tint`, `lamps`, `windows` |
| `audit/` | grille de collisions : arrivées libres, portes reliées | `tests/run.sh audit` |

### Le terrain d'essai, et les cartes du jeu

Deux sortes de tests, sur deux sortes de cartes :

- **ce qui vérifie le système du jeu** — déplacements, dialogues, menus,
  portes, sons, jour et nuit, moteur de quêtes — se joue sur **le terrain
  d'essai**, `tests/maps/field.tscn` : c'est la carte par défaut d'un test.
  24 × 16 cases, presque un écran : tout y est à quelques pas, un test n'y
  marche jamais longtemps ;
- **ce qui vérifie une carte ou une quête du jeu** se joue sur cette carte,
  nommée par `scene()` : `tests/island/` pour l'île, les portes et les pièces
  des intérieurs, la bibliothèque et son Registre.

Le terrain d'essai ne fait pas partie du jeu : aucune porte n'y mène. Il est
fabriqué par `tests/maps/build.py`, dont l'en-tête donne le plan case par
case ; on y trouve, à des cases fixes :

| Quoi | Où | Pour quels tests |
|---|---|---|
| deux gardes et leur passage | (1,1), (1,3), le passage en (1,2) | `moves/roadblock`, `dialogue/guard_*` |
| un couloir dégagé de 14 cases | la rangée 2, de x = 2 à 15 | `moves/run` |
| de hautes herbes, un chasseur qui y erre | x 5–11, y 6–8 ; lui part de (8,7) | `moves/grass_*`, `moves/wild_encounter` |
| une zone libre où les tests posent leurs nœuds (`spawn`) | x 13–18, y 5–10 ; on s'y tient en (14,8) | `quests/`, `ui/speaker_name`, `audio/jingle_item` |
| le coureur et sa boucle à deux voies | x 19–22, y 6–12 | `moves/runner_*`, `dialogue/runner_*` |
| un étang : rive, eau claire, eau profonde, un pêcheur | x 2–7, y 11–14 ; lui en (4,13) | `dialogue/fisher`, `moves/water_moves` |
| deux lampadaires, une maison à fenêtre | (9,11), (15,11) ; la maison en x 16–19, y 0–4 | `daynight/` |
| un banc, un panneau | (2,5)–(3,5) ; (22,3) | `audio/sfx_bump`, `dialogue/sign`, `ui/options_*` |
| deux portes | `Cabane` (21,1), `Salle` (17,4) | `doors/enter*`, `audio/music_*`, `ui/banner_enter` |

Les deux portes mènent à deux pièces nues, `tests/maps/room.tscn` (la cabane,
qui a la musique du terrain) et `tests/maps/hall.tscn` (la salle, qui a la
sienne) : de quoi vérifier qu'une musique continue d'une carte à l'autre, ou
change.

**Déplacer un élément du terrain, c'est reprendre les tests qui visent sa
case.** En ajouter un se fait dans `build.py`, sur une case libre.

**Ne lancer que les tests de ce qu'on vient de toucher** : on déplace le
pêcheur, on lance `fisher` et `collisions/npcs`, rien d'autre. Si un mécanisme
partagé change (lecture des touches, portes, boîte de dialogue), lancer le
dossier qui s'en sert, pas tout.

### Écrire un test

Un nouveau sujet = un nouveau fichier, jamais une section de plus dans un
fichier existant.

```gdscript
extends "res://tests/lib.gd"

# Le pecheur : il repond, puis se retourne vers l'eau.

func scene() -> String:            # carte de depart ; le terrain d'essai par defaut
	return "field"

func start() -> Vector2i:          # case de depart ; l'apparition par defaut
	return Vector2i(4, 12)

func test() -> void:
	await talk("pecheur", Vector2i(4, 12), "ui_down", "Fisher", "mord", "idle_up")
```

`scene()` et `start()` posent le joueur : c'est une mise en place. Tout ce qui
est **vérifié** se joue avec de vraies entrées clavier. Les outils sont dans
`tests/lib.gd` : `walk`, `arrival`, `examine`, `talk`, `hold_no_change`,
`hold_until_change`, `hold_and_count_changes`, `watch_banner`, `cell_of`,
`resting`, `secs`.

### PNJ mobiles et durées

Un test attend en **secondes** (`secs(t)` dans `tests/lib.gd`), pas en images :
sur un écran à 120 Hz une image dure deux fois moins. `walk()` recalcule sa
route si un PNJ s'est mis en travers. Pour parler à un PNJ qui erre, le test le
fige d'abord (`npc.movement = "static"`).

## Les quatre questions, avant toute sonde

Un test automatique vérifie ce qu'on a décidé, pas si ça a du sens. Avant de
rendre la main, se poser ces questions **case par case**, le personnage posé à
chaque endroit clé :

1. **Est-ce visuellement logique, possible ?** Un pot de fleurs ici a-t-il un
   sens ? Une fenêtre peut-elle être là ?
2. **Le comportement est-il logique ?** On entre par la porte, par le milieu de
   l'escalier ; on ne traverse pas une barrière. Comme dans la vraie vie.
3. **L'ensemble est-il cohérent ?** Pas de caillou dans une maison, pas
   d'algues sur l'herbe.
4. **Les collisions sont-elles logiques ?** Pour chaque case bloquée : qu'est-ce
   qui gêne physiquement ? Pour chaque case libre : pourrait-on s'y tenir ?

Quand une référence du jeu d'origine est fournie, c'est à elle qu'on compare,
avant la planche de tuiles.

## La règle qui coûte cher quand on l'oublie

**Ne jamais valider un rendu sur une vue d'ensemble.** Deux bugs sont passés
comme ça : un tronc d'arbre sur un toit, une entrée de grotte recouverte par le
chemin. Les deux tenaient sur quelques dizaines de pixels.

La méthode qui marche :

1. Calculer par programme **toutes** les cases où deux calques se recouvrent.
   Sur une petite carte il n'y en a qu'une dizaine.
2. Zoomer sur chacune, une par une.
3. Comparer au rendu d'avant la modification par un **diff case par case** sur
   toute la map, et annoncer le chiffre.

Et quand on demande une relecture visuelle dans l'éditeur : **le redémarrer
soi-même**. Un éditeur déjà ouvert garde les anciens fichiers en mémoire, et on
se fait renvoyer la même capture.
