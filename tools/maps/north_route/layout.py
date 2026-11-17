"""Le plan de la route du nord : du relevé de la carte d'exemple aux calques de tuiles.

Ce module ne s'exécute pas seul : `generate.py` l'importe, écrit la scène et contrôle.
Il lit `survey.json`, que `survey.py` tire de `reference.png` — la carte que Ludovic a donnée
en exemple. **Le relevé est le plan** : chaque tuile de l'exemple est posée à sa place, avec
la tuile même dont l'exemple est fait (`route.png`, découpée par `tools/route_tiles.py`).
On ne redessine rien de tête.

Ce que le plan ajoute au relevé, et rien d'autre (« Les écarts », plus bas) :

  - la **trouée du sud**, que l'exemple n'a pas : il faut bien arriver de l'île ;
  - le sol des cases que l'exemple cache entièrement (sous une forêt, sous un pont) ;
  - les objets du jeu — panneaux, objets à ramasser — aux places de ceux de l'exemple.

Ce que la carte tient de l'exemple se lit donc dans `survey.json`. Ce qui en fait une carte
où l'on joue se lit ici : quelles cases bloquent (`SOLID`), d'où l'on arrive, où l'on va.
Les collisions elles-mêmes sont portées par les tuiles, dans le TileSet (`generate.py`) ;
`SOLID` en est le calcul côté plan, que les tests comparent à ce que dit le moteur.
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import route_tiles  # noqa: E402
from island_tiles import load, save  # noqa: E402

S = json.load(open(os.path.join(HERE, 'survey.json')))
W, H = S['size']
AT, SIZES, family = route_tiles.atlas(), route_tiles.sizes(), route_tiles.family
SOURCE, GRASS_SOURCE = 11, 12          # route.png ; ses hautes herbes ont leur source à elles (TallGrass.kt)
WARN = []
CELLS = [(x, y) for y in range(H) for x in range(W)]
NEIGH4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
NEIGH8 = [(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i, j) != (0, 0)]
def inb(c): return 0 <= c[0] < W and 0 <= c[1] < H

ground = {c: S['ground'][c[1]][c[0]] for c in CELLS}
cliffs = {c: list(S['cliffs'][c[1]][c[0]]) for c in CELLS}
decor = {c: S['decor'][c[1]][c[0]] for c in CELLS}
stairs = {c: S['stairs'][c[1]][c[0]] for c in CELLS}
ledge = {c: S['ledge'][c[1]][c[0]] for c in CELLS}
deck = {c: S['deck'][c[1]][c[0]] for c in CELLS}
# (nom, colonne de gauche, rangée du pied). Un arbre que l'exemple fait de deux essences est planté d'une seule : celle de sa cime.
sprites = [(route_tiles.MIXED_TREES.get(s[0], (s[0],))[0], s[1], s[2]) for s in S['sprites']]
# Les pieds d'arbre que le jeu ne rend pas comme l'exemple, exprès : ceux de ces arbres-là, et ceux que l'exemple pose deux
# fois l'un sur l'autre (leur ombre y est double : nous n'en gardons qu'une).
RETOUCHED = {(s[1] + i, s[2]) for s in S['sprites'] if s[0] in route_tiles.MIXED_TREES for i in range(3)} | {(x + i, r) for x, r in S.get('doubled', []) for i in range(3)}
UNKNOWN = {tuple(c) for c in S['unknown']}


def feet(name, x, r):
    """Les cases que bloque ce qui est debout : c'est aussi le polygone de sa tuile."""
    if name.startswith('tree'): return [(x + i, r - j) for j in (1, 0) for i in range(3)]      # ses deux rangées du bas, sur toute sa largeur : le tronc, et la cime qui retombe de chaque côté
    if name == 'boulder': return [(x, r - 1), (x + 1, r - 1), (x, r), (x + 1, r)]
    if name in ('conif', 'sapling', 'rock_s'): return [(x, r)]
    return []          # les rochers de la rivière : l'eau qui les porte bloque déjà


# ============================================================ les écarts
# --- la trouée du sud : un couloir de piste de trois cases, du bord jusqu'à la clairière. L'exemple a là une forêt.
SOUTH_GATE = [(44, 49), (45, 49), (46, 49)]
NORTH_GATE = [(14, 0), (15, 0), (16, 0)]          # les deux sorties de l'exemple : la piste y touche le bord
EAST_GATE = [(68, 35), (68, 36), (68, 37)]
START = (45, 48)
LANE = {(x, y) for x in (44, 45, 46) for y in range(46, H)}
for c in LANE:
    if any(n not in ('rock5', 'grass5') for n in cliffs[c]) or ledge[c] or stairs[c] or deck[c]: WARN.append(('trouée', c, 'la trouée du sud traverse autre chose que de la forêt'))
def shade(name, x, r): return {(x + i, r - j) for i in range(3) for j in range(3)} if name.startswith('tree') else set(feet(name, x, r))
sprites = [s for s in sprites if not shade(*s) & LANE]          # les arbres qui la barraient, et ceux dont la cime la couvrait
for x in (41, 47):          # et la forêt se referme de chaque côté : sans eux, on longerait le bord de la carte
    for r in (48, 50):
        if not any(s[1:] == (x, r) for s in sprites): sprites.append(('treeA', x, r))
for (x, y) in LANE:
    ground[(x, y)], cliffs[(x, y)] = 'trailC', []
    decor[(x, y)] = {44: 'trail7', 45: 'trail8', 46: 'trail9'}[x] if y == 46 else {44: 'trail4', 45: None, 46: 'trail6'}[x]      # un bout arrondi côté clairière, ouvert côté île
# ============================================================ le sol que l'exemple cache
def plain(name):
    """La matière unie d'un sol : un bord d'eau profonde est de l'eau profonde, un bord de sable touche l'eau."""
    if name is None: return None
    if family(name) == 'deep': return 'deep5'
    if family(name) == 'sand': return 'water' if name != 'sand5' else 'sand5'
    return 'lawn' if name == 'lawn2' else name


HIDDEN = {c for c in CELLS if ground[c] is None}          # sous une forêt, sous un pont : rien n'en est visible
todo = set(HIDDEN)
while todo:
    filled = {}
    for c in todo:
        around = collections.Counter(plain(ground[(c[0] + i, c[1] + j)]) for i, j in NEIGH8 if inb((c[0] + i, c[1] + j)) and ground[(c[0] + i, c[1] + j)] is not None)
        if around: filled[c] = sorted(around.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    if not filled: break
    ground.update(filled); todo -= set(filled)
for c in todo: ground[c] = 'lawn'

# ============================================================ les calques
DECK = {c for c in CELLS if deck[c] and deck[c].startswith('bridge')}          # le tablier des ponts : on marche dessus
STEPS = {c for c in CELLS if stairs[c] == 'stair5'}                            # les marches d'un escalier
def tile(name, alt=0): return (SOURCE,) + AT[name] + (alt,)
def edges(c): return [n for n in cliffs[c] if n not in ('rock5', 'grass5')]
L = {n: {} for n in ['Ground', 'Cliffs1', 'Cliffs2', 'Cliffs3', 'Paths', 'Decorations', 'Grass', 'Ledges', 'Bridges', 'Props', 'Trees']}
ORDER = ['Ground', 'Cliffs1', 'Cliffs2', 'Cliffs3', 'Paths', 'Decorations', 'Grass', 'Ledges', 'Bridges']
for c in CELLS:
    free = 1 if c in DECK or c in STEPS else 0          # sous un pont ou un escalier, une tuile garde son dessin et perd sa collision
    L['Ground'][c] = tile(ground[c], free if route_tiles.blocks(ground[c]) else 0)
    for k, name in enumerate(cliffs[c][:3]): L['Cliffs%d' % (k + 1)][c] = tile(name, free if route_tiles.blocks(name) else 0)
    d = decor[c]
    if d == 'tall': L['Grass'][c] = (GRASS_SOURCE, 6, 0, 0)
    elif d and family(d) == 'fl': L['Decorations'][c] = tile(d)
    elif d: L['Paths'][c] = tile(d)
    if ledge[c]: L['Ledges'][c] = tile(ledge[c])
    if deck[c]: L['Bridges'][c] = tile(deck[c])
    elif stairs[c]: L['Bridges'][c] = tile(stairs[c])
for name, x, r in sprites:
    L['Trees' if name.startswith('tree') else 'Props'][(x, r)] = tile(name)

# ============================================================ ce qui bloque
SOLID = set()
for c in CELLS:
    if c in DECK: continue
    if route_tiles.blocks(ground[c]) or ledge[c] or (any(route_tiles.blocks(n) for n in cliffs[c]) and c not in STEPS): SOLID.add(c)
for name, x, r in sprites: SOLID |= {c for c in feet(name, x, r) if inb(c)}
def free(c): return inb(c) and c not in SOLID
def reach_from(start, closed=(), opened=()):
    """Les cases qu'on atteint à pied depuis `start`, sauts de rebord compris ; `opened` : des cases pleines qu'on suppose ouvertes (un arbre coupé)."""
    seen, queue = {start}, collections.deque([start])
    while queue:
        c = queue.popleft()
        for i, j in NEIGH4:
            n = (c[0] + i, c[1] + j)
            if route_tiles.jump(ledge.get(n)) == (i, j): n = (n[0] + i, n[1] + j)          # un rebord tourné dans ce sens se saute : on retombe une case plus loin
            if (free(n) or n in opened) and n not in seen and n not in closed: seen.add(n); queue.append(n)
    return seen
def pinches(c):
    """Un obstacle posé là couperait-il un passage ? (les cases libres autour de c ne se touchent plus)"""
    ring = [(c[0] + i, c[1] + j) for i, j in ((-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0))]
    open_ = [free(r) for r in ring]; group = list(range(8))
    def find(i):
        while group[i] != i: i = group[i]
        return i
    for i in range(8):
        if open_[i] and open_[(i + 1) % 8]: group[find(i)] = find((i + 1) % 8)
    return len({find(i) for i in range(8) if open_[i] and i % 2 == 1}) > 1


# ============================================================ objets du jeu
GATES = set(SOUTH_GATE + NORTH_GATE + EAST_GATE)
TRAIL = {c for c in CELLS if ground[c] == 'trailC'}
TALL = set(L['Grass'])
REACH0 = reach_from(START) if free(START) else set()
SIGNS = {'SignSouth': (47, 45), 'SignEast': (65, 34), 'SignNorth': (13, 3)}          # le deuxième est le panneau de l'exemple
ITEMS = {'ItemRoutePotion': (20, 11), 'ItemRouteAntidote': (59, 45), 'ItemRouteBall': (6, 9), 'ItemRouteSuper': (61, 22)}          # les deux premiers sont les Poké Balls de l'exemple
# L'exemple cache sa seconde Poké Ball derrière l'arbuste à couper : elle y reste. On ne l'atteint pas tant que le jeu ne
# sait pas couper — c'est ce qu'elle récompensera (Ludovic, 17/11/2026).
CUT = {(x, r) for name, x, r in sprites if name == 'sapling'}
BEHIND = (reach_from(START, opened=CUT) - REACH0 - CUT) if free(START) else set()          # ce qu'on n'atteint qu'une fois l'arbuste coupé
LOCKED = {'ItemRouteAntidote'}
OBJECTS = {}
MADE = route_tiles.cells()
def veil(name):
    """{(dx, dy depuis le pied)} : les cases dont ce qui est debout cache le centre (8 pixels au moins de ses 8 x 8 du milieu)."""
    w, h = SIZES.get(name, (1, 1))
    return {(i, j - h + 1) for i in range(w) for j in range(h)
            if sum(1 for b in range(4, 12) for a in range(4, 12) if MADE.get((AT[name][0] + i, AT[name][1] + j), [[(0, 0, 0, 0)] * 16] * 16)[b][a][3] == 255) >= 8}
VEIL = {name: veil(name) for name in {s[0] for s in sprites}}
def canopy(q):
    """Cette case est-elle derrière une cime, un sapin ? Ce qu'on y pose est dessiné derrière : on ne le verrait pas."""
    return any(r > q[1] and (q[0] - x, q[1] - r) in VEIL[name] for name, x, r in sprites)
def settle(name, wish):
    cells = sorted(((wish[0] + i, wish[1] + j) for i in range(-12, 13) for j in range(-12, 13)), key=lambda q: (abs(q[0] - wish[0]) + abs(q[1] - wish[1]), q))
    among = BEHIND if name in LOCKED else REACH0
    for q in cells:
        if q in among and q not in TRAIL and q not in TALL and q not in DECK and q not in GATES and q not in LANE and q not in L['Decorations'] and q not in L['Paths'] and not pinches(q) and not canopy(q) \
                and all(abs(q[0] - o[0]) + abs(q[1] - o[1]) > 2 for o in OBJECTS.values()) and not any((q[0] + i, q[1] + j) in STEPS | DECK for i, j in NEIGH4):
            return q
    WARN.append(('objet', wish, name + ' : aucune case convenable')); return wish
for name, wish in list(SIGNS.items()): SIGNS[name] = OBJECTS[name] = settle(name, wish)
for name, wish in list(ITEMS.items()): ITEMS[name] = OBJECTS[name] = settle(name, wish)
SOLID |= set(OBJECTS.values())
REACH = reach_from(START) if free(START) else set()

# ============================================================ contrôles
PLACES = {'sortie de l est': (67, 36), 'sortie du nord': (15, 1), 'pont du nord, bout sud': (15, 30), 'pont du nord, bout nord': (15, 17), 'pont de l est, bout ouest': (23, 36), 'pont de l est, bout est': (36, 36)}
for name, goal in PLACES.items():
    if goal not in REACH: WARN.append(('lieu', goal, name + ' inatteignable'))
for c in sorted(STEPS):
    if c not in REACH: WARN.append(('escalier', c, 'marche inatteignable'))
for c in sorted(REACH):
    if (c[0] in (0, W - 1) or c[1] in (0, H - 1)) and c not in GATES: WARN.append(('bord', c, 'case du bord atteignable hors des trouées'))
for c in SOUTH_GATE + EAST_GATE + NORTH_GATE:
    if c not in REACH: WARN.append(('trouée', c, 'case de trouée inatteignable'))


# ============================================================ aperçu, et comparaison à l'exemple
def render():
    """La carte telle que le jeu la dessinera : {case: 256 pixels RVB}, composée depuis route.png, ombres comprises."""
    sheet = load(route_tiles.OUTPUT)[2]
    img = [[(0, 0, 0)] * (W * 16) for _ in range(H * 16)]
    def put(c, t, big=False):
        w, h = BIG.get(t[1:3], (1, 1)) if big else (1, 1)
        ax, ay = (t[1], t[2] + 6) if t[0] == GRASS_SOURCE else t[1:3]
        for j in range(16 * (h + (DROP.get(t[1:3], 0) if big else 0))):          # l'ombre qui déborde sous le pied
            Y = (c[1] - h + 1) * 16 + j
            if not 0 <= Y < H * 16: continue
            for i in range(16 * w):
                X = c[0] * 16 + i
                if not 0 <= X < W * 16: continue
                p = sheet[ay * 16 + j][ax * 16 + i]
                if p[3] == 255: img[Y][X] = p[:3]
                elif p[3]: img[Y][X] = tuple(int(round(img[Y][X][n] * (1 - p[3] / 255.0) + p[n] * p[3] / 255.0)) for n in range(3))
    for n in ORDER:
        for c, t in L[n].items(): put(c, t)
    standing = [((c[1], 0), c, t) for c, t in L['Trees'].items()] + [((c[1], 1), c, t) for c, t in L['Props'].items()]
    for _, c, t in sorted(standing): put(c, t, True)
    return img


BIG = {AT[name]: size for name, size in SIZES.items()}
DROP = {AT[name]: route_tiles.drop(name) for name in SIZES}
SHADOWS = {(x, r + 1) for name, x, r in sprites if route_tiles.drop(name) and r + 1 < H}          # les cases où tombe cette ombre : l'exemple la coupe presque partout
def write_preview(path):
    img = render()
    for name, c in OBJECTS.items():
        for j in range(5, 11):
            for i in range(5, 11): img[c[1] * 16 + j][c[0] * 16 + i] = (230, 40, 40) if name.startswith('Item') else (200, 120, 60)
    save(path, [[p + (255,) for p in row] for row in img])


def compare():
    """Les cases où la carte diffère de l'exemple, au pixel près (hors objets du jeu)."""
    img = render(); reference = load(os.path.join(HERE, 'reference.png'))[2]
    def same(c): return all(abs(img[c[1] * 16 + j][c[0] * 16 + i][n] - reference[c[1] * 16 + j][c[0] * 16 + i][n]) <= 3 for j in range(16) for i in range(16) for n in range(3))
    return [c for c in CELLS if not same(c)]


def summary():
    kinds = collections.Counter(s[0] for s in sprites)
    return ('carte %d x %d — %d avertissements\n' % (W, H, len(WARN))
            + 'debout : %s\n' % ', '.join('%d %s' % (n, k) for k, n in sorted(kinds.items()))
            + 'hautes herbes : %d ; piste : %d ; ponts : %d cases ; marches : %d ; sol deviné (caché dans l exemple) : %d ; cases atteignables : %d' % (len(TALL), len(TRAIL), len(DECK), len(STEPS), len(HIDDEN), len(REACH)))


def show_map():
    print('    ' + ''.join(str(i // 10) for i in range(W))); print('    ' + ''.join(str(i % 10) for i in range(W)))
    for y in range(H):
        row = ''
        for x in range(W):
            c = (x, y)
            row += '=' if c in DECK else ('S' if c in STEPS else ('o' if c in OBJECTS.values() else ('~' if route_tiles.blocks(ground[c]) else ('#' if c in SOLID else ('.' if c in REACH else '?')))))
        print('%2d  %s' % (y, row))
