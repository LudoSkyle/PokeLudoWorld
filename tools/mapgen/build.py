#!/usr/bin/env python3
"""Le constructeur de cartes : un plan et un décor en entrée, une scène en sortie.

    python3 tools/mapgen/build.py tools/mapgen/plans/<carte>.toml            contrôle le plan, dit ce qui cloche
    python3 tools/mapgen/build.py <plan> --map                              montre ce qu'on atteint à pied
    python3 tools/mapgen/build.py <plan> --preview /tmp/carte.png           dessine la carte
    python3 tools/mapgen/build.py <plan> --write                            écrit scenes/levels/<carte>.tscn
    python3 tools/mapgen/build.py <plan> --write --out tests/maps/x.tscn    l'écrit ailleurs

**Il ne décide de rien et ne tire rien au hasard : le même plan donne toujours la même carte.** Tout ce qu'il y a
sur la carte est écrit dans le plan — le terrain case par case, les niveaux, chaque arbre, chaque fleur, chaque
personnage (`plans/README.md`). Toutes les textures sont dans le décor que le plan nomme (`themes/<décor>.toml`) :
quelle tuile dessine quoi, laquelle arrête, quelle place prend un arbre. Lui ne fait que **l'assemblage** :

  - les bords : chaque matière (falaise, sable, eau profonde, piste, dallage) prend la tuile de bord que demandent ses
    voisines ; la falaise a ses deux étages, le sable son liseré dans l'eau ;
  - les ouvrages : escaliers, ponts, jetées, rebords, clôtures, posés avec leurs tuiles ;
  - ce qui bloque, ce qu'on atteint à pied — et il prévient de tout ce qui ne se rejoint pas.

Qui écrit le plan ? Quelqu'un, à la main ; ou le générateur (`tools/mapgen/worldgen.py`), qui en invente un à partir
d'une graine et de quelques réglages.

Il crée la carte, il ne l'entretient pas : `--write` refuse d'écraser une scène qui existe (`--force` l'écrase, et
perd ce qui y a été retouché dans l'éditeur).
"""
import base64
import collections
import os
import struct
import sys
import tomllib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from island_tiles import load, save  # noqa: E402

GAME = os.path.join(ROOT, 'src', 'main', 'kotlin', 'fr', 'skyle', 'pokemonmirage') + os.sep
RES = 'res://src/main/kotlin/fr/skyle/pokemonmirage/'
NEIGH4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
NEIGH8 = [(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i, j) != (0, 0)]
OPEN_EDGE = 'grass8'          # TOUJOURS : la rangée du haut d'un plateau est de l'herbe, on y marche (docs/mapping.md, section J)

# Ce que dit chaque signe du plan du terrain.
TERRAIN = {'~': 'la mer', ':': 'le sable', '.': "l'herbe", '_': 'une piste', '"': 'les hautes herbes', '^': 'la montagne', 'o': 'un étang', ',': 'la terre nue', 'w': 'le blé', '#': "le vide : le noir autour d'une grotte"}
# Les signes réservés du plan des objets ; toute autre lettre ou chiffre est un repère, nommé dans le plan.
OBJECTS = {'.': 'rien', 'x': "un endroit à laisser dégagé", '=': 'un ponton ou un pont', '%': 'un dallage', 'f': 'un parc clôturé',
           'v': "un rebord qu'on saute vers le sud", '>': "un rebord qu'on saute vers l'est", '<': "un rebord qu'on saute vers l'ouest"}
# Le plan des niveaux, facultatif : sur un plateau, une terrasse est un cran plus haut que l'herbe qui l'entoure.
LEVELS = {'.': 'le niveau du plateau', '1': 'une terrasse, un cran plus haut', '2': 'une terrasse sur une terrasse', '3': 'trois crans', '4': 'quatre crans'}

# Le décor du plan en cours : ses tuiles, ce qui se pose, ses maisons, ses planches.
THEME, AT = {}, {}
ROUTE = GRASS_SOURCE = FLOWER_SOURCE = VILLAGE = 0


def load_theme(name):
    """Charge `themes/<name>.toml` : à partir de là, le constructeur sait quelle tuile dessine quoi."""
    global THEME, AT, ROUTE, GRASS_SOURCE, FLOWER_SOURCE, VILLAGE
    with open(os.path.join(HERE, 'themes', name + '.toml'), 'rb') as f:
        THEME = tomllib.load(f)
    AT = {n: (t[0], t[1]) for n, t in THEME['tiles'].items()}
    for n, p in THEME['props'].items():
        if p['source'] == 'main': AT[n] = tuple(p['at'])
    THEME.setdefault('buildings', {}); THEME.setdefault('props', {})
    def source(name): return THEME['sources'].get(name, {}).get('id', -1)          # (un décor peut n'avoir ni maisons, ni hautes herbes, ni grandes fleurs : une grotte)
    ROUTE, VILLAGE, GRASS_SOURCE, FLOWER_SOURCE = source('main'), source('buildings'), source('tall_grass'), source('blooms')


def raw(name):
    """`@10:15,3` : la tuile (15, 3) de la source 10 du TileSet, pour ce que le décor ne nomme pas. Sinon None."""
    if not name.startswith('@'): return None
    source, at = name[1:].split(':'); x, y = at.split(',')
    return (int(source), int(x), int(y))


def blocks(name):
    """La tuile `name` arrête-t-elle ? C'est le décor qui le dit."""
    return bool(THEME['tiles'].get(name, (0, 0, 0))[2])


class Plan:
    """Un plan lu : ses grilles, ses repères, ce qu'il pose, ses tables."""

    def __init__(self, path):
        with open(path, 'rb') as f:
            self.data = tomllib.load(f)
        self.path = path
        self.map = self.data['map']
        self.name = self.map['name']
        grids = {k: self.data.get(k, self.map.get(k, '')) for k in ('terrain', 'objects', 'levels', 'props')}          # avant ou après [map] : les deux se lisent
        # Les calques écrits tuile par tuile (`[[layer]]`) : une grille de signes, et sa légende — signe -> tuile du décor.
        self.layers = [(t['name'], t['grid'].strip('\n').split('\n'), t.get('legend', {})) for t in self.data.get('layer', [])]
        self.terrain = [line for line in grids['terrain'].strip('\n').split('\n')] if grids['terrain'].strip() else []
        if not self.terrain:          # un plan tout en calques : pas d'esquisse du terrain, tout est de l'herbe dessous
            if not self.layers: raise SystemExit('%s : ni terrain ni calque' % path)
            self.terrain = ['.' * len(self.layers[0][1][0])] * len(self.layers[0][1])
        self.H, self.W = len(self.terrain), len(self.terrain[0])
        things = grids['objects'].strip('\n')
        self.things = things.split('\n') if things else ['.' * self.W] * self.H
        levels = grids['levels'].strip('\n')
        self.levels = levels.split('\n') if levels else ['.' * self.W] * self.H
        self.errors = []
        for label, grid, known in (('terrain', self.terrain, TERRAIN), ('objects', self.things, None), ('levels', self.levels, LEVELS)):
            if len(grid) != self.H: self.errors.append('%s : %d rangées, le terrain en a %d' % (label, len(grid), self.H))
            for y, line in enumerate(grid):
                if len(line) != self.W: self.errors.append('%s, rangée %d : %d colonnes au lieu de %d' % (label, y, len(line), self.W))
                if known:
                    for x, sign in enumerate(line):
                        if sign not in known: self.errors.append('%s, case (%d, %d) : signe inconnu %r' % (label, x, y, sign))
        for name, grid, legend in self.layers:
            if len(grid) != self.H or any(len(line) != self.W for line in grid): self.errors.append('calque %s : sa grille ne fait pas %d x %d' % (name, self.W, self.H))
            for sign in {s for line in grid for s in line} - set(legend) - {'.'}: self.errors.append('calque %s : le signe %r n est pas dans sa légende' % (name, sign))
        self.props = []          # ce qui est posé : (sorte, colonne, rangée du pied), dans l'ordre du plan
        for n, line in enumerate(grids['props'].strip('\n').split('\n')):
            if not line.strip() or line.strip().startswith('#'): continue
            cells = line.split()
            if len(cells) not in (3, 4) or not cells[1].lstrip('-').isdigit() or not cells[2].lstrip('-').isdigit(): self.errors.append('props, ligne %d : attendu « sorte colonne rangée », lu %r' % (n + 1, line)); continue
            self.props.append((cells[0] + ('>' + cells[3] if len(cells) == 4 else ''), int(cells[1]), int(cells[2])))          # (une tuile brute dit aussi son calque)
        self.marks = collections.defaultdict(list)
        if not self.errors:
            for y, line in enumerate(self.things):
                for x, sign in enumerate(line): self.marks[sign].append((x, y))

    def cells(self, sign): return set(self.marks.get(sign, ()))

    def at(self, mark, what):
        """La case du repère `mark`, qui n'apparaît qu'une fois."""
        found = self.marks.get(mark, [])
        if len(found) != 1: self.errors.append('%s : le repère %r apparaît %d fois dans le plan des objets, il en faut une' % (what, mark, len(found)))
        return found[0] if found else (0, 0)

    def box(self, mark, what):
        """Le rectangle (x0, y0, x1, y1) que couvrent les cases du repère `mark`."""
        found = self.marks.get(mark, [])
        if not found: self.errors.append('%s : le repère %r n est pas dans le plan des objets' % (what, mark)); return (0, 0, 0, 0)
        return (min(c[0] for c in found), min(c[1] for c in found), max(c[0] for c in found), max(c[1] for c in found))

    def table(self, name): return self.data.get(name, [])


def build(plan):
    """Toute la carte : ses calques de tuiles, ses nœuds, ce qui bloque, ce qu'on atteint, et ce qui cloche."""
    load_theme(plan.map.get('theme', 'coast'))
    W, H = plan.W, plan.H
    CELLS = [(x, y) for y in range(H) for x in range(W)]
    warn = list(plan.errors)

    def inb(c): return 0 <= c[0] < W and 0 <= c[1] < H
    def rect(x0, y0, x1, y1): return {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
    def tile(name, alt=0): return (ROUTE,) + AT[name] + (alt,)
    def px(c): return (c[0] * 16 + 8, c[1] * 16 + 8)
    def around(cells, reach=1): return {(c[0] + i, c[1] + j) for c in cells for i in range(-reach, reach + 1) for j in range(-reach, reach + 1)}

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
            if grow: region |= {q for q in around(bad) if inb(q)}
            else: region -= set(bad)

    def parts(region):
        left, out = set(region), []
        while left:
            seen, todo = set(), [next(iter(left))]
            while todo:
                c = todo.pop()
                if c in seen or c not in left: continue
                seen.add(c); todo += [(c[0] + i, c[1] + j) for i, j in NEIGH4]
            out.append(seen); left -= seen
        return out

    # ============================================================ 1. la géographie : la mer, les plages, les plateaux
    sign = {c: plan.terrain[c[1]][c[0]] for c in CELLS} if not plan.errors else {c: '~' for c in CELLS}
    SEA = {c for c in CELLS if sign[c] == '~'}
    BEACH = {c for c in CELLS if sign[c] == ':'}
    PLATEAU = set(CELLS) - SEA - BEACH
    asked = set(PLATEAU)
    PLATEAU = tidy(PLATEAU)
    for crumb in parts(PLATEAU):          # un îlot d'herbe de quelques cases n'a pas la place d'une falaise : ce n'est pas un plateau
        if len(crumb) < 12: PLATEAU -= crumb; SEA |= crumb; warn.append('plateau trop petit pour sa falaise, laissé à la mer : %d cases vers %s' % (len(crumb), min(crumb)))
    # La falaise a deux étages : l'anneau d'herbe est le pourtour du plateau, l'anneau de roche l'entoure une case plus bas.
    ROCKY = tidy(PLATEAU | {q for q in around(PLATEAU) if inb(q)}, grow=True)
    ROCK = ROCKY - PLATEAU
    SEA -= ROCK
    LAND = set(CELLS) - SEA          # ce que tidy a retiré d'un plateau retombe sur la plage
    BEACH = LAND - PLATEAU - ROCK
    for pocket in parts(BEACH):          # une poche de sable de quelques cases, cernée de roche : c'est du gradin
        if len(pocket) < 8 and not any(q in SEA for q in around(pocket)): BEACH -= pocket; ROCK |= pocket; ROCKY |= pocket
    # Le sable déborde d'une case sur la mer — le liseré : la case d'eau qui touche la terre porte le bord du sable.
    SAND = tidy(LAND | {q for q in around(LAND) if inb(q)}, grow=True)
    for _ in range(4):          # une case de liseré cernée de sable de tous côtés n'est plus un bord : c'est de la plage
        full = {c for c, k in shape(SAND).items() if k == '5'} - LAND
        if not full: break
        LAND |= full; BEACH |= full - ROCK
        SAND = tidy(LAND | {q for q in around(LAND) if inb(q)}, grow=True)
    SEA = set(CELLS) - LAND
    plateau_shape = shape(PLATEAU)
    RING = {c for c in PLATEAU if plateau_shape[c] != '5'}
    INSIDE = PLATEAU - RING

    # ============================================================ 2. ce que le plan pose : maisons, escaliers, pontons, dallages, parcs
    houses, doors, house_solid, house_area = {}, {}, set(), set()
    for h in plan.table('house'):
        kind = h.get('kind', 'hut_left')
        if kind not in THEME['buildings']: warn.append('maison %s : le décor n a pas de modèle %r' % (h.get('name'), kind)); continue
        model = THEME['buildings'][kind]
        door = plan.at(h['mark'], 'maison %s' % h['name'])          # le repère est la case de la porte
        x, r = door[0] - model['door'], door[1]
        w, hh = model['size']
        houses[h['name']] = (kind, x, r, h); doors[h['name']] = door
        house_solid |= rect(x, r - 3, x + w - 1, r) - {door}          # les murs et le bas du toit : on passe derrière le haut du toit
        house_area |= rect(x, r - hh + 1, x + w - 1, r)
    stairs_at = [plan.at(s['mark'], 'escalier') for s in plan.table('stairs')]          # le repère : la colonne de gauche, sur la rangée du bord du plateau
    side_stairs = [(s['side'], *plan.at(s['mark'], 'escalier de côté')) for s in plan.table('side_stairs')]          # le repère : l'anneau d'herbe, rangée du haut des marches
    STEPS = {(x + i, r + j) for x, r in stairs_at for i in (1, 2, 3) for j in (0, 1)}
    for side, gx, y0 in side_stairs: STEPS |= {(gx + i, y0 + j) for i in ((-1, 0) if side == 'W' else (0, 1)) for j in (0, 1, 2)}
    docks = []
    for piece in parts(plan.cells('=')):
        x0, y0, x1, y1 = min(c[0] for c in piece), min(c[1] for c in piece), max(c[0] for c in piece), max(c[1] for c in piece)
        if piece != rect(x0, y0, x1, y1) or min(x1 - x0, y1 - y0) != 2: warn.append('ponton vers (%d, %d) : il faut un rectangle de trois cases de large' % (x0, y0)); continue
        way = 'V' if y1 - y0 >= x1 - x0 else 'H'
        # Un pont va du dessus d'un plateau à l'autre : à chaque bout où il touche la terre, il s'allonge par-dessus la
        # falaise (l'anneau de roche, puis l'anneau d'herbe) jusqu'à la première case où l'on marche.
        def lands(x, y): return (x, y) in LAND and (x, y) not in INSIDE and (x, y) not in BEACH
        for _ in range(3):
            if way == 'V' and y0 > 0 and all(lands(x, y0 - 1) for x in range(x0, x1 + 1)): y0 -= 1
            if way == 'V' and y1 < H - 1 and all(lands(x, y1 + 1) for x in range(x0, x1 + 1)): y1 += 1
            if way == 'H' and x0 > 0 and all(lands(x0 - 1, y) for y in range(y0, y1 + 1)): x0 -= 1
            if way == 'H' and x1 < W - 1 and all(lands(x1 + 1, y) for y in range(y0, y1 + 1)): x1 += 1
        docks.append((way, x0, y0, x1, y1))
    DECK = set().union(*[rect(*d[1:]) for d in docks]) if docks else set()
    lost = sorted(c for c in asked - INSIDE - DECK if sign[c] in '_"')          # (sous un pont, c'est attendu : la piste y arrive)
    if lost: warn.append('des pistes ou des hautes herbes sont tombées sur le bord du plateau, où elles ne se dessinent pas : %s' % lost[:6])
    PAVED = plan.cells('%')
    if PAVED and any(k is None for k in shape(PAVED).values()): warn.append('dallage : une forme que ses tuiles ne dessinent pas'); PAVED = tidy(PAVED)
    gardens = []
    gates_of = {}          # les portillons d'un parc : les cases de son pourtour qu'on n'a pas marquées (à défaut, le milieu de son côté est)
    for piece in parts(plan.cells('f')):
        gx0, gy0, gx1, gy1 = min(c[0] for c in piece), min(c[1] for c in piece), max(c[0] for c in piece), max(c[1] for c in piece)
        ring_ = {c for c in rect(gx0, gy0, gx1, gy1) if c[0] in (gx0, gx1) or c[1] in (gy0, gy1)}
        if not {(gx0, gy0), (gx1, gy0), (gx0, gy1), (gx1, gy1)} <= piece or gx1 - gx0 < 2 or gy1 - gy0 < 2: warn.append('parc vers (%d, %d) : il faut un rectangle d au moins trois cases de côté, ses quatre coins marqués' % (gx0, gy0)); continue
        gardens.append((gx0, gy0, gx1, gy1)); gates_of[(gx0, gy0, gx1, gy1)] = (ring_ - piece) or {(gx1, (gy0 + gy1) // 2)}
    GARDEN = set().union(*[rect(*g) for g in gardens]) if gardens else set()
    # Le vide : le noir autour d'une grotte. On n'y va jamais ; une paroi qui le touche n'a pas de bord de ce côté-là — pour
    # la montagne, le vide est de la roche. Son liseré se dessine sur ses propres cases, là où elles touchent le reste.
    VOID = {c for c in CELLS if sign[c] == '#'} if 'void5' in AT else set()
    if not VOID and any(v == '#' for v in sign.values()): warn.append('le décor %s n a pas de vide : les cases # sont laissées en herbe' % THEME['name'])
    MOUNTAIN = tidy({c for c in INSIDE if sign[c] == '^'} | VOID) - VOID
    for crumb in parts(MOUNTAIN):
        if len(crumb) < 9: MOUNTAIN -= crumb
    TRAIL = tidy({c for c in INSIDE if sign[c] == '_'} - MOUNTAIN - house_area)
    TALL = {c for c in INSIDE if sign[c] == '"'} - TRAIL - MOUNTAIN
    # Un étang : une eau au niveau de l'herbe, sur le dessus d'un plateau. Pas de falaise, pas de sable : sa berge est dans
    # ses propres tuiles (docs/mapping.md, O). Il lui faut trois cases dans chaque sens pour avoir de l'eau au milieu.
    POND = tidy({c for c in INSIDE if sign[c] == 'o'} - MOUNTAIN - house_area)
    for puddle in parts(POND):
        if len(puddle) < 9 or not any(all((c[0] + i, c[1] + j) in puddle for i in (-1, 0, 1) for j in (-1, 0, 1)) for c in puddle):
            POND -= puddle
    EARTH = tidy({c for c in INSIDE if sign[c] in ',w'} - MOUNTAIN - house_area)          # une plaque de terre nue, bordée d'herbe : on y marche (la clairière d'une forêt, un carrefour)
    # Le blé pousse sur la terre d'un champ, par blocs de deux cases au moins dans chaque sens. On ne le traverse pas : on suit
    # les allées de terre qu'il laisse. (Ses tuiles n'ont pas de coin rentrant : la case pleine en tient lieu.)
    WHEAT = {c for c in EARTH if sign[c] == 'w'}
    while True:
        bad = [c for c, k in shape(WHEAT).items() if k is None]
        if not bad: break
        WHEAT -= set(bad)
    lost = sorted(c for c in CELLS if sign[c] == 'o' and c not in POND)
    if lost: warn.append('%d cases d étang laissées en herbe — trop étroit pour sa berge, ou hors du dessus d un plateau : %s' % (len(lost), lost[:6]))
    # Une terrasse : un morceau du dessus d'un plateau, un cran plus haut. Son bord, là où il donne sur l'herbe d'en bas,
    # est une petite falaise d'herbe qu'on ne franchit pas — on y monte par un escalier de pierre, ou l'on en saute par
    # un rebord. Ce qui n'est pas l'herbe d'en bas (la falaise du plateau, le bord de la carte) ne lui fait pas de bord.
    # Les terrasses s'empilent : un niveau repose tout entier sur le dessus du précédent, à une case de son bord au moins —
    # chaque case ne porte ainsi qu'une petite falaise. La montagne, elle, est un mur : une terrasse n'a pas de bord contre elle.
    wished = {c: int(plan.levels[c[1]][c[0]]) for c in INSIDE - MOUNTAIN if not plan.errors and plan.levels[c[1]][c[0]] != '.'}          # (un étang a le niveau de la terrasse qui le porte)
    wall = (set(CELLS) - INSIDE) | MOUNTAIN
    tier, high_shape, below = {}, {}, None
    for k in range(1, max(wished.values(), default=0) + 1):
        region = {c for c, v in wished.items() if v >= k}
        if below is not None: region &= {c for c, s_ in below.items() if s_ == '5'}
        while True:
            bad = [c for c, s_ in shape(region | wall).items() if s_ is None and c in region]
            if not bad: break
            region -= set(bad)
        below = {c: s_ for c, s_ in shape(region | wall).items() if c in region}
        for c, s_ in below.items(): tier[c] = k; high_shape[c] = s_
    high = set(tier)
    terrace = {c: 'grass' + k for c, k in high_shape.items() if k != '5'}
    terrace_stairs = [plan.at(t['mark'], 'escalier de terrasse') for t in plan.table('terrace_stairs')]          # le repère : sa colonne de gauche, sur la rangée du bord sud de la terrasse
    TRAIL -= {c for c in terrace if c in TRAIL and high_shape[c] not in '2'} ; TALL -= set(terrace)
    exits = []
    for e in plan.table('exit'):
        gate = sorted(plan.cells(e['mark']))
        if not gate or not all(c[0] in (0, W - 1) or c[1] in (0, H - 1) for c in gate): warn.append('sortie %s : son repère doit être sur le bord de la carte' % e.get('name', e['mark']))
        exits.append((e, gate))
    GATES = {c for _, gate in exits for c in gate}
    start = plan.at(plan.map['start'], 'départ') if 'start' in plan.map else (next(iter(doors.values()), None) or min(INSIDE or LAND or {(0, 0)}))
    if 'start' not in plan.map and doors: start = (start[0], start[1] + 1)

    # ============================================================ 3. le sol
    L = {n: {} for n in ['Ground', 'Shore', 'Cliffs1', 'Cliffs2', 'Paths', 'Crops', 'Plaza', 'Decorations', 'Grass', 'Ledges', 'Bridges', 'Props', 'Trees', 'Houses']}
    ORDER = ['Ground', 'Shore', 'Cliffs1', 'Cliffs2', 'Paths', 'Plaza', 'Decorations', 'Grass', 'Ledges', 'Bridges']
    TRAIL = tidy(TRAIL)
    sand_shape, ring_shape, rock_shape, trail_shape = shape(SAND), shape(PLATEAU), shape(ROCKY), shape(TRAIL)
    # Une montagne a des gradins (docs/mapping.md, D) : sa silhouette, érodée d'une case par gradin, posée sur elle-même.
    # `mount_edge` : pour chaque case, le bord de roche du gradin le plus haut qui passe là ; `mount_floor` : ce qu'il y a dessous.
    mount_edge, mount_floor, layer_ = {}, {}, MOUNTAIN | VOID
    for k in range(max(1, int(plan.map.get('tiers', 3)))):
        if not layer_: break
        edges = shape(layer_)
        for c, s_ in edges.items():
            mount_floor[c] = 'rock5' if k or s_ == '5' else 'lawn'
            if s_ != '5': mount_edge[c] = 'rock' + s_
            else: mount_edge.pop(c, None)
        layer_ = tidy({c for c, s_ in edges.items() if s_ == '5'})
        layer_ = set().union(*[p_ for p_ in parts(layer_) if len(p_) >= 9 or p_ & VOID]) if layer_ else set()
    lit = set(CELLS) - VOID          # le liseré du vide : sur les cases de vide qui touchent le reste, côtés et coins
    void_shape = {c: k for c, k in shape(lit | {q for q in around(lit) if inb(q)}).items() if c in VOID} if VOID else {}
    DEEP = tidy({c for c in SEA - SAND if all(q not in SAND for q in around([c], 2))})          # profonde au large, à deux cases de tout sable
    deep_shape = {c: (k if k in '123456789' else '5') for c, k in shape(DEEP).items()}
    SAND_CORNER = {'i': 'j', 'j': 'i', 'k': 'l', 'l': 'k'}          # les coins rentrants du sable ne sont pas rangés comme ceux des falaises
    ground, cliffs, shore = {}, {}, {}
    for c in CELLS:
        if c in VOID: ground[c] = 'void' + (void_shape.get(c) or '5') if 'void' + (void_shape.get(c) or '5') in AT else 'void5'
        elif c in DEEP: ground[c] = 'deep' + deep_shape[c]
        elif c not in SAND: ground[c] = 'water'
        elif c not in LAND: ground[c] = 'water'; shore[c] = 'shore' + SAND_CORNER.get(sand_shape[c], sand_shape[c])
        elif c in RING or (c in ROCK and rock_shape[c] == '5'): ground[c] = 'rock5'          # sous l'anneau d'herbe : le gradin de roche
        elif c in BEACH or c in ROCK: ground[c] = 'sand5'
        elif c in MOUNTAIN: ground[c] = mount_floor[c]
        else: ground[c] = 'trailC' if c in TRAIL else 'lawn'
        cliffs[c] = (['grass' + ring_shape[c]] if c in RING else []) + (['rock' + rock_shape[c]] if c in ROCK and rock_shape[c] != '5' else []) \
            + ([mount_edge[c]] if c in mount_edge and c not in VOID else [])
    earth_shape = shape(EARTH)
    for c in sorted(EARTH): L['Paths'][c] = tile('earth' + earth_shape[c])
    for c, k in sorted(shape(WHEAT).items()): L['Crops'][c] = tile('wheat' + (k if k in '123456789' else '5'))
    if WHEAT: ORDER.insert(ORDER.index('Paths') + 1, 'Crops')
    pond_shape = shape(POND)
    for c in sorted(POND): L['Paths'][c] = tile('pond' + pond_shape[c], 1 if c in DECK else 0)          # (sur le calque des pistes : la pelouse reste dessous, on la voit aux coins de la berge)
    paved_shape = shape(PAVED)
    for c in sorted(PAVED): L['Plaza'][c] = tile('paved' + paved_shape[c])

    # ============================================================ 4. escaliers et pontons
    stairs, deck = {}, {}
    for x, r in stairs_at:
        for i, name in enumerate(('stair7', None, None, None, 'stair9')):
            if name: stairs[(x + i, r - 1)] = name
        for j, flight in enumerate('UL'):          # une volée par étage de la falaise : l'herbe, puis la roche
            for i, k in enumerate('45556'): stairs[(x + i, r + j)] = 'stair%s%s' % (flight, k)
        for i, name in enumerate(('stair1', 'stair2', 'stair2', 'stair2', 'stair3')): stairs[(x + i, r + 2)] = name
        if any(ring_shape.get((x + i, r)) != '2' for i in range(5)): warn.append('escalier (%d, %d) : le bord du plateau n est pas droit sur ses cinq cases — il ne monte que face au sud' % (x, r))
        elif any(rock_shape.get((x + i, r + 1)) != '2' for i in (1, 2, 3)): warn.append('escalier (%d, %d) : l anneau de roche n est pas droit dessous' % (x, r))
        if any((x + i, r + 2) not in BEACH for i in (1, 2, 3)): warn.append('escalier (%d, %d) : pas de plage à son pied' % (x, r))
    for side, gx, y0 in side_stairs:
        cols = [gx - 2, gx - 1, gx, gx + 1] if side == 'W' else [gx + 2, gx + 1, gx, gx - 1]          # le bas, la roche, l'herbe, le haut
        for x, i in zip(cols, (0, 1, 2, 3) if side == 'W' else (3, 2, 1, 0)):
            for y, j in [(y0 - 1, 0)] + [(y0 + k, 1) for k in range(3)] + [(y0 + 3, 2)]:
                if 'stair%s%d%d' % (side, i, j) in AT: stairs[(x, y)] = 'stair%s%d%d' % (side, i, j)
        flank = '4' if side == 'W' else '6'
        if any(ring_shape.get((gx, y0 + j)) != flank or rock_shape.get((cols[1], y0 + j)) != flank for j in range(3)): warn.append('escalier de côté (%d, %d) : le flanc du plateau n est pas droit sur trois cases' % (gx, y0))
        if any((cols[0], y0 + j) not in BEACH for j in range(3)): warn.append('escalier de côté (%d, %d) : pas de plage à son pied' % (gx, y0))
    for x, r in terrace_stairs:          # l'escalier de pierre d'une terrasse : cinq cases de large, deux poteaux en haut, les marches sur le bord, leur pied en bas
        stairs[(x, r - 1)] = 'stair7'; stairs[(x + 4, r - 1)] = 'stair9'
        for i, (mid, low) in enumerate(zip(('stair4', 'stair5', 'stair5', 'stair5', 'stair6'), ('stair1', 'stair2', 'stair2', 'stair2', 'stair3'))):
            stairs[(x + i, r)] = mid; stairs[(x + i, r + 1)] = low
        STEPS |= {(x + i, r) for i in (1, 2, 3)}
        if any(high_shape.get((x + i, r)) != '2' for i in range(5)): warn.append('escalier de terrasse (%d, %d) : le bord sud de la terrasse n est pas droit sur ses cinq cases' % (x, r))
    ledges, landings = {}, set()
    for mark, (dx, dy), names in (('v', (0, 1), ('ledgeL', 'ledgeM', 'ledgeR')), ('>', (1, 0), ('ledgeVT', 'ledgeVM', 'ledgeVB')), ('<', (-1, 0), ('ledgeWT', None, 'ledgeWB'))):
        for run in parts(plan.cells(mark)):          # un rebord : une rangée (vers le sud) ou une colonne (vers l'est, vers l'ouest) de deux cases au moins
            run = sorted(run, key=lambda c: (c[1], c[0]))
            straight = len({c[1] for c in run}) == 1 if dy else len({c[0] for c in run}) == 1
            if len(run) < 2 or not straight or (names[1] is None and len(run) != 2):
                warn.append('rebord vers %s : il lui faut %s' % (run[0], 'deux cases exactement, l une sous l autre' if names[1] is None else 'deux cases au moins, en ligne')); continue
            for n, c in enumerate(run):
                ledges[c] = names[0] if n == 0 else names[2] if n == len(run) - 1 else names[1]
                landings.add((c[0] + dx, c[1] + dy)); landings.add((c[0] - dx, c[1] - dy))
    for c, name in ledges.items(): L['Ledges'][c] = tile(name)
    DRY = LAND - POND          # là où un pont repose : la terre, pas l'eau d'un étang
    for way, x0, y0, x1, y1 in docks:
        for (x, y) in sorted(rect(x0, y0, x1, y1)):
            if way == 'V' and (x0 + 1, y1 + 1) in LAND and (x0 + 1, y0 - 1) in LAND:          # de la terre aux deux bouts : c'est un pont, pas une jetée
                deck[(x, y)] = 'bridgeV%d' % (4 + x - x0)
            elif way == 'V':
                low = y == y1 and (x, y + 1) not in DECK
                head = 'pierT' if y == y0 else 'pierU' if y == y0 + 1 else 'pier'          # les deux premiers rangs sortent du sable
                deck[(x, y)] = {0: 'pier1' if low else head + '4', 1: 'pier2' if low else head + '5', 2: 'pier3' if low else head + '6'}[x - x0]
            else:
                deck[(x, y)] = {0: 'bridgeH8', 1: 'bridgeH5', 2: 'bridgeH1' if x == x0 else 'bridgeH2'}[y - y0]
        if way == 'H':          # le dessous d'un ponton en travers déborde sur la rangée d'en dessous, là où c'est de l'eau
            for x in range(x0, x1 + 1):
                c = (x, y1 + 1)
                if c not in DECK and c not in DRY: deck[c] = 'lipL' if (x - 1, y1 + 1) in DECK | DRY or x == x0 else ('lipR' if (x + 1, y1 + 1) in DECK | DRY or x == x1 else 'lip')
    for c in sorted(DECK):
        if c in PLATEAU and c not in RING and c not in POND: warn.append('ponton : il recouvre le dessus d un plateau en %s' % (c,)); break

    for c in CELLS:
        free = 1 if c in DECK or c in STEPS or c in BEACH or c in RING else 0          # le même dessin, sans collision
        L['Ground'][c] = tile(ground[c], free if blocks(ground[c]) else 0)
        if c in shore: L['Shore'][c] = tile(shore[c])
        for k, name in enumerate(cliffs[c][:2]): L['Cliffs%d' % (k + 1)][c] = tile(name, (1 if c in DECK or c in STEPS or name == OPEN_EDGE else 0) if blocks(name) else 0)
        if c in terrace: L['Cliffs1'][c] = tile(terrace[c], 1 if c in STEPS else 0)          # (pas la variante sans collision du bord du haut : c'est elle, la barrière)
        if c in TRAIL and trail_shape[c] != '5': L['Paths'][c] = tile('trail' + trail_shape[c])
        if c in TALL: L['Grass'][c] = (GRASS_SOURCE, 6, 0, 0)
        if c in deck: L['Bridges'][c] = tile(deck[c])
        elif c in stairs: L['Bridges'][c] = tile(stairs[c])

    # ============================================================ 5. ce qui est posé : exactement ce que le plan liste, rien de plus
    sprites, flower_cells, hidden = [], set(), set()
    def feet(kind, x, r): return [(x + i, r + j) for i, j in THEME['props'][kind]['feet']]          # depuis son coin bas-gauche
    blooms = THEME['sources'].get('blooms', {})
    for kind, px_, r in plan.props:
        if kind.startswith('bloom') and kind[5:].isdigit():          # une grande fleur : son pied, et sa cime sur la case du dessus
            L['Props'][(px_, r)] = (FLOWER_SOURCE, int(kind[5:]), blooms['foot'], 0); L['Props'][(px_, r - 1)] = (FLOWER_SOURCE, int(kind[5:]), blooms['top'], 0)
            flower_cells.update({(px_, r), (px_, r - 1)}); continue
        if raw(kind.split('>')[0]):          # une tuile que le décor ne nomme pas : posée telle quelle, sur le calque qu'elle dit
            L.setdefault(kind.split('>')[1] if '>' in kind else 'Props', {})[(px_, r)] = raw(kind.split('>')[0]) + (0,); continue
        model = THEME['props'].get(kind)
        if model is None: warn.append('le décor %s n a rien qui s appelle %r (posé en %s)' % (THEME['name'], kind, (px_, r))); continue
        x = px_ - model['anchor']          # le plan donne la case du pied ; l'image commence à gauche de lui
        source = ROUTE if model['source'] == 'main' else VILLAGE
        L[model['layer']][(x, r)] = (source,) + tuple(model['at']) + (0,)
        if model['layer'] == 'Decorations': continue
        sprites.append((kind, x, r))
        if model['size'][1] > 1: hidden |= rect(x, r - model['size'][1] + 1, x + model['size'][0] - 1, r)
        for c in feet(kind, x, r):
            if inb(c) and (c in DECK or c in STEPS): warn.append('%s en %s : posé sur un ponton ou des marches' % (kind, (px_, r))); break
    for name, (kind, x, r, _) in houses.items(): L['Houses'][(x, r)] = (VILLAGE,) + tuple(THEME['buildings'][kind]['at']) + (0,)
    WOODS = hidden          # derrière un arbre, sous une palme : on n'y pose ni panneau ni personnage
    fronts = {(d[0], d[1] + j) for d in doors.values() for j in (1, 2)}
    fence = {}
    for gx0, gy0, gx1, gy1 in gardens:          # un parc : une clôture sur son pourtour, ouverte à ses portillons
        for c in sorted(rect(gx0, gy0, gx1, gy1)):
            x, y = c
            if (gx0 < x < gx1 and gy0 < y < gy1) or c in gates_of[(gx0, gy0, gx1, gy1)]: continue
            k = {(gx0, gy0): '7', (gx1, gy0): '9', (gx0, gy1): '1', (gx1, gy1): '3'}.get(c) or ('8' if y == gy0 else '2' if y == gy1 else '4' if x == gx0 else '6')
            fence[c] = 'fence' + k
    for c, name in fence.items(): L['Decorations'][c] = tile(name)

    # ============================================================ 6 bis. les calques écrits tuile par tuile
    # Un calque que le plan écrit (`[[layer]]`) est posé tel quel : chaque signe est une tuile du décor, avec sa
    # variante. Il remplace ce que l'esquisse du terrain aurait donné pour ce calque — c'est ce qui permet de refaire
    # une carte existante au pixel, quand elle n'a pas été faite selon nos règles.
    literal, blocked = bool(plan.layers) and not plan.errors, set()
    for name, grid, legend in (plan.layers if literal else []):
        if name not in L: L[name] = {}
        if name not in ORDER and name not in ('Trees', 'Props', 'Houses'): ORDER.insert(len(ORDER) - 1 if 'Bridges' in ORDER and name != 'Bridges' else len(ORDER), name)
        L[name] = {}
        for y, line in enumerate(grid):
            for x, sign in enumerate(line):
                if sign == '.': continue
                what = legend[sign]; tname, alt = (what, 0) if isinstance(what, str) else (what[0], what[1])
                if raw(tname): L[name][(x, y)] = raw(tname) + (alt,)
                elif tname == 'tall_grass': L[name][(x, y)] = (GRASS_SOURCE,) + tuple(THEME['sources']['tall_grass']['at']) + (alt,)
                elif tname in AT:
                    L[name][(x, y)] = tile(tname, alt)
                    if blocks(tname) and alt == 0: blocked.add((x, y))
                else: warn.append('calque %s : le décor n a pas de tuile %r' % (name, tname)); break
    if literal: ORDER[:] = [n for n, _, _ in plan.layers if n not in ('Trees', 'Props', 'Houses')] + [n for n in ORDER if n not in [m for m, _, _ in plan.layers]]

    # ============================================================ 7. ce qui bloque, ce qu'on atteint
    SOLID = set(house_solid)
    for c in CELLS:
        if literal: continue          # tout est dans les tuiles écrites
        if c in DECK: continue
        if c in SEA or (any(blocks(n) and n != OPEN_EDGE for n in cliffs[c]) and c not in STEPS): SOLID.add(c)
    SOLID |= blocked | VOID
    if not literal: SOLID |= (POND - DECK) | WHEAT          # (un pont passe par-dessus un étang)
    for name, x, r in sprites: SOLID |= {c for c in feet(name, x, r) if inb(c)}
    SOLID |= set(fence) | (set() if literal else set(ledges) | (set(terrace) - STEPS))
    def free(c): return inb(c) and c not in SOLID
    for c in sorted(PLATEAU):          # le bord du haut d'un plateau se foule — toujours
        if ring_shape.get(c) == '8' and c in SOLID and not any(c in feet(n, x, r) for n, x, r in sprites) and c not in house_solid:
            warn.append('bord du haut : la rangée du haut du plateau est fermée en %s, elle doit se fouler' % (c,)); break
    def reach_from(origin):
        seen, queue = {origin}, collections.deque([origin])
        while queue:
            c = queue.popleft()
            for i, j in NEIGH4:
                n = (c[0] + i, c[1] + j)
                if free(n) and n not in seen: seen.add(n); queue.append(n)
        return seen
    edge = sorted(c for c in (reach_from(start) if free(start) else set()) if (c[0] in (0, W - 1) or c[1] in (0, H - 1)) and c not in GATES)
    if edge: warn.append('le bord de la carte s atteint ailleurs qu à une sortie : %d cases, dont %s — une sortie à déclarer, ou quelque chose à y poser' % (len(edge), edge[:5]))
    def pinches(c):
        ring = [(c[0] + i, c[1] + j) for i, j in ((-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0))]
        open_ = [free(r) for r in ring]; group = list(range(8))
        def find(i):
            while group[i] != i: i = group[i]
            return i
        for i in range(8):
            if open_[i] and open_[(i + 1) % 8]: group[find(i)] = find((i + 1) % 8)
        return len({find(i) for i in range(8) if open_[i] and i % 2 == 1}) > 1
    if not free(start): warn.append('départ %s : la case est pleine' % (start,))
    REACH0 = reach_from(start) if free(start) else set()

    # ============================================================ 8. ce qu'on pose sur la carte : panneaux, lampadaires, objets, personnages
    nodes, placed = {'World': [], 'Entities': [], 'Doors': [], 'Sky': []}, {}
    NO_STAND = fronts | flower_cells | GARDEN | DECK | STEPS | GATES | around(GATES)
    def settle(name, wish, solid=True, apart=2, exact=False):
        """La case libre la plus proche de `wish` où poser quelque chose sans gêner : ni devant une porte ou un escalier, ni sur un ponton ou une piste, ni dans un passage étroit, ni derrière un arbre. `exact` : la case du plan, telle quelle."""
        if exact:
            if wish in SOLID or wish not in REACH0: warn.append('%s : la case %s est prise ou hors d atteinte' % (name, wish))
            placed[name] = wish
            if solid: SOLID.add(wish)
            return wish
        for q in sorted(((wish[0] + i, wish[1] + j) for i in range(-6, 7) for j in range(-6, 7)), key=lambda q: (abs(q[0] - wish[0]) + abs(q[1] - wish[1]), q)):
            if q in REACH0 and q not in SOLID and q not in NO_STAND and q not in WOODS and q not in house_area and q not in TALL and q not in TRAIL and (q in PAVED or not pinches(q)) \
                    and all(abs(q[0] - o[0]) + abs(q[1] - o[1]) >= apart for o in placed.values()):
                placed[name] = q
                if solid: SOLID.add(q)
                if q != wish: print('  (%s : %s -> %s)' % (name, wish, q))
                return q
        warn.append('%s : aucune case convenable près de %s' % (name, wish)); placed[name] = wish; return wish
    def quote(text): return text.replace('\\', '\\\\').replace('"', '\\"')
    for name, (kind, x, r, h) in houses.items():
        if h.get('scene'):
            nodes['Doors'].append('[node name="%s" parent="Doors" instance=ExtResource("2_door")]\nposition = Vector2(%d, %d)\ntarget_scene = "%sscenes/levels/%s.tscn"\ntarget_door = "%s"\nentry_direction = Vector2(0, 1)\n'
                                  % (name, *px(doors[name]), RES, h['scene'], h.get('door', 'Entree')))
        if doors[name] not in LAND or (doors[name][0], doors[name][1] + 1) not in REACH0: warn.append('maison %s : sa porte n est pas atteinte depuis le départ' % name)
    for e, gate in exits:
        inward = (0, 1) if gate and gate[0][1] == 0 else (0, -1) if gate and gate[0][1] == H - 1 else (1, 0) if gate and gate[0][0] == 0 else (-1, 0)
        for i, c in enumerate(gate):
            if c not in REACH0: warn.append('sortie %s : la case %s n est pas atteinte depuis le départ' % (e.get('name', e['mark']), c))
            if e.get('scene'):
                nodes['Doors'].append('[node name="%s%d" parent="Doors" instance=ExtResource("2_door")]\nposition = Vector2(%d, %d)\ntarget_scene = "%sscenes/levels/%s.tscn"\ntarget_door = "%s%d"\nentry_direction = Vector2(%d, %d)\n'
                                      % (e.get('name', 'Sortie'), i, *px(c), RES, e['scene'], e.get('door', 'Entree'), i, *inward))
    for s in plan.table('sign'):
        c = settle(s['name'], plan.at(s['mark'], 'panneau %s' % s['name']), exact=s.get('exact', False))
        if c in L['Decorations']: L['Decorations'][(c[0], c[1] - 1)] = L['Decorations'].pop(c)          # la fleur qui était là remonte d'une case
        nodes['World'].append('[node name="%s" parent="World" instance=ExtResource("3_sign")]\nposition = Vector2(%d, %d)\ntext = "%s"\n' % (s['name'], *px(c), quote(s['text'])))
    for n, lamp in enumerate(plan.table('lamp')):
        name = lamp.get('name', 'Lamp%d' % n)
        c = settle(name, plan.at(lamp['mark'], 'lampadaire %s' % name), exact=lamp.get('exact', False))
        nodes['World'].append('[node name="%s" parent="World" instance=ExtResource("10_lamp")]\nposition = Vector2(%d, %d)\n' % (name, *px(c)))
    for it in plan.table('item'):
        c = settle(it['name'], plan.at(it['mark'], 'objet %s' % it['name']), exact=it.get('exact', False))
        nodes['World'].append('[node name="%s" parent="World" instance=ExtResource("9_readable")]\nposition = Vector2(%d, %d)\nkind = "item"\ntext = "@give:%s %s"\nflag = "%s"\n'
                              % (it['name'], *px(c), it['item'], quote(it['text']), it.get('flag', 'found_%s_%s' % (plan.name, it['name'].lower()))))
        ball = THEME['sources'].get('item_ball')          # sa Poké Ball : sans elle, l'objet est là mais ne se voit pas
        if ball: nodes['World'].append('[node name="Ball" type="Sprite2D" parent="World/%s"]\ntexture = ExtResource("12_ball")\nregion_enabled = true\nregion_rect = Rect2(%d, %d, %d, %d)\n' % ((it['name'],) + tuple(ball['region'])))
    npcs = []
    for p in plan.table('npc'):
        moving = p.get('movement') in ('wander', 'patrol')
        wish = plan.at(p['mark'], 'personnage %s' % p['name'])
        c = wish if moving else settle(p['name'], wish, exact=p.get('exact', False))
        npcs.append((p['name'], c))
        lines = ['[node name="%s" parent="World/Entities" instance=ExtResource("4_npc")]' % p['name'], 'position = Vector2(%d, %d)' % px(c)]
        for k in ('display_name', 'gender'):
            if k in p: lines.append('%s = "%s"' % (k, quote(p[k])))
        lines.append('appearance = "%s"' % p['appearance'])
        if 'facing' in p: lines.append('facing = Vector2(%d, %d)' % tuple(p['facing']))
        lines.append('text = "%s"' % quote(p['text']))
        if moving: lines.append('movement = "%s"' % p['movement'])
        if 'pace' in p: lines.append('pace = %s' % p['pace'])
        if p.get('movement') == 'wander':
            x0, y0, x1, y1 = plan.box(p.get('zone', p['mark']), 'zone de %s' % p['name'])
            lines.append('wander_zone = Rect2i(%d, %d, %d, %d)' % (x0, y0, x1 - x0 + 1, y1 - y0 + 1))
        if p.get('movement') == 'patrol':
            route = [plan.at(m, 'ronde de %s' % p['name']) for m in p['route']]
            for a, b in zip(route, route[1:] + route[:1]):
                if a[0] != b[0] and a[1] != b[1]: warn.append('ronde de %s : %s et %s ne sont ni sur la même rangée ni sur la même colonne' % (p['name'], a, b))
            lines.append('route = PackedVector2Array(%s)' % ', '.join('%d, %d' % q for q in route))
        for k in ('required_flag', 'forbidden_flag'):
            if k in p: lines.append('%s = "%s"' % (k, p[k]))
        nodes['Entities'].append('\n'.join(lines) + '\n')
    for n, pack in enumerate(plan.table('flyers')):          # des Pokémon que le vent porte : un groupe partage sa graine, un seul y crie
        row = plan.at(pack['mark'], 'volants')
        for i, species in enumerate(pack['species']):
            nodes['Sky'].append('[node name="%s%d" parent="Sky" instance=ExtResource("13_flyer")]\nposition = Vector2(%d, %d)\nspecies = "%s"\nzone = Rect2i(0, 0, %d, %d)\npace = %s\nseed = %d\ndrift = %d\n%s'
                                % (pack.get('name', 'Flyers%d' % n), i, round((row[0] + 1.7 * i) * 16 + 8), round((row[1] + (1.1 if i % 2 else 0) * (1 if i else 0)) * 16 + 8), species, W, H,
                                   pack.get('pace', 1.5), pack.get('seed', 11 + 16 * n), pack.get('drift', 1), '' if i == 0 else 'cry_every = Vector2(0, 0)\n'))

    # ============================================================ 9. contrôles : tout se rejoint
    REACH = reach_from(start) if free(start) else set()
    def beside(c): return any((c[0] + i, c[1] + j) in REACH for i, j in NEIGH4)
    for name, c in placed.items():
        if not beside(c): warn.append('%s en %s : on ne peut pas s en approcher' % (name, c))
    for name, c in npcs:
        if c not in placed.values() and c not in REACH: warn.append('%s en %s : hors d atteinte' % (name, c))
    for x, r in stairs_at:
        if not ((x + 2, r - 1) in REACH and (x + 2, r + 2) in REACH): warn.append('escalier (%d, %d) : on ne passe pas du haut au bas' % (x, r))
    for c, name in sorted(ledges.items()):
        dx, dy = (0, 1) if name in ('ledgeL', 'ledgeM', 'ledgeR') else (1, 0) if name.startswith('ledgeV') else (-1, 0)
        if not free((c[0] + dx, c[1] + dy)) or not free((c[0] - dx, c[1] - dy)): warn.append('rebord %s : il faut une case libre de chaque côté, pour sauter et pour retomber' % (c,)); break
    island = [p for p in parts({c for c in CELLS if free(c)} - house_area - MOUNTAIN - hidden) if len(p) >= 6 and not (p & REACH)]          # (derrière le haut d'un toit, sur le dessus d'une montagne : ce ne sont pas des lieux)
    for piece in island[:4]: warn.append('%d cases libres hors d atteinte vers %s : un escalier, un ponton ou une piste y manque — ou c est voulu' % (len(piece), min(piece)))

    return dict(plan=plan, W=W, H=H, L=L, ORDER=ORDER, nodes=nodes, SOLID=SOLID, REACH=REACH, SEA=SEA, DECK=DECK, STEPS=STEPS, warn=warn, start=start, placed=placed, npcs=npcs,
                BEACH=BEACH, PLATEAU=PLATEAU, INSIDE=INSIDE, RING=RING, ring_shape=ring_shape, rock_shape=rock_shape, GATES=GATES, edge=edge,
                TRAIL=TRAIL, TALL=TALL, MOUNTAIN=MOUNTAIN, ROCK=ROCK, LAND=LAND, doors=doors, house_area=house_area, sprites=sprites, flower_cells=flower_cells,
                high=high, high_shape=high_shape, tier=tier, POND=POND, EARTH=EARTH, WHEAT=WHEAT, VOID=VOID, GARDEN=GARDEN, lamps=[placed.get(l.get('name', 'Lamp%d' % n)) for n, l in enumerate(plan.table('lamp'))], ledges=ledges, PAVED=PAVED, stairs=stairs, hidden=hidden, fence=fence, literal=literal)


def scene(built):
    """Le texte de la scène."""
    plan, L = built['plan'], built['L']
    def encode(cells):
        raw = struct.pack('<H', 0)
        for (x, y), t in sorted(cells.items(), key=lambda kv: (kv[0][1], kv[0][0])): raw += struct.pack('<hhHHHH', x, y, t[0], t[1], t[2], t[3] if len(t) > 3 else 0)
        return base64.b64encode(raw).decode()
    def layer(name, parent, ysort=False):
        return '[node name="%s" type="TileMapLayer" parent="%s"]\n%stile_map_data = PackedByteArray("%s")\ntile_set = ExtResource("1_tiles")\n' % (name, parent, 'y_sort_enabled = true\n' if ysort else '', encode(L[name]))
    meta = ['metadata/location = "%s"' % plan.map.get('location', plan.name), 'metadata/banner = "%s"' % plan.map.get('banner', 'wood')]
    if plan.map.get('music'): meta.append('metadata/music = "%s"' % plan.map['music'])
    if plan.map.get('daylight', True): meta.append('metadata/daylight = true')
    if plan.map.get('shade'): meta.append('metadata/shade = Color(%g, %g, %g, 1)' % tuple(plan.map['shade']))          # la pénombre d'un sous-bois : elle multiplie la teinte de l'heure (docs/daynight.md)
    if plan.map.get('wild'): meta += ['metadata/encounter_rate = %d' % plan.map.get('encounter_rate', 3), 'metadata/encounter_rate_run = %d' % plan.map.get('encounter_rate_run', 5), 'metadata/wild = "%s"' % plan.map['wild']]
    head = '''[gd_scene load_steps=8 format=4]

[ext_resource type="TileSet" uid="uid://c38ht37ho6e3a" path="{R}resources/tilesets/level.tres" id="1_tiles"]
[ext_resource type="PackedScene" path="{R}scenes/levels/scene_trigger.tscn" id="2_door"]
[ext_resource type="PackedScene" path="{R}scenes/levels/sign.tscn" id="3_sign"]
[ext_resource type="PackedScene" path="{R}scenes/characters/npc.tscn" id="4_npc"]
[ext_resource type="PackedScene" path="{R}scenes/levels/readable.tscn" id="9_readable"]
[ext_resource type="PackedScene" path="{R}scenes/levels/street_lamp.tscn" id="10_lamp"]
[ext_resource type="PackedScene" path="{R}scenes/levels/flyer.tscn" id="13_flyer"]
{BALL}
[node name="Level" type="Node2D"]
{M}

[node name="Background" type="Node2D" parent="."]
'''.replace('{R}', RES).replace('{M}', '\n'.join(meta)).replace('{BALL}', '[ext_resource type="Texture2D" path="res://%s" id="12_ball"]\n' % THEME['sources']['item_ball']['sheet'] if THEME['sources'].get('item_ball') and built['plan'].table('item') else '')
    parts = [head] + [layer(n, 'Background') for n in built['ORDER']]
    parts.append('[node name="World" type="Node2D" parent="."]\ny_sort_enabled = true\n')
    parts += [layer(n, 'World', True) for n in ('Trees', 'Props', 'Houses')] + built['nodes']['World']
    parts.append('[node name="Entities" type="Node2D" parent="World"]\ny_sort_enabled = true\n')
    parts += built['nodes']['Entities']
    parts.append('[node name="Doors" type="Node2D" parent="."]\n')
    parts += built['nodes']['Doors']
    parts.append('[node name="Sky" type="Node2D" parent="."]\nz_index = 40\n')
    parts += built['nodes']['Sky']
    return '\n'.join(parts)


def preview(built, path):
    """Dessine la carte : ses calques, puis ce qui est debout, du fond vers l'avant ; un point par chose posée."""
    L, W, H = built['L'], built['W'], built['H']
    sheets = {ROUTE: load(os.path.join(ROOT, THEME['sources']['main']['sheet']))[2]}
    if 'buildings' in THEME['sources']: sheets[VILLAGE] = load(os.path.join(ROOT, THEME['sources']['buildings']['sheet']))[2]
    img = [[(0, 0, 0)] * (W * 16) for _ in range(H * 16)]
    def put(c, t, w=1, h=1, below=0):
        if t[0] == FLOWER_SOURCE: return          # les grandes fleurs : une autre planche, un simple point dans l'aperçu
        sheet = sheets[ROUTE if t[0] == GRASS_SOURCE else t[0]]
        ax, ay = THEME['sources']['tall_grass']['drawn'] if t[0] == GRASS_SOURCE else t[1:3]
        for j in range(16 * (h + below)):
            Y = (c[1] - h + 1) * 16 + j
            if not 0 <= Y < H * 16: continue
            for i in range(16 * w):
                X = c[0] * 16 + i
                if not 0 <= X < W * 16: continue
                p = sheet[ay * 16 + j][ax * 16 + i]
                if p[3] == 255: img[Y][X] = tuple(p[:3])
                elif p[3]: img[Y][X] = tuple(int(round(img[Y][X][n] * (1 - p[3] / 255.0) + p[n] * p[3] / 255.0)) for n in range(3))
    for n in built['ORDER']:
        for c, t in L[n].items(): put(c, t)
    models = {(ROUTE if p['source'] == 'main' else VILLAGE, tuple(p['at'])): p for p in THEME['props'].values()}
    models.update({(VILLAGE, tuple(b['at'])): b for b in THEME['buildings'].values()})
    standing = [((c[1], 0), c, t) for c, t in L['Trees'].items()] + [((c[1], 1), c, t) for c, t in L['Props'].items()] + [((c[1], -1), c, t) for c, t in L['Houses'].items()]
    for _, c, t in sorted(standing):
        model = models.get((t[0], tuple(t[1:3])))
        if model: put(c, t, model['size'][0], model['size'][1], model['drop'])
        else: put(c, t)
    def dot(c, colour):
        for j in range(5, 11):
            for i in range(5, 11):
                if 0 <= c[1] * 16 + j < H * 16 and 0 <= c[0] * 16 + i < W * 16: img[c[1] * 16 + j][c[0] * 16 + i] = colour
    shade = built['plan'].map.get('shade')          # la pénombre de la carte, comme le jeu la rendra en plein jour
    if shade: img[:] = [[tuple(int(p[n] * shade[n]) for n in range(3)) for p in row] for row in img]
    for c, t in L['Props'].items():
        if t[0] == FLOWER_SOURCE and t[2] == THEME['sources']['blooms']['foot']: dot(c, (230, 120, 200))
    for name, c in built['placed'].items(): dot(c, (230, 40, 40))
    for name, c in built['npcs']: dot(c, (60, 60, 230))
    dot(built['start'], (255, 255, 255))
    save(path, [[p + (255,) for p in row] for row in img])


def show(built):
    W, H = built['W'], built['H']
    print('    ' + ''.join(str(i // 10) for i in range(W))); print('    ' + ''.join(str(i % 10) for i in range(W)))
    for y in range(H):
        print('%2d  %s' % (y, ''.join('=' if (x, y) in built['DECK'] else ('S' if (x, y) in built['STEPS'] else ('~' if (x, y) in built['SEA'] else ('#' if (x, y) in built['SOLID'] else ('.' if (x, y) in built['REACH'] else '?')))) for x in range(W))))
    print('    = ponton   S marches   ~ mer   # plein   . atteint à pied   ? libre mais hors d atteinte')


if __name__ == '__main__':
    args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and sys.argv[i - 1] not in ('--preview', '--out')]
    if not args: sys.exit(__doc__)
    plan = Plan(args[0])
    built = build(plan)
    print('%s : %d x %d cases, %d cases atteintes à pied depuis %s' % (plan.name, plan.W, plan.H, len(built['REACH']), built['start']))
    for line in built['warn']: print('  !! ' + line)
    if '--map' in sys.argv: show(built)
    if '--preview' in sys.argv:
        out = sys.argv[sys.argv.index('--preview') + 1]; preview(built, out); print('aperçu : ' + out)
    if '--write' in sys.argv:
        target = GAME + 'scenes/levels/%s.tscn' % plan.name
        if '--out' in sys.argv: target = os.path.abspath(sys.argv[sys.argv.index('--out') + 1])          # ailleurs : un terrain d'essai, par exemple
        if plan.errors: sys.exit('le plan a des erreurs : rien n est écrit')
        if os.path.exists(target) and '--force' not in sys.argv:
            sys.exit('%s existe déjà : le générateur crée une carte, il ne la refait pas. Elle se retouche dans l éditeur.\n(--force l écrase, et perd tout ce qui y a été retouché à la main.)' % os.path.relpath(target, ROOT))
        with open(target, 'w', encoding='utf-8') as f: f.write(scene(built))
        print('écrit : ' + os.path.relpath(target, ROOT))
    sys.exit(1 if built['warn'] else 0)
