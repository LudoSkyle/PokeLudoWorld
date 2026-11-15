#!/usr/bin/env python3
"""Sort des planches de assets/pokemon/sources/ les Pokémon dont le jeu se sert.

    python3 tools/pokemon_overworld.py

Les planches HGSS rangent chaque Pokémon dans un bloc de 64 × 128 : deux colonnes de
quatre images de 32 × 32. Colonne de gauche : deux images de dos (il monte), deux de
face (il descend). Colonne de droite : deux images vers la gauche, deux vers la droite.
Les blocs sont séparés par un filet blanc d'un pixel ; le fond du bloc (vert, ou gris
pour ceux qui volent) devient transparent.

Chaque Pokémon sorti donne assets/pokemon/overworld/<nom>.png, même disposition, sur fond
transparent. Le jeu ne lit jamais les planches sources.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from island_tiles import load, save   # le même lecteur et le même écrivain de PNG

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POKEMON = os.path.join(ROOT, 'src', 'main', 'kotlin', 'fr', 'skyle', 'pokeludoworld', 'assets', 'pokemon')
BLOCK_W, BLOCK_H = 64, 128

# nom du fichier -> (planche, colonne du bloc, rangée du bloc)
WANTED = {
    'wingull': ('hgss_overworld_gen3.png', 0, 2),      # Goélise
    'pelipper': ('hgss_overworld_gen3.png', 1, 2),     # Bekipan
}


def cut(sheet, column, row):
    x0, y0 = column * (BLOCK_W + 1), row * (BLOCK_H + 1)
    backdrop = sheet[y0][x0][:3]
    block = []
    for y in range(BLOCK_H):
        line = []
        for x in range(BLOCK_W):
            pixel = sheet[y0 + y][x0 + x]
            line.append((0, 0, 0, 0) if pixel[:3] == backdrop else tuple(pixel[:3]) + (255,))
        block.append(line)
    return block


if __name__ == '__main__':
    sheets = {}
    for name, (source, column, row) in WANTED.items():
        if source not in sheets: sheets[source] = load(os.path.join(POKEMON, 'sources', source))[2]
        out = os.path.join(POKEMON, 'overworld', name + '.png')
        save(out, cut(sheets[source], column, row))
        print('écrit', os.path.relpath(out, ROOT))
