# Le plan d'une carte

Un plan est un fichier `<carte>.toml` qui **dit tout ce qu'il y a sur une carte** : le terrain case par case, les
niveaux, chaque arbre, chaque fleur, chaque personnage. Le constructeur (`tools/mapgen/build.py`) l'assemble avec un
décor (`themes/<décor>.toml`) : il pose les bords, les ouvrages et les collisions, et **ne décide de rien** — le même
plan donne toujours la même carte.

Un plan s'écrit à la main, ou sort du générateur (`tools/mapgen/worldgen.py`, voir `worlds/README.md`), qui en
invente un à partir d'une graine. `demo_cove.toml` est écrit à la main ; `route_2.toml` est la Route 1 refaite ;
`prairie.toml` est inventé.

```
python3 tools/mapgen/build.py tools/mapgen/plans/ma_carte.toml                      # contrôle, dit ce qui cloche
python3 tools/mapgen/build.py tools/mapgen/plans/ma_carte.toml --map                # ce qu'on atteint à pied
python3 tools/mapgen/build.py tools/mapgen/plans/ma_carte.toml --preview /tmp/c.png # la carte dessinée
python3 tools/mapgen/build.py tools/mapgen/plans/ma_carte.toml --write              # la scène
```

**Le constructeur crée la carte, il ne l'entretient pas.** Une fois la scène écrite, elle se retouche dans l'éditeur
de Godot. `--write` refuse d'écraser une scène qui existe (`--force` l'écrase, et perd les retouches).

## Les grilles

Même taille, une case par signe, entre `'''`. Les deux premières suffisent ; la troisième est facultative.

**`terrain`** — de quoi le sol est fait :

| Signe | |
|---|---|
| `~` | la mer |
| `:` | le sable : une plage, au ras de l'eau |
| `.` | l'herbe : un plateau, cerné de sa falaise |
| `_` | une piste, sur un plateau — trois cases de large |
| `"` | les hautes herbes |
| `^` | la montagne : de la roche sur un plateau |

**`objects`** — ce qu'on pose dessus :

| Signe | |
|---|---|
| `.` | rien |
| `=` | un ponton ou un pont : un rectangle de trois cases de large. De la terre aux deux bouts, c'est un pont, qui monte de lui-même sur le dessus des deux plateaux ; sinon c'est une jetée |
| `%` | un dallage |
| `f` | un parc clôturé : un rectangle, portillon à l'est, grandes fleurs dedans |
| `x` | à laisser dégagé : ni arbre, ni fleur, ni rien |
| `v` | un rebord qu'on saute vers le sud : une rangée de deux cases au moins |
| `>` | un rebord qu'on saute vers l'est : une colonne de deux cases au moins |
| `<` | un rebord qu'on saute vers l'ouest : une colonne de deux cases exactement |
| autre lettre ou chiffre | un **repère**, nommé par une table ci-dessous |

**`levels`** — les hauteurs, sur un plateau :

| Signe | |
|---|---|
| `.` | le niveau du plateau |
| `1` | une **terrasse**, un cran plus haut |

Le bord d'une terrasse, là où il donne sur l'herbe d'en bas, est une petite falaise d'herbe qu'on ne franchit pas :
on y monte par un escalier de pierre (`[[terrace_stairs]]`), on en redescend aussi par un rebord. La forme d'une
terrasse doit être fermée — par son bord, par la falaise du plateau ou par le bord de la carte.

**`props`** — tout ce qui est posé, un par ligne : `sorte colonne rangée` (la case de son pied).

```
treeA 12 8
palm 7 19
bloom2 30 14
fl3 31 15
```

Les sortes sont celles du décor (`[props]` de `themes/<décor>.toml`) : arbres, sapin, blocs, rochers, palmiers,
buisson, petites fleurs `fl1`…`fl5`, coquillages. `bloom0`…`bloom7` est une grande fleur. Le constructeur pose
exactement cette liste, dans cet ordre, et rien d'autre.

## Écrire une carte tuile par tuile : `[[layer]]`

Les grilles ci-dessus sont une **esquisse** : le constructeur en déduit les bords. Une carte dessinée à la main —
la Route 1, avec ses terrasses multiples et sa montagne à gradins — ne suit pas ces règles : près de la moitié de
ses tuiles de falaise ne se déduisent pas de leurs voisines. Pour elle, le plan écrit chaque calque **tel quel** :

```
[[layer]]
name = "Cliffs1"
grid = '''
..ab....
..cd....
'''
[layer.legend]
a = "rock7"            # un signe = une tuile du décor
b = "rock9"
c = ["grass4", 1]      # avec sa variante : 1, sans collision
d = "@10:15,3"         # une tuile que le décor ne nomme pas : sa source dans le TileSet, sa colonne, sa rangée
```

Les calques sont posés dans l'ordre du plan. Un calque écrit remplace ce que l'esquisse aurait donné pour lui ; un
plan peut n'avoir que des calques, sans `terrain`. Dans `props`, une tuile sans nom s'écrit de même, avec son calque :
`@10:0,5 7 28 Props`.

**Refaire une carte qui existe**, sans faute :

```
python3 tools/mapgen/scene_to_plan.py <scène.tscn> <nom>          # son plan, relevé tuile par tuile
python3 tools/mapgen/build.py tools/mapgen/plans/<nom>.toml --write --out tests/maps/<nom>.tscn --force
python3 tools/mapgen/compare.py <scène.tscn> tests/maps/<nom>.tscn  # les cases qui diffèrent : zéro
```

`route_1_bis.toml` et `start_island_bis.toml` sont la Route 1 et l'île de départ relevées ainsi : le constructeur
les refait à l'identique, calque par calque, variantes de collision comprises. **C'est le contrôle à repasser quand
on touche au constructeur** : tant qu'il rend zéro, il sait dire n'importe quelle carte du jeu. Seules les tuiles
sont reprises : panneaux, personnages et portes sont des tables du plan, à écrire.

## Ce qu'on nomme : les tables

Chaque table désigne sa place par un repère (`mark`) posé dans la grille des objets.

| Table | Le repère est… | Champs |
|---|---|---|
| `[map]` | — | `name` (le fichier de la scène), `theme` (le décor), `location`, `banner`, `music`, `daylight`, `wild`, `start` (repère du départ) |
| `[[house]]` | la case de la porte | `name`, `kind` (`hut_left`, `hut_right`, `hall`), `scene` et `door` (où mène la porte) |
| `[[stairs]]` | la colonne de gauche de l'escalier, sur la rangée du bord du plateau | — il fait cinq cases de large et ne monte que face au sud |
| `[[side_stairs]]` | l'anneau d'herbe, rangée du haut des marches | `side` : `W` ou `E`, le côté bas |
| `[[terrace_stairs]]` | la colonne de gauche de l'escalier, sur la rangée du bord sud de la terrasse | — cinq cases de large, face au sud |
| `[[exit]]` | les cases du bord de la carte par où l'on sort | `name`, `scene`, `door` |
| `[[sign]]` | sa case | `name`, `text` |
| `[[lamp]]` | sa case | `name` |
| `[[item]]` | sa case | `name`, `item`, `text`, `flag` |
| `[[npc]]` | sa case | `name`, `appearance`, `text`, `facing`, `display_name`, `required_flag`, `forbidden_flag` ; `movement = "wander"` avec `zone` (repère d'une zone) ; `movement = "patrol"` avec `route` (liste de repères) et `pace` |
| `[[flyers]]` | la hauteur où passe le groupe | `name`, `species` (liste), `pace`, `drift` |

Un panneau, un lampadaire, un objet ou un personnage immobile est posé **sur la case libre la plus proche** de son
repère qui ne gêne pas : ni devant une porte ou un escalier, ni sur une piste, ni dans un passage étroit. Avec
`exact = true`, il prend la case du plan telle quelle, et le constructeur prévient si elle ne convient pas.

## Ce que le constructeur contrôle

Il le dit en `!!`, et sort en erreur : un signe inconnu, un plateau trop petit pour sa falaise, un escalier dont le
bord n'est pas droit ou qui n'a pas de plage à son pied, un rebord sans case libre pour sauter ou retomber, une porte ou une sortie qu'on n'atteint pas depuis le
départ, une chose dont on ne peut pas s'approcher, un morceau de carte libre mais coupé du reste, le bord de la carte
atteint ailleurs qu'à une sortie, la rangée du haut d'un plateau qui ne se foulerait pas.

## Ce qu'il ne fait pas encore

Une montagne à plusieurs gradins, une terrasse sur une terrasse, les grottes et les intérieurs, les lueurs aux fenêtres, les passages gardés.

`route_2.toml` est la Route 1 refaite par le constructeur, pour juger ce qu'il sait faire : son plan est tiré de la
Route 1 d'origine, et `route_1_et_route_2.png` montre les deux côte à côte. La Route 1 et l'île de départ ont été
faites avant lui, par leurs propres programmes (`tools/maps/route_1`, `tools/maps/start_island`) : ce sont des cartes
finies, on ne les refait pas.
