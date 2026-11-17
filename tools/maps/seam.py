#!/usr/bin/env python3
"""Colle le bas de la Route 1 et le haut de l'île de départ, comme si c'était une seule carte.

    python3 tools/maps/seam.py couture.png        # l'image des deux cartes collées, autour de leur couture

Les deux cartes se suivent par leur chemin : la colonne x de l'île est la colonne x + SEAM de la
Route 1 (`start_island/layout.SEAM`), la rangée 0 de l'île suit la rangée 49 de la route. Collées,
elles doivent n'en faire qu'une : même sol, même hauteur, la piste en face de la piste, et chaque
arbre que la couture coupe en deux a ses deux moitiés. Ce script en fait l'image — à regarder —
et contrôle ce qui se contrôle : la piste, et les arbres à cheval.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from island_tiles import save  # noqa: E402


def load(name, folder):
    sys.path.insert(0, os.path.join(HERE, folder))
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, folder, 'layout.py'))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    sys.path.pop(0)
    return module


island = load('island_layout', 'start_island')
route = island.ROUTE_1
SEAM, ROWS = island.SEAM, 12
bad = []
for x in island.ROAD:          # la piste en face de la piste
    if route.ground[(x + SEAM, route.H - 1)] != 'trailC' or island.ground[(x, 0)] != 'trailC': bad.append('la piste ne se suit pas à la colonne %d de l île' % x)
ours = {(x, r, n) for n, x, r in island.sprites if n.startswith('tree') and r < 2 and any(c in island.SHARED for c in range(x, x + 3))}
theirs = {(x - SEAM, r - route.H, n) for n, x, r in route.sprites if n.startswith('tree') and r >= route.H and any(c in island.SHARED for c in range(x - SEAM, x - SEAM + 3))}
bad += ['arbre à cheval sans sa moitié sur la route : %s' % (t,) for t in sorted(ours - theirs)] + ['arbre à cheval sans sa moitié sur l île : %s' % (t,) for t in sorted(theirs - ours)]
for x in island.SHARED:          # même hauteur, même sol : ni falaise ni eau au bord, des deux côtés
    if island.cliffs[(x, 0)] or (x, 0) in island.SEA or route.cliffs[(x + SEAM, route.H - 1)] or route.route_tiles.blocks(route.ground[(x + SEAM, route.H - 1)]):
        bad.append('une falaise ou de l eau touche la couture à la colonne %d de l île' % x)
print('couture : colonnes %d à %d de l île sous les colonnes %d à %d de la route' % (island.SHARED[0], island.SHARED[-1], island.SHARED[0] + SEAM, island.SHARED[-1] + SEAM))
print('\n'.join('  !! ' + b for b in bad) if bad else '  la piste se suit, les arbres à cheval ont leurs deux moitiés, ni falaise ni eau au bord')
if len(sys.argv) > 1:
    top, bottom = route.render(), island.render()
    x0, x1 = min(0, SEAM), max(route.W, island.W + SEAM)          # en colonnes de la route
    out = [[(20, 20, 24, 255)] * ((x1 - x0) * 16) for _ in range(2 * ROWS * 16)]
    for j in range(ROWS * 16):
        for i in range(route.W * 16): out[j][i - x0 * 16] = tuple(top[(route.H - ROWS) * 16 + j][i]) + (255,)
        for i in range(island.W * 16): out[ROWS * 16 + j][i + (SEAM - x0) * 16] = tuple(bottom[j][i]) + (255,)
    save(sys.argv[1], out)
