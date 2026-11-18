#!/usr/bin/env python3
"""Relève la carte d'exemple de la grotte de glace, case par case et **par couches** : reference.png -> survey.json.

    python3 tools/maps/ice_cave/survey.py            # écrit survey.json, dit ce qui reste inexpliqué
    python3 tools/maps/ice_cave/survey.py --map      # en plus, les deux couches à l'écran

`reference.png` est la carte « old n random mountain entrance » de Phyromatical, fournie par Ludovic le 18/11/2026
(544 × 880, cases de 16). Elle est faite des tuiles de `assets/levels/sources/ice_cave.png`, du même auteur : on ne
devine donc rien, on **retrouve** chaque case dans la planche.

Deux différences avec `tools/maps/route_1/survey.py` :

  - l'image nous est parvenue en **JPEG** : ses pixels ont bougé, on ne peut pas exiger l'égalité. On prend
    l'explication la plus proche (écart quadratique moyen par pixel, sur 441 possibles) et l'on rend l'écart ;
  - la planche est faite pour être **superposée** : beaucoup de ses tuiles ont du transparent (le bord d'un plateau,
    le liseré du vide, un rocher). Une case de la carte s'explique donc par **une tuile pleine, ou une tuile à trous
    posée sur une tuile pleine**. C'est ce que la première version de ce relevé ne savait pas, et pourquoi elle
    trouvait un écart médian de 33 : elle cherchait une seule tuile par case.

Les tuiles sont nommées par leur place sur la planche : rangée en lettre (a = y 0), colonne en chiffre ou lettre
(0 = x 0, a = x 160) — `b1` est la case (16, 16).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from island_tiles import load  # noqa: E402

REF = os.path.join(HERE, 'reference.png')
SHEET = os.path.join(ROOT, 'src', 'main', 'kotlin', 'fr', 'skyle', 'pokemonmirage', 'assets', 'levels', 'sources', 'ice_cave.png')
OUT = os.path.join(HERE, 'survey.json')
COLS = '0123456789abcdefghijk'
ROWS = 'abcdefghijklmnopqrstu'


def code(at): return ROWS[at[1]] + COLS[at[0]]


def main():
    rw, rh, ref = load(REF)
    sw, sh, sheet = load(SHEET)
    tiles = {}
    for cy in range(sh // 16):
        for cx in range(sw // 16):
            px = [sheet[cy * 16 + j][cx * 16 + i] for j in range(16) for i in range(16)]
            solid = [k for k in range(256) if px[k][3] >= 128]
            if len(solid) < 12: continue
            tiles[(cx, cy)] = ([tuple(p[:3]) for p in px], solid, [k for k in range(256) if px[k][3] < 128])
    full = {at: t for at, t in tiles.items() if len(t[1]) == 256}
    holed = {at: t for at, t in tiles.items() if len(t[1]) < 256}
    print('%d tuiles : %d pleines, %d à trous' % (len(tiles), len(full), len(holed)))

    cells, errs = {}, []
    for cy in range(rh // 16):
        for cx in range(rw // 16):
            px = [tuple(ref[cy * 16 + j][cx * 16 + i][:3]) for j in range(16) for i in range(16)]
            if max(max(p) for p in px) < 30:
                cells[(cx, cy)] = (None, None, 0.0)
                continue
            # l'écart de chaque pixel à chaque tuile pleine, une fois pour toutes
            under = {at: [sum((t[0][k][c] - px[k][c]) ** 2 for c in range(3)) for k in range(256)] for at, t in full.items()}
            best = min(((sum(e), None, at) for at, e in under.items()))
            # une tuile à trous n'est candidate que si ce qu'elle montre colle à l'image
            for at, (rgb, solid, clear) in holed.items():
                top = sum(sum((rgb[k][c] - px[k][c]) ** 2 for c in range(3)) for k in solid)
                if top / len(solid) > 3 * 18 * 18 or top >= best[0]: continue
                rest, base = min((sum(e[k] for k in clear), b) for b, e in under.items())
                if top + rest < best[0]: best = (top + rest, at, base)
            d = (best[0] / 256.0 / 3.0) ** 0.5
            cells[(cx, cy)] = (best[1], best[2], d)
            errs.append(d)
    errs.sort()
    print('%d cases relevées — écart par pixel et par canal : médiane %.1f, moyenne %.1f, 9 sur 10 sous %.1f, pire %.1f'
          % (len(errs), errs[len(errs) // 2], sum(errs) / len(errs), errs[len(errs) * 9 // 10], errs[-1]))
    W, H = rw // 16, rh // 16
    json.dump({'size': [W, H],
               'cells': [[cx, cy, list(t) if t else None, list(b) if b else None, round(d, 1)] for (cx, cy), (t, b, d) in sorted(cells.items(), key=lambda kv: (kv[0][1], kv[0][0]))]},
              open(OUT, 'w'), separators=(',', ':'))
    print('écrit : %s' % os.path.relpath(OUT, ROOT))
    if '--map' in sys.argv:
        for title, k in (('la couche du dessous (tuile pleine)', 1), ('la couche du dessus (tuile à trous)', 0)):
            print('\n' + title)
            for cy in range(H):
                print('  ' + ' '.join(code(cells[(cx, cy)][k]) if cells[(cx, cy)][k] else ('..' if cells[(cx, cy)][1] is None else '--') for cx in range(W)))
        print('\nles cases mal expliquées (écart > 14)')
        for cy in range(H):
            print('  ' + ''.join('#' if cells[(cx, cy)][2] > 14 else ('.' if cells[(cx, cy)][1] is None else 'o') for cx in range(W)))


main()
