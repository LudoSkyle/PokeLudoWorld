#!/usr/bin/env python3
"""Écrit `cave.toml` : le décor « grotte » — la planche `assets/levels/cavern.png`.

    python3 tools/mapgen/themes/cave.py

Mêmes noms que les autres décors : `lawn` est ici le sol de la grotte, `rock…` sa paroi, `pond…` un bassin, `earth…` une
plaque de sol sombre. Il a en plus le **vide** (`void…`), le noir autour d'une grotte, que le plan écrit `#`.
Ni maisons, ni hautes herbes, ni grandes fleurs : ce décor n'en déclare pas. Tiré de `tools/cavern_tiles.py` : on le
relance quand la planche change.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
import cavern_tiles  # noqa: E402

AT = cavern_tiles.atlas()
ASSETS = 'src/main/kotlin/fr/skyle/pokemonmirage/assets/levels/'

lines = ['# Le décor « grotte ». Fabriqué par tools/mapgen/themes/cave.py : ne pas modifier à la main.', '',
         'name = "cave"', '',
         '# Les planches : leur numéro de source dans le TileSet (resources/tilesets/level.tres), et l\'image, pour l\'aperçu.',
         '[sources]',
         'main = { id = %d, sheet = "%scavern.png" }' % (cavern_tiles.SOURCE_ID, ASSETS),
         'item_ball = { sheet = "%sisland.png", region = [48, 96, 16, 16] }          # la Poké Ball d\'un objet à ramasser' % ASSETS, '',
         '# Les tuiles du sol, des bords et du vide : nom = [colonne, rangée, 1 si elle arrête].',
         '[tiles]']
for name in sorted(AT):
    if name in cavern_tiles.SPRITES: continue
    lines.append('%s = [%d, %d, %d]' % (name, AT[name][0], AT[name][1], 1 if cavern_tiles.blocks(name) else 0))
lines += ['', '# Ce qui se pose : `at` sa case sur la planche, `size` sa taille en cases, `feet` les cases qu\'il occupe.', '[props]']
for name, ((_, _, w, h), at, feet) in sorted(cavern_tiles.SPRITES.items()):
    lines.append('%s = { source = "main", at = [%d, %d], size = [%d, %d], drop = 0, anchor = 0, feet = %s, layer = "Props" }' % (name, at[0], at[1], w, h, [list(f) for f in feet]))
out = os.path.join(HERE, 'cave.toml')
open(out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('%s : %d tuiles, %d choses à poser' % (os.path.relpath(out), len(AT) - len(cavern_tiles.SPRITES), len(cavern_tiles.SPRITES)))
