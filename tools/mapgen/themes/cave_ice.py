#!/usr/bin/env python3
"""Écrit `cave_ice.toml` : le décor « grotte de glace » — la planche `assets/levels/ice_cavern.png`.

    python3 tools/mapgen/themes/cave_ice.py

Ce décor n'est **pas** le décor `cave` à la teinte près : son kit se superpose. Il déclare un grand plateau (`tall…`),
un petit (`short…`) et le liseré du vide (`ring…`), et c'est à leur présence que le constructeur reconnaît qu'il doit
bâtir la paroi par plateaux emboîtés (`tools/mapgen/build.py`, « un décor à plateaux »). Le sol est une matière à bords
(`floor…`), la plaque de sol du plan (`,`) est de la glace lisse (`earth…`). Pas de bassin : la planche n'a pas d'eau.

Tiré de `tools/ice_cave_tiles.py` : on le relance quand la planche change.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
import ice_cave_tiles as kit  # noqa: E402

AT = kit.atlas()
ASSETS = 'src/main/kotlin/fr/skyle/pokemonmirage/assets/levels/'

lines = ['# Le décor « grotte de glace ». Fabriqué par tools/mapgen/themes/cave_ice.py : ne pas modifier à la main.', '',
         'name = "cave_ice"',
         'slick = "earth"          # on glisse sur cette matière : le verglas (la donnée `ice` de ses tuiles)', '',
         '# Les planches : leur numéro de source dans le TileSet (resources/tilesets/level.tres), et l\'image, pour l\'aperçu.',
         '[sources]',
         'main = { id = %d, sheet = "%sice_cavern.png" }' % (kit.SOURCE_ID, ASSETS),
         'item_ball = { sheet = "%sisland.png", region = [48, 96, 16, 16] }          # la Poké Ball d\'un objet à ramasser' % ASSETS, '',
         '# Les tuiles : nom = [colonne, rangée, 1 si elle arrête].',
         '[tiles]']
for name in sorted(AT):
    lines.append('%s = [%d, %d, %d]' % (name, AT[name][0], AT[name][1], 1 if kit.blocks(name) else 0))
lines += ['', '# Ce qui se pose : `at` sa case sur la planche, `size` sa taille en cases, `feet` les cases qu\'il occupe.', '[props]']
for name, (at, (w, h), feet) in sorted(kit.SPRITES.items()):
    lines.append('%s = { source = "main", at = [%d, %d], size = [%d, %d], drop = 0, anchor = 0, feet = %s, layer = "Props" }' % (name, at[0], at[1], w, h, [list(f) for f in feet]))
for name, (at, (w, h), anchor) in sorted(kit.DECOR.items()):          # sans pied : on monte dessus, et le joueur passe devant
    lines.append('%s = { source = "main", at = [%d, %d], size = [%d, %d], drop = 0, anchor = %d, feet = [], layer = "Bridges" }' % (name, at[0], at[1], w, h, anchor))
out = os.path.join(HERE, 'cave_ice.toml')
open(out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('%s : %d tuiles, %d choses à poser dont %d sans collision' % (os.path.relpath(out), len(AT), len(kit.SPRITES) + len(kit.DECOR), len(kit.DECOR)))
