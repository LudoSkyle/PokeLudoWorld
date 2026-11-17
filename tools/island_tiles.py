#!/usr/bin/env python3
"""Fabrique assets/levels/island.png : les tuiles de l'île que environments.png n'a pas.

    python3 tools/island_tiles.py

Rien n'est dessiné à la main : les trois premières rangées sont dérivées de
environments.png, les suivantes sont découpées dans les planches de assets/levels/sources/
(que le jeu ne lit jamais directement) et recalées sur la grille. Relancer le script
redonne exactement la même planche. Sa disposition est fixe (cases de 16 px, sans marge) :

    rangée 0, colonnes 0..15   planche de ponton, selon ses côtés à rambarde
                               (gauche = 1, droite = 2, haut = 4, bas = 8, additionnés)
    rangée 1, colonnes 0..3    bout de ponton posé sur la rive, bout en haut
                               (rambarde gauche = 1, droite = 2)
    rangée 1, colonnes 4..7    idem, bout en bas
    rangée 2, colonnes 0..3    bout à gauche (rambarde haut = 1, bas = 2)
    rangée 2, colonnes 4..7    bout à droite
    rangée 2, colonnes 8..11   petits rochers dans l'eau (les cailloux de terre, cernés d'écume)
    rangée 2, colonne 12       planches tournées d'un quart (ancien escalier de côté, plus posé)

    rangées 3-4, colonnes 0-1    escalier au bas d'un plateau (la rangée 4 est la case de bord ;
                                 la rangée 3, le haut des poteaux, déborde sur le dessus)
    rangées 3-4, colonnes 2-3    escalier en haut d'un plateau (rangée 3 : la case de bord)
    rangées 3-4, colonnes 4-5    escalier sur le bord gauche (colonne 4 : la case de bord)
    rangées 3-4, colonnes 6-7    escalier sur le bord droit (colonne 7 : la case de bord)
    rangées 3-5, colonnes 11-12  parasol bleu ; colonnes 13-14, parasol orange (rangée 5 : le pied)
    rangées 3-4, colonne 15      serviette claire ; rangées 5-6, colonne 15, serviette bleue
    rangées 5-6, colonne 0       caisses empilées ; rangée 6, colonne 1 : une caisse
    rangées 5-6, colonne 2       pot de fleurs
    rangée 6, colonne 3          Poké Ball posée au sol (un objet à ramasser)
    rangées 5-6, colonnes 4-5    banc de bois vu de face (rangée 5 : le haut du dossier)
    rangées 3-5, colonne 8       banc de bois de profil, dossier à gauche ; colonne 9, dossier à droite
                                 (rangée 3 : deux pixels qui dépassent ; le banc tient sur deux cases)

Pourquoi : dans environments.png, le ponton n'a de rambarde que sur ses flancs gauche et
droit, pas de pièce d'angle, et aucune planche pour finir proprement sur le sable ; il n'a
ni escalier à poteaux, ni parasol, ni objet posé au sol. Ses bancs de bois, eux, y sont
mais posés hors grille : ils sont recalés ici.
"""
import os
import struct
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEVELS = os.path.join(ROOT, 'src', 'main', 'kotlin', 'fr', 'skyle', 'pokeludoworld', 'assets', 'levels')
SOURCE = os.path.join(LEVELS, 'environments.png')
OUTPUT = os.path.join(LEVELS, 'island.png')
SOURCES = os.path.join(LEVELS, 'sources')
COLUMNS, ROWS = 16, 7

# Ce qui est découpé dans les planches sources :
#   (planche, (x, y, largeur, hauteur) dans la planche, transformation,
#    (colonne, rangée) du bloc dans island.png, (colonnes, rangées) du bloc, calage dans le bloc)
TOWN = 'town_compilation.png'
INDOOR = 'public_indoor.png'
ATLAS = 'environments.png'      # l'atlas du jeu lui-même : ses bancs de bois sont posés hors grille
STAIRS = (TOWN, (392, 988, 32, 22))     # poteaux bruns, marches grises : 2 cases de large
PIECES = [
    (STAIRS, None, (0, 3), (2, 2), 'bottom'),                       # la dernière marche au ras du sol d'en bas
    (STAIRS, 'flip', (2, 3), (2, 2), 'top'),                        # vu d'en haut : la dernière marche est au nord
    (STAIRS, 'right', (4, 3), (2, 2), 'left'),                      # quart de tour à droite : la dernière marche à gauche
    (STAIRS, 'left', (6, 3), (2, 2), 'right'),
    ((TOWN, (1568, 983, 32, 41)), None, (11, 3), (2, 3), 'bottom'),       # parasol bleu, avec son ombre
    ((TOWN, (1568, 1031, 32, 41)), None, (13, 3), (2, 3), 'bottom'),      # parasol orange
    ((TOWN, (1601, 994, 15, 29)), None, (15, 3), (1, 2), 'center'),       # serviette claire
    ((TOWN, (1601, 1026, 15, 29)), None, (15, 5), (1, 2), 'center'),      # serviette bleue
    ((TOWN, (770, 1029, 12, 27)), None, (0, 5), (1, 2), 'bottom'),        # caisses empilées
    ((TOWN, (754, 1041, 12, 15)), None, (1, 6), (1, 1), 'bottom'),        # une caisse
    ((TOWN, (752, 1017, 16, 23)), None, (2, 5), (1, 2), 'bottom'),        # pot de fleurs
    ((INDOOR, (899, 35, 9, 9)), None, (3, 6), (1, 1), 'center'),          # Poké Ball posée au sol : un objet à ramasser
    ((ATLAS, (1121, 619, 32, 22)), None, (4, 5), (2, 2), 'bottom'),       # banc de bois vu de face, dossier au fond
    ((ATLAS, (1089, 651, 14, 34)), None, (8, 3), (1, 3), 'bottom'),       # banc de bois de profil, dossier à gauche
    ((ATLAS, (1107, 651, 14, 34)), None, (9, 3), (1, 3), 'bottom'),       # banc de bois de profil, dossier à droite
]
RAIL = 4                      # largeur, en pixels, de la rambarde reprise sur le flanc du ponton
FOAM = (190, 226, 244, 255)   # l'écume au pied des rochers de l'atlas
# Les bancs de l'atlas sont cernés de presque noir : à côté des tuiles de la Route 1, cernées de brun, ils ressortent trop
# (Ludovic, 17/11/2026). Leur cerne et son ombre prennent deux bruns du bois.
SOFT = {(19, 37, 46): (98, 80, 54), (45, 45, 45): (120, 100, 66)}


def load(path):
    """Décode un PNG 8 bits (RVBA, RVB ou palette) en lignes de pixels RVBA."""
    data = open(path, 'rb').read()
    pos, idat, palette, alpha = 8, b'', None, None
    while pos < len(data):
        length, = struct.unpack('>I', data[pos:pos + 4])
        kind, chunk = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + length]
        if kind == b'IHDR': width, height, depth, colour = struct.unpack('>IIBB', chunk[:10])
        elif kind == b'IDAT': idat += chunk
        elif kind == b'PLTE': palette = chunk
        elif kind == b'tRNS': alpha = chunk
        pos += 12 + length
    assert depth == 8, 'PNG 8 bits attendu'
    bpp = {6: 4, 2: 3, 3: 1}[colour]
    raw = zlib.decompress(idat)
    stride = width * bpp + 1
    previous, rows = bytearray(width * bpp), []
    for y in range(height):
        mode, line = raw[y * stride], bytearray(raw[y * stride + 1:(y + 1) * stride])
        for i in range(len(line)):
            a = line[i - bpp] if i >= bpp else 0
            b = previous[i]
            c = previous[i - bpp] if i >= bpp else 0
            if mode == 1: line[i] = (line[i] + a) & 255
            elif mode == 2: line[i] = (line[i] + b) & 255
            elif mode == 3: line[i] = (line[i] + (a + b) // 2) & 255
            elif mode == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else (b if pb <= pc else c))) & 255
        previous = line
        if colour == 6: rows.append([tuple(line[i:i + 4]) for i in range(0, len(line), 4)])
        elif colour == 2: rows.append([tuple(line[i:i + 3]) + (255,) for i in range(0, len(line), 3)])
        else: rows.append([tuple(palette[v * 3:v * 3 + 3]) + ((alpha[v] if alpha and v < len(alpha) else 255),) for v in line])
    return width, height, rows


def save(path, rows):
    """Écrit des lignes de pixels RVBA dans un PNG."""
    raw = b''.join(b'\0' + bytes(v for pixel in row for v in pixel) for row in rows)
    def chunk(kind, body): return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body) & 0xffffffff)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', len(rows[0]), len(rows), 8, 6, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


def cells(atlas):
    """Les cases de la planche : {(colonne, rangée): 16 lignes de 16 pixels RVBA}."""
    def tile(ax, ay): return [[atlas[1 + ay * 16 + y][1 + ax * 16 + x] for x in range(16)] for y in range(16)]   # l'atlas a une marge d'un pixel
    def turned(t): return [[t[15 - x][y] for x in range(16)] for y in range(16)]                                 # quart de tour à droite
    planks, left, right = tile(48, 22), tile(47, 22), tile(49, 22)
    top, bottom = turned(left), turned(right)
    outline = left[8][0]                       # le trait sombre qui cerne le ponton

    def deck(rails, end=None):
        t = [row[:] for row in planks]
        near, far = range(RAIL), range(16 - RAIL, 16)
        if 'L' in rails:
            for y in range(16):
                for x in near: t[y][x] = left[y][x]
        if 'R' in rails:
            for y in range(16):
                for x in far: t[y][x] = right[y][x]
        if 'T' in rails:
            for y in near: t[y] = top[y][:]
        if 'B' in rails:
            for y in far: t[y] = bottom[y][:]
        # les rambardes d'abord, le coin ensuite : là où deux rambardes se croisent, celle du flanc garde la main
        if 'L' in rails and ('T' in rails or 'B' in rails):
            for y in (list(near) if 'T' in rails else []) + (list(far) if 'B' in rails else []):
                for x in near: t[y][x] = left[y][x]
        if 'R' in rails and ('T' in rails or 'B' in rails):
            for y in (list(near) if 'T' in rails else []) + (list(far) if 'B' in rails else []):
                for x in far: t[y][x] = right[y][x]
        if end == 'T': t[0] = [outline] * 16
        if end == 'B': t[15] = [outline] * 16
        if end == 'L':
            for y in range(16): t[y][0] = outline
        if end == 'R':
            for y in range(16): t[y][15] = outline
        return t

    def rock(k):
        source = tile(39 + k, 29)
        t = [row[:] for row in source]
        for y in range(5, 16):
            for x in range(16):
                if source[y][x][3] > 127: continue
                around = ((x + 1, y), (x - 1, y), (x, y - 1), (x + 1, y - 1), (x - 1, y - 1))
                if any(0 <= a < 16 and source[b][a][3] > 127 for a, b in around): t[y][x] = FOAM
        return t

    out = {}
    for mask in range(16): out[(mask, 0)] = deck({s for i, s in enumerate('LRTB') if mask >> i & 1})
    for e, end in enumerate('TB'):
        for mask in range(4): out[(e * 4 + mask, 1)] = deck({s for i, s in enumerate('LR') if mask >> i & 1}, end)
    for e, end in enumerate('LR'):
        for mask in range(4): out[(e * 4 + mask, 2)] = deck({s for i, s in enumerate('TB') if mask >> i & 1}, end)
    for k in range(4): out[(8 + k, 2)] = rock(k)
    out[(12, 2)] = turned(planks)
    return out


def pieces(sheets):
    """Les blocs découpés dans les planches sources : {(colonne, rangée): 16 lignes de 16 pixels}.

    `sheets` donne les pixels d'une planche par son nom de fichier."""
    out = {}
    for (name, (x0, y0, w, h)), transform, (col, row), (cols, rows), align in PIECES:
        source = sheets(name)
        art = [[source[y0 + y][x0 + x] for x in range(w)] for y in range(h)]
        if name == ATLAS: art = [[(SOFT[p[:3]] + (p[3],)) if tuple(p[:3]) in SOFT else p for p in row] for row in art]
        if transform == 'flip': art = art[::-1]
        if transform == 'right': art = [[art[h - 1 - x][y] for x in range(h)] for y in range(w)]
        if transform == 'left': art = [[art[x][w - 1 - y] for x in range(h)] for y in range(w)]
        h, w = len(art), len(art[0])
        assert w <= cols * 16 and h <= rows * 16, (name, w, h)
        ox = 0 if align == 'left' else (cols * 16 - w if align == 'right' else (cols * 16 - w) // 2)
        oy = 0 if align == 'top' else (rows * 16 - h if align == 'bottom' else (rows * 16 - h) // 2)
        block = [[(0, 0, 0, 0)] * (cols * 16) for _ in range(rows * 16)]
        for y in range(h):
            for x in range(w):
                if art[y][x][3] > 0: block[oy + y][ox + x] = tuple(art[y][x])
        for j in range(rows):
            for i in range(cols):
                assert (col + i, row + j) not in out, (name, col + i, row + j)
                out[(col + i, row + j)] = [block[j * 16 + y][i * 16:(i + 1) * 16] for y in range(16)]
    return out


_loaded = {}
def source_sheet(name):
    if name not in _loaded: _loaded[name] = load(SOURCE if name == ATLAS else os.path.join(SOURCES, name))[2]
    return _loaded[name]


def all_cells(atlas=None):
    """Toute la planche : les cases dérivées de l'atlas, puis celles découpées dans les sources."""
    if atlas is None: atlas = load(SOURCE)[2]
    _loaded[ATLAS] = atlas          # les pièces prises dans l'atlas le relisent sans le redécoder
    made = cells(atlas)
    cut = pieces(source_sheet)
    assert not set(made) & set(cut)
    made.update(cut)
    return made


def sheet(atlas):
    made = all_cells(atlas)
    rows = [[(0, 0, 0, 0)] * (COLUMNS * 16) for _ in range(ROWS * 16)]
    for (cx, cy), t in made.items():
        for y in range(16):
            for x in range(16): rows[cy * 16 + y][cx * 16 + x] = tuple(t[y][x])
    return rows


if __name__ == '__main__':
    save(OUTPUT, sheet(load(SOURCE)[2]))
    print('écrit', os.path.relpath(OUTPUT, ROOT))
