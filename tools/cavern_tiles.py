#!/usr/bin/env python3
"""Fabrique assets/levels/cavern.png : les tuiles d'une grotte, et les déclare dans le TileSet.

    python3 tools/cavern_tiles.py            # écrit la planche, dit si le TileSet est à jour
    python3 tools/cavern_tiles.py --write    # et réécrit sa source dans resources/tilesets/level.tres

Tout vient de `assets/levels/sources/cliffs_caves.png` (« Evolina mountains, full set », Phyromatical), du kit de
grotte brune : rien n'est redessiné, on découpe sur la grille de 16 et relancer le script redonne le même fichier. Le
jeu ne lit jamais la planche source.

Mêmes conventions que `route_tiles.py` : une matière à bords est un bloc 3 x 3 nommé comme un pavé numérique (`rock7` en
haut à gauche, `rock5` au centre, `rock3` en bas à droite), suivi de ses quatre coins rentrants `i j / k l`. Les noms
sont ceux que le constructeur de cartes attend (`tools/mapgen/build.py`) : `lawn` est ici le sol de la grotte.

Le **vide** — le noir autour d'une grotte — a son bloc à lui, lu à l'envers : ses huit tuiles de bord sont des cases de
vide qui touchent le sol, avec un liseré de roche du côté du sol ; sa case du centre est le noir plein. Ses coins
rentrants sont rangés à l'inverse des autres (`l k / j i`).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from island_tiles import load, save, LEVELS  # noqa: E402

SOURCE = os.path.join(LEVELS, 'sources', 'cliffs_caves.png')
OUTPUT = os.path.join(LEVELS, 'cavern.png')
TILESET = os.path.join(os.path.dirname(LEVELS.rstrip('/')), '..', 'resources', 'tilesets', 'level.tres')
RES = 'res://src/main/kotlin/fr/skyle/pokemonmirage/'
SOURCE_ID, TEXTURE_ID = 15, '10_cavern'
CLEAR = (0, 0, 0, 0)
KEYS = '789456123'

# nom : (bloc 3 x 3 sur la planche, ses coins rentrants, (colonne, rangée) dans cavern.png, idem pour les coins, l'ordre des coins)
BLOCKS = {
    'rock':  ((176, 16), (224, 16), (0, 0), (3, 0), 'ijkl'),          # la paroi : un gradin de roche, sa face en bas
    'void':  ((176, 144), (224, 144), (5, 0), (8, 0), 'lkji'),        # le vide : du noir, un liseré de roche du côté du sol
    'pond':  ((176, 256), (224, 256), (0, 3), (3, 3), 'ijkl'),        # un bassin, dans sa berge de roche
    'earth': ((176, 192), (224, 192), (5, 3), (8, 3), 'ijkl'),        # une plaque de sol sombre : on y marche
}
SINGLES = {'lawn': ((192, 32), (10, 0))}          # le sol de la grotte : le dessus uni de la roche
# ce qui est debout — nom : (x, y sur la planche, largeur, hauteur en cases), sa case haut-gauche dans cavern.png, les cases de son pied
SPRITES = {
    'rock_s':  ((288, 144, 1, 1), (11, 0), [(0, 0)]),
    'pebbleA': ((272, 160, 1, 1), (12, 0), [(0, 0)]),
    'pebbleB': ((272, 176, 1, 1), (13, 0), [(0, 0)]),
    'spire':   ((256, 160, 1, 2), (14, 0), [(0, 0)]),                          # une stalagmite
    'boulder': ((288, 160, 2, 2), (10, 2), [(0, -1), (1, -1), (0, 0), (1, 0)]),
}


def atlas():
    """{nom: (colonne, rangée) dans cavern.png} — tuiles d'une case et, pour ce qui est debout, la case haut-gauche."""
    out = {name: at for name, (_, at) in SINGLES.items()}
    for name, (_, _, at, inner, order) in BLOCKS.items():
        out.update({name + KEYS[j * 3 + i]: (at[0] + i, at[1] + j) for j in range(3) for i in range(3)})
        out.update({name + order[j * 2 + i]: (inner[0] + i, inner[1] + j) for j in range(2) for i in range(2)})
    out.update({name: at for name, (_, at, _) in SPRITES.items()})
    return out


def family(name): return next((b for b in BLOCKS if name.startswith(b) and len(name) == len(b) + 1), name)


def blocks(name):
    """Cette tuile arrête-t-elle ? La paroi (son dessus plat excepté), le vide tout entier, le bassin et sa berge."""
    if family(name) == 'rock': return name[-1] != '5'
    return family(name) in ('void', 'pond')


def cells():
    """{(colonne, rangée): image 16 x 16} de toute la planche."""
    sheet = load(SOURCE)[2]
    def cut(x, y): return [[tuple(sheet[y + j][x + i]) if sheet[y + j][x + i][3] else CLEAR for i in range(16)] for j in range(16)]
    made = {at: cut(*xy) for xy, at in SINGLES.values()}
    for (xy, corners, at, inner, _) in BLOCKS.values():
        for j in range(3):
            for i in range(3): made[(at[0] + i, at[1] + j)] = cut(xy[0] + 16 * i, xy[1] + 16 * j)
        for j in range(2):
            for i in range(2): made[(inner[0] + i, inner[1] + j)] = cut(corners[0] + 16 * i, corners[1] + 16 * j)
    for (x, y, w, h), at, _ in SPRITES.values():
        for j in range(h):
            for i in range(w): made[(at[0] + i, at[1] + j)] = cut(x + 16 * i, y + 16 * j)
    return made


def polygon(feet):
    xs, ys = [c[0] for c in feet], [c[1] for c in feet]
    x0, x1, y0, y1 = min(xs) * 16 - 8, max(xs) * 16 + 8, min(ys) * 16 - 8, max(ys) * 16 + 8
    return 'PackedVector2Array(%d, %d, %d, %d, %d, %d, %d, %d)' % (x0, y0, x1, y0, x1, y1, x0, y1)


def source():
    """Le texte de la source `cavern` du TileSet."""
    at = atlas()
    out = ['[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_cavern"]', 'resource_name = "cavern"', 'texture = ExtResource("%s")' % TEXTURE_ID]
    standing = set()
    for name, ((_, _, w, h), where, feet) in sorted(SPRITES.items(), key=lambda kv: kv[1][1]):          # ce qui est debout : une seule tuile, posée sur la case en bas à gauche de son pied
        key = '%d:%d' % where
        standing |= {(where[0] + i, where[1] + j) for i in range(w) for j in range(h)}
        if (w, h) != (1, 1): out += ['%s/size_in_atlas = Vector2i(%d, %d)' % (key, w, h)]
        out += ['%s/0 = 0' % key, '%s/0/texture_origin = Vector2i(%d, %d)' % (key, -8 * (w - 1), 8 * (h - 1)), '%s/0/y_sort_origin = -1' % key,
                '%s/0/physics_layer_0/polygon_0/points = %s' % (key, polygon(feet))]
    for name, where in sorted(at.items(), key=lambda kv: (kv[1][1], kv[1][0])):
        if where in standing or name in SPRITES: continue
        key, wet = '%d:%d' % where, family(name) == 'pond'
        if blocks(name): out.append('%s/next_alternative_id = 2' % key)
        out.append('%s/0 = 0' % key)
        if wet: out += ['%s/0/material = SubResource("ShaderMaterial_water")' % key, '%s/0/custom_data_1 = true' % key]
        if blocks(name):
            out += ['%s/0/physics_layer_0/polygon_0/points = %s' % (key, polygon([(0, 0)])), '%s/1 = 1' % key]          # la variante 1 : le même dessin, sans collision (sous un pont)
            if wet: out += ['%s/1/material = SubResource("ShaderMaterial_water")' % key, '%s/1/custom_data_1 = true' % key]
    return '\n'.join(out) + '\n'


def patch_tileset(write):
    s = open(TILESET, encoding='utf-8').read()
    before = s
    s = re.sub(r'\[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_cavern"\]\n(?:[^\[\n][^\n]*\n)*\n?', '', s)
    s = re.sub(r'^sources/%d = [^\n]*\n' % SOURCE_ID, '', s, flags=re.M)
    texture = '[ext_resource type="Texture2D" path="%sassets/levels/cavern.png" id="%s"]' % (RES, TEXTURE_ID)
    if texture not in s:
        village = '[ext_resource type="Texture2D" path="%sassets/levels/village.png" id="9_village"]' % RES
        assert s.count(village) == 1
        s = s.replace(village, village + '\n' + texture)
    # Avant les sources de la route : `tools/maps/route_1/generate.py` retire les siennes et les remet en dernier. Rangée là,
    # celle de la grotte ne bouge pas quand il passe, et les deux outils laissent le fichier tel quel.
    route, first = '[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_route"]', 'sources/11 = '
    assert s.count(route) == 1 and s.count('\n' + first) == 1
    s = s.replace(route, source() + '\n' + route)
    s = s.replace('\n' + first, '\nsources/%d = SubResource("TileSetAtlasSource_cavern")\n' % SOURCE_ID + first)
    if write and s != before: open(TILESET, 'w', encoding='utf-8').write(s)
    return s != before


if __name__ == '__main__':
    made = cells()
    columns, lines = max(c for c, _ in made) + 1, max(r for _, r in made) + 1
    sheet = [[CLEAR] * (columns * 16) for _ in range(lines * 16)]
    for (c, r), img in made.items():
        for y in range(16):
            for x in range(16): sheet[r * 16 + y][c * 16 + x] = img[y][x]
    save(OUTPUT, sheet)
    print('%d tuiles dans %s (%d x %d cases)' % (len(made), os.path.relpath(OUTPUT, os.path.dirname(HERE)), columns, lines))
    changed = patch_tileset('--write' in sys.argv)
    print('TileSet :', ('source de la grotte réécrite' if '--write' in sys.argv else 'source de la grotte à réécrire (--write)') if changed else 'à jour')
