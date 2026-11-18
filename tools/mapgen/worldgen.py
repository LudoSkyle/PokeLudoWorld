#!/usr/bin/env python3
"""Le générateur de cartes : une graine et des réglages en entrée, un plan en sortie.

    python3 tools/mapgen/worldgen.py tools/mapgen/worlds/<monde>.toml                 écrit plans/<carte>.toml
    python3 tools/mapgen/worldgen.py <monde> --preview /tmp/carte.png               et dessine la carte qu'il donne

Il **invente** une carte : son relief, ses plages, ses forêts, ses hautes herbes, ses chemins, son décor — à partir
d'une graine. Il n'écrit pas de scène : il écrit un **plan**, que le constructeur (`build.py`) assemble. Entre les
deux, le plan se lit et se retouche à la main.

**La même graine redonne la même carte.** Chaque couche a sa propre graine, dérivée de la graine du monde : changer
celle du décor déplace les fleurs sans toucher au relief (`[seed]`).

Ce qu'on règle (`worlds/README.md`) :

  - le relief : un bruit à plusieurs octaves (`scale`, `octaves`, `persistence`, `lacunarity`), découpé par des
    seuils en mer, sable, herbe, terrasse, montagne ;
  - le climat : un second bruit, l'humidité, qui dit où pousse la forêt ;
  - la végétation : la part de hautes herbes et la taille de leurs taches, la fréquence des fleurs, l'écart entre
    les arbres ;
  - la jouabilité : la largeur des chemins qui relient les sorties et les maisons, le rayon laissé libre autour de
    chaque point d'intérêt.

Les bords (rives, falaises, angles de chemin) ne le regardent pas : c'est le constructeur qui les pose.
"""
import heapq
import math
import os
import random
import sys
import tomllib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as builder  # noqa: E402

DEFAULTS = {
    'relief': dict(scale=16.0, octaves=4, persistence=0.5, lacunarity=2.0, water=0.34, sand=0.40, terrace=2.0, mountain=2.0, island=False, smooth=2),
    'climate': dict(scale=12.0, forest=0.56),
    'vegetation': dict(tall_grass=0.10, tall_grass_scale=6.0, decorations=0.06, blooms=5, tree_spacing=4, tree_dark=0.15, palms=2, sea_rocks=0.02, shells=16),
    'gameplay': dict(path_width=3, poi_radius=2, close_edges=True),
}
NEIGH4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def lattice(seed, x, y):
    """Un nombre de 0 à 1, toujours le même pour la même graine et le même point."""
    n = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFFFF) / float(0xFFFFFF)


def noise(seed, x, y):
    """Un bruit lisse : les valeurs du treillis, fondues entre elles."""
    x0, y0 = math.floor(x), math.floor(y)
    fx, fy = x - x0, y - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = lattice(seed, x0, y0), lattice(seed, x0 + 1, y0)
    c, d = lattice(seed, x0, y0 + 1), lattice(seed, x0 + 1, y0 + 1)
    return (a + (b - a) * fx) * (1 - fy) + (c + (d - c) * fx) * fy


def fractal(seed, x, y, scale, octaves=1, persistence=0.5, lacunarity=2.0):
    """Plusieurs octaves : la première donne les grandes formes, les suivantes le détail des contours."""
    total, weight, amplitude, frequency = 0.0, 0.0, 1.0, 1.0 / scale
    for o in range(octaves):
        total += noise(seed + 97 * o, x * frequency, y * frequency) * amplitude
        weight += amplitude; amplitude *= persistence; frequency *= lacunarity
    return total / weight


def generate(world):
    m = world['map']
    W, H = m['size']
    S = {k: dict(DEFAULTS[k], **world.get(k, {})) for k in DEFAULTS}
    seeds = world.get('seed', {})
    def sub(layer): return seeds.get(layer) or (seeds.get('world', 1) * 1000003 + sum(ord(ch) for ch in layer) * 7919) & 0x7FFFFFFF
    CELLS = [(x, y) for y in range(H) for x in range(W)]
    def inb(c): return 0 <= c[0] < W and 0 <= c[1] < H
    notes = []

    # ============================================================ 1. le relief : un bruit, découpé par des seuils
    R = S['relief']
    height = {}
    for x, y in CELLS:
        h = fractal(sub('relief'), x, y, R['scale'], R['octaves'], R['persistence'], R['lacunarity'])
        if R['island']:          # une île : le relief retombe vers la mer en approchant du bord de la carte
            edge = min(x, y, W - 1 - x, H - 1 - y) / (min(W, H) * 0.32)
            h *= min(1.0, edge) ** 0.7
        height[(x, y)] = h
    lo, hi = min(height.values()), max(height.values())
    height = {c: (h - lo) / (hi - lo or 1) for c, h in height.items()}          # de 0 à 1, pour que les seuils veuillent dire la même chose d'une graine à l'autre
    def kind(h): return '~' if h < R['water'] else ':' if h < R['sand'] else '.'
    ground = {c: kind(h) for c, h in height.items()}
    for _ in range(R['smooth']):          # pas de confettis : une case isolée prend le terrain de ses voisines
        nxt = {}
        for c in CELLS:
            around = [ground[(c[0] + i, c[1] + j)] for i in (-1, 0, 1) for j in (-1, 0, 1) if inb((c[0] + i, c[1] + j))]
            best = max('~:.', key=around.count)
            nxt[c] = best if around.count(ground[c]) < 4 else ground[c]
        ground = nxt
    def pieces(cells):
        left, out = set(cells), []
        while left:
            seen, todo = set(), [next(iter(left))]
            while todo:
                c = todo.pop()
                if c in seen or c not in left: continue
                seen.add(c); todo += [(c[0] + i, c[1] + j) for i, j in NEIGH4]
            out.append(seen); left -= seen
        return out
    for piece in pieces({c for c in CELLS if ground[c] == '.'}):          # un îlot d'herbe trop petit pour une falaise redevient du sable
        if len(piece) < 40:
            for c in piece: ground[c] = ':'
    for piece in pieces({c for c in CELLS if ground[c] == '~'}):          # une flaque : de l'herbe
        if len(piece) < 12:
            for c in piece: ground[c] = '.'
    for piece in pieces({c for c in CELLS if ground[c] == ':'}):          # une tache de sable loin de l'eau : de l'herbe
        if not any(ground.get((c[0] + i, c[1] + j)) == '~' for c in piece for i in (-1, 0, 1) for j in (-1, 0, 1)):
            for c in piece: ground[c] = '.'
    grass = {c for c in CELLS if ground[c] == '.'}
    mountain = {c for c in grass if height[c] >= R['mountain']}
    levels = {c for c in grass - mountain if height[c] >= R['terrace']}

    # ============================================================ 2. les points d'intérêt : sorties et maisons
    G = S['gameplay']
    def nearest(wish, among):
        return min(among, key=lambda c: (abs(c[0] - wish[0]) + abs(c[1] - wish[1]), c)) if among else None
    def deep(c, n): return all(ground.get((c[0] + i, c[1] + j), '.') == '.' for i in range(-n, n + 1) for j in range(-n, n + 1))          # loin du bord du plateau (le hors-carte compte pour de l'herbe)
    exits, pois, marks = [], [], {}
    letters = iter('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    for e in world.get('exit', []):
        side, at = e['side'], e.get('at', 0.5)
        line = [(x, 0 if side == 'north' else H - 1) for x in range(2, W - 2)] if side in ('north', 'south') else [(0 if side == 'west' else W - 1, y) for y in range(2, H - 2)]
        wish = line[int(at * (len(line) - 1))]
        inward = (0, 1) if side == 'north' else (0, -1) if side == 'south' else (1, 0) if side == 'west' else (-1, 0)
        ok = [c for c in line if deep((c[0] + inward[0] * 3, c[1] + inward[1] * 3), 4)]          # en plein plateau : loin de sa falaise, de part et d'autre
        c = nearest(wish, ok)
        if c is None: notes.append('sortie %s : pas d herbe sur le bord %s' % (e.get('name', side), side)); continue
        mark = next(letters)
        span = [(c[0] + i, c[1]) for i in (-1, 0, 1)] if side in ('north', 'south') else [(c[0], c[1] + i) for i in (-1, 0, 1)]
        exits.append((e, mark, span, inward)); pois.append((c[0] + inward[0] * 2, c[1] + inward[1] * 2)); marks[mark] = span
    houses = []
    for h in world.get('house', []):
        wish = (int(h.get('near', [0.5, 0.5])[0] * (W - 1)), int(h.get('near', [0.5, 0.5])[1] * (H - 1)))
        taken = [d for _, _, d in houses]
        ok = [c for c in grass - mountain if deep((c[0], c[1] - 3), 4) and deep(c, 3) and c[1] >= 8 and all(abs(c[0] - d[0]) + abs(c[1] - d[1]) >= 12 for d in taken)]
        door = nearest(wish, ok)
        if door is None: notes.append('maison %s : pas de place sur l herbe' % h['name']); continue
        mark = next(letters); houses.append((h, mark, door)); marks[mark] = [door]; pois.append((door[0], door[1] + 1))
    house_area = {(d[0] + i, d[1] - j) for _, _, d in houses for i in range(-5, 6) for j in range(0, 7)}

    # ============================================================ 3. les chemins : un tracé praticable entre tous les points d'intérêt
    trail = set()
    half = G['path_width'] // 2
    def cost(c):
        if c in house_area or ground[c] != '.' or c in mountain: return None
        return 1.0 + (0.0 if c in trail else 0.6) + (6.0 if not deep(c, half + 1) else 0.0) + lattice(sub('paths'), *c) * 1.5          # un peu de hasard : un chemin qui serpente, pas une règle
    def route(a, b):
        best, queue, came = {a: 0.0}, [(0.0, 0.0, a)], {}
        while queue:
            _, d, c = heapq.heappop(queue)
            if c == b: break
            if d > best.get(c, 1e9): continue
            for i, j in NEIGH4:
                n = (c[0] + i, c[1] + j)
                if not inb(n): continue
                w = cost(n)
                if w is None and n != b: continue
                nd = d + (w or 1.0)
                if nd < best.get(n, 1e9): best[n] = nd; came[n] = c; heapq.heappush(queue, (nd + abs(n[0] - b[0]) + abs(n[1] - b[1]), nd, n))
        if b not in came and a != b: return None
        path, c = [b], b
        while c != a: c = came[c]; path.append(c)
        return path
    for n, target in enumerate(pois[1:], 1):
        path = route(pois[0], target)
        if path is None: notes.append('pas de chemin à pied sec jusqu au point %d : il faudra un pont ou un escalier' % n); continue
        for c in path: trail |= {(c[0] + i, c[1] + j) for i in range(-half, half + 1) for j in range(-half, half + 1) if inb((c[0] + i, c[1] + j)) and ground[(c[0] + i, c[1] + j)] == '.'}
    for _, _, span, inward in exits:          # la sortie elle-même, et son débouché sur trois cases
        for c in span: trail |= {(c[0] + inward[0] * k, c[1] + inward[1] * k) for k in range(0, 4) if inb((c[0] + inward[0] * k, c[1] + inward[1] * k))}
    trail = {c for c in trail if ground[c] == '.' and c not in mountain and c not in house_area}
    clear = set(trail) | {(p[0] + i, p[1] + j) for p in pois for i in range(-G['poi_radius'], G['poi_radius'] + 1) for j in range(-G['poi_radius'], G['poi_radius'] + 1)} | house_area

    # ============================================================ 4. le climat et la végétation
    C, V = S['climate'], S['vegetation']
    moist = {c: fractal(sub('climate'), c[0], c[1], C['scale'], 3) for c in CELLS}
    forest = {c for c in grass - mountain - clear if moist[c] >= C['forest']}
    meadow = grass - mountain - clear - forest
    patch = sorted(meadow, key=lambda c: -fractal(sub('grass'), c[0], c[1], V['tall_grass_scale'], 2))          # les hautes herbes : les sommets d'un bruit, donc des taches, pas un semis
    tall = set(patch[:int(len(grass) * V['tall_grass'])])
    props, rng = [], random.Random(sub('trees'))
    occupied = set()
    step = max(3, int(V['tree_spacing']))
    for r in range(0, H + 1):          # la forêt : en quinconce, un arbre tous les `tree_spacing` — à 4 elle est fermée, au-delà on passe entre les troncs
        for x in range(-2, W):
            if (x - (step // 2) * (r % 2)) % step or r % 2 and step > 4 and rng.random() < 0.0: continue
            feet = [(x + i, r - j) for i in range(3) for j in (0, 1) if inb((x + i, r - j))]
            if feet and sum(1 for c in feet if c in forest) * 3 >= len(feet) * 2 and not any(c in clear or c in tall or ground[c] != '.' for c in feet):
                props.append(('treeB' if rng.random() < V['tree_dark'] else 'treeA', x, r)); occupied |= set(feet)
    decor = random.Random(sub('decor'))
    lawn = sorted(meadow - tall - occupied)
    beds = []
    spots = list(lawn); decor.shuffle(spots)
    for c in spots:          # les grandes fleurs, par deux, jamais en rang, loin les unes des autres
        if len(beds) >= V['blooms']: break
        pair = [c, (c[0] + 2, c[1] + 1)]
        if all(q in meadow and q not in tall and q not in occupied and (q[0], q[1] - 1) in meadow for q in pair) and all(abs(c[0] - b[0]) + abs(c[1] - b[1]) >= 8 for b in beds):
            for k, q in enumerate(pair): props.append(('bloom%d' % ((len(beds) + k) % 4), q[0], q[1])); occupied |= {q, (q[0], q[1] - 1)}
            beds.append(c)
    for c in lawn:
        if c not in occupied and decor.random() < V['decorations']: props.append(('fl%d' % decor.randint(1, 5), c[0], c[1]))
    shore = random.Random(sub('shore'))
    sand = {c for c in CELLS if ground[c] == ':'}
    dry = sorted(c for c in sand if all(ground.get((c[0] + i, c[1] + j), ':') == ':' for i in (-2, -1, 0, 1, 2) for j in (-2, -1, 0, 1, 2)))          # du sable sec, à deux cases de l'eau et de la falaise
    for beach in sorted(pieces(set(dry)), key=min):
        spots = sorted(beach); shore.shuffle(spots)
        for c in spots[:V['palms']]: props.append(('palm', c[0], c[1])); occupied.add(c)
    shells, spots = [], list(dry); shore.shuffle(spots)
    for c in spots:
        if V['shells'] and len(shells) < len(dry) // V['shells'] and c not in occupied and all(abs(c[0] - o[0]) + abs(c[1] - o[1]) >= 5 for o in shells): props.append(('shell%d' % (1 + len(shells) % 4), c[0], c[1])); shells.append(c)
    open_sea = [c for c in CELLS if ground[c] == '~' and all(ground.get((c[0] + i, c[1] + j), '~') == '~' for i in (-2, -1, 0, 1, 2) for j in (-2, -1, 0, 1, 2))]
    rocks = []
    for c in open_sea:          # quelques rochers au large, jamais deux côte à côte
        if shore.random() < V['sea_rocks'] and all(abs(c[0] - o[0]) + abs(c[1] - o[1]) >= 4 for o in rocks): props.append((('riverrock', 'spire', 'pebbleB')[len(rocks) % 3], c[0], c[1])); rocks.append(c)

    # ============================================================ 5. le plan
    def terrain_sign(c): return '^' if c in mountain else '_' if c in trail else '"' if c in tall else ground[c]
    objects = [['.'] * W for _ in range(H)]
    for mark, cells in marks.items():
        for c in cells: objects[c[1]][c[0]] = mark
    start = pois[0] if pois else nearest((W // 2, H // 2), grass)
    objects[start[1]][start[0]] = '*'
    plan = dict(terrain=[''.join(terrain_sign((x, y)) for x in range(W)) for y in range(H)], objects=[''.join(r) for r in objects],
                levels=[''.join('1' if (x, y) in levels else '.' for x in range(W)) for y in range(H)], props=props, exits=exits, houses=houses, map=m, world=world, notes=notes, seeds={k: sub(k) for k in ('relief', 'climate', 'grass', 'paths', 'trees', 'decor', 'shore')})
    return plan


def write(plan, path):
    m = plan['map']
    out = ['# Plan inventé par tools/mapgen/worldgen.py à partir de %s.' % os.path.basename(plan['source']),
           '# Graines : %s' % ', '.join('%s %d' % kv for kv in plan['seeds'].items()),
           '# Il se lit et se retouche à la main ; relancer le générateur l\'écrase.', '',
           "terrain = '''", *plan['terrain'], "'''", '', "objects = '''", *plan['objects'], "'''", '']
    if any('1' in row for row in plan['levels']): out += ["levels = '''", *plan['levels'], "'''", '']
    out += ["props = '''", *('%s %d %d' % p for p in plan['props']), "'''", '', '[map]', 'name = "%s"' % m['name'], 'theme = "%s"' % m.get('theme', 'coast'), 'start = "*"']
    for key in ('location', 'banner', 'music', 'wild'):
        if key in m: out.append('%s = "%s"' % (key, m[key]))
    out.append('daylight = %s' % str(m.get('daylight', True)).lower())
    for e, mark, _, _ in plan['exits']:
        out += ['', '[[exit]]', 'mark = "%s"' % mark] + ['%s = "%s"' % (k, e[k]) for k in ('name', 'scene', 'door') if k in e]
    for h, mark, _ in plan['houses']:
        out += ['', '[[house]]', 'mark = "%s"' % mark] + ['%s = "%s"' % (k, h[k]) for k in ('name', 'kind', 'scene', 'door') if k in h]
    for table in ('sign', 'lamp', 'item', 'npc', 'flyers', 'stairs'):          # ce que le monde nomme déjà par un repère passe tel quel
        for entry in plan['world'].get(table, []):
            out += ['', '[[%s]]' % table] + ['%s = %s' % (k, ('"%s"' % v) if isinstance(v, str) else str(v).replace("'", '"')) for k, v in entry.items()]
    with open(path, 'w', encoding='utf-8') as f: f.write('\n'.join(out) + '\n')


def close_edges(path, limit=8):
    """Le bord de la carte ne doit s'atteindre qu'aux sorties : ailleurs, un sapin sur l'herbe, un caillou sur le sable."""
    added = 0
    for _ in range(limit):
        plan = builder.Plan(path); built = builder.build(plan)
        if not built['edge']: break
        src = open(path, encoding='utf-8').read()
        extra = '\n'.join('%s %d %d' % ('rock_s' if c in built['BEACH'] else 'conif', c[0], c[1]) for c in built['edge'])
        i = src.index("props = '''") + len("props = '''")
        open(path, 'w', encoding='utf-8').write(src[:i] + '\n' + extra + src[i:]); added += len(built['edge'])
    return added


if __name__ == '__main__':
    args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and sys.argv[i - 1] not in ('--preview', '--plan')]
    if not args: sys.exit(__doc__)
    with open(args[0], 'rb') as f: world = tomllib.load(f)
    plan = generate(world); plan['source'] = args[0]
    out = sys.argv[sys.argv.index('--plan') + 1] if '--plan' in sys.argv else os.path.join(HERE, 'plans', world['map']['name'] + '.toml')
    write(plan, out)
    S = {k: dict(DEFAULTS[k], **world.get(k, {})) for k in DEFAULTS}
    closed = close_edges(out) if S['gameplay']['close_edges'] else 0
    counts = {s: sum(row.count(s) for row in plan['terrain']) for s in '~:._"^'}
    print('%s : %d x %d — mer %d, sable %d, herbe %d, piste %d, hautes herbes %d, montagne %d ; %d choses posées, %d pour fermer les bords' % (world['map']['name'], *world['map']['size'], *[counts[s] for s in '~:._"^'], len(plan['props']), closed))
    for note in plan['notes']: print('  !! ' + note)
    print('plan : ' + os.path.relpath(out))
    built = builder.build(builder.Plan(out))
    for line in built['warn']: print('  !! ' + line)
    print('%d cases atteintes à pied depuis %s' % (len(built['REACH']), built['start']))
    if '--preview' in sys.argv:
        target = sys.argv[sys.argv.index('--preview') + 1]; builder.preview(built, target); print('aperçu : ' + target)
