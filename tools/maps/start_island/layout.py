"""Le plan de l'île de départ : de sa géographie aux calques de tuiles.

Ce module ne s'exécute pas seul : `generate.py` l'importe, écrit la scène et contrôle.
`geography.py` dit où sont la mer, les plages et les plateaux ; ici on les pose avec les tuiles
de la Route 1 (`route.png`, source 11) et les maisons de `village.png` (source 14), et l'on
calcule ce qui bloque (`SOLID`) et ce qu'on atteint à pied.

Trois niveaux, comme sur la Route 1 mais avec une plage :

  - la **mer** : pleine. Profonde au large, fondue dans l'eau claire par les bords de son bloc ;
  - la **plage** : du sable, au ras de l'eau, où l'on marche. Son bord ondule dans la case d'eau
    voisine (le liseré), qui reste pleine ;
  - les **plateaux** : toute l'herbe. Leur pourtour est une falaise d'une case (`RING`), pleine,
    sauf ses deux coins rentrants du haut. On y monte par un escalier, face au sud, ou par un
    ponton, qui va du dessus d'un plateau à l'autre.
"""
import collections
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools')); sys.path.insert(0, HERE)
import route_tiles  # noqa: E402
import village_tiles  # noqa: E402
import geography as geo  # noqa: E402
from geography import W, H, CELLS, NEIGH4, NEIGH8, inb, rect, shape, tidy, SEA, BEACH, PLATEAU, LAND, SAND, RING  # noqa: E402
from island_tiles import load, save  # noqa: E402

AT, SIZES = route_tiles.atlas(), route_tiles.sizes()
ROUTE, GRASS_SOURCE, VILLAGE = 11, 12, 14
WARN = []
RNG = random.Random(1711)          # le même tirage à chaque fois : relancer redonne la même île
INSIDE = PLATEAU - RING

# ============================================================ ce qu'on pose sur la géographie
# --- les maisons : nom -> (modèle de village.png, colonne de gauche, rangée du pied). La porte est sur la rangée du pied.
HOUSES = {'ludo': ('hut_left', 5, 8), 'north': ('hut_right', 10, 9), 'library': ('hut_left', 2, 29), 'lab': ('hall', 41, 8), 'south': ('hut_right', 40, 33)}
def box(name):
    kind, x, r = HOUSES[name]; w, h = village_tiles.sizes()[kind]
    return rect(x, r - h + 1, x + w - 1, r)
DOORS = {name: (x + village_tiles.door(kind), r) for name, (kind, x, r) in HOUSES.items()}
HOUSE_SOLID = set()
for name, (kind, x, r) in HOUSES.items():          # les murs et le bas du toit : quatre rangées ; on passe derrière le haut du toit
    HOUSE_SOLID |= rect(x, r - 3, x + village_tiles.sizes()[kind][0] - 1, r) - {DOORS[name]}
HOUSE_AREA = set().union(*[box(n) for n in HOUSES])

# --- la place : son dallage, le socle de la cloche au milieu du haut, le tour qu'en fait le coureur
PLAZA = (24, 22, 32, 27)          # x0, y0, x1, y1 du dallage
PAVED = rect(*PLAZA)
LOOP = [(PLAZA[0] - 1, PLAZA[1] - 1), (PLAZA[2] + 1, PLAZA[1] - 1), (PLAZA[2] + 1, PLAZA[3] + 1), (PLAZA[0] - 1, PLAZA[3] + 1)]
LOOP_CELLS = rect(LOOP[0][0], LOOP[0][1], LOOP[2][0], LOOP[2][1]) - rect(LOOP[0][0] + 1, LOOP[0][1] + 1, LOOP[2][0] - 1, LOOP[2][1] - 1)

# --- les escaliers : (colonne de gauche, rangée du bord). Cinq cases de large : un poteau, trois marches, un poteau.
STAIRS = {'nord-ouest': (14, 13), 'nord-est': (31, 13), 'place': (26, 31), 'bibliotheque': (2, 33), 'sud-est': (36, 37)}
STEPS = {(x + i, r) for x, r in STAIRS.values() for i in (1, 2, 3)}

# --- les pontons, larges de trois cases : (sens, x0, y0, x1, y1). Ils vont du dessus d'un plateau à l'autre.
DOCKS = [('V', 8, 17, 10, 21), ('H', 8, 22, 21, 24), ('V', 15, 25, 17, 37),          # du nord-ouest à la place, et de là au jardin du sud-ouest
         ('V', 40, 18, 42, 21), ('H', 36, 22, 48, 24), ('V', 46, 25, 48, 26),         # du nord-est à la place, et de là au sud-est
         ('V', 32, 43, 34, 48)]                                                       # la jetée du sud, depuis la plage
DECK = set().union(*[rect(*d[1:]) for d in DOCKS])
PIER_END = (33, 48)

# --- la trouée du nord : le couloir de plage qui mène à la Route 1
ROAD = [23, 24, 25, 26, 27]
NORTH_GATE = [(x, 0) for x in ROAD]
GUARD_Y = 3
START = (DOORS['ludo'][0], DOORS['ludo'][1] + 1)

# --- la montagne du nord-est : la roche de l'exemple, hors de la terrasse du laboratoire
MOUNTAIN = tidy(({c for c in rect(35, 0, 54, 9) if geo.at(c) == '#' and c in INSIDE} - rect(39, 1, 50, 9)) | rect(44, 0, 47, 0))          # et le mur du fond court d'un bout à l'autre, sans trou
for crumb in geo.parts(MOUNTAIN):
    if len(crumb) < 9: MOUNTAIN -= crumb

# --- les pistes : les chemins de l'exemple, plus ce qui mène aux portes, aux escaliers et aux pontons
# Trois cases de large, d'un seul tenant sur chaque plateau : plus étroite, une piste n'est que deux bords collés, et les
# chemins de l'exemple, lus case par case, donnaient des taches. On les trace donc à la main, là où l'exemple en a.
PATHS = [(5, 9, 7, 12), (5, 10, 18, 12), (8, 13, 10, 16),                                              # nord-ouest : chez Ludo, chez Anselme, l'escalier, le ponton
         (44, 9, 46, 12), (32, 10, 46, 12), (40, 13, 42, 17),                                          # nord-est : le laboratoire, l'escalier, le ponton
         (2, 30, 5, 32), (6, 30, 11, 32),                                                              # ouest : la bibliothèque, son escalier
         (14, 38, 18, 40),                                                                             # le jardin, au bout de son ponton
         (42, 34, 44, 36), (37, 34, 48, 36), (46, 27, 48, 36), (44, 37, 46, 46)]                        # sud-est : chez Solange, l'escalier, le ponton, la presqu'île
TRAIL = tidy(set().union(*[rect(*r) for r in PATHS]) & INSIDE - MOUNTAIN - HOUSE_AREA)

# --- les hautes herbes
TALL = (rect(10, 41, 20, 43) | rect(20, 38, 21, 40) | rect(14, 4, 18, 6) | rect(49, 12, 52, 15)) & INSIDE - TRAIL - MOUNTAIN

# ============================================================ le sol
def tile(name, alt=0): return (ROUTE,) + AT[name] + (alt,)
L = {n: {} for n in ['Ground', 'Shore', 'Cliffs1', 'Cliffs2', 'Paths', 'Plaza', 'Decorations', 'Grass', 'Bridges', 'Props', 'Trees', 'Houses']}
ORDER = ['Ground', 'Shore', 'Cliffs1', 'Cliffs2', 'Paths', 'Plaza', 'Decorations', 'Grass', 'Bridges']
sand_shape, ring_shape, trail_shape, mount_shape = shape(SAND), shape(PLATEAU), shape(TRAIL), shape(MOUNTAIN)
FAR = {c for c in SEA - SAND if all((c[0] + i, c[1] + j) not in SAND for i in range(-2, 3) for j in range(-2, 3))}
DEEP = tidy(FAR)
deep_shape = {c: (k if k in '123456789' else '5') for c, k in shape(DEEP).items()}          # le bloc d'eau profonde n'a pas de coins rentrants
# Les quatre coins rentrants du bloc de sable ne sont pas rangés comme ceux des falaises : sur la planche, l'eau de `sandi`
# est en bas à gauche, celle de `sandk` en haut à gauche. `shape` nomme les coins comme les falaises : on traduit.
SAND_CORNER = {'i': 'j', 'j': 'i', 'k': 'l', 'l': 'k'}
# Le bord du haut d'un plateau est de l'herbe, avec un liseré tout en haut : rien n'y dit « falaise ». Derrière lui, sur
# l'île, c'est la plage : on s'y tient, et l'on passe de l'un à l'autre (Ludovic, 17/11/2026). Il prend sa variante sans collision.
OPEN_EDGE = 'grass8'
ground, cliffs, shore = {}, {}, {}
for c in CELLS:
    if c in DEEP: ground[c] = 'deep' + deep_shape[c]
    elif c not in SAND: ground[c] = 'water'
    elif c not in LAND: ground[c] = 'water'; shore[c] = 'shore' + SAND_CORNER.get(sand_shape[c], sand_shape[c])          # le liseré : de l'eau, et par-dessus le bord du sable
    elif c in BEACH or c in RING: ground[c] = 'sand5'
    elif c in MOUNTAIN: ground[c] = 'rock5' if mount_shape[c] == '5' else 'lawn'
    else: ground[c] = 'trailC' if c in TRAIL else 'lawn'
    cliffs[c] = (['grass' + ring_shape[c]] if c in RING else []) + (['rock' + mount_shape[c]] if c in MOUNTAIN and mount_shape[c] != '5' else [])
for c in sorted(PAVED):          # le dallage de la place, bordé d'herbe
    k = shape(PAVED)[c]; L['Plaza'][c] = tile('paved' + k)

# ============================================================ escaliers et pontons
stairs, deck = {}, {}
for x, r in STAIRS.values():
    for i, name in enumerate(('stair7', None, None, None, 'stair9')):
        if name: stairs[(x + i, r - 1)] = name
    for i, name in enumerate(('stair4', 'stair5', 'stair5', 'stair5', 'stair6')): stairs[(x + i, r)] = name
    for i, name in enumerate(('stair1', 'stair2', 'stair2', 'stair2', 'stair3')): stairs[(x + i, r + 1)] = name
    if any(ring_shape.get((x + i, r)) != '2' for i in range(5)): WARN.append(('escalier', (x, r), 'le bord du plateau n est pas droit sous l escalier : %s' % [ring_shape.get((x + i, r)) for i in range(5)]))
    if any((x + i, r + 1) not in BEACH for i in range(5)): WARN.append(('escalier', (x, r), 'pas de plage au pied de l escalier'))
for way, x0, y0, x1, y1 in DOCKS:
    for (x, y) in sorted(rect(x0, y0, x1, y1)):
        if way == 'V':
            low = y == y1 and (x, y + 1) not in DECK          # le dernier rang de planches, au bout
            deck[(x, y)] = {0: 'bridgeV1' if low else 'bridgeV4', 1: 'bridgeV5', 2: 'bridgeV3' if low else 'bridgeV6'}[x - x0]
        else:
            deck[(x, y)] = {0: 'bridgeH8', 1: 'bridgeH5', 2: 'bridgeH1' if x == x0 else 'bridgeH2'}[y - y0]
    if way == 'H':          # le dessous d'un ponton en travers déborde sur la rangée d'en dessous, là où c'est de l'eau
        for x in range(x0, x1 + 1):
            c = (x, y1 + 1)
            if c not in DECK and c not in LAND: deck[c] = 'lipL' if (x - 1, y1 + 1) in DECK | LAND or x == x0 else ('lipR' if (x + 1, y1 + 1) in DECK | LAND or x == x1 else 'lip')
for c in sorted(DECK):
    if c in PLATEAU and c not in RING: WARN.append(('ponton', c, 'le ponton recouvre le dessus d un plateau'))

for c in CELLS:
    free = 1 if c in DECK or c in STEPS or c in BEACH or c in RING else 0          # sous un ponton ou un escalier, sur la plage, et sous une falaise (c'est elle qui arrête) : le même dessin, sans collision
    L['Ground'][c] = tile(ground[c], free if route_tiles.blocks(ground[c]) else 0)
    if c in shore: L['Shore'][c] = tile(shore[c])
    for k, name in enumerate(cliffs[c][:2]): L['Cliffs%d' % (k + 1)][c] = tile(name, (1 if c in DECK or c in STEPS or name == OPEN_EDGE else 0) if route_tiles.blocks(name) else 0)
    if c in TRAIL and trail_shape[c] != '5': L['Paths'][c] = tile('trail' + trail_shape[c])
    if c in TALL: L['Grass'][c] = (GRASS_SOURCE, 6, 0, 0)
    if c in deck: L['Bridges'][c] = tile(deck[c])
    elif c in stairs: L['Bridges'][c] = tile(stairs[c])

# ============================================================ ce qui est debout
def feet(name, x, r):
    if name.startswith('tree'): return [(x + i, r - j) for j in (1, 0) for i in range(3)]
    if name == 'boulder': return [(x, r - 1), (x + 1, r - 1), (x, r), (x + 1, r)]
    if name in ('conif', 'sapling', 'rock_s'): return [(x, r)]
    if name in village_tiles.PLANTS: return [(x + village_tiles.door(name), r)]          # le tronc
    return []
sprites = []
NO_TREES = rect(37, 1, 40, 6)          # entre la montagne et le laboratoire : un passage, pas un bosquet (Ludovic, 17/11/2026)
KEEP = NO_TREES | TRAIL | TALL | PAVED | LOOP_CELLS | HOUSE_AREA | DECK | set(stairs) | {(d[0], d[1] + j) for d in DOORS.values() for j in (1, 2)} \
    | {(x + i, r - 1 - j) for x, r in STAIRS.values() for i in range(5) for j in (0, 1)} | {(c[0] + i, c[1] + j) for c in DECK for i, j in NEIGH8}
taken = set()
# la forêt de l'exemple, et une lisière tout le long des bords de la carte : elle la ferme, mieux qu'une rangée de sapins
FOREST = set(geo.FOREST) | {c for c in INSIDE if c[0] in (0, 1, W - 2, W - 1) or c[1] in (0, 1) or c[1] >= H - 4}
def plant(name, x, r):
    cells = [c for c in feet(name, x, r) if inb(c)]
    if any(c not in INSIDE or c in KEEP or c in MOUNTAIN or (c in taken and not name.startswith('tree')) for c in cells): return False
    sprites.append((name, x, r))
    if not name.startswith('tree'): taken.update(cells)          # deux arbres voisins se recouvrent : c'est la forêt
    return True
# la forêt : un arbre toutes les quatre colonnes, la rangée suivante décalée de deux, là où l'exemple a de la forêt
for r in range(1, H + 1):
    for x in range(-2, W):
        if (x - 2 * (r % 2)) % 4: continue
        cells = [c for c in feet('treeA', x, r) if inb(c)]          # au bord de la carte, un arbre dépasse : seules comptent ses cases qui y sont
        if cells and sum(1 for c in cells if c in FOREST) * 3 >= len(cells) * 2: plant('treeB' if RNG.random() < 0.15 else 'treeA', x, r)
# quelques blocs sur la montagne, des rochers dans la mer là où l'exemple en a
for c in sorted(MOUNTAIN):
    if mount_shape[c] == '5' and all(mount_shape.get((c[0] + i, c[1] + j)) == '5' for i in (0, 1) for j in (-1, 0)) and RNG.random() < 0.12 \
            and not any((c[0] + i, c[1] + j) in taken for i in (-1, 0, 1, 2) for j in (-2, -1, 0, 1)):
        sprites.append(('boulder', c[0], c[1])); taken.update(feet('boulder', *c))
ROCKS = sorted(c for c in CELLS if geo.at(c) == '#' and c in SEA and c not in SAND and all((c[0] + i, c[1] + j) not in DECK and (c[0] + i, c[1] + j) not in deck for i in (-1, 0, 1) for j in (-1, 0, 1)))
for n, c in enumerate(ROCKS):
    if (c[0] - 1, c[1]) in ROCKS and n % 2: continue
    sprites.append((('pebbleA', 'spire', 'pebbleB')[n % 3], c[0], c[1]))
# --- les palmiers des plages : là où l'exemple pose quelque chose sur le sable, espacés, jamais dans un passage
palms = []
FURNISHED = rect(19, 9, 29, 13) | rect(22, 33, 31, 38) | rect(5, 34, 9, 38) | rect(29, 39, 37, 43)          # parasols et serviettes, Roland, le pied de la jetée : generate.py les pose là
for c in sorted(BEACH, key=lambda c: (c[1], c[0])):
    if geo.OBJECTS[c[1]][c[0]] != '#' or c in KEEP or c in FURNISHED or c in DECK or c in stairs or any((c[0] + i, c[1] + j) not in BEACH for i, j in NEIGH4): continue
    if any((c[0] + i, c[1] + j) in set(stairs) | DECK for i in range(-2, 3) for j in range(-2, 3)) or c[0] in ROAD and c[1] < 10: continue
    if all(abs(c[0] - p[0]) + abs(c[1] - p[1]) >= 5 for p in palms): palms.append(c)
for n, c in enumerate(palms):
    name = 'palm_big' if n % 3 == 1 else 'palm'
    sprites.append((name, c[0] - village_tiles.door(name), c[1])); taken.add(c)
# --- des massifs de buissons : aux coins de la place, et çà et là sur l'herbe
for wish in [(22, 30), (32, 30), (22, 19), (10, 15), (50, 16), (44, 40), (3, 26), (12, 34)]:
    cells = [(wish[0] + i, wish[1]) for i in range(3)]
    if all(c in INSIDE and c not in KEEP and c not in taken and c not in MOUNTAIN for c in cells): sprites.append(('bush', wish[0], wish[1])); taken.update(cells)
for name, x, r in sprites:
    if name in village_tiles.PLANTS: L['Props'][(x, r)] = (VILLAGE,) + village_tiles.atlas()[name] + (0,)
    else: L['Trees' if name.startswith('tree') else 'Props'][(x, r)] = tile(name)
for name, (kind, x, r) in HOUSES.items(): L['Houses'][(x, r)] = (VILLAGE,) + village_tiles.atlas()[kind] + (0,)
# des fleurs, clairsemées, sur la pelouse
WOODS = {c for name, x, r in sprites if name.startswith('tree') for c in rect(x, r - 2, x + 2, r)}
WOODS |= {c for name, x, r in sprites if name in village_tiles.PLANTS for c in rect(x, r - village_tiles.sizes()[name][1] + 1, x + village_tiles.sizes()[name][0] - 1, r)}          # et sous une palme, un buisson
PLAZA_LAWN = rect(21, 19, 36, 31) & INSIDE
for c in sorted(INSIDE - KEEP - taken - MOUNTAIN - WOODS):          # plus serrées autour de la place et sur la presqu'île du sud-est
    if RNG.random() < (0.3 if c in PLAZA_LAWN else (0.22 if c[1] >= 37 and c[0] >= 40 else 0.08)): L['Decorations'][c] = tile('fl%d' % RNG.randint(1, 5))

# ============================================================ ce qui bloque
SOLID = set(HOUSE_SOLID)
for c in CELLS:
    if c in DECK: continue
    if c in SEA or (any(route_tiles.blocks(n) and n != OPEN_EDGE for n in cliffs[c]) and c not in STEPS): SOLID.add(c)
for name, x, r in sprites: SOLID |= {c for c in feet(name, x, r) if inb(c)}
def free(c): return inb(c) and c not in SOLID
def reach_from(start, closed=()):
    seen, queue = {start}, collections.deque([start])
    while queue:
        c = queue.popleft()
        for i, j in NEIGH4:
            n = (c[0] + i, c[1] + j)
            if free(n) and n not in seen and n not in closed: seen.add(n); queue.append(n)
    return seen
# le bord de la carte ne s'atteint qu'à la trouée du nord : ailleurs on le ferme, d'un sapin sur l'herbe, d'un caillou sur le sable
for _ in range(6):
    edge = sorted(c for c in reach_from(START) if (c[0] in (0, W - 1) or c[1] in (0, H - 1)) and c not in NORTH_GATE)
    if not edge: break
    for c in edge:
        name = 'rock_s' if c in BEACH else 'conif'
        sprites.append((name, c[0], c[1])); L['Props'][c] = tile(name); SOLID.add(c)
def pinches(c):
    ring = [(c[0] + i, c[1] + j) for i, j in ((-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0))]
    open_ = [free(r) for r in ring]; group = list(range(8))
    def find(i):
        while group[i] != i: i = group[i]
        return i
    for i in range(8):
        if open_[i] and open_[(i + 1) % 8]: group[find(i)] = find((i + 1) % 8)
    return len({find(i) for i in range(8) if open_[i] and i % 2 == 1}) > 1
REACH = reach_from(START) if free(START) else set()
if not free(START): WARN.append(('départ', START, 'la case de départ est pleine'))

# ============================================================ aperçu
def render():
    sheets = {ROUTE: load(route_tiles.OUTPUT)[2], VILLAGE: load(village_tiles.OUTPUT)[2], 10: load(os.path.join(os.path.dirname(route_tiles.OUTPUT), 'island.png'))[2]}
    img = [[(0, 0, 0)] * (W * 16) for _ in range(H * 16)]
    def put(c, t, w=1, h=1, below=0):
        sheet = sheets[ROUTE if t[0] == GRASS_SOURCE else t[0]]
        ax, ay = (t[1], t[2] + 6) if t[0] == GRASS_SOURCE else t[1:3]
        for j in range(16 * (h + below)):
            Y = (c[1] - h + 1) * 16 + j
            if not 0 <= Y < H * 16: continue
            for i in range(16 * w):
                X = c[0] * 16 + i
                if not 0 <= X < W * 16: continue
                p = sheet[ay * 16 + j][ax * 16 + i]
                if p[3] == 255: img[Y][X] = tuple(p[:3])
                elif p[3]: img[Y][X] = tuple(int(round(img[Y][X][n] * (1 - p[3] / 255.0) + p[n] * p[3] / 255.0)) for n in range(3))
    for n in ORDER:
        for c, t in L[n].items(): put(c, t)
    names = {AT[n]: n for n in SIZES}
    standing = [((c[1], 0), c, t) for c, t in L['Trees'].items()] + [((c[1], 1), c, t) for c, t in L['Props'].items()] + [((c[1], -1), c, t) for c, t in L['Houses'].items()]
    for _, c, t in sorted(standing):
        if t[0] == VILLAGE:
            kind = [k for k, a in village_tiles.atlas().items() if a == t[1:3]][0]
            put(c, t, *village_tiles.sizes()[kind], below=village_tiles.drop(kind))
        elif t[0] == 10: put(c, t)
        else:
            n = names.get(t[1:3]); w, h = SIZES.get(n, (1, 1)); put(c, t, w, h, route_tiles.drop(n) if n else 0)
    return img


def write_preview(path, marks=()):
    img = render()
    for c, colour in marks:
        for j in range(5, 11):
            for i in range(5, 11): img[c[1] * 16 + j][c[0] * 16 + i] = colour
    save(path, [[p + (255,) for p in row] for row in img])


def show_map():
    print('    ' + ''.join(str(i // 10) for i in range(W))); print('    ' + ''.join(str(i % 10) for i in range(W)))
    for y in range(H):
        print('%2d  %s' % (y, ''.join('=' if (x, y) in DECK else ('S' if (x, y) in STEPS else ('~' if (x, y) in SEA else ('#' if (x, y) in SOLID else ('.' if (x, y) in REACH else '?')))) for x in range(W))))
