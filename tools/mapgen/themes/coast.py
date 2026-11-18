#!/usr/bin/env python3
"""Écrit `coast.toml` : le décor « bord de mer » — les planches de la Route 1 et de l'île.

    python3 tools/mapgen/themes/coast.py

Un **décor** dit au constructeur de cartes quelle tuile dessine quoi : pour chaque nom (`rock8`, `stair5`, `treeA`),
sa planche, sa case, si elle arrête, et pour ce qui est debout sa taille et les cases qu'il occupe. Le constructeur ne
connaît aucune texture : il ne lit que ce fichier. Un autre décor (une ville, la neige) est un autre fichier, avec les
mêmes noms.

Celui-ci est tiré des tables qui fabriquent les planches (`tools/route_tiles.py`, `tools/village_tiles.py`) : on le
relance quand une planche change.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
import route_tiles  # noqa: E402
import village_tiles  # noqa: E402

AT, SIZES, MADE = route_tiles.atlas(), route_tiles.sizes(), set(route_tiles.cells())
ASSETS = 'src/main/kotlin/fr/skyle/pokemonmirage/assets/levels/'
FEET = {'tree': [[i, -j] for j in (1, 0) for i in range(3)], 'boulder': [[0, -1], [1, -1], [0, 0], [1, 0]]}
LOW = ('fl', 'shell', 'lily')          # du décor bas, sans collision : sur le calque des décorations

lines = ['# Le décor « bord de mer ». Fabriqué par tools/mapgen/themes/coast.py : ne pas modifier à la main.', '',
         'name = "coast"', '',
         '# Les planches : leur numéro de source dans le TileSet (resources/tilesets/level.tres), et l\'image, pour l\'aperçu.',
         '[sources]',
         'main = { id = 11, sheet = "%sroute.png" }' % ASSETS,
         'buildings = { id = 14, sheet = "%svillage.png" }' % ASSETS,
         'tall_grass = { id = 12, at = [6, 0], drawn = [6, 6] }          # la touffe animée ; `drawn` : où la voir sur la planche principale',
         'blooms = { id = 5, foot = 4, top = 3 }                         # les grandes fleurs : une colonne par sorte, la rangée du pied, celle de la cime', '',
         '# Les tuiles du sol, des bords et des ouvrages : nom = [colonne, rangée, 1 si elle arrête].',
         '[tiles]']
for name in sorted(AT):
    if name in SIZES or AT[name] not in MADE: continue
    lines.append('%s = [%d, %d, %d]' % (name, AT[name][0], AT[name][1], 1 if route_tiles.blocks(name) else 0))
lines += ['', '# Ce qui se pose : `at` sa case sur la planche, `size` sa taille en cases, `drop` les rangées d\'ombre sous son pied,',
          '# `anchor` la colonne de son pied dans son image, `feet` les cases qu\'il occupe (depuis son coin bas-gauche),',
          '# `layer` le calque où il va.', '[props]']
for name in sorted(SIZES):
    if AT[name] not in MADE: continue
    w, h = SIZES[name]
    feet = FEET['tree'] if name.startswith('tree') else FEET.get(name, [[0, 0]])
    lines.append('%s = { source = "main", at = [%d, %d], size = [%d, %d], drop = %d, anchor = 0, feet = %s, layer = "%s" }'
                 % (name, AT[name][0], AT[name][1], w, h, route_tiles.drop(name), feet, 'Trees' if name.startswith('tree') else 'Props'))
for name in ('pebbleA', 'pebbleB'):
    if name in AT and name not in SIZES: lines.append('%s = { source = "main", at = [%d, %d], size = [1, 1], drop = 0, anchor = 0, feet = [[0, 0]], layer = "Props" }' % (name, AT[name][0], AT[name][1]))
for name in sorted(village_tiles.PLANTS):
    w, h = village_tiles.sizes()[name]; a = village_tiles.atlas()[name]; door = village_tiles.door(name)
    feet = [[door, 0]] if name != 'bush' else [[i, 0] for i in range(w)]
    lines.append('%s = { source = "buildings", at = [%d, %d], size = [%d, %d], drop = %d, anchor = %d, feet = %s, layer = "Props" }' % (name, a[0], a[1], w, h, village_tiles.drop(name), door, feet))
for name in sorted(AT):
    if name.startswith(LOW) and AT[name] in MADE: lines.append('%s = { source = "main", at = [%d, %d], size = [1, 1], drop = 0, anchor = 0, feet = [], layer = "Decorations" }' % (name, AT[name][0], AT[name][1]))
lines += ['', '# Les maisons : `door` la colonne de la porte dans l\'image, sur sa rangée du bas.', '[buildings]']
for name in sorted(village_tiles.sizes()):
    if name in village_tiles.PLANTS: continue
    w, h = village_tiles.sizes()[name]; a = village_tiles.atlas()[name]
    lines.append('%s = { at = [%d, %d], size = [%d, %d], door = %d, drop = %d }' % (name, a[0], a[1], w, h, village_tiles.door(name), village_tiles.drop(name)))
out = os.path.join(HERE, 'coast.toml')
open(out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('%s : %d tuiles, %d choses à poser' % (os.path.relpath(out), sum(1 for l in lines if ' = [' in l and not l.startswith(('main', 'buildings', 'tall', 'blooms'))), sum(1 for l in lines if 'layer =' in l)))
