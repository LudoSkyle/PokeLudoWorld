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
    'bellossom': ('hgss_overworld_gen2.png', 10, 2),   # Joliflor : au bout de la troisième rangée, dans une colonne plus étroite que les autres
}
# Ceux qu'on pose au sol comme des personnages : en plus, une planche de PNJ (assets/characters/pkmn_<nom>.png, quatre
# rangées — bas, gauche, droite, haut — de quatre images, voir `character`).
STANDING = ('shellder', 'corphish', 'bellossom')
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
            pixel = sheet[y0 + y][x0 + x] if x0 + x < len(sheet[y0 + y]) else sheet[y0][x0]          # la dernière colonne d'une planche peut être rognée de deux pixels
            line.append((0, 0, 0, 0) if pixel[:3] == backdrop else tuple(pixel[:3]) + (255,))
        block.append(line)
    return block


# ============================================================ toutes les espèces des planches HGSS
# Une planche HGSS range ses espèces dans l'ordre du Pokédex, un bloc de 64 x 128 chacune, avec des blocs en plus :
#   - `extra` : les blocs qui suivent celui de l'espèce et ne sont pas elle par défaut — sa femelle (point rose), ses
#     autres formes (les 27 autres Zarbi, les capes de Cheniti, Motisma...) ; on les saute ;
#   - `tall` : un gros Pokémon, sur quatre blocs — dos, face, gauche, droite —, deux images de 64 x 64 par bloc ;
#   - `wide` : un gros Pokémon de la planche de la 3e génération, sur deux blocs côte à côte (128 x 128) : quatre
#     rangées — face, dos, gauche, droite — de deux images de 64 x 32.
# Les comptes tombent juste : 153, 144, 142 et 141 blocs.
SHEETS = [
    dict(file='hgss_overworld_gen1.png', columns=15, first=1, last=151, extra={3: 1, 25: 1}, tall=(), wide=()),
    dict(file='hgss_overworld_gen2.png', columns=11, first=152, last=251, extra={154: 1, 172: 1, 201: 27, 202: 1, 208: 4, 214: 1}, tall=(208, 249, 250), wide=()),
    dict(file='hgss_overworld_gen3.png', columns=13, first=252, last=386, extra={386: 3}, tall=(), wide=(321, 382, 383, 384)),
    dict(file='hgss_overworld_gen4.png', columns=11, first=387, last=493, extra={412: 2, 413: 2, 415: 1, 422: 1, 423: 1, 449: 1, 450: 1, 479: 5, 487: 4, 492: 1}, tall=(483, 484, 486, 487, 493), wide=()),
]
ATLAS = os.path.join(POKEMON, 'overworld.png')          # toutes les espèces de taille ordinaire, une case de 64 x 128 chacune, à la place de son numéro
ATLAS_COLUMNS = 25
NATIONAL = os.path.join(ROOT, 'src', 'main', 'kotlin', 'fr', 'skyle', 'pokeludoworld', 'resources', 'pokedex', 'national.tsv')


def raw(sheet, column, row, w=64, h=128):
    """Le bloc tel quel, fond compris, complété là où la planche est rognée."""
    x0, y0 = column * (BLOCK_W + 1), row * (BLOCK_H + 1)
    return [[tuple(sheet[y0 + y][x0 + x][:3]) if y0 + y < len(sheet) and x0 + x < len(sheet[y0 + y]) else None for x in range(w)] for y in range(h)]


def clear(block):
    """Le fond du bloc (sa couleur la plus fréquente) et les points de couleur des variantes deviennent transparents."""
    counts = {}
    for line in block:
        for p in line:
            if p is not None: counts[p] = counts.get(p, 0) + 1
    backdrop = max(counts, key=counts.get)
    out = [[(0, 0, 0, 0) if p is None or p == backdrop or p in ((0, 128, 255), (255, 0, 255), (255, 255, 255)) else p + (255,) for p in line] for line in block]
    # Un filet de séparation qui déborde dans le bloc (la planche n'est pas toujours calée au pixel) : une ligne ou une
    # colonne du bord faite d'une seule couleur sur plus de la moitié de sa longueur n'est pas le Pokémon.
    height, width = len(out), len(out[0])
    for y in (0, 1, height - 2, height - 1):
        tones = [p for p in out[y] if p[3]]
        if len(tones) > width // 2 and len(set(tones)) <= 2: out[y] = [(0, 0, 0, 0)] * width
    for x in (0, 1, width - 2, width - 1):
        tones = [out[y][x] for y in range(height) if out[y][x][3]]
        if len(tones) > height // 4 and len(set(tones)) <= 2:
            for y in range(height): out[y][x] = (0, 0, 0, 0)
    return out


def big(frames):
    """Un gros Pokémon au format ordinaire, en double : 128 x 256, deux colonnes de quatre images de 64 x 64 — dos, dos, face, face ; gauche, gauche, droite, droite."""
    up, down, left, right = frames
    out = [[(0, 0, 0, 0)] * 128 for _ in range(256)]
    for column, pairs in enumerate(((up, down), (left, right))):
        for k, pair in enumerate(pairs):
            for f, frame in enumerate(pair):
                y0 = (k * 2 + f) * 64 + 64 - len(frame)          # calé en bas de sa case
                for y, line in enumerate(frame):
                    out[y0 + y][column * 64:column * 64 + 64] = line
    return out


def everyone():
    """Découpe toutes les espèces des planches HGSS : {numéro: bloc ordinaire} et {numéro: gros bloc}."""
    small, large = {}, {}
    for spec in SHEETS:
        sheet = load(os.path.join(POKEMON, 'sources', spec['file']))[2]
        slot = 0
        for number in range(spec['first'], spec['last'] + 1):
            def at(k): return ((slot + k) % spec['columns'], (slot + k) // spec['columns'])
            if number in spec['tall']:
                parts = [clear(raw(sheet, *at(k))) for k in range(4)]
                large[number] = big([(part[:64], part[64:]) for part in parts])
                slot += 4
            elif number in spec['wide']:
                c, r = at(0)
                area = clear(raw(sheet, c, r, w=129, h=128))
                rows = [([line[:64] for line in area[k * 32:k * 32 + 32]], [line[65:129] for line in area[k * 32:k * 32 + 32]]) for k in range(4)]
                large[number] = big([rows[1], rows[0], rows[2], rows[3]])
                slot += 2
            else:
                small[number] = clear(raw(sheet, *at(0)))
                slot += 1
            slot += spec['extra'].get(number, 0)
    return small, large


if __name__ == '__main__':
    sheets = {}
    # toutes les espèces des planches : une planche pour les tailles ordinaires, un fichier par gros Pokémon
    ids = {}
    with open(NATIONAL, encoding='utf-8') as f:
        for line in f:
            if not line.startswith('#'): ids[int(line.split('\t')[0])] = line.split('\t')[1]
    small, large = everyone()
    rows_needed = (max(ids) - 1) // ATLAS_COLUMNS + 1
    atlas = [[(0, 0, 0, 0)] * (ATLAS_COLUMNS * 64) for _ in range(rows_needed * 128)]
    for number, block in small.items():
        x0, y0 = ((number - 1) % ATLAS_COLUMNS) * 64, ((number - 1) // ATLAS_COLUMNS) * 128
        for y in range(128): atlas[y0 + y][x0:x0 + 64] = block[y]
    last = max((n - 1) // ATLAS_COLUMNS for n in small) + 1
    save(ATLAS, atlas[:last * 128])
    for number, block in large.items(): save(os.path.join(POKEMON, 'overworld', ids[number] + '.png'), block)
    print('%d espèces dans %s, %d gros Pokémon à part : %s' % (len(small), os.path.relpath(ATLAS, ROOT), len(large), ', '.join(ids[n] for n in sorted(large))))
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
