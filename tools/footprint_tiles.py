#!/usr/bin/env python3
"""Fabrique assets/levels/footprints.png : les traces de pas laissées dans le sable.

    python3 tools/footprint_tiles.py

La planche fait 64 x 8 : huit cases de 8 px, une par (direction, pied). Les cases vont
par paires, dans l'ordre des rangées du sprite sheet des personnages — bas, gauche,
droite, haut — et dans chaque paire vient d'abord le pied le plus haut ou le plus à
gauche à l'écran :

    colonnes 0-1   marche vers le bas    (pied de gauche, pied de droite)
    colonnes 2-3   marche vers la gauche (pied du haut, pied du bas)
    colonnes 4-5   marche vers la droite (pied du haut, pied du bas)
    colonnes 6-7   marche vers le haut   (pied de gauche, pied de droite)

Tout vient d'une seule forme, EMPREINTE, tournée et retournée : une marque de 3 x 6
pixels pour la marche verticale, la même d'un quart de tour (6 x 3) pour l'horizontale.
Elle est dessinée en **noir plein** : la transparence ne vient pas d'ici mais du
`modulate` de Footprint.kt, qui assombrit le sable d'environ 20 % puis s'efface.
Relancer le script redonne exactement la même planche.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from island_tiles import save  # noqa: E402  — le même écrivain de PNG que la planche de l'île

OUTPUT = os.path.join(
    os.path.dirname(HERE), 'src', 'main', 'kotlin', 'fr', 'skyle', 'pokeludoworld',
    'assets', 'levels', 'footprints.png',
)
CELL = 8
INK = (0, 0, 0, 255)
CLEAR = (0, 0, 0, 0)

# Un pied qui marche vers le bas : talon étroit en haut, plante large, orteils en bas.
EMPREINTE = [
    '.X.',
    'XX.',
    'XXX',
    'XXX',
    'XXX',
    '.X.',
]


def mirror_x(shape):
    return [row[::-1] for row in shape]


def mirror_y(shape):
    return shape[::-1]


def turn(shape):
    """Un quart de tour à droite."""
    height, width = len(shape), len(shape[0])
    return [''.join(shape[height - 1 - x][y] for x in range(height)) for y in range(width)]


def columns():
    """Les huit cases, dans l'ordre de la planche."""
    down = EMPREINTE
    up = mirror_y(down)
    right = turn(down)
    left = mirror_x(right)
    return [
        down, mirror_x(down),          # vers le bas : pied de gauche, pied de droite
        left, mirror_y(left),          # vers la gauche : pied du haut, pied du bas
        right, mirror_y(right),        # vers la droite : pied du haut, pied du bas
        up, mirror_x(up),              # vers le haut : pied de gauche, pied de droite
    ]


def sheet():
    shapes = columns()
    rows = [[CLEAR] * (CELL * len(shapes)) for _ in range(CELL)]
    for index, shape in enumerate(shapes):
        height, width = len(shape), len(shape[0])
        # L'empreinte est centrée dans sa case : c'est son centre que le jeu pose sur la case de sable.
        ox, oy = index * CELL + (CELL - width) // 2, (CELL - height) // 2
        for y in range(height):
            for x in range(width):
                if shape[y][x] == 'X':
                    rows[oy + y][ox + x] = INK
    return rows


if __name__ == '__main__':
    save(OUTPUT, sheet())
    print('écrit', OUTPUT)
