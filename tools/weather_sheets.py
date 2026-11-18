#!/usr/bin/env python3
"""Fabrique les planches de météo de assets/weather/ à partir de celles de Pokémon Essentials.

    python3 tools/weather_sheets.py

Les images du kit (assets/weather/sources/, que le jeu ne lit jamais) sont dessinées pour
des cases de 32 px, en **pixels doublés** : chaque bloc de 2 x 2 est d'une seule couleur.
Nos cases font 16 px. On garde donc un pixel par bloc — une réduction de moitié **sans
aucune perte**, qui remet chaque goutte, chaque flocon et chaque nappe sur notre grille.

Le script refuse de continuer si un bloc n'est pas uniforme : ce serait une planche qui
ne suit pas cette règle, et la réduire l'abîmerait. Relancer le script redonne exactement
les mêmes fichiers.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from island_tiles import load, save  # noqa: E402  — les mêmes lecteur et écrivain de PNG

WEATHER = os.path.join(
    os.path.dirname(HERE), 'src', 'main', 'kotlin', 'fr', 'skyle', 'pokemonmirage', 'assets', 'weather',
)
SOURCES = os.path.join(WEATHER, 'sources')
CLEAR = (0, 0, 0, 0)


def halve(name):
    width, height, rows = load(os.path.join(SOURCES, name))
    assert width % 2 == 0 and height % 2 == 0, (name, width, height)
    out = []
    for y in range(0, height, 2):
        line = []
        for x in range(0, width, 2):
            block = {p if p[3] > 0 else CLEAR for p in (rows[y][x], rows[y][x + 1], rows[y + 1][x], rows[y + 1][x + 1])}
            assert len(block) == 1, '%s : le bloc (%d, %d) n\'est pas uniforme' % (name, x, y)
            line.append(block.pop())
        out.append(line)
    save(os.path.join(WEATHER, name), out)
    return width // 2, height // 2


if __name__ == '__main__':
    for name in sorted(os.listdir(SOURCES)):
        if name.endswith('.png'):
            print('%-20s %3d x %d' % ((name,) + halve(name)))
