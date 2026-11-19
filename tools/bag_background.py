#!/usr/bin/env python3
"""Porte le fond du sac à la taille de l'écran : assets/ui/bag/background.png, de 288 × 162 à 320 × 240.

    python3 tools/bag_background.py

L'écran est en 4:3, 320 × 240 pixels de jeu ; le fond du sac était resté à l'ancien format. Rien n'est redessiné :
on **recopie des bandes** du fond, comme on l'avait fait pour passer de 240 × 160 à 288 × 162.

  - 32 colonnes de plus dans le panneau de la liste : les colonnes 160 à 191, soit quatre périodes de ses pointillés
    (un tiret de 6 pixels tous les 8), qui restent donc réguliers ;
  - 48 rangées de plus dans la liste : la bande 48-63, qui porte une ligne de pointillés, recopiée trois fois — trois
    lignes de plus, neuf au lieu de six ; à gauche ce sont les rayures du fond, de période 2 ;
  - 30 rangées de bleu de plus dans le bandeau du bas : 14 au-dessus de la case de l'icône, 16 au-dessous — elle reste
    au milieu du bandeau, et la description a une ligne de plus.

Le script ne fait rien si le fond est déjà à la bonne taille : l'ancien est dans l'historique du dépôt.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from island_tiles import load, save  # noqa: E402

PATH = os.path.join(os.path.dirname(HERE), 'src', 'main', 'kotlin', 'fr', 'skyle', 'pokemonmirage', 'assets', 'ui', 'bag', 'background.png')
OLD, NEW = (288, 162), (320, 240)
COLUMNS = (160, 192)          # les colonnes recopiées une fois, à leur suite
BAND, TIMES = (48, 64), 3     # la bande de liste recopiée, et combien de fois
ABOVE, BELOW = (116, 14), (157, 16)          # une rangée de bleu au-dessus de la case de l'icône, une au-dessous : (rangée, copies)

if __name__ == '__main__':
    w, h, px = load(PATH)
    if (w, h) == NEW: sys.exit('%s : déjà en %d × %d' % (os.path.relpath(PATH), w, h))
    if (w, h) != OLD: sys.exit('%s : %d × %d, on attendait %d × %d' % (os.path.relpath(PATH), w, h, OLD[0], OLD[1]))
    rows = []
    for y in range(h):
        rows.append(px[y])
        if y == BAND[1] - 1: rows += [px[j] for _ in range(TIMES) for j in range(*BAND)]
        for at, copies in (ABOVE, BELOW):
            if y == at: rows += [px[at]] * copies
    out = [[tuple(p) for p in row[:COLUMNS[1]] + row[COLUMNS[0]:COLUMNS[1]] + row[COLUMNS[1]:]] for row in rows]
    assert (len(out[0]), len(out)) == NEW, (len(out[0]), len(out))
    save(PATH, out)
    print('%s : %d × %d' % (os.path.relpath(PATH), NEW[0], NEW[1]))
