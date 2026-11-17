#!/usr/bin/env python3
"""Fabrique assets/levels/village.png : les maisons de l'île de départ.

    python3 tools/village_tiles.py

Comme `route_tiles.py`, il découpe dans `assets/levels/sources/town_compilation.png` — la planche
de la Route 1 — sans rien redessiner. Les maisons n'y sont pas sur la grille de 16 : chacune est
recopiée dans une boîte de cases entières, calée pour que **sa porte tombe au milieu d'une
case** et que le bas de ses murs tombe au bas d'une rangée. Son ombre, translucide sur la
planche, déborde sous ses murs : la boîte a des rangées de plus en bas pour la garder entière.

Chaque maison est une seule tuile de plusieurs cases (source 14 du TileSet), comme un arbre de
la route. `HOUSES` dit, pour chacune : où elle est sur la planche, la taille de sa boîte, où
elle y est calée, la colonne de sa porte, et combien de rangées d'ombre elle a sous le pied.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import island_tiles  # noqa: E402
from island_tiles import save, LEVELS  # noqa: E402

OUTPUT = os.path.join(LEVELS, 'village.png')
CLEAR = (0, 0, 0, 0)
SHADOW = 3          # rangées d'ombre sous le pied des maisons
# nom : (x0, y0, x1, y1 des murs et du toit sur la planche, largeur et hauteur de la boîte en cases (sans l'ombre), décalage en x dans la boîte, colonne de la porte, colonne dans village.png)
HOUSES = {
    'hut_left':  ((547, 1541, 615, 1631), (5, 6), 7, 1, 0),       # hutte de chaume, porte à gauche
    'hut_right': ((648, 1541, 716, 1631), (5, 6), 9, 3, 5),       # la même, porte à droite
    'hall':      ((743, 1540, 855, 1631), (8, 6), 7, 4, 10),      # la grande maison de chaume, porte au milieu
}


# Ce qui pousse sur l'île et que route.png n'a pas — même forme : la « porte » est ici la colonne du pied, la seule case pleine.
PLANTS = {
    'palm':     ((662, 146, 697, 187), (3, 3), 6, 1, 18),      # le petit palmier des plages
    'palm_big': ((717, 152, 769, 202), (5, 4), 14, 2, 21),     # le grand
    'bush':     ((400, 144, 447, 187), (3, 3), 0, 1, 26),      # un massif de trois buissons
}
ALL = dict(HOUSES); ALL.update(PLANTS)


def atlas(): return {name: (col, 0) for name, (_, _, _, _, col) in ALL.items()}
def sizes(): return {name: size for name, (_, size, _, _, _) in ALL.items()}
def door(name): return ALL[name][3]
def drop(name): return SHADOW if name in HOUSES else 1


def cells():
    """L'image entière : une liste de rangées de pixels RVBA."""
    town = island_tiles.source_sheet(island_tiles.TOWN)
    columns = max(col + size[0] for _, size, _, _, col in ALL.values())
    lines = max(size[1] for _, size, _, _, _ in ALL.values()) + SHADOW
    sheet = [[CLEAR] * (columns * 16) for _ in range(lines * 16)]
    for name, ((x0, y0, x1, y1), (w, h), shift, _, col) in ALL.items():
        top = h * 16 - (y1 - y0 + 1)          # le bas des murs au bas de la rangée du pied
        for y in range(y0, y1 + 1 + drop(name) * 16):
            for x in range(x0 - shift, x0 - shift + w * 16):
                p = town[y][x]
                if p[3] and x0 - 2 <= x <= x1 + 2 + (16 if name in HOUSES else 0) or p[3] and name in HOUSES: sheet[top + y - y0][col * 16 + x - (x0 - shift)] = tuple(p)
    return sheet


if __name__ == '__main__':
    sheet = cells()
    save(OUTPUT, sheet)
    print('%s : %d x %d' % (os.path.relpath(OUTPUT, os.path.dirname(HERE)), len(sheet[0]), len(sheet)))
