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

# Ceux qu'on pose au sol comme des personnages (leur nom dans national.tsv) : en plus, une planche de PNJ (assets/characters/pkmn_<nom>.png, quatre
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


# ============================================================ toutes les espèces des planches HGSS
# Une planche HGSS range ses espèces dans l'ordre du Pokédex, un bloc de 64 x 128 chacune, avec des blocs en plus :
#   - `extra` : les blocs qui suivent celui de l'espèce et ne sont pas elle par défaut — sa femelle (point rose), ses
#     autres formes (les 27 autres Zarbi, les capes de Cheniti, Motisma...) ; on les saute ;
#   - `tall` : un gros Pokémon, sur quatre blocs — dos, face, gauche, droite —, deux images de 64 x 64 par bloc ;
#   - `wide` : un gros Pokémon de la planche de la 3e génération, sur deux blocs côte à côte (128 x 128) : quatre
#     rangées — face, dos, gauche, droite — de deux images de 64 x 32 ;
#   - `sideways` : un crabe, qui marche de côté — ses deux colonnes sont échangées (les profils à gauche, le dos et
#     la face à droite) ; on les remet dans l'ordre des autres.
# Un bloc ordinaire est découpé par son contenu (`split`), puis chaque paire d'images recentrée dans sa case (`settle`).
# Les comptes tombent juste : 153, 144, 142 et 141 blocs.
SHEETS = [
    dict(file='hgss_overworld_gen1.png', columns=15, first=1, last=151, extra={3: 1, 25: 1}, tall=(), wide=(), sideways=(98, 99)),
    dict(file='hgss_overworld_gen2.png', columns=11, first=152, last=251, extra={154: 1, 172: 1, 201: 27, 202: 1, 208: 4, 214: 1}, tall=(208, 249, 250), wide=()),
    dict(file='hgss_overworld_gen3.png', columns=13, first=252, last=386, extra={386: 3}, tall=(), wide=(321, 382, 383, 384)),
    dict(file='hgss_overworld_gen4.png', columns=11, first=387, last=493, extra={412: 2, 413: 2, 415: 1, 422: 1, 423: 1, 449: 1, 450: 1, 479: 5, 487: 4, 492: 1}, tall=(483, 484, 486, 487, 493), wide=()),
]
NATIONAL = os.path.join(ROOT, 'src', 'main', 'kotlin', 'fr', 'skyle', 'pokeludoworld', 'resources', 'pokedex', 'national.tsv')


def grid(sheet):
    """Où commence vraiment chaque bloc : [[(x, y) de chaque bloc d'une rangée] pour chaque rangée], entre les filets.

    Les planches ne sont **pas** sur une grille régulière : une colonne de 63 pixels dans celle de la 1re génération
    — et même de 61 sur ses deux dernières rangées seulement —, des rangées de 129 à 131 dans celle de la 2e, plus
    hautes encore à côté d'un gros Pokémon. Compter 65 par colonne et 129 par rangée coupe de travers des centaines
    d'espèces (Ludovic, 17/11/2026 : « après le numéro 200, il y en a énormément de mal découpés »). On lit donc
    les filets : les rangées sur toute la largeur, puis les colonnes **rangée par rangée**, puis le haut de chaque
    bloc sur sa propre largeur. Dans un bloc plus grand, les images restent calées en haut à gauche, au pas de 32.
    """
    height, width = len(sheet), len(sheet[0])
    line = tuple(sheet[10][64][:3])
    def is_line(x, y): return tuple(sheet[y][x][:3]) == line
    def spans(cuts, end, least):
        out, prev = [], -1
        for c in cuts + [end]:
            if c - prev - 1 >= least: out.append(prev + 1)
            prev = c
        return out
    rows = spans([y for y in range(height) if sum(1 for x in range(width) if is_line(x, y)) > width * 0.6], height, 60)
    while rows[-1] + 2 * BLOCK_H + 1 <= height + 8: rows.append(rows[-1] + BLOCK_H + 1)          # la dernière rangée, sous le dernier filet
    out = []
    for r, y0 in enumerate(rows):
        tall = (rows[r + 1] - 1 if r + 1 < len(rows) else height) - y0          # sa hauteur, jusqu'au filet suivant : de 128 à 135
        band = range(y0 + 8, min(y0 + 120, height))
        columns = spans([x for x in range(width) if sum(1 for y in band if is_line(x, y)) > len(band) * 0.6], width, 30)
        blocks = []
        for k, x0 in enumerate(columns):
            span = range(x0, min(x0 + 60, width))
            tops = [y for y in range(max(0, y0 - 8), min(height, y0 + 8)) if sum(1 for x in span if is_line(x, y)) > len(span) * 0.9]
            room = (columns[k + 1] - 1 if k + 1 < len(columns) else width) - x0          # sa largeur, jusqu'au filet suivant : parfois 61 ou 63
            top = tops[-1] + 1 if tops else y0
            blocks.append((x0, top, room, min(tall + y0 - top, 136)))          # (sous la dernière rangée il y a les crédits : on ne descend pas plus bas)
        out.append(blocks)
    return out


def raw(sheet, x0, y0, room=64, w=64, h=128):
    """Le bloc qui commence en (x0, y0), tel quel, fond compris ; vide au-delà de sa largeur `room` (le filet suivant, le bord de la planche)."""
    return [[tuple(sheet[y0 + y][x0 + x][:3]) if y0 + y < len(sheet) and x0 + x < len(sheet[y0 + y]) and x < room else None for x in range(w)] for y in range(h)]


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
    for y in range(100, height):          # sous le bloc, un filet d'une autre couleur ou le bandeau des crédits : tout ce qui suit n'est plus le bloc
        tones = [p for p in out[y] if p[3]]
        if len(tones) > width * 0.7 and len(set(tones)) <= 2:
            for below in range(y, height): out[below] = [(0, 0, 0, 0)] * width
            break
    for x in (0, 1, width - 2, width - 1):
        tones = [out[y][x] for y in range(height) if out[y][x][3]]
        if len(tones) > height // 4 and len(set(tones)) <= 2:
            for y in range(height): out[y][x] = (0, 0, 0, 0)
    return out


def pieces(block, slot, count):
    """Les sprites d'un morceau de planche, chacun avec ses pixels : [{(x, y): couleur}], rangés par `slot`.

    On ne coupe pas au pas : on repère les morceaux d'un seul tenant, on donne chaque gros morceau à la case que dit
    `slot(cx, cy)` d'après son centre, et chaque petit morceau détaché (une étincelle, un ruban) au gros le plus proche.
    """
    height, width = len(block), len(block[0])
    solid = {(x, y): block[y][x] for y in range(height) for x in range(width) if block[y][x][3]}
    left, parts = set(solid), []
    while left:
        seed = left.pop(); part, todo = {seed}, [seed]
        while todo:
            x, y = todo.pop()
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    q = (x + i, y + j)
                    if q in left: left.discard(q); part.add(q); todo.append(q)
        parts.append(part)
    def home(part): return slot(sum(x for x, _ in part) / len(part), sum(y for _, y in part) / len(part))
    sprites = [dict() for _ in range(count)]
    big_parts = [(part, home(part)) for part in parts if len(part) >= 30]
    for part, k in big_parts:
        for q in part: sprites[k][q] = solid[q]
    for part in parts:
        if len(part) >= 30: continue
        near = min(big_parts, key=lambda b: min(abs(x - a) + abs(y - c) for x, y in part for a, c in b[0]), default=None)
        k = near[1] if near and min(abs(x - a) + abs(y - c) for x, y in part for a, c in near[0]) <= 8 else home(part)
        for q in part: sprites[k][q] = solid[q]
    return sprites


def lanes(area):
    """Les huit sprites d'un bloc double (gros Pokémon de la 3e génération) : quatre rangées de deux, rangée par rangée.

    Ils y sont serrés jusqu'à se toucher (Groudon, Rayquaza) : les morceaux d'un seul tenant ne les séparent plus. On
    cherche donc où couper — la colonne et les trois rangées **les moins remplies** près du milieu et des quarts — et
    chaque pixel va à la case où il tombe.
    """
    height, width = len(area), len(area[0])
    def emptiest(counts, around, reach=7):
        span = range(max(1, int(around) - reach), min(len(counts) - 1, int(around) + reach + 1))
        return min(span, key=lambda k: (counts[k], abs(k - around)))
    across = [sum(1 for y in range(height) if area[y][x][3]) for x in range(width)]
    down = [sum(1 for p in line if p[3]) for line in area]
    used = [y for y in range(height) if down[y]]
    top, bottom = used[0], used[-1] + 1
    cut_x = emptiest(across, width / 2, 14)
    cuts_y = [top] + [emptiest(down, top + (bottom - top) * k / 4) for k in (1, 2, 3)] + [bottom]
    def region(x, y):
        row = next((k for k in range(4) if cuts_y[k] <= y < cuts_y[k + 1]), 3 if y >= cuts_y[3] else 0)
        return row * 2 + (0 if x < cut_x else 1)
    # Un morceau d'un seul tenant va tout entier à la case où il est presque en entier : une queue qui dépasse la coupe
    # suit son corps. S'il est à cheval pour de bon (deux sprites qui se touchent), il est coupé pixel par pixel.
    solid = {(x, y) for y in range(height) for x in range(width) if area[y][x][3]}
    sprites = [dict() for _ in range(8)]
    while solid:
        seed = solid.pop(); part, todo = [seed], [seed]
        while todo:
            x, y = todo.pop()
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    q = (x + i, y + j)
                    if q in solid: solid.discard(q); part.append(q); todo.append(q)
        share = {}
        for x, y in part: share[region(x, y)] = share.get(region(x, y), 0) + 1
        best = max(share, key=share.get)
        whole = share[best] >= len(part) * 0.8
        for x, y in part: sprites[best if whole else region(x, y)][(x, y)] = area[y][x]
    return sprites


def split(block):
    """Les huit sprites d'un bloc ordinaire — colonne de gauche de haut en bas, puis celle de droite.

    Dans la planche, les images ne sont **pas** toujours sur un pas de 32 à l'intérieur du bloc : Caratroc est posé deux
    pixels plus bas (ses pattes tombaient dans l'image d'en dessous), le profil de Suicune déborde d'un pixel sur la
    colonne voisine.
    """
    return pieces(block, lambda cx, cy: (0 if cx < 32 else 4) + min(3, max(0, int(cy // 32))), 8)


def settle_big(directions):
    """Un gros Pokémon : (côté d'une image, sa planche). `directions` = les deux sprites de dos, de face, de gauche, de droite.

    Ses images ne sont sur aucun pas régulier dans la planche : chacune est posée pour elle-même, centrée dans sa case,
    pieds à deux pixels du bas. Le côté de la case est le plus petit de 64 ou 96 où tout tient.
    """
    boxes = [(min(x for x, _ in sp), max(x for x, _ in sp), min(y for _, y in sp), max(y for _, y in sp)) for pair in directions for sp in pair if sp]
    side = 64 if all(b - a < 64 and d - c < 62 for a, b, c, d in boxes) else 96
    cell = [[(0, 0, 0, 0)] * (2 * side) for _ in range(4 * side)]
    for column, (first, second) in enumerate(((0, 1), (2, 3))):
        for k, way in enumerate((first, second)):
            for f, sprite in enumerate(directions[way]):
                if not sprite: continue
                a, b = min(x for x, _ in sprite), max(x for x, _ in sprite)
                d = max(y for _, y in sprite)
                dx, dy = (side - (b - a + 1)) // 2 - a, (side - 3) - d
                for (x, y), colour in sprite.items():
                    cell[(k * 2 + f) * side + y + dy][column * side + x + dx] = colour
    return side, cell


def settle(sprites):
    """Pose les huit sprites dans leurs cases : (côté d'une image, la planche du Pokémon — deux colonnes de quatre images).

    Les deux images d'une même direction gardent leur écart l'une par rapport à l'autre (c'est l'animation), et la paire
    est **centrée** dans sa case, pieds à deux pixels du bas. Des deux, la plus basse est rangée en premier. Si une paire ne tient pas dans 32 x 32, toutes les images
    passent à 64 x 64 : c'est un gros Pokémon.
    """
    pairs = []
    for column in (0, 1):
        for k in (0, 2):
            two = [sprites[column * 4 + k], sprites[column * 4 + k + 1]]
            local = [{(x - column * 32, y - (k + f) * 32): c for (x, y), c in sprite.items()} for f, sprite in enumerate(two)]          # chacun par rapport au coin de sa case d'origine
            # L'image posée au sol passe en premier : c'est elle qu'un Pokémon immobile montre, et il ne doit pas flotter
            # un pixel au-dessus de ses voisins. L'animation est la même, elle part seulement de l'autre temps.
            if all(local) and max(y for _, y in local[0]) < max(y for _, y in local[1]): local.reverse()
            pairs.append((column, k, local))
    spans = []
    for _, _, local in pairs:
        xs = [x for sprite in local for x, _ in sprite]; ys = [y for sprite in local for _, y in sprite]
        spans.append((min(xs), max(xs), min(ys), max(ys)) if xs else (0, 0, 0, 0))
    side = 32 if all(b - a < 32 and d - c < 31 for a, b, c, d in spans) else 64
    cell = [[(0, 0, 0, 0)] * (2 * side) for _ in range(4 * side)]
    for (column, k, local), (a, b, c, d) in zip(pairs, spans):
        dx = (side - (b - a + 1)) // 2 - a
        dy = (side - 2) - d - 1 + 1          # la rangée la plus basse de la paire à deux pixels du bas
        for f, sprite in enumerate(local):
            for (x, y), colour in sprite.items():
                cell[(k + f) * side + y + dy][column * side + x + dx] = colour
    return side, cell


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
        blocks = grid(sheet)
        slot = 0
        for number in range(spec['first'], spec['last'] + 1):
            def at(k):
                """Le bloc de la case `slot + k` : celui de sa rangée qui commence le plus près de sa place théorique. Deux
                blocs d'un gros Pokémon n'ont pas de filet entre eux : le second est alors à sa place théorique."""
                line, column = blocks[(slot + k) // spec['columns']], (slot + k) % spec['columns']
                near = min(line, key=lambda b: abs(b[0] - column * (BLOCK_W + 1)))
                return near if abs(near[0] - column * (BLOCK_W + 1)) <= 12 else (column * (BLOCK_W + 1), line[0][1], BLOCK_W, line[0][3])
            if number in spec['tall']:          # quatre blocs — dos, face, gauche, droite —, deux images l'une sous l'autre dans chacun
                ways = []
                for k in range(4):
                    x0, y0, room, tall = at(k)
                    ways.append(pieces(clear(raw(sheet, x0, y0, room, h=tall)), lambda cx, cy, half=tall / 2: 0 if cy < half else 1, 2))
                large[number] = settle_big(ways)[1]
                slot += 4
            elif number in spec['wide']:        # un seul bloc double : quatre rangées — face, dos, gauche, droite — de deux images côte à côte
                x0, y0, room, tall = at(0)
                room = max(room, 2 * BLOCK_W + 1)
                line = slot // spec['columns']          # sa vraie hauteur : jusqu'à la rangée suivante, ou au bas de la planche (Groudon et Rayquaza font 160 de haut)
                tall = (blocks[line + 1][0][1] - 1 if line + 1 < len(blocks) else len(sheet)) - y0
                eight = lanes(clear(raw(sheet, x0, y0, room, w=room, h=tall)))
                large[number] = settle_big([eight[2:4], eight[0:2], eight[4:6], eight[6:8]])[1]
                slot += 2
            else:
                x0, y0, room, tall = at(0)
                sprites = split(clear(raw(sheet, x0, y0, room, h=tall)))
                if number in spec.get('sideways', ()): sprites = sprites[4:] + sprites[:4]
                side, cell = settle(sprites)
                (small if side == 32 else large)[number] = cell
                slot += 1
            slot += spec['extra'].get(number, 0)
    return small, large


if __name__ == '__main__':
    # Un fichier par espèce, à son nom : 64 x 128 pour une taille ordinaire, 128 x 256 pour un gros Pokémon. Pas de
    # planche commune : chaque espèce se lit, se remplace et se versionne seule.
    ids = {}
    with open(NATIONAL, encoding='utf-8') as f:
        for line in f:
            if not line.startswith('#'): ids[int(line.split('\t')[0])] = line.split('\t')[1]
    small, large = everyone()
    folder = os.path.join(POKEMON, 'overworld')
    for number, block in sorted({**small, **large}.items()): save(os.path.join(folder, ids[number] + '.png'), block)
    # Un fichier qu'on n'écrit plus ne doit pas rester : on le prendrait pour le sprite d'une espèce.
    kept = {ids[n] + '.png' for n in list(small) + list(large)}
    for name in sorted(os.listdir(folder)):
        if name.endswith('.png') and name not in kept:
            for stale in (name, name + '.import'):
                path = os.path.join(folder, stale)
                if os.path.exists(path): os.remove(path); print('retiré', os.path.relpath(path, ROOT))
    print('%d espèces dans %s, dont %d gros Pokémon : %s' % (len(kept), os.path.relpath(folder, ROOT), len(large), ', '.join(ids[n] for n in sorted(large))))
    numbers = {name: number for number, name in ids.items()}
    for name in STANDING:
        block = small[numbers[name]]
        def frame(x0, y0): return [line[x0:x0 + 32] for line in block[y0:y0 + 32]]
        out = os.path.join(CHARACTERS, 'pkmn_%s.png' % name)          # le bloc : dos puis face à gauche, gauche puis droite à droite
        save(out, character([(frame(0, 64), frame(0, 96)), (frame(32, 0), frame(32, 32)), (frame(32, 64), frame(32, 96)), (frame(0, 0), frame(0, 32))]))
        print('écrit', os.path.relpath(out, ROOT))
