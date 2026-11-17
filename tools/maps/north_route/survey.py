#!/usr/bin/env python3
"""Relève la carte d'exemple tuile par tuile : reference.png -> survey.json.

    python3 tools/maps/north_route/survey.py            # écrit survey.json, dit ce qui reste inexpliqué
    python3 tools/maps/north_route/survey.py --map      # en plus, la carte des cases non reconstituées

La carte d'exemple est faite des tuiles de `assets/levels/sources/town_compilation.png` :
on ne devine donc rien, on **retrouve** chaque tuile, au pixel près. Le catalogue des tuiles
cherchées est celui de `tools/route_tiles.py` (ce qu'il découpe pour le jeu).

On épluche la carte du dessus vers le dessous :

  1. ce qui est debout — arbres, sapins, buissons, rochers — rangée par rangée, de
     l'avant vers l'arrière : un arbre cache le pied de celui de derrière ;
  2. les escaliers, puis les décors au sol (hautes herbes, fleurs, contour des pistes) ;
  3. les falaises, jusqu'à trois anneaux l'un sur l'autre ;
  4. le sol : pelouse, eau, sable, roche, piste.

À chaque couche, une tuile n'est retenue que si **tous** ses pixels encore visibles sont
ceux de l'exemple. Les ombres des arbres et des falaises sont translucides sur la planche :
un pixel sous une ombre est comparé assombri d'autant. Une tuile de bord (falaise, sable,
eau profonde) n'est retenue que si l'on voit de quoi la distinguer du centre de sa matière.

Deux cas où l'on ne voit pas tout, et où l'on ne devine pas pour autant :

  - l'ombre du sapin et de l'arbuste déborde d'une rangée sous leur pied sur la planche, et
    l'exemple ne la garde que par endroits : là où elle est, on la relève (`shadows`), pour
    lire à travers elle la tuile qu'elle assombrit ;
  - un bord de falaise dont ce qui le distingue est caché (sous un rocher) est retenu s'il est
    le seul genre de tuile dont tous les pixels visibles concordent ;
  - l'exemple pose parfois deux pieds d'arbre l'un sur l'autre : l'ombre y est double. On le
    relève (`doubled`) pour lire le sol à travers elle — le jeu, lui, n'en dessine qu'une.

Pour finir, la carte est recomposée à partir du relevé et comparée à l'exemple : les cases
qui diffèrent sont rangées dans `unknown` — ce sont les dessins qui ne viennent pas de la
planche (ponts, rochers de l'eau, panneau…), que `route_tiles.py` découpe dans l'exemple.
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import island_tiles  # noqa: E402
import route_tiles  # noqa: E402

RW, RH, REF = island_tiles.load(os.path.join(HERE, 'reference.png'))
CW, CH = RW // 16, RH // 16
MADE, WHERE, SIZES = route_tiles.cells(survey=True), route_tiles.atlas(), route_tiles.sizes()
EMPTY = (None,) * 256


def image(at):
    """Une case de route.png : 256 pixels RVBA, None là où elle est vide."""
    t = MADE.get(at)
    return EMPTY if t is None else tuple((tuple(t[j][i]) if t[j][i][3] else None) for j in range(16) for i in range(16))


CELL = {(cx, cy): tuple(tuple(REF[cy * 16 + j][cx * 16 + i][:3]) for j in range(16) for i in range(16)) for cy in range(CH) for cx in range(CW)}
# ce qui est debout se cherche par son pied ; le reste, case par case
SPRITES = {name: {(i, j - SIZES.get(name, (1, 1))[1] + 1): image((WHERE[name][0] + i, WHERE[name][1] + j)) for j in range(SIZES.get(name, (1, 1))[1]) for i in range(SIZES.get(name, (1, 1))[0])} for name in sorted(route_tiles.STANDING)}
# l'ombre du sapin et de l'arbuste déborde d'une rangée sous leur pied : l'exemple ne la garde que par endroits
SHADOW = {name: image((WHERE[name][0], WHERE[name][1] + SIZES[name][1])) for name in route_tiles.SHADOW_ROW}
TILES = {name: image(at) for name, at in sorted(WHERE.items()) if name not in SPRITES and not name.startswith('tall_')}
TILES = {name: t for name, t in TILES.items() if sum(1 for p in t if p is not None and p[3] == 255) >= 8}      # un centre vide n'est pas une tuile
TREES = [n for n in SPRITES if n.startswith('tree')]
assert TILES['grass5'] == TILES['lawn']      # le dessus d'un plateau d'herbe est la pelouse
CENTRE = {'rock': 'rock5', 'grass': 'lawn', 'sand': 'sand5', 'deep': 'deep5'}       # le centre de chaque matière à bords


family = route_tiles.family
def opaque(t): return [k for k in range(256) if t[k] is not None and t[k][3] == 255]
def signature(name):
    """Les pixels qui distinguent une tuile de bord du centre de sa matière."""
    t = TILES[name]; centre = CENTRE.get(family(name))
    if centre is None or name == centre: return set(opaque(t))
    base = TILES[centre]
    return {k for k in opaque(t) if base[k] is None or base[k][:3] != t[k][:3]}


SIGN = {name: signature(name) for name in TILES}
def near(a, b): return abs(a[0] - b[0]) <= 3 and abs(a[1] - b[1]) <= 3 and abs(a[2] - b[2]) <= 3
HIDDEN = collections.defaultdict(lambda: [False] * 256)      # pixel caché par un pixel opaque du dessus
SHADE = collections.defaultdict(lambda: [1.0] * 256)         # assombri par les ombres du dessus


def fit(c, t, sign=None):
    """(pixels visibles qui concordent, qui discordent, dont pixels distinctifs) de la tuile t sous ce qui est déjà trouvé."""
    cell, hidden, shade = CELL[c], HIDDEN[c], SHADE[c]; vis = bad = marks = 0
    for k in range(256):
        p = t[k]
        if p is None or p[3] != 255 or hidden[k]: continue
        s = shade[k]
        if (cell[k] == p[:3]) if s == 1.0 else near(cell[k], (p[0] * s, p[1] * s, p[2] * s)):
            vis += 1
            if sign is not None and k in sign: marks += 1
        else: bad += 1
    return vis, bad, marks


def cover(c, t, only_shade=False):
    hidden, shade = HIDDEN[c], SHADE[c]
    for k in range(256):
        p = t[k]
        if p is None: continue
        if p[3] == 255: hidden[k] = hidden[k] or not only_shade
        elif not hidden[k]: shade[k] *= 1 - p[3] / 255.0


# ------------------------------------------------------------------ 1. ce qui est debout
sprites = []          # (rangée du pied, 0 arbre / 1 autre, nom, colonne de gauche)
shadows = []          # (colonne, rangée, nom) : les cases où l'exemple a gardé la rangée d'ombre sous un sapin
doubled = []          # (colonne, rangée du pied, nom) : les arbres dont l'exemple a posé le pied deux fois
LAWNS = sorted({p[:3] for p in image(WHERE['lawn']) if p is not None})
def twice(name, x, r):
    """L'ombre de cet arbre est-elle deux fois plus sombre qu'elle ne devrait, sur la pelouse ?"""
    once = twice_ = 0
    for i in range(3):
        c = (x + i, r)
        if c not in CELL: continue
        t = SPRITES[name][(i, 0)]
        for k in range(256):
            if t[k] is None or t[k][3] == 255 or HIDDEN[c][k]: continue
            s = SHADE[c][k]; a = 1 - t[k][3] / 255.0          # SHADE compte déjà cette ombre une fois
            if any(near(CELL[c][k], (g[0] * s, g[1] * s, g[2] * s)) for g in LAWNS): once += 1
            elif any(near(CELL[c][k], (g[0] * s * a, g[1] * s * a, g[2] * s * a)) for g in LAWNS): twice_ += 1
    return twice_ >= 16 and twice_ > 4 * once
def shadowed(c, t):
    """L'ombre t tombe-t-elle sur cette case ? Ses pixels y sont nettement plus sombres que leurs voisins de rangée."""
    cell = CELL[c]; rows = {k // 16 for k in range(256) if t[k] is not None}
    dark = [sum(cell[k]) for k in range(256) if t[k] is not None and not HIDDEN[c][k]]
    light = [sum(cell[k]) for k in range(256) if t[k] is None and k // 16 in rows and not HIDDEN[c][k]]
    return len(dark) >= 4 and len(light) >= 4 and max(dark) < 0.8 * min(light)
def sprite_fit(name, x, r):
    vis = bad = 0
    for (i, j), t in SPRITES[name].items():
        if (x + i, r + j) in CELL:
            v, b, _ = fit((x + i, r + j), t); vis += v; bad += b
    return vis, bad
def stand(name, x, r, order):
    sprites.append((r, order, name, x))
    for (i, j), t in SPRITES[name].items():
        if (x + i, r + j) in CELL: cover((x + i, r + j), t)
for r in range(CH + 1, -1, -1):
    got = {}
    for x in range(-2, CW):
        for kind in TREES:
            top = (x + 1, r - 2)          # la cime : aucun arbre de devant ne la cache
            if top in CELL:
                v, b, _ = fit(top, SPRITES[kind][(1, -2)]); ok = v >= 60 and b <= v * 0.1
                if ok: v, b = sprite_fit(kind, x, r)          # la cime dit l'essence du haut ; l'arbre entier, celle du pied
            else:
                v, b = sprite_fit(kind, x, r); ok = v >= 24 and b <= v * 0.08
            if ok and (x not in got or (b, -v) < got[x][1:]): got[x] = (kind, b, -v)
    for x, (kind, _, _) in sorted(got.items()):
        stand(kind, x, r, 0)
        if twice(kind, x, r):          # deux pieds d'arbre l'un sur l'autre dans l'exemple : leur ombre compte double
            doubled.append((x, r, kind))
            for i in range(3):
                if (x + i, r) in CELL: cover((x + i, r), SPRITES[kind][(i, 0)], only_shade=True)
    for name in SPRITES:
        if name in TREES: continue
        for x in range(1 - SIZES.get(name, (1, 1))[0], CW):          # un rocher peut dépasser du bord gauche de la carte
            v, b = sprite_fit(name, x, r)
            if not b and v >= 30:
                stand(name, x, r, 1)
                if name in SHADOW and (x, r + 1) in CELL and shadowed((x, r + 1), SHADOW[name]): shadows.append((x, r + 1, name)); cover((x, r + 1), SHADOW[name])

# ------------------------------------------------------------------ 2 à 4. les couches à plat
EDGES = [n for n in TILES if family(n) in ('rock', 'grass', 'hollow') and n not in ('rock5', 'grass5')]
LAYERS = [
    ('deck', [n for n in TILES if n.startswith(('bridge', 'lip'))], 20),
    ('stairs', [n for n in TILES if family(n) == 'stair'], 8),          # 8 : le pied d'un poteau ne dépasse que de deux rangées sur la case du dessous
    ('ledge', [n for n in TILES if family(n).startswith('ledge')], 20),
    ('decor', ['tall'] + [n for n in TILES if family(n) in ('fl', 'trail', 'paved') and n != 'trailC'], 6),
    ('cliff3', EDGES, 10), ('cliff2', EDGES, 10), ('cliff1', EDGES, 10),
    ('ground', [n for n in TILES if family(n) in ('sand', 'deep') and n not in ('sand5', 'deep5')], 1),
]
PLAIN = ['lawn', 'water', 'deep5', 'sand5', 'rock5', 'trailC', 'lawn2']          # les sols unis, du plus au moins courant
found = {c: {} for c in CELL}
for layer, names, least in LAYERS:
    chosen = {}
    for c in CELL:
        best = None
        for name in names:
            vis, bad, marks = fit(c, TILES[name], SIGN[name])
            if not bad and vis >= least and marks >= min(6, len(SIGN[name])) and (best is None or (marks, vis) > best[:2]): best = (marks, vis, name)
        if best is None and layer == 'ground':
            for name in PLAIN:
                vis, bad, _ = fit(c, TILES[name])
                if not bad and vis >= 1 and (best is None or vis > best[1]): best = (0, vis, name)
        if best is None and layer == 'ground' and not found[c]:
            # Rien ne convient, pas même un sol uni : c'est un bord dont ce qui le distingue est caché (sous un rocher…).
            # On retient celui dont tous les pixels visibles concordent — plusieurs le peuvent, ils se valent à l'écran.
            for name in EDGES:
                vis, bad, _ = fit(c, TILES[name])
                if not bad and vis >= 32 and (best is None or vis > best[1]): best = (0, vis, name)
            if best:
                found[c]['cliff1'] = best[2]; cover(c, TILES[best[2]]); best = None
                for name in PLAIN:          # et ce qui dépasse encore de ce bord est le sol qui le porte
                    vis, bad, _ = fit(c, TILES[name])
                    if not bad and vis >= 1 and (best is None or vis > best[1]): best = (0, vis, name)
        if best: found[c][layer] = best[2]; chosen[c] = TILES[best[2]]
    for c, t in chosen.items(): cover(c, t)


# ------------------------------------------------------------------ recomposition et comparaison
def compose(c):
    img = [None] * 256
    def put(t):
        for k in range(256):
            p = t[k]
            if p is None: continue
            if p[3] == 255: img[k] = p[:3]
            elif img[k] is not None:
                a = p[3] / 255.0; img[k] = tuple(img[k][n] * (1 - a) + p[n] * a for n in range(3))
    for layer in ('ground', 'cliff1', 'cliff2', 'cliff3', 'decor', 'ledge', 'stairs', 'deck'):
        if layer in found[c]: put(TILES[found[c][layer]])
    for r, order, name, x in sorted(sprites):
        t = SPRITES[name].get((c[0] - x, c[1] - r))
        if t is not None: put(t)
    for x, y, name in shadows:
        if (x, y) == c: put(SHADOW[name])
    for x, r, name in doubled:
        if c[1] == r and 0 <= c[0] - x < 3: put(tuple(p if p is not None and p[3] < 255 else None for p in SPRITES[name][(c[0] - x, 0)]))
    return img


unknown = []
for c, cell in CELL.items():
    img = compose(c)
    if any(img[k] is None or not near(img[k], cell[k]) for k in range(256)): unknown.append(c)
unknown.sort(key=lambda c: (c[1], c[0]))
data = {
    'size': [CW, CH],
    'ground': [[found[(x, y)].get('ground') for x in range(CW)] for y in range(CH)],
    'cliffs': [[[found[(x, y)][k] for k in ('cliff1', 'cliff2', 'cliff3') if k in found[(x, y)]] for x in range(CW)] for y in range(CH)],
    'decor': [[found[(x, y)].get('decor') for x in range(CW)] for y in range(CH)],
    'stairs': [[found[(x, y)].get('stairs') for x in range(CW)] for y in range(CH)],
    'ledge': [[found[(x, y)].get('ledge') for x in range(CW)] for y in range(CH)],
    'deck': [[found[(x, y)].get('deck') for x in range(CW)] for y in range(CH)],
    'sprites': [[name, x, r] for r, order, name, x in sorted(sprites)],
    'doubled': [[x, r] for x, r, name in doubled],
    'unknown': [list(c) for c in unknown],
}
with open(os.path.join(HERE, 'survey.json'), 'w') as f:
    f.write('{\n' + ',\n'.join('"%s": %s' % (k, json.dumps(v, separators=(',', ':'))) for k, v in data.items()) + '\n}\n')
print('%d x %d cases ; %d reconstituées au pixel près, %d à voir' % (CW, CH, CW * CH - len(unknown), len(unknown)))
print('debout :', dict(sorted(collections.Counter(s[2] for s in sprites).items())), '; ombres entières sous', len(shadows), 'sapins ; pieds d arbre posés deux fois :', [d[:2] for d in doubled])
for arg in sys.argv[1:]:
    if arg.startswith('--why='):          # --why=15,8 : ce qui a été trouvé sur une case, et les pixels que ça n'explique pas
        c = tuple(int(v) for v in arg[6:].split(',')); img = compose(c); seen = {}
        print(c, found[c], [s for s in sprites if any((c[0] - s[3], c[1] - s[0]) == k for k in SPRITES[s[2]])])
        for j in range(16):
            print(''.join('.' if img[j * 16 + i] is not None and near(img[j * 16 + i], CELL[c][j * 16 + i]) else ('?' if img[j * 16 + i] is None else 'X') for i in range(16))
                  + '  ' + ''.join(seen.setdefault(CELL[c][j * 16 + i], chr(97 + len(seen))) for i in range(16)))
        print({v: k for k, v in seen.items()})
if '--map' in sys.argv:
    bad = set(unknown)
    for y in range(CH): print('%2d  %s' % (y, ''.join('#' if (x, y) in bad else '.' for x in range(CW))))
