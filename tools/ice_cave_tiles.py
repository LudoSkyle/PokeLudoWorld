#!/usr/bin/env python3
"""Fabrique assets/levels/ice_cavern.png : les tuiles d'une grotte de glace, et les déclare dans le TileSet.

    python3 tools/ice_cave_tiles.py            # écrit la planche, dit si le TileSet est à jour
    python3 tools/ice_cave_tiles.py --write    # et réécrit sa source dans resources/tilesets/level.tres

Tout vient de `assets/levels/sources/ice_cave.png` (« DOT Day 17 — Evolina ice cave », Phyromatical). Rien n'est
redessiné, et **rien n'est déplacé** : les onze premières colonnes de `ice_cavern.png` sont la planche source telle
quelle, case pour case — une tuile s'appelle donc comme dans le relevé de la carte d'exemple
(`tools/maps/ice_cave/survey.py`). Quatre colonnes de plus portent ce qui a dû être recalé : l'échelle et le trou à
échelle.

**Ce kit se superpose.** Ce n'est pas une variante de la grotte brune, et le lire ainsi a donné deux décors faux de
suite. Relevée tuile par tuile, la carte d'exemple de son auteur est faite de cinq familles, de bas en haut :

    floor…   le **sol** : le bleu-gris foncé, une matière à bords pleine (ses bords portent la glace pâle en dur)
    earth…   la **glace lisse**, striée : une autre matière à bords pleine, posée à la place du sol
    tall…    le **grand plateau** : toute la paroi. Un bloc de 3 x 4 — bord du haut, côtés, puis **deux rangées de
             face** au sud — et six pièces de pli (colonnes 3 et 4) pour les marches que fait la face
    short…   le **petit plateau**, posé sur le grand : le dessus du grand, en retrait d'une case sur les côtés, avec
             sa lèvre d'une rangée juste au-dessus de la face du grand
    ring…    le **liseré du vide** : du noir dehors, un filet, du transparent dedans. Il se pose **sur** la dernière
             case de paroi, pas à côté : c'est pourquoi le bord de la grotte ne fait qu'une case de glace pâle

La glace pâle est donc le **dessus des parois** — là où l'on ne va pas —, et entre elle et le sol il y a toujours une
face de falaise. `tools/mapgen/build.py` applique cette grammaire quand le décor déclare des `tall…`.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from island_tiles import load, save, LEVELS  # noqa: E402
from cavern_tiles import polygon, KEYS, CLEAR  # noqa: E402

SOURCE = os.path.join(LEVELS, 'sources', 'ice_cave.png')
OUTPUT = os.path.join(LEVELS, 'ice_cavern.png')
TILESET = os.path.join(os.path.dirname(LEVELS.rstrip('/')), '..', 'resources', 'tilesets', 'level.tres')
RES = 'res://src/main/kotlin/fr/skyle/pokemonmirage/'
SOURCE_ID, TEXTURE_ID = 16, '11_ice_cavern'
ICE_LAYER = 3          # la couche de données perso `ice` du TileSet (0 `sand`, 1 `water`, 2 `jump`)
COPIED = (11, 16)          # ce qui est repris tel quel de la planche source : ses onze premières colonnes, seize rangées

# Les matières à bords — nom : (colonne, rangée) du bloc 3 x 3, (colonne, rangée) de ses coins rentrants 2 x 2, et
# l'ordre de ces coins. `ijkl` : la case haut-gauche du 2 x 2 sert quand la diagonale **sud-est** manque (c'est l'ordre
# de `build.shape`) ; le liseré du vide est rangé à l'inverse.
BLOCKS = {
    'short': ((0, 0), (3, 0), 'ijkl'),
    'ring':  ((0, 7), (3, 7), 'lkji'),
    'floor': ((0, 11), (3, 11), 'ijkl'),
    'earth': ((5, 13), (8, 13), 'ijkl'),
}
TALL = (0, 3)          # le grand plateau : 3 x 4 en (0, 3), ses plis 2 x 3 en (3, 3) — `tall<rangée a-d><colonne 0-4>`
SINGLES = {'void5': (1, 8), 'lawn': (1, 12)}          # le noir plein ; le sol, sous son nom de toujours
# ce qui est debout — nom : sa case haut-gauche, (largeur, hauteur), les cases de son pied.
# **Chaque caillou a sa place** (Ludovic, 18/11/2026, et la carte d'exemple le confirme case par case) : au sol, il n'y a
# que les deux foncés — le caillou (28 fois sur l'exemple) et le pic (23 fois) ; les deux **ronds et pâles** ne sont
# jamais au sol : ils sont sur le dessus du grand plateau, là où le petit ne le couvre pas (14 fois sur l'exemple), ou
# sur la glace lisse, où ils serviront d'obstacles aux casse-têtes.
SPRITES = {
    'pebbleA': ((7, 0), (1, 1), [(0, 0)]),          # le caillou foncé : au sol
    'spire':   ((5, 1), (1, 2), [(0, 0)]),          # le pic foncé, deux cases de haut : au sol
    'roundA':  ((6, 1), (1, 1), [(0, 0)]),          # les cailloux ronds et pâles : sur le dessus d'une paroi, ou sur la glace lisse
    'roundB':  ((6, 2), (1, 1), [(0, 0)]),
    'boulder': ((7, 1), (2, 2), [(0, -1), (1, -1), (0, 0), (1, 0)]),
}
# ce qui se pose sans arrêter — nom : sa case haut-gauche, (largeur, hauteur), `anchor`
DECOR = {
    'ladder': ((11, 0), (1, 2), 0),          # l'échelle qui monte : son pied sur le sol, son haut sur la face de la paroi
    'hole':   ((12, 0), (3, 2), 1),          # l'échelle qui descend : un trou vu de dessus, centré dans un bloc impair
    'crack':  ((6, 8), (2, 2), 0),           # des fissures dans le sol : du décor à plat, pour que le sol ne soit pas partout le même carreau
}
# ce qui est recalé dans les colonnes de droite : (x, y, largeur, hauteur) sur la planche source, (colonne, rangée), retourné ?
MOVED = [((192, 64, 16, 32), (11, 0), False)]          # l'échelle (sans son ombre portée, qui est de la planche de présentation)
CENTRED = [((97, 99, 29, 27), (12, 0), (3, 2))]          # le trou : son dessin posé centré en largeur, calé en bas


def atlas():
    """{nom: (colonne, rangée) dans ice_cavern.png} pour tout ce qui n'est ni debout ni posé."""
    out = dict(SINGLES)
    for name, (at, inner, order) in BLOCKS.items():
        out.update({name + KEYS[j * 3 + i]: (at[0] + i, at[1] + j) for j in range(3) for i in range(3)})
        out.update({name + order[j * 2 + i]: (inner[0] + i, inner[1] + j) for j in range(2) for i in range(2)})
    out.update({'tall%s%d' % ('abcd'[j], i): (TALL[0] + i, TALL[1] + j) for j in range(4) for i in range(3)})
    out.update({'tall%s%d' % ('abc'[j], 3 + i): (TALL[0] + 3 + i, TALL[1] + j) for j in range(3) for i in range(2)})
    del out['ring5']          # le centre du bloc du liseré est le noir plein : c'est `void5`
    return out


def blocks(name):
    """Cette tuile arrête-t-elle ? Toute la paroi — le grand plateau est sous chacune de ses cases — et le vide."""
    return name.startswith('tall') or name == 'void5'


def slick(name):
    """Glisse-t-on sur cette tuile ? Le verglas : toute la matière `earth…`, bords compris (la donnée `ice` du TileSet)."""
    return name.startswith('earth')


def sheet():
    src = load(SOURCE)[2]
    cols, rows = COPIED[0] + 4, COPIED[1]
    out = [[CLEAR] * (cols * 16) for _ in range(rows * 16)]
    for y in range(COPIED[1] * 16):
        for x in range(COPIED[0] * 16):
            if src[y][x][3]: out[y][x] = tuple(src[y][x])
    for (x, y, w, h), at, flip in MOVED:
        for j in range(h):
            for i in range(w):
                p = src[y + j][x + (w - 1 - i if flip else i)]
                if p[3]: out[at[1] * 16 + j][at[0] * 16 + i] = tuple(p)
    for (x, y, w, h), at, (cw, ch) in CENTRED:
        dx, dy = (cw * 16 - w) // 2, ch * 16 - h
        for j in range(h):
            for i in range(w):
                if src[y + j][x + i][3]: out[at[1] * 16 + dy + j][at[0] * 16 + dx + i] = tuple(src[y + j][x + i])
    return out


def source():
    """Le texte de la source `ice_cavern` du TileSet."""
    out = ['[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_ice_cavern"]', 'resource_name = "ice_cavern"',
           'texture = ExtResource("%s")' % TEXTURE_ID]
    big = {}
    for name, (where, (w, h), feet) in SPRITES.items(): big[where] = (w, h, feet)
    for name, (where, (w, h), _) in DECOR.items(): big[where] = (w, h, None)
    hidden = {(x + i, y + j) for (x, y), (w, h, _) in big.items() for i in range(w) for j in range(h)} - set(big)
    names = {}
    for name, where in atlas().items(): names.setdefault(where, name)
    for where in sorted(set(names) | set(big), key=lambda c: (c[1], c[0])):
        if where in hidden: continue
        key = '%d:%d' % where
        if where in big:
            w, h, feet = big[where]
            if (w, h) != (1, 1): out.append('%s/size_in_atlas = Vector2i(%d, %d)' % (key, w, h))
            out += ['%s/0 = 0' % key, '%s/0/texture_origin = Vector2i(%d, %d)' % (key, -8 * (w - 1), 8 * (h - 1)), '%s/0/y_sort_origin = -1' % key]
            if feet: out.append('%s/0/physics_layer_0/polygon_0/points = %s' % (key, polygon(feet)))
            continue
        solid = blocks(names[where])
        if solid: out.append('%s/next_alternative_id = 2' % key)
        out.append('%s/0 = 0' % key)
        if slick(names[where]): out.append('%s/0/custom_data_%d = true' % (key, ICE_LAYER))          # on y glisse (CharacterMovement.kt)
        if solid: out += ['%s/0/physics_layer_0/polygon_0/points = %s' % (key, polygon([(0, 0)])), '%s/1 = 1' % key]          # la variante 1 : le même dessin, sans collision
    return '\n'.join(out) + '\n'


def patch_tileset(write):
    s = open(TILESET, encoding='utf-8').read()
    before = s
    s = re.sub(r'\[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_ice_cavern"\]\n(?:[^\[\n][^\n]*\n)*\n?', '', s)
    s = re.sub(r'^sources/%d = [^\n]*\n' % SOURCE_ID, '', s, flags=re.M)
    texture = '[ext_resource type="Texture2D" path="%sassets/levels/ice_cavern.png" id="%s"]' % (RES, TEXTURE_ID)
    if 'custom_data_layer_%d/name = "ice"' % ICE_LAYER not in s:          # la donnée du verglas : un booléen (type 1), après celle des rebords
        last = 'custom_data_layer_%d/type = 6\n' % (ICE_LAYER - 1)
        assert s.count(last) == 1
        s = s.replace(last, last + 'custom_data_layer_%d/name = "ice"\ncustom_data_layer_%d/type = 1\n' % (ICE_LAYER, ICE_LAYER))
    if texture not in s:
        cavern = '[ext_resource type="Texture2D" path="%sassets/levels/cavern.png" id="10_cavern"]' % RES
        assert s.count(cavern) == 1
        s = s.replace(cavern, cavern + '\n' + texture)
    # **Juste avant** la source de la grotte brune, elle-même juste avant celles de la route : `tools/cavern_tiles.py`
    # remet toujours la sienne avant la route, `tools/maps/route_1/generate.py` les siennes en dernier. Accrochés ainsi,
    # les trois outils laissent chacun le fichier tel que les autres l'ont écrit.
    cavern, first = '[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_cavern"]', 'sources/15 = '
    assert s.count(cavern) == 1 and s.count('\n' + first) == 1
    s = s.replace(cavern, source() + '\n' + cavern)
    s = s.replace('\n' + first, '\nsources/%d = SubResource("TileSetAtlasSource_ice_cavern")\n' % SOURCE_ID + first)
    if write and s != before: open(TILESET, 'w', encoding='utf-8').write(s)
    return s != before


if __name__ == '__main__':
    img = sheet()
    save(OUTPUT, img)
    print('%s : %d x %d cases, %d tuiles nommées' % (os.path.relpath(OUTPUT, os.path.dirname(HERE)), len(img[0]) // 16, len(img) // 16, len(atlas())))
    changed = patch_tileset('--write' in sys.argv)
    print('TileSet :', ('source de la grotte de glace réécrite' if '--write' in sys.argv else 'source de la grotte de glace à réécrire (--write)') if changed else 'à jour')
