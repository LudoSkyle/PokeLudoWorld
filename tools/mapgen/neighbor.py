#!/usr/bin/env python3
"""Ce qu'une carte montre à son bord, pour que sa voisine la prolonge.

    python3 tools/mapgen/neighbor.py tools/mapgen/plans/route_1_bis.toml north

Lit le plan d'une carte (écrit à la main, inventé ou relevé d'une scène) et rend, en TOML, ce qu'il faut coller dans
le monde de la carte qu'on veut faire **de ce côté-là** (`north` : la nouvelle carte est au nord, son bord du sud
touche le bord du nord de celle-ci) :

  - `[[exit]]` avec `cell` : sous chaque sortie de la voisine, à la case près ;
  - `[[shore]]` : les colonnes où son eau (et sa falaise sur l'eau) touche le bord ;
  - `[seam]` : la trame de ses arbres près du bord, zone par zone, ses arbres que le bord coupe — la nouvelle carte
    en dessine l'autre moitié —, et les colonnes où sa terre est un cran plus haut que sa sortie (`high`) : ses
    falaises d'herbe qui filent hors de la carte continuent en face.

Les deux cartes ont la même largeur, colonne pour colonne. Seul `north` est fait : c'est le cas qui s'est présenté.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as builder  # noqa: E402


def runs(values):
    out, start, prev = [], None, None
    for v in sorted(values):
        if prev is None or v != prev + 1:
            if start is not None: out.append((start, prev))
            start = v
        prev = v
    if start is not None: out.append((start, prev))
    return out


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 2 or args[1] != 'north': sys.exit(__doc__)
    plan = builder.Plan(args[0])
    b = builder.build(plan)
    W, L = b['W'], b['L']
    names = {}
    for k, v in builder.AT.items(): names.setdefault(tuple(v), k)
    def ground(x): return names.get(tuple(L['Ground'][(x, 0)][1:3]), '') if (x, 0) in L['Ground'] else ''
    print('# Le bord du nord de %s (%d cases de large), lu par tools/mapgen/neighbor.py : à coller dans le monde de la carte du nord.' % (plan.map['name'], W))
    print('# Sa taille : size = [%d, <hauteur paire>]' % W)
    way = [x for x in range(W) if (x, 0) not in b['SOLID']]
    for a, z in runs(way):
        print('\n[[exit]]\nside = "south"\ncell = %d          # sa sortie : colonnes %d à %d\nname = "Sud"' % ((a + z) // 2, a, z))
    low = [x for x in range(W) if ground(x).startswith(('water', 'deep', 'sand'))]
    for a, z in runs(low):
        if z - a >= 2: print('\n[[shore]]\nside = "south"\nfrom = %d\nto = %d\ndepth = 14' % (a, z))
    cut = sorted((x, r, k) for k, x, r in b['sprites'] if k.startswith('tree') and r <= 1)          # ceux dont la cime dépasse du bord : la carte du nord en porte le haut
    zones = []          # des zones de même trame, lues sur ces arbres-là : c'est leur grille que la carte du nord continue
    for x, r, k in cut:
        phase = (x - 2 * (r % 2)) % 4
        if zones and zones[-1][2] == phase and x - zones[-1][1] <= 8: zones[-1][1] = x + 2
        else: zones.append([x, x + 2, phase])
    merged = zones
    edges = [(x, names.get(tuple(L['Cliffs1'][(x, 0)][1:3]), '')) for x in range(W) if (x, 0) in L['Cliffs1']]
    flanks = [(x, n[-1]) for x, n in edges if n in ('grass4', 'grass6')]          # un flanc ouest ouvre une terre haute, un flanc est la ferme
    high, start = [], (0 if flanks and flanks[0][1] == '6' else None)
    for x, k in flanks:
        if k == '4': start = x
        elif start is not None: high.append([start, x]); start = None
    if start is not None: high.append([start, W - 1])
    print('\n[seam]\nside = "south"')
    print('high = [%s]          # de la colonne … à la colonne … : sa terre y est un cran plus haut que sa sortie' % ', '.join('[%d, %d]' % tuple(h) for h in high))
    print('phases = [%s]          # de la colonne … à la colonne …, la trame : (colonne − trame − 2 × (rangée impaire)) multiple de 4' % ', '.join('[%d, %d, %d]' % tuple(m) for m in merged))
    print('trees = [%s]          # ses arbres des rangées 0 et 1, que son bord coupe' % ', '.join('["%s", %d, %d]' % (k, x, r) for x, r, k in cut))
