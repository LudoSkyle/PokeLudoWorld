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
    'hoppip': ('hgss_overworld_gen2.png', 4, 3),       # Granivol
    'skiploom': ('hgss_overworld_gen2.png', 5, 3),     # Floravol
    'jumpluff': ('hgss_overworld_gen2.png', 6, 3),     # Cotovol
    'shellder': ('hgss_overworld_gen1.png', 1, 6),     # Kokiyas
    'corphish': ('hgss_overworld_gen3.png', 12, 6),    # Écrapince
}
# Ceux qu'on pose au sol comme des personnages : en plus, une planche de PNJ (assets/characters/pkmn_<nom>.png, quatre
# rangées — bas, gauche, droite, haut — de quatre images, voir `character`).
STANDING = ('shellder', 'corphish')
# Les planches HGSS n'ont pas tout le monde. Joliflor vient de son icône du kit Essentials (deux images de face, pixels
# doublés : une sur deux suffit) — il n'a donc qu'une face, quel que soit le côté d'où on lui parle.
ICONS = {'bellossom': 'essentials_icon_bellossom.png'}
CHARACTERS = os.path.join(ROOT, 'src', 'main', 'kotlin', 'fr', 'skyle', 'pokeludoworld', 'assets', 'characters')


def character(rows_of_frames):
    """La planche de PNJ faite de quatre rangées de deux images de 32 x 32 : chaque rangée les alterne sur quatre colonnes."""
    # Le jeu dessine un PNJ à demi-échelle, centré quatre pixels au-dessus du milieu de sa case (npc.tscn) : une
    # planche de personnage est au double. Le Pokémon y est donc doublé lui aussi (64 x 64), dans une case de 64 x 80
    # dont les seize rangées du bas restent vides : ses pieds tombent au bas de la case du jeu, à la taille des volants.
    sheet = [[(0, 0, 0, 0)] * 256 for _ in range(320)]
    for r, (a, b) in enumerate(rows_of_frames):
        for c, frame in enumerate((a, b, a, b)):
            for y in range(64):
                for x in range(64): sheet[r * 80 + y][c * 64 + x] = frame[y // 2][x // 2]
    return sheet


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
        block = cut(sheets[source], column, row)
        save(out, block)
        print('écrit', os.path.relpath(out, ROOT))
        if name in STANDING:
            def frame(x0, y0): return [line[x0:x0 + 32] for line in block[y0:y0 + 32]]
            out = os.path.join(CHARACTERS, 'pkmn_%s.png' % name)          # le bloc : dos puis face à gauche, gauche puis droite à droite
            save(out, character([(frame(0, 64), frame(0, 96)), (frame(32, 0), frame(32, 32)), (frame(32, 64), frame(32, 96)), (frame(0, 0), frame(0, 32))]))
            print('écrit', os.path.relpath(out, ROOT))
    for name, source in ICONS.items():
        icon = load(os.path.join(POKEMON, 'sources', source))[2]
        frames = [[[tuple(icon[2 * y][2 * (x + 32 * k)]) for x in range(32)] for y in range(32)] for k in (0, 1)]
        out = os.path.join(CHARACTERS, 'pkmn_%s.png' % name)
        save(out, character([tuple(frames)] * 4))
        print('écrit', os.path.relpath(out, ROOT))
