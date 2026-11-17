"""La géographie de l'île de départ, lue sur sa carte d'exemple (reference.png).

Ce module ne s'exécute pas seul : `layout.py` l'importe. `python3 geography.py --read` relit
l'image et réécrit `classes.json` ; sans cela on travaille sur ce fichier, qui est versionné.

L'exemple de l'île n'est **pas reproduit tuile pour tuile** : ses arbres, ses huttes et ses
pontons viennent de planches que le projet n'a pas, et l'île du jeu a une place et une cloche
que l'exemple n'a pas. On en garde la **géographie** — où est la mer, où sont les plages, où
sont les terres en hauteur, où passent les chemins, où pousse la forêt — et on la pose avec
les tuiles de la Route 1 (`route.png`).

Chaque case de l'exemple est rangée dans une classe d'après ses couleurs :

    ~ mer        : plage (sable clair)      _ chemin (sable sombre)      . herbe
    T forêt (t : en partie)      H toit (h : en partie)      # roche ou bois      ? autre

et l'on note à part les cases où **quelque chose est posé sur le terrain** (`read_objects`).

De là, trois niveaux : la **mer**, les **plages** (au ras de l'eau, de sable) et les
**plateaux** (toute l'herbe, cernée d'une falaise d'une case). Puis ce que l'exemple ne peut pas
dire et que le jeu demande — retouches, pontons, escaliers, maisons, place — est déclaré ici,
à la main, en clair.
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
CLASSES = os.path.join(HERE, 'classes.json')


def read_reference():
    """Range chaque case de l'exemple dans une classe, d'après la couleur de ses 256 pixels."""
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    from island_tiles import load
    w, h, ref = load(os.path.join(HERE, 'reference.png'))
    def kind(p):
        r, g, b = p[:3]
        if b > r + 15 and b >= g - 25 and g > r: return '~'
        if r > 215 and g > 205 and b > 140 and r - b < 95 and g > b: return ':' if b > 170 else '_'
        if r > 200 and 100 < g < 180 and b < 110: return 'H'
        if g > r and g > b: return '.' if g > 175 else 'T'
        if r >= g >= b and r - b > 25: return '#' if r < 200 else '_'
        return '?'
    rows = []
    for cy in range(h // 16):
        row = ''
        for cx in range(w // 16):
            top = collections.Counter(kind(ref[cy * 16 + j][cx * 16 + i]) for j in range(16) for i in range(16)).most_common(1)[0]
            row += top[0] if top[1] >= 100 else (top[0].lower() if top[0] in 'TH' else top[0])
        rows.append(row)
    return {'classes': rows, 'objects': read_objects(ref, w, h, load)}


def read_objects(ref, w, h, load):
    """Les cases de l'exemple où quelque chose est posé sur le terrain : un arbre, une hutte, un ponton, un personnage.

    Le **terrain** de l'exemple — herbe, sable, eau, falaises, chemins — est fait des tuiles de
    `sources/seasons_trees_ponds.png` ; ce qui est posé dessus vient de planches que le projet n'a
    pas. Une case que les tuiles de cette planche expliquent en entier, du dessus vers le dessous,
    est du terrain nu ; les autres portent un objet ('#').
    """
    sw, sh, px = load(os.path.join(ROOT, 'src', 'main', 'kotlin', 'fr', 'skyle', 'pokeludoworld', 'assets', 'levels', 'sources', 'seasons_trees_ponds.png'))
    tiles, probe = set(), (0, 5, 10, 15, 34, 51, 68, 85, 102, 119, 120, 136, 153, 170, 187, 204, 221, 238, 240, 255, 17, 30, 225, 72, 183)
    for y in range(0, sh - 15, 16):
        for x in range(0, sw - 15, 16):
            t = tuple((tuple(px[y + j][x + i][:3]) if px[y + j][x + i][3] == 255 else None) for j in range(16) for i in range(16))
            if sum(1 for p in t if p is not None) >= 6: tiles.add(t)
    tiles = sorted(tiles, key=str); index = collections.defaultdict(list)
    for n, t in enumerate(tiles):
        for k in probe:
            if t[k] is not None: index[(k, t[k])].append(n)
    rows = []
    for cy in range(h // 16):
        row = ''
        for cx in range(w // 16):
            cell = [tuple(ref[cy * 16 + j][cx * 16 + i][:3]) for j in range(16) for i in range(16)]
            done = [False] * 256
            while not all(done):
                best = None
                for n in {n for k in probe if not done[k] for n in index.get((k, cell[k]), ())}:
                    t = tiles[n]; new = 0
                    for k in range(256):
                        if t[k] is None or done[k]: continue
                        if t[k] != cell[k]: new = -1; break
                        new += 1
                    if new >= 6 and (best is None or new > best[0]): best = (new, n)
                if best is None: break
                for k in range(256):
                    if tiles[best[1]][k] is not None: done[k] = True
            row += '.' if all(done) else '#'
        rows.append(row)
    return rows


if '--read' in sys.argv:
    json.dump(read_reference(), open(CLASSES, 'w'), indent=0)
READ = json.load(open(CLASSES))
G, OBJECTS = READ['classes'], READ['objects']
W, H = len(G[0]), len(G)
CELLS = [(x, y) for y in range(H) for x in range(W)]
NEIGH4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
NEIGH8 = [(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i, j) != (0, 0)]
def inb(c): return 0 <= c[0] < W and 0 <= c[1] < H
def rect(x0, y0, x1, y1): return {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
def at(c): return G[c[1]][c[0]]

SEA = {c for c in CELLS if at(c) == '~'}
BEACH = {c for c in CELLS if at(c) == ':'}
PLATEAU = set(CELLS) - SEA - BEACH
TRAIL = {c for c in CELLS if at(c) == '_'}
FOREST = {c for c in CELLS if OBJECTS[c[1]][c[0]] == '#'}          # sur un plateau, ce qui est posé sur l'herbe est presque toujours un arbre

# ============================================================ ce que l'exemple ne dit pas : les retouches
# Dans l'ordre : chaque ligne range un rectangle (x0, y0, x1, y1, bornes comprises) dans un niveau.
SEA_, BEACH_, PLATEAU_ = 'sea', 'beach', 'plateau'
RETOUCH = [
    # --- les pontons et les rochers de l'exemple sont du bois et de la pierre posés sur la mer : dessous, c'est la mer
    (SEA_, (0, 18, 12, 22)), (SEA_, (8, 23, 20, 24)), (SEA_, (14, 25, 20, 33)), (SEA_, (13, 34, 21, 36)), (SEA_, (0, 15, 0, 16)),
    (SEA_, (37, 19, 41, 22)), (SEA_, (37, 23, 50, 24)), (SEA_, (45, 25, 49, 25)), (SEA_, (51, 18, 54, 22)),
    (SEA_, (18, 46, 38, 49)), (SEA_, (0, 47, 17, 49)), (SEA_, (35, 41, 39, 47)), (SEA_, (50, 38, 54, 49)),
    # --- la trouée du nord : un couloir au ras de la plage, entre deux falaises, jusqu'au bord de la carte (vers la Route 1)
    (BEACH_, (23, 0, 27, 8)),
    # --- la plage du sud, d'un seul tenant, sans la mare que l'exemple y laisse
    (BEACH_, (22, 32, 35, 40)), (BEACH_, (36, 30, 38, 33)),
    (BEACH_, (30, 40, 36, 43)),                                                        # et une langue de sable plus large que la jetée : ses premières planches y reposent
    # --- les escaliers ne montent que face au sud : sous chacun, une anse de plage ; au-dessus, un bord de plateau tout droit
    (BEACH_, (14, 14, 18, 16)), (PLATEAU_, (19, 12, 19, 13)),                          # du plateau du nord-ouest à la crique
    (PLATEAU_, (30, 12, 36, 13)), (BEACH_, (31, 14, 35, 17)),                          # du plateau du nord-est à la crique
    (PLATEAU_, (21, 19, 35, 31)),                                                      # la place : un plateau d'un seul bloc, et son bord du sud
    (BEACH_, (2, 34, 7, 37)),                                                          # de la bibliothèque à la plage de l'ouest
    (PLATEAU_, (35, 36, 35, 37)), (BEACH_, (36, 38, 40, 40)),                          # du plateau du sud-est à la plage du sud
    # --- de quoi poser les maisons et faire arriver les pontons
    (PLATEAU_, (39, 27, 45, 34)), (PLATEAU_, (44, 26, 54, 27)), (PLATEAU_, (13, 37, 19, 38)), (PLATEAU_, (0, 24, 7, 29)),
    (PLATEAU_, (35, 16, 46, 18)), (SEA_, (36, 19, 46, 21)),                            # le plateau du nord-est finit droit, là où part son ponton
]
for level, r in RETOUCH:
    cells = rect(*r)
    SEA -= cells; BEACH -= cells; PLATEAU -= cells
    {SEA_: SEA, BEACH_: BEACH, PLATEAU_: PLATEAU}[level].update(cells)


# ============================================================ des formes que les tuiles savent dessiner
def shape(region):
    """Le nom de bord de chaque case d'une région : 7 8 9 / 4 5 6 / 1 2 3, coins rentrants i j k l, ou None si aucune tuile ne le dessine."""
    out = {}
    for c in region:
        n, s, w, e = [((c[0] + i, c[1] + j) in region or not inb((c[0] + i, c[1] + j))) for i, j in ((0, -1), (0, 1), (-1, 0), (1, 0))]
        if n and s and w and e:
            miss = [k for k, (i, j) in zip('lkji', ((-1, -1), (1, -1), (-1, 1), (1, 1))) if inb((c[0] + i, c[1] + j)) and (c[0] + i, c[1] + j) not in region]
            out[c] = '5' if not miss else (miss[0] if len(miss) == 1 else None)
        else:
            out[c] = {(False, True, False, True): '7', (False, True, True, True): '8', (False, True, True, False): '9', (True, True, False, True): '4', (True, True, True, False): '6',
                      (True, False, False, True): '1', (True, False, True, True): '2', (True, False, True, False): '3'}.get((n, s, w, e))
    return out


def tidy(region, grow=False):
    """Retire (ou, avec `grow`, comble) jusqu'à ce que chaque case de la région ait sa tuile de bord."""
    region = set(region)
    while True:
        bad = [c for c, k in shape(region).items() if k is None]
        if not bad: return region
        if grow: region |= {(c[0] + i, c[1] + j) for c in bad for i, j in NEIGH8 if inb((c[0] + i, c[1] + j))}
        else: region -= set(bad)


def parts(region):
    """Les morceaux d'un seul tenant d'une région."""
    left, out = set(region), []
    while left:
        seen, todo = set(), [next(iter(left))]
        while todo:
            c = todo.pop()
            if c in seen or c not in left: continue
            seen.add(c); todo += [(c[0] + i, c[1] + j) for i, j in NEIGH4]
        out.append(seen); left -= seen
    return out


for pocket in parts(SEA):            # une tache bleue au milieu des terres (une fenêtre, un personnage de l'exemple) n'est pas la mer
    if len(pocket) < 12: SEA -= pocket; PLATEAU |= pocket
for pocket in parts(BEACH):          # et une tache claire au milieu de l'herbe, loin de l'eau, n'est pas une plage
    if len(pocket) < 15 and not any((c[0] + i, c[1] + j) in SEA for c in pocket for i, j in NEIGH8): BEACH -= pocket; PLATEAU |= pocket
PLATEAU = tidy(PLATEAU)
for crumb in parts(PLATEAU):         # un rocher, un bout de ponton oublié : pas un plateau
    if len(crumb) < 12: PLATEAU -= crumb; SEA |= crumb
LAND = set(CELLS) - SEA          # ce que tidy a retiré d'un plateau retombe sur la plage
BEACH = LAND - PLATEAU
# Le sable déborde d'une case sur la mer — c'est le liseré : la case d'eau qui touche la terre porte le bord du sable.
SAND = tidy(LAND | {(c[0] + i, c[1] + j) for c in LAND for i, j in NEIGH8 if inb((c[0] + i, c[1] + j))}, grow=True)
for _ in range(4):          # une case de liseré cernée de sable de tous côtés n'est plus un bord : c'est de la plage
    full = {c for c, k in shape(SAND).items() if k == '5'} - LAND
    if not full: break
    LAND |= full; BEACH |= full
    SAND = tidy(LAND | {(c[0] + i, c[1] + j) for c in LAND for i, j in NEIGH8 if inb((c[0] + i, c[1] + j))}, grow=True)
SEA = set(CELLS) - LAND
RING = {c for c in PLATEAU if shape(PLATEAU)[c] != '5'}          # la falaise : le pourtour de chaque plateau
