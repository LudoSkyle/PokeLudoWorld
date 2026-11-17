import sys, random, math, collections
sys.path.insert(0, '/tmp/plw'); sys.path.insert(0, '/tmp/plw/island')
import plan
from plan import W, H, OX, OY, P, R, PX, PY, SEA, SAND, GRASS, inb, in_padding, in_hard
from crop import load

random.seed(20261118)
ATLAS = '/Users/godart/Documents/Projects/Perso/PokeLudoWorld/src/main/kotlin/fr/skyle/pokeludoworld/assets/levels/environments.png'
AW, AH, A = load(ATLAS)
def opacity(ax, ay): return sum(1 for j in range(16) for i in range(16) if A[1 + ay * 16 + j][1 + ax * 16 + i][3] > 127) / 256.0
def tile_of(ax, ay): return [[A[1 + ay * 16 + y][1 + ax * 16 + x] for x in range(16)] for y in range(16)]
def rot_cw(t): return [[t[15 - x][y] for x in range(16)] for y in range(16)]

T, DIST = plan.build()
WARN = []

# ============================================================ la planche fabriquée (source 10)
# `island.png` : ce que l'atlas n'a pas. Sa disposition est fixe, quelle que soit la carte.
#   rangée 0 : planches de ponton, selon les côtés à rambarde (G=1, D=2, H=4, B=8)
#   rangée 1 : planches de bout posées sur la rive, bout en haut (0..3) puis en bas (4..7)
#   rangée 2 : bout à gauche (0..3), à droite (4..7) ; petits rochers dans l'eau (8..11) ;
#              planches d'escalier pour un bord latéral (12)
sys.path.insert(0, '/Users/godart/Documents/Projects/Perso/PokeLudoWorld/tools')
import island_tiles
ISL_IMG = island_tiles.all_cells(A)     # la même fabrique que celle du dépôt : tools/island_tiles.py
def deck_tile(rails, end=None):
    if end is None: return (10, sum(1 << i for i, s in enumerate('LRTB') if s in rails), 0)
    if end in 'TB': return (10, 'TB'.index(end) * 4 + sum(1 << i for i, s in enumerate('LR') if s in rails), 1)
    return (10, 'LR'.index(end) * 4 + sum(1 << i for i, s in enumerate('TB') if s in rails), 2)
def small_rock(k): return (10, 8 + k, 2)
SIDE_STAIR = (10, 12, 2)

# ============================================================ le terrain
DECK = set(); DECK_AXIS = {}
for (x0, y0, x1, y1) in plan.DECKS:
    vertical = (x1 - x0) == 1
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if T[y][x] == SEA: DECK.add((x, y)); DECK_AXIS.setdefault((x, y), 'v' if vertical else 'h')

def kind(x, y): return T[y][x] if inb(x, y) else None
def is_water(x, y): return kind(x, y) == SEA
def is_land(x, y): return kind(x, y) in (SAND, GRASS)
def is_grass(x, y): return kind(x, y) == GRASS
def is_sand(x, y): return kind(x, y) == SAND
def open_sea(x, y): return kind(x, y) == SEA and (x, y) not in DECK
def dry(x, y, d): return inb(x, y) and DIST[y][x] >= d          # à d cases au moins de l'eau
NEIGH8 = [(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i, j) != (0, 0)]
NEIGH4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
SIDES = {'L': (-1, 0), 'R': (1, 0), 'T': (0, -1), 'B': (0, 1)}

L = {n: {} for n in ['Ground', 'Paths', 'Plaza', 'Relief', 'Bridges', 'Decorations', 'Grass', 'Cliffs', 'CliffsMid', 'CliffsTop', 'Props', 'Houses', 'Trees']}
def blob(x, y, inside, c, r, name, inner=None):
    """Raccord 3x3 + 4 coins rentrants. inside(x,y) : la case voisine est de la même matière."""
    inner = inner or {(-1, -1): (c + 3, r), (1, -1): (c + 4, r), (-1, 1): (c + 3, r + 1), (1, 1): (c + 4, r + 1)}
    n, s, w, e = inside(x, y - 1), inside(x, y + 1), inside(x - 1, y), inside(x + 1, y)
    if n and s and w and e:
        out = [inner[d] for d in inner if not inside(x + d[0], y + d[1])]
        if len(out) == 1: return out[0]
        if len(out) > 1: WARN.append((name, x, y, 'deux coins rentrants'))
        return (c + 1, r + 1)
    if (not n and not s) or (not w and not e):
        WARN.append((name, x, y, 'une seule case de large')); return (c + 1, r + 1)
    return (c if not w else (c + 2 if not e else c + 1), r if not n else (r + 2 if not s else r + 1))

# --- sol : herbe sous toute la terre ; la mer ; l'eau sans collision sous les pontons ---
GRASS_TILES = [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0)]
for y in range(H):
    for x in range(W):
        k = T[y][x]
        if (x, y) in DECK: L['Ground'][(x, y)] = (5, 9, 31)
        elif k == SEA: L['Ground'][(x, y)] = (5, 6, 32)
        else:
            L['Ground'][(x, y)] = (5,) + random.choice(GRASS_TILES)
            if k == SAND:
                wet = any(is_water(x + i, y + j) for i, j in NEIGH8)
                green = any(is_grass(x + i, y + j) for i, j in NEIGH8)
                if wet and green: WARN.append(('plage', x, y, 'touche l eau et l herbe'))
                if wet: L['Paths'][(x, y)] = (5,) + blob(x, y, lambda a, b: not is_water(a, b), 15, 31, 'rivage')
                elif green: L['Paths'][(x, y)] = (5,) + blob(x, y, lambda a, b: not is_grass(a, b), 10, 13, 'plage')
                else: L['Paths'][(x, y)] = (5, 11, 14)

# --- plateaux : herbe surélevée, falaise basse sur le bord du bas. Jamais sur une case de rive. ---
def tidy(s):
    """Retire d'un plateau ce que ses raccords ne savent pas dessiner : une avancée d'une case de large."""
    changed = True
    while changed:
        changed = False
        for (x, y) in list(s):
            n, so, w, e = (x, y - 1) in s, (x, y + 1) in s, (x - 1, y) in s, (x + 1, y) in s
            if (not n and not so) or (not w and not e): s.discard((x, y)); changed = True
    return s
CLIFF_CELLS = {(x, j) for (x0, x1) in plan.ROCK for x in range(x0, x1 + 1) for j in range(plan.CLIFF_ROWS)}
PLATS = []
for rects in plan.PLATEAUS:
    s = set()
    for (x0, y0, x1, y1) in rects:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if is_land(x, y) and dry(x, y, 2) and (x, y) not in plan.NIBBLES: s.add((x, y))
    PLATS.append(tidy(s))
# escaliers : deux cases sur le bord du plateau. Si les deux voies n'ont pas le bord à la
# même hauteur, on rogne celle qui dépasse.
STAIRS = set(); STAIR_SIDE = {}; STAIR_GROUPS = []
for (pi, side, lane) in plan.STAIRS:
    s = PLATS[pi]; lanes = (lane, lane + 1)
    try:
        if side in 'BT':
            ext = [(max if side == 'B' else min)(y for (x, y) in s if x == l) for l in lanes]
            edge = min(ext) if side == 'B' else max(ext)
            for l in lanes:
                for (x, y) in [c for c in s if c[0] == l and (c[1] > edge if side == 'B' else c[1] < edge)]: s.discard((x, y))
            cells = [(l, edge) for l in lanes]
        else:
            ext = [(min if side == 'L' else max)(x for (x, y) in s if y == l) for l in lanes]
            edge = max(ext) if side == 'L' else min(ext)
            for l in lanes:
                for (x, y) in [c for c in s if c[1] == l and (c[0] < edge if side == 'L' else c[0] > edge)]: s.discard((x, y))
            cells = [(edge, l) for l in lanes]
    except ValueError:
        WARN.append(('escalier', pi, lane, 'le plateau n a pas de bord sur cette voie')); continue
    tidy(s)
    for c in cells:
        if c not in s: WARN.append(('escalier', c[0], c[1], 'la case d escalier a été rognée'))
        STAIRS.add(c); STAIR_SIDE[c] = side
    STAIR_GROUPS.append((side, cells))
PLAT = set().union(*PLATS)
RING = {(-1, -1): (43, 26), (1, -1): (41, 26), (-1, 1): (43, 24), (1, 1): (41, 24)}
# Un plateau adossé à la falaise n'a pas de bord du haut : il continue sous elle. Un plateau posé
# sur un autre (le second étage du labo) recouvre les tuiles du premier : il vient après dans la liste.
for s in PLATS:
    for (x, y) in s:
        L['Relief'][(x, y)] = (5,) + blob(x, y, lambda a, b: (a, b) in s or (a, b) in CLIFF_CELLS, 38, 24, 'plateau', RING)
PLAT_TOP = {c for c, t in L['Relief'].items() if t == (5, 39, 25)}
# Le bord du haut d'un plateau est de l'herbe : on s'y tient. Ce qu'on ne franchit pas, c'est le
# rebord lui-même, entre cette case et celle du dessus (LEDGE). Deux coins rentrants sont de l'herbe aussi.
TOP_EDGE = {c for c, t in L['Relief'].items() if t == (5, 39, 24)}
SOFT_CORNER = {c for c, t in L['Relief'].items() if t in ((5, 41, 26), (5, 43, 26))}
PLAT_WALK = PLAT_TOP | TOP_EDGE | SOFT_CORNER
PLAT_EDGE = set(L['Relief']) - PLAT_WALK - STAIRS
LEDGE = {frozenset((c, (c[0], c[1] - 1))) for c in TOP_EDGE if (c[0], c[1] - 1) not in CLIFF_CELLS}
# Un escalier à poteaux (planche de l'île), posé par-dessus le bord : la case de bord garde son
# dessin mais prend sa variante sans collision ; le haut des poteaux déborde de 6 px sur la
# case du dessus du plateau, vers l'intérieur.
STAIR_BLOCK = {'B': (0, 3), 'T': (2, 3), 'L': (4, 3), 'R': (6, 3)}
STAIR_ART = {}
for side, cells_ in STAIR_GROUPS:
    bx, by = STAIR_BLOCK[side]
    for k, (x, y) in enumerate(sorted(cells_)):
        if side == 'B': on, over, spill = (bx + k, by + 1), (bx + k, by), (x, y - 1)
        if side == 'T': on, over, spill = (bx + k, by), (bx + k, by + 1), (x, y + 1)
        if side == 'L': on, over, spill = (bx, by + k), (bx + 1, by + k), (x + 1, y)
        if side == 'R': on, over, spill = (bx + 1, by + k), (bx, by + k), (x - 1, y)
        STAIR_ART[(x, y)] = (10,) + on; STAIR_ART[spill] = (10,) + over
        if spill not in PLAT_TOP: WARN.append(('escalier', spill[0], spill[1], 'derrière un escalier, il faut le dessus du plateau'))
        if (x, y) in L['Relief']: L['Relief'][(x, y)] = L['Relief'][(x, y)] + (1,)      # variante 1 : même dessin, sans collision
STAIR_UNDER = sorted({L['Relief'][c][1:3] for c in STAIRS if c in L['Relief']})          # les tuiles de bord à doter de cette variante

# --- pontons : rambarde grise sur chaque côté qui donne sur l'eau ; aux deux bouts, une
# planche à bord fermé posée sur la rive, de la largeur du ponton, ni plus ni moins ---
for (x, y) in DECK:
    rails = {s for s, (dx, dy) in SIDES.items() if open_sea(x + dx, y + dy)}
    L['Bridges'][(x, y)] = deck_tile(rails)
    if open_sea(x, y + 1): L['Bridges'][(x, y + 1)] = (5, 48, 24)
LANDINGS = set()
for (x, y), axis in DECK_AXIS.items():
    for end, (dx, dy) in SIDES.items():
        c = (x + dx, y + dy)
        if not is_land(*c): continue
        if (axis == 'v') != (dx == 0):
            # un ponton ne touche la terre que par ses bouts : jamais par le flanc
            if not any((c[0] + i, c[1] + j) in DECK and DECK_AXIS[(c[0] + i, c[1] + j)] != axis for i, j in NEIGH4):
                WARN.append(('ponton', x, y, 'touche la terre par le flanc'))
            continue
        side = {s for s, (i, j) in SIDES.items() if (i == 0) != (dx == 0) and not (is_land(c[0] + i, c[1] + j) and (x + i, y + j) in DECK)}
        L['Bridges'][c] = deck_tile(side, end); LANDINGS.add(c)
DECK_TILES = dict(L['Bridges'])
L['Bridges'].update(STAIR_ART)

# --- place : le dallage, sur l'herbe uniquement ---
PLZ = R(28, 23, 36, 27)
for y in range(PLZ[1], PLZ[3] + 1):
    for x in range(PLZ[0], PLZ[2] + 1):
        L['Plaza'][(x, y)] = (5, 5 if x == PLZ[0] else (7 if x == PLZ[2] else 6), 47 if y == PLZ[1] else (49 if y == PLZ[3] else 48))
for (x, y) in list(L['Plaza']):
    for i, j in NEIGH8 + [(0, 0)]:
        if not is_grass(x + i, y + j): WARN.append(('place', x + i, y + j, 'le dallage et son tour doivent être en herbe'))
        if (x + i, y + j) in PLAT and (x + i, y + j) not in PLAT_TOP: WARN.append(('place', x + i, y + j, 'le dallage touche un bord de plateau'))

# --- falaise haute du nord ---
# Une montagne en gradins qui se superposent, comme sur les références de Ludovic : un socle sur les quatre
# rangées, puis des buttes posées dessus (calque CliffsMid), et sur les plus larges une butte de plus
# (CliffsTop). Une butte est le même bloc de roche que le socle : ses coins arrondis laissent voir le
# gradin du dessous. La rangée 0 n'a pas de bord : la montagne continue au nord, hors de la carte.
def mesa(layer, c0, c1, face, open_left=False, open_right=False):
    for x in range(c0, c1 + 1):
        for j in range(0, face + 1):
            col = 26 if (x == c0 and not open_left) else (28 if (x == c1 and not open_right) else 27)
            L[layer][(x, j)] = (5, col, 23 if j == face else 22)
MESAS = []
for (x0, x1) in plan.ROCK:
    mesa('Cliffs', x0, x1, plan.CLIFF_ROWS - 1, open_left=(x0 == 0), open_right=(x1 == W - 1))
    lo = x0 if x0 == 0 else x0 + 2            # côté trouée : le socle dépasse de deux cases
    hi = x1 if x1 == W - 1 else x1 - 2
    widths, gaps, faces = [8, 5, 10, 6, 7], [2, 3, 1, 2], [2, 1, 2, 2, 1]
    x = lo; k = (x0 // 3) % 5
    while x <= hi - 2:
        w = min(widths[k % 5], hi - x + 1); f = faces[k % 5]
        c0, c1 = x, x + w - 1
        if hi - c1 <= 2: c1 = hi                                # pas de moignon au bout
        mesa('CliffsMid', c0, c1, f, open_left=(c0 == 0), open_right=(c1 == W - 1))
        MESAS.append((c0, c1, f))
        if f == 2 and c1 - c0 >= 6:                             # un troisième gradin sur les buttes larges
            t0 = c0 + (2 if k % 2 else 1); t1 = c1 - (1 if k % 2 else 3)
            mesa('CliffsTop', 0 if c0 == 0 else t0, W - 1 if c1 == W - 1 else t1, 1, open_left=(c0 == 0), open_right=(c1 == W - 1))
        x = c1 + 1 + gaps[k % 4]; k += 1

# --- bâtiments : nom -> (atlas x0, y0, largeur, hauteur, case haut-gauche, colonne de la porte).
# Ni au centre, ni alignés : chacun à sa hauteur. ---
HOUSES = {'ludo': (8, 94, 5, 6, P(8, 2), 1), 'orange_small': (17, 95, 4, 5, P(14, 2), 2), 'lab': (0, 94, 8, 6, P(49, 3), 2),
          'library': (13, 95, 4, 5, P(8, 24), 1), 'orange_big': (21, 94, 5, 6, P(49, 33), 2)}
DOORS = {}; HOUSE_SOLID = set(); SOFT_ROOF = set()
# Les maisons de la première carte gardent leurs collisions : on les lit dans le TileSet.
import re as _re
_ts = open('/tmp/plw/level_clean.tres').read(); _a = _ts.index('resource_name = "environments"'); _b = _ts.index('[sub_resource', _a)
TS_SOLID = {(int(m.group(1)), int(m.group(2))) for m in _re.finditer(r'^(\d+):(\d+)/0/physics_layer_0/polygon_0/points', _ts[_a:_b], flags=_re.M)}
for name, (ax, ay, w, h, (x, y), door) in HOUSES.items():
    for j in range(h):
        for i in range(w):
            o = opacity(ax + i, ay + j)
            if o == 0: continue
            L['Houses'][(x + i, y + j)] = (5, ax + i, ay + j)
            # On passe derrière une maison : la rangée du haut de son toit se franchit tout entière (le
            # toit, trié devant, recouvre le joueur), et dans la deuxième rangée les coins où le sol se voit.
            if j == 0 or (j == 1 and o < 0.6): SOFT_ROOF.add((ax + i, ay + j))
            elif (o >= 0.25) if name.startswith('orange') else ((ax + i, ay + j) in TS_SOLID): HOUSE_SOLID.add((x + i, y + j))
    DOORS[name] = (x + door, y + h - 1)
    for i in range(w):
        if not is_land(x + i, y + h - 1): WARN.append(('maison', x + i, y + h - 1, name + ' a un pied dans l eau'))
LUDO, LIB, LAB, OBIG, OSMALL = DOORS['ludo'], DOORS['library'], DOORS['lab'], DOORS['orange_big'], DOORS['orange_small']
import os as _os
for n in DOORS:
    if not (n.startswith('orange') and _os.environ.get('ISLAND_FACADES')): HOUSE_SOLID.discard(DOORS[n])          # les portes s'ouvrent

BLOCKED = set(HOUSE_SOLID) | set(L['Cliffs']) | PLAT_EDGE
def walkable(c): return (is_land(*c) and c not in BLOCKED) or c in DECK
def step_ok(a, b):
    """On passe de la case a à sa voisine b : b se foule, et aucun rebord ne les sépare."""
    return (walkable(b) or b in STAIRS) and frozenset((a, b)) not in LEDGE
def pinches(c):
    """Vrai si un objet solide en c fermerait ou étranglerait un passage : ses voisines libres
    ne se rejoindraient plus sans passer par lui."""
    ring = [(c[0] + i, c[1] + j) for i, j in ((-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0))]
    free = [walkable(r) for r in ring]
    comp = list(range(8))
    def find(i):
        while comp[i] != i: i = comp[i]
        return i
    for i in range(8):
        j = (i + 1) % 8
        if free[i] and free[j]: comp[find(i)] = find(j)
    return len({find(i) for i in range(8) if free[i] and i % 2 == 1}) > 1

# --- le tour de la place, où court le coureur ---
LOOP = [P(27, 22), P(37, 22), P(37, 28), P(27, 28)]
LOOP_CELLS = set()
for i in range(4):
    a, b = LOOP[i], LOOP[(i + 1) % 4]
    for x in range(min(a[0], b[0]), max(a[0], b[0]) + 1):
        for y in range(min(a[1], b[1]), max(a[1], b[1]) + 1): LOOP_CELLS.add((x, y))

# --- objets posés par la scène : chacun à une place qui a un sens ---
LIB_STAIR = min(c for c in STAIRS if STAIR_SIDE[c] == 'B' and abs(c[0] - LIB[0]) <= 2)      # l'escalier de la bibliothèque : son lampadaire est au pied
PIER = min(c for c in LANDINGS if c[1] > PLZ[3] + 8)                                        # la première planche de la jetée du sud
SIGNS = {'SignLudo': (LUDO[0] + 2, LUDO[1] + 1), 'SignLibrary': (LIB[0] + 2, LIB[1] + 1), 'SignLab': (LAB[0] + 2, LAB[1] + 1), 'SignNorth': (PX(36) + 1, plan.CLIFF_ROWS + 1), 'SignPier': (PIER[0] - 1, PIER[1])}
LAMPS = {  # nom : (case, ce qu'il éclaire)
    'LampLudo': ((LUDO[0] - 1, LUDO[1] + 2), 'l escalier de chez Ludo'), 'LampLab': ((LAB[0] - 1, LAB[1] + 2), 'l escalier du labo'),
    'LampLibrary': ((LIB_STAIR[0] - 1, LIB_STAIR[1] + 1), 'l escalier de la bibliothèque'), 'LampOrange': ((OBIG[0] - 1, OBIG[1] + 2), 'l escalier de la maison du sud-est'),
    'LampDeckNW': (P(13, 18), 'le débarcadère du nord-ouest'), 'LampDeckNE': (P(52, 18), 'le débarcadère du nord-est'),
    'LampDeckWest': (P(14, 26), 'le débarcadère de l ouest'), 'LampSquareNW': (P(26, 21), 'un coin de la place'), 'LampSquareNE': (P(38, 21), 'un coin de la place'),
    'LampSquareSW': (P(26, 29), 'un coin de la place'), 'LampSquareSE': (P(38, 29), 'un coin de la place'),
    'LampNorth': ((PX(29) - 1, plan.CLIFF_ROWS + 1), 'la trouée de la route du nord'), 'LampPier': ((PIER[0] + 2, PIER[1]), 'la jetée du sud')}
# La côte ondule : un objet prend la case voulue si elle convient, sinon la plus proche qui convient.
OBJECTS = {}
def settle(name, c):
    cands = sorted(((c[0] + i, c[1] + j) for i in range(-2, 3) for j in range(-2, 3)), key=lambda q: (abs(q[0] - c[0]) + abs(q[1] - c[1]), q))
    for q in cands:
        if is_land(*q) and walkable(q) and q not in LANDINGS and q not in STAIRS and q not in L['Plaza'] and q not in LOOP_CELLS and not pinches(q) \
                and all(q != d and q != (d[0], d[1] + 1) for d in DOORS.values()) \
                and all(abs(q[0] - s[0]) + abs(q[1] - s[1]) > 1 for s in STAIRS) \
                and all(abs(q[0] - o[0]) + abs(q[1] - o[1]) > 1 for o in OBJECTS.values()):
            OBJECTS[name] = q; BLOCKED.add(q); return q
    WARN.append(('objet', c[0], c[1], name + ' : aucune case convenable à deux cases à la ronde')); return c
for name in list(SIGNS): SIGNS[name] = settle(name, SIGNS[name])
for name in list(LAMPS): LAMPS[name] = (settle(name, LAMPS[name][0]), LAMPS[name][1])

# --- le mobilier : bancs, parasols, serviettes, caisses, pots de fleurs. Chacun à une place choisie ;
# aucun ne ferme un passage (le parcours depuis le départ ne perd que les cases qu'il occupe). ---
START = (LUDO[0], LUDO[1] + 1)
def reach_now(extra=()):
    extra = set(extra); seen = {START}; q = collections.deque([START])
    while q:
        c = q.popleft()
        for d in NEIGH4:
            n = (c[0] + d[0], c[1] + d[1])
            if inb(*n) and n not in seen and n not in extra and step_ok(c, n): seen.add(n); q.append(n)
    return seen
FURN = {}            # nom -> cases solides
FURN_ALL = set()     # tout ce que le mobilier recouvre, serviettes comprises
def furnish(name, solid, tiles, layer='Props'):
    """solid : cases prises au sol ; tiles : {case: tuile} à poser."""
    before = reach_now()
    bad = [c for c in solid if not (walkable(c) and is_land(*c)) or c in LANDINGS or c in STAIRS or c in L['Plaza'] or c in LOOP_CELLS
           or any(abs(c[0] - s[0]) + abs(c[1] - s[1]) <= 1 for s in STAIRS | LANDINGS) or any(c == (d[0], d[1] + 1) for d in DOORS.values()) or c in OBJECTS.values()]
    if bad: WARN.append(('mobilier', bad[0][0], bad[0][1], name + ' : case prise ou réservée')); return
    lost = before - reach_now(solid) - set(solid)
    if lost: WARN.append(('mobilier', solid[0][0], solid[0][1], name + ' : coupe %d cases du reste' % len(lost))); return
    for c, t in tiles.items():
        if c in L[layer]: WARN.append(('mobilier', c[0], c[1], name + ' : case déjà décorée'))
        L[layer][c] = t; FURN_ALL.add(c)
    FURN[name] = list(solid)
    for c in solid: BLOCKED.add(c)
def bench(name, x, y, side=None):   # le banc de bois. De face : 2 cases de large, le dossier dépasse sur la case du dessus.
    if side is None:                # De profil ('left' : on y regarde vers la gauche, dossier à droite) : 1 case de large, 2 de haut.
        furnish(name, [(x, y), (x + 1, y)], {(x + i, y - 1 + j): (10, 4 + i, 5 + j) for i in range(2) for j in range(2)})
    else:
        col = 9 if side == 'left' else 8
        furnish(name, [(x, y - 1), (x, y)], {(x, y - 2 + j): (10, col, 3 + j) for j in range(3)})
def parasol(name, x, y, kind):    # 2 cases de large, 3 de haut ; seul le pied (la rangée du bas) est solide
    col = 11 + 2 * kind
    furnish(name, [(x, y), (x + 1, y)], {(x + i, y - 2 + j): (10, col + i, 3 + j) for i in range(2) for j in range(3)})
TOWELS = {}
def towel(name, x, y, kind):      # 1 case de large, 2 de haut : on marche dessus
    row = 3 + 2 * kind; TOWELS[name] = (x, y)
    furnish(name, [], {(x, y - 1): (10, 15, row), (x, y): (10, 15, row + 1)}, layer='Decorations')
def crates(name, x, y): furnish(name, [(x, y)], {(x, y - 1): (10, 0, 5), (x, y): (10, 0, 6)})
def box(name, x, y): furnish(name, [(x, y)], {(x, y): (10, 1, 6)})
def pot(name, x, y): furnish(name, [(x, y)], {(x, y - 1): (10, 2, 5), (x, y): (10, 2, 6)})
for (kind_, name_, args_) in plan.FURNITURE:
    {'bench': bench, 'parasol': parasol, 'towel': towel, 'crates': crates, 'box': box, 'pot': pot}[kind_](name_, *args_)
crates('CratesPier', PIER[0] + 3, PIER[1]); box('BoxPier', PIER[0] + 4, PIER[1])   # le quai, à côté du lampadaire
# un pot de fleurs de chaque côté d'une porte, jamais devant
pot('PotOrangeW', OSMALL[0] - 1, OSMALL[1] + 1); pot('PotOrangeE', OSMALL[0] + 1, OSMALL[1] + 1)
pot('PotBigE', OBIG[0] + 2, OBIG[1] + 1)
# les objets à ramasser : une Poké Ball posée au sol, pleine tant qu'on ne l'a pas prise
ITEMS = {}
for name_, c in plan.ITEMS.items():
    if not (walkable(c) and is_land(*c)) or c in FURN_ALL or c in OBJECTS.values() or reach_now() - reach_now([c]) - {c}:
        WARN.append(('objet à ramasser', c[0], c[1], name_ + ' : case prise, ou elle coupe un passage'))
    ITEMS[name_] = c; FURN_ALL.add(c)
FURN_SOLID = {c for cells_ in FURN.values() for c in cells_}

# --- cases où rien ne pousse : devant les portes, sentiers, débarcadères, escaliers, place, routes ---
KEEP = set(L['Plaza']) | set(LANDINGS) | set(LOOP_CELLS)
for name, (ax, ay, w, h, (x, y), door) in HOUSES.items():
    for i in range(-1, w + 1):
        for j in (h, h + 1): KEEP.add((x + i, y + j))
for (x0, y0, x1, y1) in plan.TRAILS:
    for yy in range(y0 - 1, y1 + 2):
        for xx in range(x0 - 1, x1 + 2): KEEP.add((xx, yy))
for (x, y) in STAIRS | DECK | LANDINGS:
    for i in range(-2, 3):
        for j in range(-2, 3): KEEP.add((x + i, y + j))
def keep_rect(x0, y0, x1, y1):
    a = R(x0, y0, x1, y1)
    for y in range(a[1], a[3] + 1):
        for x in range(a[0], a[2] + 1): KEEP.add((x, y))
keep_rect(31, 3, 34, 9)                                     # la route du nord, de la trouée à la plage de la crique
GUARD_Y = plan.CLIFF_ROWS - 1                               # les gardes tiennent la trouée de la falaise : le passage le plus étroit
ROAD = [PX(32)]
while walkable((ROAD[0] - 1, GUARD_Y)): ROAD.insert(0, ROAD[0] - 1)
while walkable((ROAD[-1] + 1, GUARD_Y)): ROAD.append(ROAD[-1] + 1)
for x in ROAD:
    for j in (-1, 0, 1): KEEP.add((x, GUARD_Y + j))
    if not walkable((x, GUARD_Y)): WARN.append(('gardes', x, GUARD_Y, 'la rangée des gardes est encombrée'))
if len(ROAD) > 9: WARN.append(('gardes', ROAD[0], GUARD_Y, 'chaussée trop large pour deux gardes : %d cases' % len(ROAD)))
keep_rect(31, 30, 34, 42)                                   # l'allée de la place à la jetée
TALL = [R(6, 40, 13, 43), R(13, 14, 16, 15)] + plan.TALL_MORE
NO_TREE = {(x, y) for (x0, y0, x1, y1) in TALL for x in range(x0 - 1, x1 + 2) for y in range(y0 - 1, y1 + 2)}
NO_TREE |= {(x + i, y + j) for (x, y) in FURN_ALL for i in (-1, 0, 1) for j in (-1, 0, 1)}      # rien ne pousse contre le mobilier

def _path(a, b):
    prev = {a: a}; q = collections.deque([a])
    while q:
        c = q.popleft()
        if c == b: break
        for d in NEIGH4:
            n = (c[0] + d[0], c[1] + d[1])
            if n not in prev and inb(*n) and step_ok(c, n): prev[n] = c; q.append(n)
    if b not in prev: WARN.append(('couloir', b[0], b[1], 'inatteignable')); return []
    out = [b]
    while out[-1] != a: out.append(prev[out[-1]])
    return out
BELL = P(20, 26)                     # dans l'eau, au nord du ponton de l'ouest
if not open_sea(*BELL) or (BELL[0], BELL[1] + 1) not in DECK: WARN.append(('cloche', BELL[0], BELL[1], 'la cloche doit être dans l eau, juste au nord du ponton'))
PLACES = {'bibliothèque': (LIB[0], LIB[1] + 1), 'labo': (LAB[0], LAB[1] + 1), 'maison orange NO': (OSMALL[0], OSMALL[1] + 1), 'maison orange SE': (OBIG[0], OBIG[1] + 1),
          'ponton de la cloche': (BELL[0], BELL[1] + 1), 'place': P(32, 28), 'jetée': P(32, 44), 'hautes herbes': P(14, 41), 'route du nord': P(32, 6),
          'plage ouest': P(10, 33), 'plage sud-est': (42, 42), 'herbes NO': P(14, 15), 'crique du nord': (30, 9)}
for goal in PLACES.values():
    for c in _path(START, goal): KEEP.add(c)
KEEP = {c for c in KEEP if not in_padding(*c)}          # la marge n'est à personne : rien n'y est réservé

HARD = set(L['Houses']) | set(L['Cliffs']) | PLAT_EDGE | set(OBJECTS.values()) | STAIRS | FURN_SOLID | FURN_ALL
def can_grow(x, y): return is_land(x, y) and (x, y) not in BLOCKED and (x, y) not in HARD and (x, y) not in KEEP and (x, y) not in NO_TREE

# ============================================================ la végétation
# --- arbres (source 6, 3x3 ancrés au centre ; pied : les deux rangées du bas).
# Toujours en retrait de l'eau, jamais devant un bâtiment, jamais à cheval sur un bord de plateau.
# Pas d'arbre à fruits : c'est un arbre spécial. ---
ROUND = [15, 18, 21]
def feet_of(x, y): return [(x + i, y + j) for j in (0, 1) for i in (-1, 0, 1)]
def plant(x, y, t):
    L['Trees'][(x, y)] = (6, t, 0)
    for c in feet_of(x, y):
        if inb(*c): BLOCKED.add(c)
def over_house(x, y, w=1, h=1): return any((x + i, y + j) in L['Houses'] for i in range(-w, w + 1) for j in range(-h, h + 1))
def level_ok(cells):          # tout sur le dessus d'un plateau, ou tout au sol
    cells = [c for c in cells if inb(*c)]
    return all(c in PLAT_TOP for c in cells) or not any(c in PLAT for c in cells)
def forest_ok(x, y, keep=True):          # en lisière, les pieds de deux voisins peuvent se chevaucher
    cells = {(min(max(c[0], 0), W - 1), min(max(c[1], 0), H - 1)) for c in feet_of(x, y)}     # hors carte : on juge sur la case du bord
    return not over_house(x, y) and level_ok(feet_of(x, y)) and \
        all(is_grass(*c) and c not in HARD and (not keep or c not in KEEP) and c not in NO_TREE and dry(c[0], c[1], 3) and c not in L['Bridges'] for c in cells)
def lone_ok(x, y):            # un arbre isolé ne chevauche rien
    return not over_house(x, y) and level_ok(feet_of(x, y)) and all(can_grow(*c) and is_grass(*c) and dry(c[0], c[1], 3) for c in feet_of(x, y))
# rideau au pied de la falaise du nord : en dents de scie, pas tiré au cordeau
for k, x in enumerate(range(0, W + 1, 2)):
    for y in (plan.CLIFF_ROWS + (k % 2), plan.CLIFF_ROWS):
        if forest_ok(x, y) and not (PX(29) <= x <= PX(36)):
            plant(x, y, random.choice(ROUND + [12])); break
# ceintures boisées de la marge : en quinconce, cimes qui se recouvrent
for k, y in enumerate(range(1, H + 2, 2)):
    for x in range(k % 2, W + 2, 2):
        if in_padding(min(x, W - 1), min(y, H - 1)) and y > plan.CLIFF_ROWS + 1 and forest_ok(x, y):
            plant(x, y, random.choice(ROUND + ROUND + [12]))
# quelques arbres posés exprès : contre une maison, au fond d'un plateau, pour border un passage
for (x, y, t) in [(19, 7, 18), (19, 9, 15), (47, 7, 21), (47, 9, 12), (56, 36, 18), (56, 38, 21), (55, 33, 15),
                  (5, 13, 21), (5, 15, 15), (60, 13, 18), (5, 40, 15), (17, 42, 12), (19, 42, 18), (61, 16, 21), (2, 13, 15)]:
    if lone_ok(*P(x, y)): plant(*P(x, y), t)

# --- palmiers (source 6, 4x4 : le dessin fait 53 px de large ; pied : la case sous l'ancre).
# Sur le sable sec, à deux cases de l'eau au moins, jamais dans un passage, espacés. ---
palm_feet = []
cands = [(x, y) for y in range(H) for x in range(W) if is_sand(x, y)]
random.shuffle(cands)
for foot in cands:
    if can_grow(*foot) and foot not in PLAT and not in_padding(*foot) and foot[1] >= 14 and dry(foot[0], foot[1], 3) and not pinches(foot) and not over_house(foot[0], foot[1] - 1, 2, 2) \
            and all(abs(foot[0] - a) + abs(foot[1] - b) >= 5 for a, b in palm_feet) and (foot[0], foot[1] - 1) not in L['Trees'] \
            and all(max(abs(foot[0] - a), abs(foot[1] - b)) > 3 for a, b in FURN_ALL) \
            and not any((foot[0] + i, foot[1] + j) in PLAT for i in (-2, -1, 0, 1) for j in (-3, -2, -1, 0)):
        L['Trees'][(foot[0], foot[1] - 1)] = (6, 30, 11); BLOCKED.add(foot); palm_feet.append(foot)

# --- petits sapins (une case sur deux de haut, pied solide), buissons et souches : au bord d'un bois ---
ROCKLET_T = (42, 29)
PINES = [(33, 0), (34, 0), (36, 0), (37, 0), (38, 0)]
BUSHES = [(40, 0), (41, 0), (40, 1)]
STUMPS = [(20, 9)]
def tall_prop(x, y, a): L['Props'][(x, y - 1)] = (5, a[0], a[1]); L['Props'][(x, y)] = (5, a[0], a[1] + 1)
def roof_above(x, y): return (x, y - 1) in L['Houses'] or (x, y - 1) in L['Props'] or (x, y - 1) in STAIRS or (x, y - 1) in L['Cliffs'] or (x, y - 1) in PLAT_EDGE or (x, y - 1) in OBJECTS.values() or (x, y - 1) in L['Bridges']
for y in range(plan.CLIFF_ROWS + 2, H):
    for x in range(W):
        c = (x, y)
        if is_grass(x, y) and can_grow(x, y) and not in_padding(x, y) and not in_padding(x, y - 1) and c not in L['Props'] and not roof_above(x, y) and not pinches(c) and dry(x, y, 3) and level_ok([c, (x, y - 1)]):
            near_wood = any((x + i, y + j) in BLOCKED for i, j in NEIGH8)
            r = random.random()
            if near_wood and r < 0.10: tall_prop(x, y, random.choice(PINES)); BLOCKED.add(c)
            elif near_wood and r < 0.17: L['Props'][c] = (5,) + random.choice(BUSHES + STUMPS); BLOCKED.add(c)

# --- quelques cailloux sur le sable sec, à l'écart des passages (ils sont solides, comme sur la première carte) ---
PEBBLES = [(39, 29), (40, 29), (41, 29)]
pebbled = []
cands = [(x, y) for y in range(H) for x in range(W) if is_sand(x, y)]
random.shuffle(cands)
for c in cands:
    if len(pebbled) >= 16: break
    if can_grow(*c) and not in_padding(*c) and dry(c[0], c[1], 2) and c not in PLAT and c not in L['Props'] and (c[0], c[1] + 1) not in L['Props'] and c not in L['Bridges'] \
            and not pinches(c) and all(abs(c[0] - a) + abs(c[1] - b) >= 6 for a, b in pebbled) and not any(is_grass(c[0] + i, c[1] + j) for i, j in NEIGH8):
        L['Props'][c] = (5,) + (random.choice(PEBBLES) if random.random() < 0.75 else ROCKLET_T); BLOCKED.add(c); pebbled.append(c)

# --- grandes fleurs (une case sur deux de haut) : aucune collision, on marche dessus ---
BLOOMS = [(0, 3), (1, 3), (2, 3), (3, 3), (5, 3), (7, 3)]
def lawn(x, y): return is_grass(x, y) and (x, y) not in BLOCKED and (x, y) not in L['Plaza'] and (x, y) not in L['Props'] and (x, y) not in L['Bridges'] and ((x, y) not in PLAT or (x, y) in PLAT_TOP)
for y in range(plan.CLIFF_ROWS + 2, H):
    for x in range(W):
        if lawn(x, y) and not in_padding(x, y) and not in_padding(x, y - 1) and (x, y) not in KEEP and (x, y) not in NO_TREE and not roof_above(x, y) and (x, y + 1) not in L['Props'] \
                and level_ok([(x, y), (x, y - 1)]) and random.random() < 0.09:
            tall_prop(x, y, random.choice(BLOOMS))

# ============================================================ les rochers
ROCKS2 = [(26, 32), (28, 32), (30, 32), (32, 32), (34, 32), (36, 32), (38, 32)]   # dans l'eau, 2x2 (le dernier est plus étroit)
LAND_ROCKS = [(32, 30), (26, 27), (34, 27)]    # sur la terre, 2x2 — jamais les rochers moussus : ce sont des obstacles spéciaux
ROCKLET = (42, 29)                             # sur la terre, une case
ROCKED = set()
def sea_free(c): return open_sea(*c) and c not in ROCKED and c not in L['Bridges'] and c != BELL
def rock_at(x, y):
    cells = [(x + i, y + j) for j in range(2) for i in range(2)]
    if not all(sea_free(c) for c in cells): return False
    ax, ay = random.choice(ROCKS2)
    for j in range(2):
        for i in range(2): L['Props'][(x + i, y + j)] = (5, ax + i, ay + j); ROCKED.add((x + i, y + j))
    return True
def pebble_at(c, k=3):
    if not sea_free(c): return False
    L['Props'][c] = small_rock(k); ROCKED.add(c); return True
# Une embouchure est barrée par une chaîne de rochers qui serpente d'une rive à l'autre : gros
# et petits mêlés, chacun touchant le précédent (par un côté ou par un coin), aucun aligné.
def chain(kind_, fixed, a, b):
    def at(pos, off): return (fixed + off, pos) if kind_ == 'v' else (pos, fixed + off)
    span = [p for p in range(a - 4, b + 5) if open_sea(*at(p, 0))]
    if not span: WARN.append(('barrière', fixed, a, 'pas d eau sur la ligne de la barrière')); return
    lo, hi = min(span), max(span)
    pos = lo; prev = None; smalls = 0          # prev : (premier décalage, dernier décalage) de l'élément précédent
    while pos <= hi:
        placed = False
        can_big = pos + 1 <= hi
        want_big = can_big and (smalls >= 1 or random.random() < 0.7)        # jamais deux petits de suite si un gros tient
        for big in ((True, False) if want_big else (False, True)):
            if big and not can_big: continue
            size = 2 if big else 1
            ends = pos == lo or pos + size > hi                               # aux deux bouts, l'élément tient la ligne : il touche la rive
            if ends: offs = [o for o in range(1 - size, 1)]
            else: offs = [o for o in range(prev[0] - size, prev[1] + 2)]      # il touche le précédent, par un côté ou par un coin
            if prev is not None: offs = [o for o in offs if o + size - 1 >= prev[0] - 1 and o <= prev[1] + 1]
            offs = [o for o in offs if o >= -2 and o + size - 1 <= 2]
            random.shuffle(offs)
            if prev is not None: offs.sort(key=lambda o: (o, o + size - 1) == prev)   # jamais dans l'alignement du précédent, si possible
            for o in offs:
                if big:
                    cells_ok = rock_at(*at(pos, o)) if kind_ == 'h' else rock_at(*at(pos, o))
                    if cells_ok: prev = (o, o + 1); pos += 2; smalls = 0; placed = True; break
                elif pebble_at(at(pos, o)): prev = (o, o); pos += 1; smalls += 1; placed = True; break
            if placed: break
        if not placed:
            WARN.append(('barrière', fixed, pos, 'aucun rocher ne tient ici')); pos += 1
for (k, fixed, a, b) in plan.BARRIERS: chain(k, fixed, a, b)
# de petits rochers autour des gros, pour casser la monotonie
for c in sorted(ROCKED):
    for (i, j) in random.sample(NEIGH8 + [(2, 0), (-2, 0), (0, 2), (0, -2), (2, 1), (-2, -1)], 3):
        q = (c[0] + i, c[1] + j)
        if random.random() < 0.08 and not any((q[0] + a, q[1] + b) in DECK for a in (-1, 0, 1) for b in (-1, 0, 1)): pebble_at(q, random.randrange(3))
# la barrière tient-elle ? depuis le bord de la carte, la mer libre ne doit pas rejoindre l'intérieur
edge = [(x, y) for y in range(H) for x in range(W) if (x in (0, W - 1) or y == H - 1) and open_sea(x, y) and (x, y) not in ROCKED]
seen = set(edge); q = collections.deque(edge)
while q:
    x, y = q.popleft()
    for d in NEIGH4:
        c = (x + d[0], y + d[1])
        if inb(*c) and c not in seen and kind(*c) == SEA and c not in ROCKED: seen.add(c); q.append(c)
INNER_SEA = P(26, 12)
if not open_sea(*INNER_SEA): WARN.append(('barrière', INNER_SEA[0], INNER_SEA[1], 'le point de contrôle de la mer intérieure n est pas dans l eau'))
if INNER_SEA in seen: WARN.append(('barrière', 0, 0, 'la mer du bord rejoint l intérieur : une barrière fuit'))

# ============================================================ la marge ne se foule pas
# Des arbres d'abord. Un rocher seulement là où un arbre ne peut pas pousser : sur le sable.
def reach_from(start):
    seen = {start}; q = collections.deque([start])
    while q:
        c = q.popleft()
        for d in NEIGH4:
            n = (c[0] + d[0], c[1] + d[1])
            if inb(*n) and n not in seen and step_ok(c, n): seen.add(n); q.append(n)
    return seen
def boulder(x, y):
    cells = [(x + i, y + j) for j in range(2) for i in range(2)]
    if not all(is_sand(*c) and c not in BLOCKED and c not in KEEP and c not in L['Props'] and c not in PLAT and c not in L['Bridges'] for c in cells): return False
    ax, ay = random.choice(LAND_ROCKS)
    for j in range(2):
        for i in range(2): L['Props'][(x + i, y + j)] = (5, ax + i, ay + j); BLOCKED.add((x + i, y + j))
    return True
def depth(c): return min(c[0], W - 1 - c[0], H - 1 - c[1])
SEALED = collections.Counter()
for _ in range(600):
    inside = [c for c in reach_from(START) if in_hard(*c)]
    if not inside: break
    x, y = max(inside, key=lambda c: (depth(c), c))           # la plus proche de la zone de jeu
    done = False
    if is_grass(x, y):
        for (ax, ay) in [(x + i, y - j) for j in (0, 1) for i in (-1, 0, 1)]:          # un arbre dont le pied couvre la case
            if (ax, ay) not in L['Trees'] and forest_ok(ax, ay, keep=False): plant(ax, ay, random.choice(ROUND + [12])); SEALED['arbre'] += 1; done = True; break
    if not done and is_sand(x, y):
        for (ox, oy) in ((0, 0), (-1, 0), (0, -1), (-1, -1)):
            if boulder(x + ox, y + oy): SEALED['rocher de plage'] += 1; done = True; break
    if not done:
        if (x, y) in L['Props'] or (x, y) in L['Bridges']: WARN.append(('marge', x, y, 'case de la marge atteignable et impossible à fermer')); break
        L['Props'][(x, y)] = (5,) + (random.choice(BUSHES) if is_grass(x, y) else ROCKLET); BLOCKED.add((x, y)); SEALED['buisson' if is_grass(x, y) else 'caillou'] += 1
MARGIN_OPEN = sorted(c for c in reach_from(START) if in_hard(*c))
if MARGIN_OPEN: WARN.append(('marge', MARGIN_OPEN[0][0], MARGIN_OPEN[0][1], '%d cases de la marge restent atteignables' % len(MARGIN_OPEN)))

# ============================================================ ni à pied, ni à la nage
# Le jour où le joueur saura nager, il passera de la terre à l'eau et de l'eau à la terre où il
# veut : une barrière de rochers ne vaut que si la plage, à son bout, est fermée elle aussi. On
# refait donc le parcours en amphibie, et on bouche ce qui fuit — un rocher dans l'eau, un rocher
# sur le sable, un arbre sur l'herbe.
def reach_amph(start, parents=None):
    seen = {start}; q = collections.deque([start])
    while q:
        c = q.popleft(); swimming = open_sea(*c)
        for d in NEIGH4:
            n = (c[0] + d[0], c[1] + d[1])
            if not inb(*n) or n in seen: continue
            if open_sea(*n): ok = n not in ROCKED
            elif swimming: ok = walkable(n) or n in STAIRS
            else: ok = step_ok(c, n)
            if ok:
                seen.add(n); q.append(n)
                if parents is not None: parents[n] = c
    return seen
SEAL_LOG = []
def escaped(c):
    """Sorti de la carte : à pied dans la marge interdite, ou à la nage jusqu'au bord."""
    return c[0] in (0, W - 1) or c[1] == H - 1 or (in_hard(*c) and not open_sea(*c))
# On ne bouche pas au hasard : on remonte le chemin de la fuite jusqu'à l'endroit où le nageur
# quitte la plage pour l'eau du large, et c'est cette case d'eau qui reçoit un rocher. La chaîne
# se prolonge ainsi le long de la rive, jusqu'au rocher de plage — sans rangée de cailloux alignés.
for _ in range(80):
    parents = {}
    out = [c for c in reach_amph(START, parents) if escaped(c)]
    if not out: break
    c = min(out, key=lambda c: (-depth(c), c))
    path = [c]
    while path[-1] in parents: path.append(parents[path[-1]])
    path.reverse()                                    # du départ vers la marge
    # la mer du large : celle qui touche le bord de la carte sans franchir un rocher
    outer = {(x, y) for y in range(H) for x in range(W) if (x in (0, W - 1) or y == H - 1) and open_sea(x, y) and (x, y) not in ROCKED}
    todo = collections.deque(outer)
    while todo:
        x, y = todo.popleft()
        for d in NEIGH4:
            n = (x + d[0], y + d[1])
            if inb(*n) and n not in outer and open_sea(*n) and n not in ROCKED: outer.add(n); todo.append(n)
    wet = [p for p in path if p in outer]
    done = False
    if wet:
        # le chemin passe par le large : c'est sa mise à l'eau qu'on bouche, d'un rocher
        first = wet[0]
        if pebble_at(first): SEALED['rocher dans l eau'] += 1; done = True; SEAL_LOG.append((first, c))
    else:
        # il n'accoste dans la marge que depuis les eaux de l'île : c'est la première case de marge qu'on ferme
        first = next(p for p in path if escaped(p))
        x, y = first
        if is_grass(x, y):
            for (ax, ay) in [(x + i, y - j) for j in (0, 1) for i in (-1, 0, 1)]:
                if (ax, ay) not in L['Trees'] and forest_ok(ax, ay, keep=False): plant(ax, ay, random.choice(ROUND + [12])); SEALED['arbre'] += 1; done = True; break
        elif is_sand(x, y):
            for (ox, oy) in ((0, 0), (-1, 0), (0, -1), (-1, -1)):
                if boulder(x + ox, y + oy): SEALED['rocher de plage'] += 1; done = True; break
        if not done and (x, y) not in L['Props'] and (x, y) not in L['Bridges'] and (x, y) not in KEEP and walkable((x, y)):
            L['Props'][(x, y)] = (5,) + (random.choice(BUSHES) if is_grass(x, y) else ROCKLET); BLOCKED.add((x, y)); SEALED['buisson' if is_grass(x, y) else 'caillou'] += 1; done = True
        if done: SEAL_LOG.append((first, c))
    if not done: WARN.append(('nage', first[0], first[1], 'fuite à la nage impossible à fermer, vers %s' % (c,))); break
SWIM_OPEN = sorted(c for c in reach_amph(START) if escaped(c))
if SWIM_OPEN: WARN.append(('nage', SWIM_OPEN[0][0], SWIM_OPEN[0][1], '%d cases de la marge restent atteignables à la nage' % len(SWIM_OPEN)))

# ============================================================ fleurs au sol, hautes herbes
spots = [(x, y) for y in range(plan.CLIFF_ROWS + 2, H) for x in range(W) if lawn(x, y)]
for _ in range(95):
    cx, cy = random.choice(spots); fam = random.randint(0, 10)
    for _ in range(random.randint(2, 5)):
        x, y = cx + random.randint(-2, 2), cy + random.randint(-1, 1)
        if lawn(x, y): L['Decorations'][(x, y)] = (5, min(11, max(0, fam + random.randint(0, 1))), random.choice((1, 2)))
for (x0, y0, x1, y1) in TALL:
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if is_grass(x, y) and (x, y) not in BLOCKED and (x, y) not in L['Props'] and (x, y) not in PLAT and (x, y + 1) not in L['Props'] and (x, y) not in L['Bridges']:
                L['Grass'][(x, y)] = (5, 6, 0); L['Decorations'].pop((x, y), None)

# ============================================================ contrôles d'ensemble
for c in LOOP_CELLS:
    if not walkable(c): WARN.append(('boucle', c[0], c[1], 'le tour de la place est bloqué'))
for (x, y), t in L['Trees'].items():
    if t[2] == 0 and over_house(x, y): WARN.append(('arbre', x, y, 'un arbre recouvre un bâtiment'))
for name, goal in PLACES.items():
    if goal not in reach_from(START): WARN.append(('lieu', goal[0], goal[1], name + ' inatteignable'))

def render(path, scale=1):
    from crop import save
    img = [[(30, 30, 40)] * (W * 16) for _ in range(H * 16)]
    def put(x, y, ax, ay, tw=1, th=1, ox=0, oy=0):
        for j in range(16 * th):
            Y = y * 16 + j + oy
            if not 0 <= Y < H * 16: continue
            src = A[1 + ay * 16 + j]; row = img[Y]
            for i in range(16 * tw):
                X = x * 16 + i + ox
                if 0 <= X < W * 16:
                    p = src[1 + ax * 16 + i]
                    if p[3] > 127: row[X] = p[:3]
    def put10(x, y, c):
        for j in range(16):
            for i in range(16):
                p = ISL_IMG[c][j][i]
                if p[3] > 127: img[y * 16 + j][x * 16 + i] = p[:3]
    def any_put(x, y, t):
        if t[0] == 10: put10(x, y, (t[1], t[2]))
        elif t[0] == 6 and t[2] == 11: put(x, y, t[1], t[2], 4, 4, -24, -24)
        elif t[0] == 6: put(x, y, t[1], t[2], 3, 3, -16, -16)
        else: put(x, y, t[1], t[2])
    for n in ['Ground', 'Paths', 'Relief', 'Plaza', 'Bridges', 'Decorations', 'Grass', 'Cliffs']:
        for (x, y), t in L[n].items(): any_put(x, y, t)
    world = [((y + (1 if (x, y + 1) in L['Props'] and t[0] == 5 and t[2] in (0, 3) else 0), 0), x, y, t) for (x, y), t in L['Props'].items()] \
        + [((y, 1), x, y, t) for (x, y), t in L['Houses'].items()] + [((y + 1, 2), x, y, t) for (x, y), t in L['Trees'].items()]
    for _, x, y, t in sorted(world, key=lambda v: v[0]): any_put(x, y, t)
    for name, c in OBJECTS.items():
        col = (255, 220, 60) if name.startswith('Lamp') else (200, 120, 60)
        for j in range(4, 12):
            for i in range(5, 11): img[c[1] * 16 + j][c[0] * 16 + i] = col
    save(path, img if scale == 1 else [[p for p in r for _ in range(scale)] for r in img for _ in range(scale)])

if __name__ == '__main__':
    print('carte %d x %d — avertissements : %d' % (W, H, len(WARN)))
    for w in WARN[:40]: print('  ', w)
    print('marge fermée par :', dict(SEALED))
    render(sys.argv[1] if len(sys.argv) > 1 else 'preview.png')
