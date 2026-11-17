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
from geography import W, H, CELLS, NEIGH4, NEIGH8, inb, rect, shape, tidy, SEA, BEACH, PLATEAU, LAND, SAND, RING, ROCK, ROCKY  # noqa: E402
from island_tiles import load, save  # noqa: E402

AT, SIZES = route_tiles.atlas(), route_tiles.sizes()
ROUTE, GRASS_SOURCE, VILLAGE = 11, 12, 14
WARN = []
RNG = random.Random(1711)          # le même tirage à chaque fois : relancer redonne la même île
INSIDE = PLATEAU - RING

# ============================================================ ce qu'on pose sur la géographie
# --- les maisons : nom -> (modèle de village.png, colonne de gauche, rangée du pied). La porte est sur la rangée du pied.
HOUSES = {'ludo': ('hut_left', 9, 8), 'north': ('hut_right', 14, 9), 'library': ('hut_left', 2, 29), 'lab': ('hall', 41, 8), 'south': ('hut_right', 41, 33)}
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
STAIRS = {'nord-ouest': (14, 13), 'nord-est': (39, 18), 'place': (26, 31), 'bibliotheque': (2, 33), 'sud-est': (36, 37)}
# --- et trois escaliers de côté, là où l'on passait par un ponton : (côté bas 'W' ou 'E', colonne de l'anneau d'herbe, rangée
#     du haut des marches). Trois rangées de marches, une barre de poteaux au-dessus et en dessous.
SIDE_STAIRS = {'place, depuis la crique': ('W', 20, 19), 'jardin, vers la plage du sud': ('E', 21, 37)}
STEPS = {(x + i, r + j) for x, r in STAIRS.values() for i in (1, 2, 3) for j in (0, 1)}          # deux rangées de marches : une par étage de la falaise
for side, gx, y0 in SIDE_STAIRS.values(): STEPS |= {(gx + i, y0 + j) for i in ((-1, 0) if side == 'W' else (0, 1)) for j in (0, 1, 2)}

# --- les pontons, larges de trois cases : (sens, x0, y0, x1, y1). Ils vont du dessus d'un plateau à l'autre.
DOCKS = [('V', 32, 43, 34, 48)]          # un seul : la jetée du sud, depuis la plage. On passe d'une terre à l'autre par les plages et leurs escaliers (Ludovic, 17/11/2026)
DECK = set().union(*[rect(*d[1:]) for d in DOCKS])
PIER_END = (33, 48)

# --- la sortie du nord : une piste de trois cases dans la forêt, qui mène à la Route 1. Trois cases, comme la piste de la
#     route : une route plus large est très rare (Ludovic, 17/11/2026).
#
#     **Collées par ce chemin, les deux cartes n'en font qu'une** : la colonne x de l'île est la colonne x + SEAM de la
#     Route 1, la rangée 0 de l'île suit sa rangée 49. Le décalage est choisi pour que le haut de l'île tombe sous la forêt
#     du bas de la route, à l'est de sa rivière — sinon la rivière déboucherait au milieu du plateau de Ludo.
SEAM = 41
ROAD = [3, 4, 5]
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
PATHS = [(ROAD[0], 0, ROAD[-1], 12),                                                                   # la sortie du nord, de la croisée des pistes au bord de la carte
         (9, 9, 11, 12), (3, 10, 18, 12),                                                              # nord-ouest : chez Ludo, chez Anselme, l'escalier
         (44, 9, 46, 12), (36, 10, 46, 12), (40, 13, 42, 17),                                          # nord-est : le laboratoire, ses deux escaliers
         (2, 30, 5, 32), (6, 30, 11, 32),                                                              # ouest : la bibliothèque, son escalier
         (9, 33, 11, 37), (9, 37, 20, 39),                                                             # de là au jardin, jusqu'à son escalier de côté
         (43, 34, 45, 36), (37, 34, 48, 36), (46, 28, 48, 36), (44, 37, 46, 46)]                        # sud-est : chez Solange, l'escalier, l'allée du banc, la presqu'île
TRAIL = tidy(set().union(*[rect(*r) for r in PATHS]) & INSIDE - MOUNTAIN - HOUSE_AREA)

# --- les hautes herbes
TALL = (rect(10, 41, 20, 43) | rect(49, 12, 52, 15)) & INSIDE - TRAIL - MOUNTAIN

# ============================================================ le sol
def tile(name, alt=0): return (ROUTE,) + AT[name] + (alt,)
L = {n: {} for n in ['Ground', 'Shore', 'Cliffs1', 'Cliffs2', 'Paths', 'Plaza', 'Decorations', 'Grass', 'Bridges', 'Props', 'Trees', 'Houses']}
ORDER = ['Ground', 'Shore', 'Cliffs1', 'Cliffs2', 'Paths', 'Plaza', 'Decorations', 'Grass', 'Bridges']
sand_shape, ring_shape, rock_shape, trail_shape, mount_shape = shape(SAND), shape(PLATEAU), shape(ROCKY), shape(TRAIL), shape(MOUNTAIN)
FAR = {c for c in SEA - SAND if all((c[0] + i, c[1] + j) not in SAND for i in range(-2, 3) for j in range(-2, 3))}
DEEP = tidy(FAR)
deep_shape = {c: (k if k in '123456789' else '5') for c, k in shape(DEEP).items()}          # le bloc d'eau profonde n'a pas de coins rentrants
# Les quatre coins rentrants du bloc de sable ne sont pas rangés comme ceux des falaises : sur la planche, l'eau de `sandi`
# est en bas à gauche, celle de `sandk` en haut à gauche. `shape` nomme les coins comme les falaises : on traduit.
SAND_CORNER = {'i': 'j', 'j': 'i', 'k': 'l', 'l': 'k'}
# Le bord du haut d'un plateau est de l'herbe, avec un liseré tout en haut : rien n'y dit « falaise ». Derrière lui, sur
# l'île, c'est la plage : on s'y tient, et l'on passe de l'un à l'autre (Ludovic, 17/11/2026). Il prend sa variante sans collision.
OPEN_EDGE = 'grass8'          # TOUJOURS : la rangée du haut d'un plateau est de l'herbe, on y marche. C'est le gradin de roche, derrière, qui arrête (Ludovic, 17/11/2026 : « tu n'arrêtes pas de la faire, cette erreur »)
ground, cliffs, shore = {}, {}, {}
for c in CELLS:
    if c in DEEP: ground[c] = 'deep' + deep_shape[c]
    elif c not in SAND: ground[c] = 'water'
    elif c not in LAND: ground[c] = 'water'; shore[c] = 'shore' + SAND_CORNER.get(sand_shape[c], sand_shape[c])          # le liseré : de l'eau, et par-dessus le bord du sable
    elif c in RING or (c in ROCK and rock_shape[c] == '5'): ground[c] = 'rock5'          # sous l'anneau d'herbe : le gradin de roche, comme sur la Route 1
    elif c in BEACH or c in ROCK: ground[c] = 'sand5'                                    # sous l'anneau de roche : le sable
    elif c in MOUNTAIN: ground[c] = 'rock5' if mount_shape[c] == '5' else 'lawn'
    else: ground[c] = 'trailC' if c in TRAIL else 'lawn'
    cliffs[c] = (['grass' + ring_shape[c]] if c in RING else []) + (['rock' + rock_shape[c]] if c in ROCK and rock_shape[c] != '5' else []) \
        + (['rock' + mount_shape[c]] if c in MOUNTAIN and mount_shape[c] != '5' else [])
for c in sorted(PAVED):          # le dallage de la place, bordé d'herbe
    k = shape(PAVED)[c]; L['Plaza'][c] = tile('paved' + k)

# ============================================================ escaliers et pontons
stairs, deck = {}, {}
MADE_TILES = set(route_tiles.cells())
for x, r in STAIRS.values():
    for i, name in enumerate(('stair7', None, None, None, 'stair9')):
        if name: stairs[(x + i, r - 1)] = name
    for j, flight in enumerate('UL'):          # une volée double, une rangée par étage de la falaise : l'herbe, puis la roche — deux rangées faites pour se suivre
        for i, k in enumerate('45556'): stairs[(x + i, r + j)] = 'stair%s%s' % (flight, k)
    for i, name in enumerate(('stair1', 'stair2', 'stair2', 'stair2', 'stair3')): stairs[(x + i, r + 2)] = name
    if any(ring_shape.get((x + i, r)) != '2' for i in range(5)): WARN.append(('escalier', (x, r), 'le bord du plateau n est pas droit sous l escalier : %s' % [ring_shape.get((x + i, r)) for i in range(5)]))
    if any(rock_shape.get((x + i, r + 1)) != '2' for i in (1, 2, 3)): WARN.append(('escalier', (x, r), 'l anneau de roche n est pas droit sous l escalier : %s' % [rock_shape.get((x + i, r + 1)) for i in range(5)]))
    if any((x + i, r + 2) not in BEACH for i in (1, 2, 3)): WARN.append(('escalier', (x, r), 'pas de plage au pied de l escalier'))
for where, (side, gx, y0) in SIDE_STAIRS.items():
    cols = [gx - 2, gx - 1, gx, gx + 1] if side == 'W' else [gx + 2, gx + 1, gx, gx - 1]          # le bas, la roche, l'herbe, le haut
    for x, i in zip(cols, (0, 1, 2, 3) if side == 'W' else (3, 2, 1, 0)):          # dans la planche : le bas est à gauche pour `W`, à droite pour `E`
        for y, j in [(y0 - 1, 0)] + [(y0 + k, 1) for k in range(3)] + [(y0 + 3, 2)]:
            if AT['stair%s%d%d' % (side, i, j)] in MADE_TILES: stairs[(x, y)] = 'stair%s%d%d' % (side, i, j)
    flank = '4' if side == 'W' else '6'
    if any(ring_shape.get((gx, y0 + j)) != flank or rock_shape.get((cols[1], y0 + j)) != flank for j in range(3)):
        WARN.append(('escalier de côté', where, 'le flanc du plateau n est pas droit : %s %s' % ([ring_shape.get((gx, y0 + j)) for j in range(3)], [rock_shape.get((cols[1], y0 + j)) for j in range(3)])))
    if any((cols[0], y0 + j) not in BEACH for j in range(3)): WARN.append(('escalier de côté', where, 'pas de plage au pied'))
for way, x0, y0, x1, y1 in DOCKS:
    for (x, y) in sorted(rect(x0, y0, x1, y1)):
        if way == 'V':
            low = y == y1 and (x, y + 1) not in DECK          # le dernier rang de planches, au bout
            deck[(x, y)] = {0: 'pier1' if low else 'pier4', 1: 'pier2' if low else 'pier5', 2: 'pier3' if low else 'pier6'}[x - x0]          # des planches de jetée, pas le tablier d'un pont (Ludovic, 17/11/2026)
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
NO_TREES = rect(37, 1, 40, 6) | {(48, 1), (48, 2)} | rect(20, 18, 34, 21)          # entre la montagne et le laboratoire : un passage, pas un bosquet (Ludovic, 17/11/2026)
KEEP = NO_TREES | TRAIL | TALL | PAVED | LOOP_CELLS | HOUSE_AREA | DECK | set(stairs) | {(d[0], d[1] + j) for d in DOORS.values() for j in (1, 2)} \
    | {(x + i, r - 1 - j) for x, r in STAIRS.values() for i in range(5) for j in (0, 1)} | {(gx + i, y0 + j) for side, gx, y0 in SIDE_STAIRS.values() for i in range(-3, 4) for j in range(-1, 4)} | {(c[0] + i, c[1] + j) for c in DECK for i, j in NEIGH8}
taken = set()
# la forêt de l'exemple, et une lisière tout le long des bords de la carte : elle la ferme, mieux qu'une rangée de sapins
FOREST = set(geo.FOREST) | {c for c in INSIDE if c[0] in (0, 1, W - 2, W - 1) or c[1] in (0, 1) or c[1] >= H - 4} | (rect(0, 0, 31, 2) & INSIDE)          # et tout le haut de la carte, sous la forêt de la Route 1
def plant(name, x, r):
    cells = [c for c in feet(name, x, r) if inb(c)]
    if any(c not in INSIDE or c in KEEP or c in MOUNTAIN or (c in taken and not name.startswith('tree')) for c in cells): return False
    sprites.append((name, x, r))
    if not name.startswith('tree'): taken.update(cells)          # deux arbres voisins se recouvrent : c'est la forêt
    return True
# --- la couture avec la Route 1. Un arbre du bas de la route dont le pied dépasse sous sa dernière rangée a sa suite ici :
#     on le replante tel quel, à la même colonne. Et aucun autre arbre de l'île ne dépasse au-dessus de sa rangée 0, là où
#     la route existe : il lui manquerait la cime de l'autre côté.
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location('route_1_layout', os.path.join(HERE, '..', 'route_1', 'layout.py'))
ROUTE_1 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(ROUTE_1)
SHARED = range(max(0, -SEAM), min(W, ROUTE_1.W - SEAM))          # les colonnes de l'île qui ont la route au-dessus d'elles
SEAM_TREES = sorted((x - SEAM, r - ROUTE_1.H, name) for name, x, r in ROUTE_1.sprites if name.startswith('tree') and r >= ROUTE_1.H and -3 < x - SEAM < W)
for x, r, name in SEAM_TREES:
    if not plant(name, x, r): WARN.append(('couture', (x, r), 'un arbre du bas de la Route 1 n a pas sa suite sur l île'))
# la sortie du nord est une trouée dans la forêt : des arbres serrés contre la piste, des deux côtés, comme au bas de la
# route, pour qu'on ne contourne pas les gardes par l'herbe
for r in (2, 4, 6, 8):
    plant('treeA', ROAD[0] - 3, r); plant('treeA', ROAD[-1] + 1, r)
# la forêt : un arbre toutes les quatre colonnes, la rangée suivante décalée de deux, là où l'exemple a de la forêt. Sous
# la Route 1, sur les premières rangées, la trame est la sienne, prolongée : ses colonnes tombent en face des siennes.
for r in range(0, H + 1):
    for x in range(-2, W):
        if ((x + SEAM - 2 * ((r + 1) % 2)) if r <= 8 and x <= 36 else (x - 2 * (r % 2))) % 4: continue          # (jusqu'à la montagne : une trame qui change au milieu d'un bois y laisse une allée)
        if r < 2 and any(c in SHARED for c in range(x, x + 3)): continue          # au-dessus de la rangée 0, seuls les arbres de la route
        cells = [c for c in feet('treeA', x, r) if inb(c)]          # au bord de la carte, un arbre dépasse : seules comptent ses cases qui y sont
        if cells and sum(1 for c in cells if c in FOREST) * 3 >= len(cells) * 2: plant('treeB' if RNG.random() < 0.15 else 'treeA', x, r)
# quelques blocs sur la montagne, des rochers dans la mer là où l'exemple en a
for c in sorted(MOUNTAIN):
    if mount_shape[c] == '5' and all(mount_shape.get((c[0] + i, c[1] + j)) == '5' for i in (0, 1) for j in (-1, 0)) and RNG.random() < 0.12 \
            and not any((c[0] + i, c[1] + j) in taken for i in (-1, 0, 1, 2) for j in (-2, -1, 0, 1)):
        sprites.append(('boulder', c[0], c[1])); taken.update(feet('boulder', *c))
# Les rochers de la mer sont ceux de l'exemple, là où il les pose. Dans les cinq groupes que Ludovic a entourés (17/11/2026),
# quelques-uns de plus ferment l'eau où l'on entrera en surfant : on ne sortira pas de la carte. Jamais en ligne droite, et
# aucun ailleurs — chaque case d'eau du dedans est fermée par des rochers qui se touchent par un côté ou par un coin.
BARRIERS = {
    "l'ouest": [(4, 19), (3, 22)],
    "l'est": [(54, 17), (53, 18), (54, 21), (53, 22), (54, 23)],
    'la plage du sud-ouest': [(1, 46), (1, 47), (2, 48), (3, 49), (6, 49), (7, 48), (9, 48)],
    "l'ouest de la jetée": [(25, 46), (27, 49), (28, 48), (29, 49), (30, 48), (31, 49)],
    "l'est de la jetée": [(35, 48), (36, 49), (37, 48), (38, 49)],
}
FORMER_DOCKS = set().union(*[rect(*d) for d in [(8, 17, 10, 21), (8, 22, 21, 24), (15, 25, 17, 37), (40, 18, 42, 21), (36, 22, 48, 24), (46, 25, 48, 26)]])          # les pontons de l'exemple, retirés : ce que l'exemple pose là, c'était leur bois, pas des rochers
PLANKS = DECK | FORMER_DOCKS
ROCKS = sorted(c for c in CELLS if geo.at(c) == '#' and c in SEA and c not in SAND and all((c[0] + i, c[1] + j) not in PLANKS and (c[0] + i, c[1] + j) not in deck for i in (-1, 0, 1) for j in (-1, 0, 1)))
ROCKS = [c for n, c in enumerate(ROCKS) if not ((c[0] - 1, c[1]) in ROCKS and n % 2)]
for where, more in BARRIERS.items():
    for c in more:
        if c not in SEA or c in DECK: WARN.append(('rocher', where, 'pas dans l eau : %s' % (c,)))
        elif c not in ROCKS: ROCKS.append(c)
for n, c in enumerate(ROCKS):
    sprites.append((('pebbleA', 'spire', 'pebbleB')[n % 3], c[0], c[1]))
# --- les palmiers des plages : là où l'exemple pose quelque chose sur le sable, espacés, jamais dans un passage
palms = []
COVE = rect(15, 9, 34, 18)          # la crique du nord : agrandie pour être une plage, pas une palmeraie — deux palmiers, pas plus (Ludovic, 17/11/2026)
NO_PALMS = rect(36, 22, 38, 33) | rect(33, 30, 35, 33) | rect(19, 29, 21, 34)          # les passages entre deux plages : on vient de les élargir, on n'y plante rien
def palm_ok(c): return c not in NO_PALMS and (c not in COVE or sum(1 for p in palms if p in COVE) < 2)
FURNISHED = rect(20, 12, 34, 17) | rect(22, 33, 31, 38) | rect(5, 34, 9, 38) | rect(29, 39, 37, 43)          # parasols et serviettes, Roland, le pied de la jetée : generate.py les pose là
for c in sorted(BEACH, key=lambda c: (c[1], c[0])):
    if geo.OBJECTS[c[1]][c[0]] != '#' or c in KEEP or c in FURNISHED or c in DECK or c in stairs or any((c[0] + i, c[1] + j) not in BEACH for i, j in NEIGH4): continue
    if any((c[0] + i, c[1] + j) in set(stairs) | DECK for i in range(-2, 3) for j in range(-2, 3)) or c[0] in ROAD and c[1] < 10: continue
    if palm_ok(c) and all(abs(c[0] - p[0]) + abs(c[1] - p[1]) >= 5 for p in palms): palms.append(c)
# ...et sur les grandes plages, où l'exemple n'a rien posé (c'était de la forêt, ou de l'eau), d'autres au hasard : une plage
# nue paraît vide. Toujours à l'écart des escaliers, des passages, du mobilier, et jamais deux à moins de cinq cases.
for c in sorted(BEACH, key=lambda c: (c[1], c[0])):
    if c in KEEP or c in FURNISHED or c in DECK or any((c[0] + i, c[1] + j) not in BEACH for i, j in NEIGH4): continue
    if any((c[0] + i, c[1] + j) in set(stairs) | DECK for i in range(-2, 3) for j in range(-2, 3)): continue
    if RNG.random() < 0.5 and palm_ok(c) and all(abs(c[0] - p[0]) + abs(c[1] - p[1]) >= 4 for p in palms): palms.append(c)
for n, c in enumerate(palms):
    name = 'palm_big' if n % 3 == 1 else 'palm'
    sprites.append((name, c[0] - village_tiles.door(name), c[1])); taken.add(c)
# --- des massifs de buissons : aux coins de la place, et çà et là sur l'herbe
for wish in [ (50, 16), (44, 40), (3, 26), (12, 34)]:
    cells = [(wish[0] + i, wish[1]) for i in range(3)]
    if all(c in INSIDE and c not in KEEP and c not in taken and c not in MOUNTAIN for c in cells): sprites.append(('bush', wish[0], wish[1])); taken.update(cells)
for name, x, r in sprites:
    if name in village_tiles.PLANTS: L['Props'][(x, r)] = (VILLAGE,) + village_tiles.atlas()[name] + (0,)
    else: L['Trees' if name.startswith('tree') else 'Props'][(x, r)] = tile(name)
for name, (kind, x, r) in HOUSES.items(): L['Houses'][(x, r)] = (VILLAGE,) + village_tiles.atlas()[kind] + (0,)
# des fleurs, clairsemées, sur la pelouse
WOODS = {c for name, x, r in sprites if name.startswith('tree') for c in rect(x, r - 2, x + 2, r)}
WOODS |= {c for name, x, r in sprites if name in village_tiles.PLANTS for c in rect(x, r - village_tiles.sizes()[name][1] + 1, x + village_tiles.sizes()[name][0] - 1, r)}          # et sous une palme, un buisson
# --- les grandes fleurs, que le vent couche (`5:0-7,3-4` : un pied, une cime, on marche dedans) : par deux ou trois, près
#     de chaque maison et autour de la place, éparses. Elles ont leur propre tirage : en ajouter ne déplace rien d'autre.
BLOOM = random.Random(11)
FLOWER_CELLS, beds = set(), []
lawn = INSIDE - KEEP - taken - MOUNTAIN - WOODS - HOUSE_AREA - rect(9, 13, 14, 16)          # (pas sous le banc de Ludo, que generate.py pose là)
SCATTER = ([(0, 0), (2, 1)], [(1, 0), (0, 2), (3, 1)], [(0, 1), (2, 0)], [(0, 0), (1, 2)], [(0, 0), (2, 2), (3, 0)], [(0, 0)], [(1, 0), (0, 2)])
KINDS = (0, 1, 2, 3, 5, 7)
def bed(c, n):
    """Deux ou trois grandes fleurs éparses autour de `c` : jamais côte à côte, jamais en rang (Ludovic, 17/11/2026 : « pas en pack en ligne »)."""
    cells = [(c[0] + i, c[1] + j) for i, j in SCATTER[n % len(SCATTER)]]
    tops = [(x, y - 1) for x, y in cells]
    if any(q not in lawn or q in FLOWER_CELLS or q in L['Props'] for q in cells + tops) or any(abs(c[0] - b[0]) + abs(c[1] - b[1]) < 6 for b in beds): return False
    for k, (x, y) in enumerate(cells):
        kind = KINDS[(n + k) % len(KINDS)]
        L['Props'][(x, y)] = (5, kind, 4, 0); L['Props'][(x, y - 1)] = (5, kind, 3, 0)
    FLOWER_CELLS.update(cells + tops); beds.append(c); return True
spots = sorted(lawn); BLOOM.shuffle(spots)
for c in [c for c in spots if c in rect(20, 18, 34, 31)]:          # autour de la place
    if len(beds) < 3: bed(c, len(beds))
for d in sorted(DOORS.values()):                                   # près de chaque maison, au plus près de sa porte
    for c in sorted(spots, key=lambda c: (abs(c[0] - d[0]) + abs(c[1] - d[1]), c)):
        if abs(c[0] - d[0]) + abs(c[1] - d[1]) > 9 or bed(c, len(beds)): break
for c in spots:                                                    # et d'autres çà et là
    if len(beds) < 14: bed(c, len(beds)) or bed(c, len(beds) + 3) or bed(c, len(beds) + 5)
# --- des coquillages sur le sable sec, sans collision : rien sous un escalier, ni sous un parasol
SHELL, shells = random.Random(5), 0
for c in sorted(BEACH - KEEP - taken - FURNISHED - set(stairs) - DECK):
    if ground.get(c) == 'sand5' and SHELL.random() < 0.08:          # chacun son tour : au hasard, on ne voyait que des étoiles de mer
        L['Decorations'][c] = tile('shell%d' % (1 + shells % 4)); shells += 1
PLAZA_LAWN = rect(21, 19, 36, 31) & INSIDE
for c in sorted(INSIDE - KEEP - taken - MOUNTAIN - WOODS - FLOWER_CELLS):          # plus serrées autour de la place et sur la presqu'île du sud-est
    if RNG.random() < (0.3 if c in PLAZA_LAWN else (0.22 if c[1] >= 37 and c[0] >= 40 else 0.08)): L['Decorations'][c] = tile('fl%d' % RNG.randint(1, 5))

# ============================================================ ce qui bloque
SOLID = set(HOUSE_SOLID)
for c in CELLS:
    if c in DECK: continue
    if c in SEA or (any(route_tiles.blocks(n) and n != OPEN_EDGE for n in cliffs[c]) and c not in STEPS): SOLID.add(c)
for name, x, r in sprites: SOLID |= {c for c in feet(name, x, r) if inb(c)}
def free(c): return inb(c) and c not in SOLID
# Le bord du haut d'un plateau se foule — toujours. L'erreur est revenue deux fois (la rangée du haut fermée par une
# collision) : le générateur la refuse maintenant lui-même.
for c in sorted(PLATEAU):
    if ring_shape.get(c) == '8' and c in SOLID and not any(c in feet(n, x, r) for n, x, r in sprites) and c not in HOUSE_SOLID:
        WARN.append(('bord du haut', c, 'la rangée du haut du plateau est fermée : elle doit se fouler')); break
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
