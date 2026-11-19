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
    'relief': dict(scale=16.0, octaves=4, persistence=0.5, lacunarity=2.0, water=0.34, sand=0.42, terrace=0.80, mountain=2.0, island=False, smooth=2, pond_max=150),
    'climate': dict(scale=12.0, forest=0.56),
    'vegetation': dict(tall_grass=0.10, tall_grass_scale=6.0, decorations=0.06, blooms=5, tree_spacing=4, tree_dark=0.15, palms=2, palm_gap=5, sea_rocks=0.02, shells=16, sand_rocks=0),
    'gameplay': dict(path_width=3, poi_radius=2, close_edges=True, frame=7, items=4, bridge_max=18, ledges=8, path='dotted', grass_bars=4),
}
NEIGH4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
NEIGH8 = [(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i, j) != (0, 0)]

# ============================================================ les directives : orienter la carte en quelques mots
# `[style]` règle plusieurs nombres d'un coup. Ce qu'on écrit soi-même dans [relief], [climate], [vegetation] passe
# toujours devant. Les styles viennent des cartes d'exemple (une plaine de champs et de bosquets, une côte et sa
# baie, une route en couloir dans la forêt) et de ce que les planches savent dessiner.
SIZES = {'small': (40, 30), 'medium': (64, 44), 'large': (90, 64)}
CAVE_SIZES = {'small': (46, 36), 'medium': (52, 40), 'large': (66, 50)}          # une grotte est une salle, pas une région
TINTS = {'brown': 'cave', 'ice': 'cave_ice'}          # la teinte d'une grotte (`tint` dans sa table `[style]`) : le décor qu'elle dessine
KITS = ('cave_ice',)          # les décors à plateaux emboîtés : leur paroi a une face au nord, et pas de bassin
THEME_DECOR = {'cave': ('ladder',), 'cave_ice': ('ladder', 'hole', 'crack')}
THEME_WATER = {'cave': True, 'cave_ice': False}
# Les petits rochers du sol d'une grotte, par décor. En glace il n'y en a que deux, les foncés ; les ronds et pâles ne
# sont jamais au sol : sur le dessus d'une paroi, ou sur le verglas (Ludovic, 18/11/2026, et sa carte d'exemple).
THEME_ROCKS = {'cave': ('spire', 'spire', 'rock_s', 'pebbleA', 'pebbleB'), 'cave_ice': ('pebbleA', 'spire')}
THEME_TOPS = {'cave_ice': ('roundA', 'roundB')}          # une grotte de glace n'a pas d'eau : ni la planche ni la carte de référence n'en montrent
# La forme : un masque qui se mêle au relief. `weight` : la part du masque (0 : le bruit seul ; 1 : la forme pure).
SHAPES = {
    'free': dict(weight=0.0),                                          # le bruit décide de tout
    'island': dict(weight=0.55),                                       # la terre au milieu, la mer tout autour
    'ring': dict(weight=0.65),                                         # un anneau de terre autour d'un lac (ou d'un massif : `core`)
    'plain': dict(weight=0.5, relief=dict(water=0.12, sand=0.15), vegetation=dict(border_forest=True)),     # de la terre presque partout, quelques mares ; une lisière la ferme
    'coast': dict(weight=0.55),                                        # la mer d'un côté (`sea`), la terre de l'autre
    'bay': dict(weight=0.6),                                           # la mer entre par un côté et creuse la carte
    'corridor': dict(weight=0.5, relief=dict(water=0.10, sand=0.12), vegetation=dict(border_forest=True)),          # une route d'un bord à l'autre, fermée par la forêt
    'archipelago': dict(weight=0.0, relief=dict(water=0.52, sand=0.60, scale=10.0)),
}
# Le style (docs/mapping.md, « Les styles de carte ») : ce que la carte est. Il fixe ce qui ferme la carte, le sol qu'on
# foule, les seuils que le contrôleur lui applique. `route` est le défaut ; les autres styles que le contrôleur connaît
# (forest, fields, village, city) ne s'inventent pas encore.
KINDS = {
    'route': dict(),
    # la grotte : une tache irrégulière posée sur du noir, fermée par sa paroi ; des massifs de roche au milieu, des bassins,
    # des stalagmites le long des murs. Rien de vivant. Elle a son propre déroulé (`generate_cave`) et son décor (`cave`).
    'cave': dict(cavern=True, gameplay=dict(close_edges=False, items=3)),
    # les champs : des blocs de blé clôturés, aux bords droits, chacun un petit labyrinthe d'allées de terre ; des chemins
    # continus passent entre eux, des bosquets remplissent le reste, deux étangs tiennent entre les blocs. Pas de hautes herbes.
    'fields': dict(shape='plain', farm=True, relief=dict(water=0.02, sand=0.03, terrace=2.0), climate=dict(forest=0.55),
                   vegetation=dict(tall_grass=0.0, decorations=0.07, blooms=2),
                   gameplay=dict(path='full', grass_bars=0, ledges=0, items=2)),
    # le village : cinq maisons autour d'une placette dallée, un réseau de chemins continu qui relie chaque porte, deux étangs
    # au contact du bâti, des lampadaires, des massifs clôturés. Ni hautes herbes au centre, ni relief, ni rebord.
    'village': dict(shape='plain', hamlet=True, relief=dict(water=0.02, sand=0.03, terrace=2.0), climate=dict(forest=0.58),
                    vegetation=dict(tall_grass=0.03, decorations=0.12, blooms=3),
                    gameplay=dict(path='full', grass_bars=0, ledges=0, items=2)),
    # la forêt profonde : les arbres sont les murs, les hautes herbes le sol ; des clairières reliées par des couloirs, aucun
    # chemin, une plaque de terre nue par clairière, quelques mares. Ni plateau, ni maison, presque pas de fleurs.
    'forest': dict(shape='plain', deep=True, relief=dict(water=0.02, sand=0.03, terrace=2.0), vegetation=dict(decorations=0.01, blooms=0),
                   gameplay=dict(path='none', grass_bars=0, items=5)),
    # la route côtière : la mer longe un flanc jusqu'au bord de la carte, une chaîne de rochers la borde au large ; peu de sable
    'seaside': dict(shape='coast', open_sea=True, level=0.50, chain=True, vegetation=dict(sea_rocks=0.01)),
    # la route de montagne : c'est la roche qui ferme la carte, pas la forêt ; des blocs, peu d'arbres
    'mountain': dict(wall=True, terraces=True, relief=dict(mountain=0.78, water_more=-0.05), climate=dict(forest=0.62), vegetation=dict(boulders=0.16, tall_grass=0.12)),
    # la plage : la mer va jusqu'au bord, et monte assez haut dans la carte (`level`) pour en prendre près d'un tiers ; le sable est le sol
    'beach': dict(shape='coast', open_sea=True, level=0.32, relief=dict(sand_band=0.30, beach=14),
                  vegetation=dict(palms=8, palm_gap=3, shells=9, sand_rocks=18, sea_rocks=0.04)),
}
# Le caractère : un ou plusieurs mots, qui se cumulent.
TRAITS = {
    'rocky': dict(relief=dict(mountain=0.74, persistence=0.6), vegetation=dict(boulders=0.14, sea_rocks=0.05)),
    'sandy': dict(relief=dict(sand_band=0.12, beach=6), vegetation=dict(palms=4, shells=10)),
    'wooded': dict(climate=dict(forest=0.44), vegetation=dict(border_forest=True)),
    'open': dict(climate=dict(forest=0.70), vegetation=dict(tall_grass=0.06)),
    'grassy': dict(vegetation=dict(tall_grass=0.22, tall_grass_scale=8.0)),
    'flowery': dict(vegetation=dict(decorations=0.14, blooms=10)),
    'wet': dict(relief=dict(water_more=0.08)),
    'jagged': dict(relief=dict(octaves=5, persistence=0.62)),          # des rives déchiquetées
    'smooth': dict(relief=dict(octaves=2, persistence=0.4, smooth=3)),          # de grandes courbes calmes
}


def settings(world):
    """Les réglages d'un monde : les défauts, puis la forme, puis les caractères, puis ce que le monde écrit lui-même."""
    style = world.get('style', {})
    S = {k: dict(v) for k, v in DEFAULTS.items()}
    S['vegetation'].update(boulders=0.08, border_forest=False)
    kind = style.get('kind', 'route')
    if kind not in KINDS: raise SystemExit('style %r : le générateur ne sait pas encore l inventer (il sait : %s). Le contrôleur, lui, le connaît : un plan écrit à la main peut le déclarer.' % (kind, ', '.join(KINDS)))
    form = style.get('shape', KINDS[kind].get('shape', 'free'))
    shape = SHAPES.get(form)
    if shape is None: raise SystemExit('forme inconnue : %r (connues : %s)' % (form, ', '.join(SHAPES)))
    layers = [shape]
    for trait in style.get('character', []):
        if trait not in TRAITS: raise SystemExit('caractère inconnu : %r (connus : %s)' % (trait, ', '.join(TRAITS)))
        layers.append(TRAITS[trait])
    layers.append(KINDS[kind])          # le style passe après les caractères : une plage garde son sable, même « rocheuse »
    for layer in layers:
        for k in S: S[k].update(layer.get(k, {}))
    R = S['relief']
    if 'water_more' in R: R['water'] += R.pop('water_more'); R['sand'] = max(R['sand'], R['water'] + 0.05)
    if 'sand_band' in R: R['sand'] = R['water'] + R.pop('sand_band')
    for k in S: S[k].update(world.get(k, {}))          # ce que le monde écrit lui-même passe devant
    S['cavern'] = bool(KINDS[kind].get('cavern'))
    S['deep'], S['hamlet'], S['farm'] = bool(KINDS[kind].get('deep')), bool(KINDS[kind].get('hamlet')), bool(KINDS[kind].get('farm'))
    S['kind'], S['open_sea'], S['chain'], S['wall'], S['terraces'] = kind, bool(KINDS[kind].get('open_sea')), bool(KINDS[kind].get('chain')), bool(KINDS[kind].get('wall')), bool(KINDS[kind].get('terraces'))
    S['shape'] = dict(level=KINDS[kind].get('level', 0.55), name=form, weight=shape['weight'], core=style.get('core', 'lake'), sea=style.get('sea', 'south'), axis=style.get('axis', 'vertical'))
    return S


def mask(shape, x, y, W, H, frame=0):
    """De 0 (la mer) à 1 (la terre haute) : la forme voulue, sans aucun hasard. Elle se dessine dans le dedans de la carte : sa ceinture (`frame` cases) n'en fait pas partie."""
    u = max(-1.0, min(1.0, (x - frame + 0.5) / max(1, W - 2 * frame) * 2 - 1))          # de -1 à 1
    v = max(-1.0, min(1.0, (y - frame + 0.5) / max(1, H - 2 * frame) * 2 - 1))
    d = math.hypot(u, v)
    name = shape['name']
    if name == 'island': return max(0.0, 1.0 - d * 0.95)
    if name == 'ring':          # un bourrelet de terre à mi-rayon ; le milieu est un lac, ou un massif
        ring = max(0.0, 1.0 - abs(d - 0.58) * 3.2)
        return max(ring, 1.0 - d * 2.2) if shape['core'] == 'mountain' else ring * 0.95
    if name == 'coast': return min(1.0, max(0.0, shape.get('level', 0.55) + 0.6 * {'south': -v, 'north': v, 'west': u, 'east': -u}[shape['sea']]))
    if name == 'bay':
        side = {'south': (u, v - 1.0), 'north': (u, v + 1.0), 'west': (u + 1.0, v), 'east': (u - 1.0, v)}[shape['sea']]
        return min(1.0, math.hypot(side[0] * 0.95, side[1] * 0.62) * 0.62)
    if name in ('plain', 'corridor'): return 0.75
    return 0.5


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


MARKS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdeghijklmnopqstuwyz'          # (pas les signes réservés du plan : f v x et = % < >)
ITEMS = [('potion', 'une Potion', 'la Potion', 'Objets'), ('poke_ball', 'une Poké Ball', 'la Poké Ball', 'Poké Balls'), ('antidote', 'un Antidote', "l'Antidote", 'Objets'),
         ('super_potion', 'une Super Potion', 'la Super Potion', 'Objets'), ('fresh_water', 'une Eau Fraîche', "l'Eau Fraîche", 'Objets'), ('revive', 'un Rappel', 'le Rappel', 'Objets')]
Q3 = "'" * 3          # les trois apostrophes qui ouvrent et ferment une grille du plan


def pieces(cells, neigh=NEIGH4):
    left, out = set(cells), []
    while left:
        seen, todo = set(), [next(iter(left))]
        while todo:
            c = todo.pop()
            if c in seen or c not in left: continue
            seen.add(c); todo += [(c[0] + i, c[1] + j) for i, j in neigh]
        out.append(seen); left -= seen
    return out


class World:
    """Une carte en cours d'invention : son terrain, ce qu'on y a posé, et le plan qu'on en tire."""

    def __init__(self, world, source):
        self.world, self.source, self.m = world, source, world['map']
        size = world.get('style', {}).get('size', self.m.get('size', 'medium'))
        self.S = settings(world)
        self.W, self.H = (CAVE_SIZES if self.S.get('cavern') else SIZES)[size] if isinstance(size, str) else size
        self.m['size'] = [self.W, self.H]
        self.CELLS = [(x, y) for y in range(self.H) for x in range(self.W)]
        self.ground, self.trail, self.tall, self.mountain, self.levels = {}, set(), set(), set(), set()
        self.marks, self.props, self.tables, self.notes = {}, [], [], []
        self.letters = iter(MARKS)
        self.exits, self.houses, self.pois, self.lanes, self.start = [], [], [], set(), None
        self.far, self.stairs = [], []
        self.tier, self.climbs, self.rim, self.way = {}, [], set(), set()
        self.glades, self.earth, self.hearts = set(), set(), []
        self.wheat, self.fields = set(), []          # les champs : leurs cases de blé, et leurs enclos (x0, y0, x1, y1)
        self.plaza, self.spots = set(), set()          # le village : sa placette dallée, et les cases gardées pour son mobilier          # la forêt profonde : ses clairières, leurs plaques de terre nue, leurs centres          # les terrasses où l'on marche (case → niveau) et leurs escaliers
        self.routes, self.waypoints, self.bars, self.hops = [], [], [], []          # (`hops` : les rebords prévus, chacun avec son signe et ses cases)          # les trajets tracés, case par case ; les détours imposés à une route en couloir
        self.open = self.S['shape']['sea'] if self.S['open_sea'] else None          # le côté où la mer va jusqu'au bord (une plage)

    def sub(self, layer):
        seeds = self.world.get('seed', {})
        return seeds.get(layer) or (seeds.get('world', 1) * 1000003 + sum(ord(ch) for ch in layer) * 7919) & 0x7FFFFFFF

    def inb(self, c): return 0 <= c[0] < self.W and 0 <= c[1] < self.H
    def edge(self, c):
        """La distance au bord de la carte — sans compter le côté de la mer ouverte : là, rien ne ferme, la mer est la limite."""
        o = self.open
        if o is None: return min(c[0], c[1], self.W - 1 - c[0], self.H - 1 - c[1])
        return min(c[0] if o != 'west' else 999, c[1] if o != 'north' else 999, self.W - 1 - c[0] if o != 'east' else 999, self.H - 1 - c[1] if o != 'south' else 999)
    def offshore(self, c):
        """La distance au bord de la mer ouverte (très grande s'il n'y en a pas)."""
        return {'west': c[0], 'north': c[1], 'east': self.W - 1 - c[0], 'south': self.H - 1 - c[1]}.get(self.open, 999)
    def mark(self, cells):
        m = next(self.letters); self.marks[m] = list(cells); return m

    # ------------------------------------------------------------ le plan, et ce que le constructeur en dit
    def lines(self):
        def sign(c): return '^' if c in self.mountain else '_' if c in self.trail else 'w' if c in self.wheat else ',' if c in self.earth and self.ground[c] == '.' else '"' if c in self.tall else self.ground[c]
        objects = [['.'] * self.W for _ in range(self.H)]
        for m, cells in self.marks.items():
            for c in cells: objects[c[1]][c[0]] = m
        start = None
        if self.start:
            if objects[self.start[1]][self.start[0]] == '.': objects[self.start[1]][self.start[0]] = '*'
            start = objects[self.start[1]][self.start[0]]
        m = self.m
        out = ['# Plan inventé par tools/mapgen/worldgen.py à partir de %s.' % os.path.basename(self.source),
               '# Graines : %s' % ', '.join('%s %d' % (k, self.sub(k)) for k in ('relief', 'climate', 'grass', 'paths', 'trees', 'decor', 'shore')),
               "# Il se lit et se retouche à la main ; relancer le générateur l'écrase.", '',
               'terrain = ' + Q3, *(''.join(sign((x, y)) for x in range(self.W)) for y in range(self.H)), Q3, '',
               'objects = ' + Q3, *(''.join(r) for r in objects), Q3, '']
        if self.levels or self.tier:          # une butte est un cran au-dessus de la terrasse qui la porte
            def level(c): return self.tier.get(c, 0) + (1 if c in self.levels else 0)
            out += ['levels = ' + Q3, *(''.join(str(level((x, y))) if level((x, y)) else '.' for x in range(self.W)) for y in range(self.H)), Q3, '']
        out += ['props = ' + Q3, *('%s %d %d' % p for p in self.props), Q3, '', '[map]', 'name = "%s"' % m['name'], 'theme = "%s"' % m.get('theme', 'coast'), 'style = "%s"' % self.S['kind']]
        if start and len(self.marks.get(start, [0])) == 1: out.append('start = "%s"' % start)
        for key in ('location', 'banner', 'music', 'wild'):
            if key in m: out.append('%s = "%s"' % (key, m[key]))
        out.append('daylight = %s' % str(m.get('daylight', True)).lower())
        if 'tiers' in m: out.append('tiers = %d' % m['tiers'])
        shade = m.get('shade', [0.74, 0.84, 0.78] if self.S['deep'] else None)          # un sous-bois est dans la pénombre
        if shade: out.append('shade = [%s]' % ', '.join('%g' % v for v in shade))
        for name, entry in self.tables:
            out += ['', '[[%s]]' % name]
            for k, v in entry.items():
                if isinstance(v, bool): out.append('%s = %s' % (k, str(v).lower()))
                elif isinstance(v, str): out.append('%s = "%s"' % (k, v.replace('\\', '\\\\').replace('"', '\\"')))
                else: out.append('%s = %s' % (k, str(v).replace("'", '"')))
        return out

    def write(self, path):
        with open(path, 'w', encoding='utf-8') as f: f.write('\n'.join(self.lines()) + '\n')

    def probe(self):
        """Ce que le constructeur déduit de la carte telle qu'elle est : sa géographie, ce qu'on y atteint."""
        path = os.path.join('/tmp', 'worldgen_%s_%d.toml' % (self.m['name'], os.getpid()))
        self.write(path)
        built = builder.build(builder.Plan(path))
        os.remove(path)
        return built


def generate_cave(w):
    """Une grotte (docs/mapping.md, « Grotte ») : son empreinte, sa paroi, ses massifs, ses bassins, ses rochers, ses objets."""
    W, H, CELLS, inb, sub, G = w.W, w.H, w.CELLS, w.inb, w.sub, w.S['gameplay']
    rng = random.Random(sub('relief') + 61)
    # La teinte de la grotte (docs/mapping.md, « Grotte » : une teinte par grotte). Elle ne change que le décor — même
    # empreinte, mêmes massifs, mêmes bassins : rien ici ne tire au hasard, une graine donne la même grotte des deux teintes.
    tint = w.world.get('style', {}).get('tint', 'brown')
    if tint not in TINTS:
        w.notes.append('teinte %s inconnue : la grotte reste brune (connues : %s)' % (tint, ', '.join(sorted(TINTS))))
        tint = 'brown'
    kit = TINTS[tint] in KITS
    w.m.update(theme=TINTS[tint], daylight=False, tiers=1)          # un seul gradin : la bordure extérieure d'une grotte ne fait qu'une marche, pas quatre empilées (Ludovic, 18/11/2026); w.m.setdefault('banner', 'cave')
    WALL = 3          # l'épaisseur de la paroi : deux gradins et leur dessus
    def blob(cx, cy, rx, ry, salt): return {(cx + i, cy + j) for i in range(-8, 9) for j in range(-7, 8) if (i / rx) ** 2 + (j / ry) ** 2 <= 1.0 + (lattice(sub('relief') + salt, cx + i, cy + j) - 0.5) * 0.6}
    def biggest(cells): return max(pieces(cells), key=len) if cells else set()
    def grown(cells, n): return {(c[0] + i, c[1] + j) for c in cells for i in range(-n, n + 1) for j in range(-n, n + 1)}

    # 1. l'empreinte : une tache, ni ronde ni droite — un bruit ajouté à la distance au centre
    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0 - 1
    def within(c):
        d = math.hypot((c[0] - cx) / (W / 2.0 - 3), (c[1] - cy) / (H / 2.0 - 4))
        return d + (fractal(sub('relief'), c[0], c[1], 9.0, 3) - 0.5) * 1.0 < 1.0
    foot = biggest({c for c in CELLS if within(c) and 2 <= c[0] < W - 2 and (3 if kit else 2) <= c[1] < H - 4})          # (un décor à plateaux prend une rangée de plus au nord, pour sa face)
    # 2. le sol : l'empreinte moins sa paroi ; jamais d'une case de large — on ne garde que ce qui tient dans des carrés de deux
    floor = {c for c in foot if all((c[0] + i, c[1] + j) in foot for i in range(-WALL, WALL + 1) for j in range(-WALL, WALL + 1))}
    for _ in range(4):
        floor = biggest({q for c in floor if all((c[0] + i, c[1] + j) in floor for i in (0, 1) for j in (0, 1)) for q in ((c[0] + i, c[1] + j) for i in (0, 1) for j in (0, 1))})
    rock = grown(floor, WALL) - floor          # la paroi suit le sol, à trois cases
    # Un décor à plateaux (la glace) montre la paroi du nord **de face**, sur deux rangées, sous la lèvre du petit plateau
    # et sous le liseré : il lui faut une rangée de plus au nord du sol — liseré, lèvre, deux rangées de face.
    if kit: rock |= {(c[0], c[1] - 1) for c in rock} - floor
    # 3. la sortie : un couloir de trois cases, de la salle au bord du bas (et au bord du haut, si on le demande)
    w.exits = []
    asked = [e.get('side', 'south') for e in w.world.get('exit', [])] or ['south']
    for side in asked:
        if side not in ('south', 'north'): w.notes.append('sortie %s : une grotte ne s ouvre qu au sud ou au nord' % side); continue
        row = max(c[1] for c in floor) if side == 'south' else min(c[1] for c in floor)
        x = min((c[0] for c in floor if c[1] == row), key=lambda q: abs(q - cx))
        x = max(WALL + 2, min(W - WALL - 3, x))
        rows = range(row - 2, H) if side == 'south' else range(0, row + 3)
        lane = {(x + i, y) for y in rows for i in (-1, 0, 1)}
        floor |= lane; rock -= lane
        rock |= {(x + i, y) for y in rows for i in range(-1 - WALL, 2 + WALL) if inb((x + i, y))} - floor
        edge = H - 1 if side == 'south' else 0
        m = w.mark([(x - 1, edge), (x, edge), (x + 1, edge)])
        w.tables.append(('exit', dict(mark=m, name='Sud' if side == 'south' else 'Nord')))
        w.exits.append((x, edge)); w.lanes |= lane
        if w.start is None: w.start = (x, edge - 2 if side == 'south' else edge + 2)
    # 4. les massifs de roche, au milieu : on tourne autour, par des couloirs de deux cases au moins. Ce sont eux qui font la
    # grotte — sans eux, c'est une salle vide.
    def squared(cells): return {q for c in cells if all((c[0] + i, c[1] + j) in cells for i in (0, 1) for j in (0, 1)) for q in ((c[0] + i, c[1] + j) for i in (0, 1) for j in (0, 1))}          # sans pointe d'une case
    plate = squared          # (une plaque au sol, elle, se contente de deux cases dans chaque sens)
    # Un décor à plateaux montre chaque roche de face : son dessus, puis deux rangées de face. Un massif y est donc fait
    # de blocs de deux cases de large sur **trois de haut** — plus bas, sa face commencerait sans dessus, coupée net.
    if kit:
        def squared(cells): return {q for c in cells if all((c[0] + i, c[1] + j) in cells for i in (0, 1) for j in (0, 1, 2)) for q in ((c[0] + i, c[1] + j) for i in (0, 1) for j in (0, 1, 2))}
    solid, masses, wet, whole = set(), [], set(), len(floor) + len(rock)
    room = floor - grown(w.lanes, 3)          # ni massif ni bassin devant la sortie
    def box(c, wide, tall): return {(c[0] + i, c[1] + j) for i in range(wide) for j in range(tall)}
    def raise_(most, share):
        """Des massifs, jusqu'à `most`, tant que le sol dépasse `share` de la tache. Bousculés et à trois cases les uns des
        autres d'abord ; puis plus petits et à deux cases ; droits enfin, s'il n'y en a toujours pas deux."""
        for kind in ('loose', 'tight', 'straight'):
            if kind == 'straight' and len(masses) >= min(most, 2): return
            spots = sorted(floor - solid - wet); rng.shuffle(spots)
            for c in spots:
                if len(masses) >= most or len(floor) - len(solid) <= share * whole: return
                mass = box(c, 4, 3) if kind == 'straight' else squared(blob(c[0], c[1], *((rng.uniform(2.0, 3.6), rng.uniform(1.8, 2.6)) if kind == 'loose' else (rng.uniform(1.8, 2.8), rng.uniform(1.6, 2.2))), 63 + len(masses)))
                if 12 <= len(mass) <= 60 and grown(mass, 2) <= room - solid - wet and (kind != 'loose' or not grown(mass, 3) & (solid | wet)): solid.update(mass); masses.append(mass)
    # Les éperons : des langues de roche qui partent de la paroi et coupent la salle en chambres. Une grande grotte sans eux
    # est une halle ; chacun laisse deux cases de sol sur ses flancs et devant lui, et ne ferme rien.
    bases = sorted(c for c in room if any((c[0] - i, c[1] - j) in rock for i, j in NEIGH4)); rng.shuffle(bases)
    spurs = 0
    for c in bases:
        if spurs >= len(floor) // 450: break
        for dx, dy in rng.sample(NEIGH4, 4):
            long_, wide = rng.randint(5, 11), rng.choice((3, 3, 4))
            px, py = -dy, dx
            if not {(c[0] - dx + px * u, c[1] - dy + py * u) for u in range(wide)} <= rock: continue          # adossé à la paroi sur toute sa largeur
            body = {(c[0] + dx * t + px * u, c[1] + dy * t + py * u) for t in range(long_) for u in range(wide)}
            body = squared(body | blob(c[0] + dx * (long_ - 2) + px * (wide // 2), c[1] + dy * (long_ - 2) + py * (wide // 2), 2.4, 2.1, 67 + spurs))          # un bout renflé
            def depth(q): return (q[0] - c[0]) * dx + (q[1] - c[1]) * dy
            free = room - solid
            if any(depth(q) < 0 for q in body) or any(depth(q) >= 0 and q not in free for q in grown(body, 2) - body): continue
            if any(q in solid for q in grown(body, 4)) or len(pieces(floor - solid - body)) != 1: continue
            solid |= body; spurs += 1; break
    raise_(1, 0.0)          # un massif, un bassin, un second massif, puis le reste : sur une petite grotte, chacun a sa place
    # 5. les bassins : un à trois, là où il reste de la place, qu'on longe de tous côtés
    def flood(most):
        spots = sorted(room - solid - wet); rng.shuffle(spots)
        for c in spots:
            if len(pieces(wet)) >= most: return
            pool = squared(blob(c[0], c[1], rng.uniform(2.0, 3.2), rng.uniform(1.7, 2.4), 71 + len(wet)))
            if 12 <= len(pool) <= 50 and any(all((q[0] + i, q[1] + j) in pool for i in (-1, 0, 1) for j in (-1, 0, 1)) for q in pool) and grown(pool, 2) <= room - solid and not grown(pool, 4) & wet: wet.update(pool)
        for wide, tall in ((5, 3), (4, 3)):          # pas de place pour un bassin aux bords bousculés : un petit, droit
            for c in spots:
                if not wet and grown(box(c, wide, tall), 2) <= room - solid: wet.update(box(c, wide, tall))
    if THEME_WATER.get(w.m['theme'], True): flood(1)
    raise_(2, 0.0)
    if THEME_WATER.get(w.m['theme'], True): flood(min(3, 1 + len(floor) // 300))
    raise_(max(2, len(floor) // 60), 0.50)
    # Halle, couloirs, ou un peu des deux : **cela dépend de la carte, ce n'est pas une règle** (Ludovic, 18/11/2026 :
    # « on peut avoir des couloirs ou pas de couloirs ou un peu des deux, ça dépend. Dans l'exemple c'est 3 couloirs,
    # mais ça aurait pu être différent »). `corridors = n` dans la table `[style]` d'un monde resserre la salle : on
    # pose des massifs tant qu'une case de sol reste à plus de `n` cases de toute roche — `2` donne des couloirs de
    # deux à quatre cases, comme la carte de référence. Sans ce réglage, la salle reste ce que les passes du dessus
    # en ont fait, et aucune graine ne bouge.
    tight = w.world.get('style', {}).get('corridors')
    if tight:
        for _ in range(80):
            free = floor - solid - wet
            wide = sorted(c for c in free if all((c[0] + i, c[1] + j) in free for i in range(-tight, tight + 1) for j in range(-tight, tight + 1)))
            if not wide: break
            rng.shuffle(wide)
            thin_now = len(free - squared(free))          # les cases de sol qui ne tiennent pas dans un carré de deux : on ne veut pas en créer
            def fits(mass):
                rest = free - mass
                if not (12 <= len(mass) <= 60) or not (grown(mass, 2) if kit else mass) <= room - solid - wet: return False          # (un décor à plateaux veut deux cases de sol autour, coins compris : ses bords de sol n'ont pas de tuile pour deux angles à la fois)
                return len(pieces(rest)) == 1 and len(rest - squared(rest)) <= thin_now          # la salle reste d'un seul tenant, et pas plus étroite qu'avant
            for c in wide:
                mass = squared(blob(c[0], c[1], rng.uniform(2.0, 3.2), rng.uniform(1.7, 2.4), 97 + len(masses)))
                if kit and not fits(mass): mass = box((c[0] - 1, c[1] - 1), 4, 3)          # à défaut, un bloc droit : il lui faut moins de place
                if not fits(mass): continue
                solid.update(mass); masses.append(mass); break
            else: break
    floor -= solid; rock |= solid
    # Un décor à plateaux montre chaque paroi de face : il lui faut **son dessus et ses deux rangées de face**, donc trois
    # cases de haut au-dessus de tout sol, et deux de large — sinon la face commence sans dessus, coupée net (Ludovic,
    # 18/11/2026). Ce qui est plus mince, au milieu de la salle, redevient du sol ; on ne touche pas à ce qui borde le vide.
    if kit:
        def bare(q): return q not in floor and q not in rock          # le vide
        while True:
            thin = {c for c in rock if not any(bare((c[0] + i, c[1] + j)) for i in (-2, -1, 0, 1, 2) for j in (-2, -1, 0, 1, 2))
                    and (((c[0], c[1] + 1) in floor and ((c[0], c[1] - 1) in floor or (c[0], c[1] - 2) in floor))
                         or ((c[0], c[1] - 1) in floor and (c[0], c[1] + 1) in floor)
                         or ((c[0] - 1, c[1]) in floor and (c[0] + 1, c[1]) in floor))}
            if not thin: break
            rock -= thin; floor |= thin; solid -= thin
        # Et l'inverse : une encoche de sol d'une seule case de large, entre un massif et la paroi, n'a pas la place de
        # ses deux bords — elle redevient de la roche (jamais dans le couloir de sortie).
        for _ in range(4):
            lone = floor - plate(floor) - w.lanes
            if not lone: break
            floor -= lone; rock |= lone
    # 6. des plaques de sol sombre, pour l'œil (en glace, la plaque est du verglas, et elle a une autre règle : plus bas)
    spots = sorted(floor - wet - w.lanes); rng.shuffle(spots)
    for c in (() if kit else spots):
        if len(pieces(w.earth)) >= 2 + len(floor) // 300: break
        patch = blob(c[0], c[1], rng.uniform(1.6, 2.6), rng.uniform(1.3, 2.0), 79 + len(w.earth))
        if 6 <= len(patch) <= 24 and grown(patch, 1) <= floor - wet and not grown(patch, 2) & w.earth: w.earth |= patch
    # le plan
    for c in CELLS: w.ground[c] = '.' if c in floor else '#'
    for c in wet: w.ground[c] = 'o'
    w.mountain = {c for c in rock if inb(c)}
    for hole in pieces({c for c in CELLS if w.ground[c] == '#'} - w.mountain):          # une poche de noir enfermée dans la roche : c'est de la roche
        if not any(c[0] in (0, W - 1) or c[1] in (0, H - 1) for c in hole): w.mountain |= hole
    # une entaille de noir de moins de trois cases dans la roche ne se dessine pas (son liseré n'a pas la place) : de la roche
    dark = {c for c in CELLS if w.ground[c] == '#'} - w.mountain
    def void(c): return c in dark or not inb(c)
    kept = {(c[0] + i, c[1] + j) for c in dark for i in (-1, 0, 1) for j in (-1, 0, 1) if all(void((c[0] + a, c[1] + b)) for a in (-1, 0, 1) for b in (-1, 0, 1))}
    w.mountain |= dark - kept
    for c in w.mountain: w.ground[c] = '.'
    # 6 bis. Le **verglas** d'une grotte de glace n'est pas là pour l'œil : c'est un **passage obligé** (Ludovic,
    # 18/11/2026 : « les plaques de verglas doivent faire la largeur d'un passage […] s'il est là, le joueur devra
    # passer par-dessus pour accéder à ce qu'il y a derrière. C'est pas obligé qu'il soit là »). Une plaque barre donc
    # un passage **d'une paroi à l'autre**, sur deux à huit cases de profondeur, et coupe le sol en deux : ce qui est
    # derrière ne s'atteint qu'en la traversant. On barre d'abord un bras ou une chambre (moins de la moitié du sol
    # derrière : c'est là que vont les objets, plus bas) ; à défaut, le débouché du couloir d'entrée, qu'on traverse
    # pour entrer dans la salle. S'il n'y a aucun passage à barrer, il n'y a pas de verglas.
    guarded = set()          # ce qu'on n'atteint qu'en traversant une plaque de verglas
    if kit:
        WIDE = 8          # au-delà, ce n'est plus un passage, c'est une salle
        def bands(cells):
            cols = {}
            for x, y in sorted(cells):
                runs = cols.setdefault(x, [])
                if runs and runs[-1][1] == y - 1: runs[-1][1] = y
                else: runs.append([y, y])
            out = []
            for x in sorted(cols):
                for y0, y1 in cols[x]:          # une colonne de sol, d'une paroi à l'autre…
                    if not 2 <= y1 - y0 + 1 <= WIDE: continue
                    band, span = [(x, y0, y1)], (y0, y1)
                    for d in range(1, 8):          # … et ses voisines, tant que c'est le même passage
                        nxt = [r for r in cols.get(x + d, []) if min(r[1], span[1]) - max(r[0], span[0]) + 1 >= 2]
                        if len(nxt) != 1 or nxt[0][1] - nxt[0][0] + 1 > WIDE: break
                        span = tuple(nxt[0]); band.append((x + d,) + span)
                        out.append({(bx, y) for bx, a, b in band for y in range(a, b + 1)})
            return out
        turn = lambda cells: {(c[1], c[0]) for c in cells}
        def stranded(b):
            """Sur le verglas on glisse (CharacterMovement.kt) : aller quelque part n'assure plus d'en revenir. Les cases
            de sol qu'on n'atteint pas en glissant, puis les cases où l'on s'arrête et d'où l'on ne revient pas au départ."""
            free_ = lambda c: inb(c) and c not in b['SOLID']
            rest, _ = builder.glide(w.start, free_, b['SLICK'])
            lost = sorted(c for c in floor - w.earth - rest if free_(c))
            if lost: return lost
            dry = floor - w.earth
            probes = (rest & b['SLICK']) | {min(part) for part in pieces(dry & rest)}
            return sorted(c for c in probes if w.start not in builder.glide(c, free_, b['SLICK'])[0])
        thin_now = len(floor - plate(floor))
        gates = []
        for patch in bands(floor) + [turn(b) for b in bands(turn(floor))]:
            if plate(patch) != patch or patch & grown({w.start}, 3): continue          # une matière à bords, et pas sous les pieds du joueur qui entre
            rest = floor - patch
            parts = pieces(rest)
            if len(parts) != 2 or len(rest - plate(rest)) > thin_now: continue          # elle coupe le sol en deux, sans y laisser de case étroite
            behind = min(parts, key=lambda part: w.start in part)
            if len(behind) >= 8: gates.append((len(behind) > len(floor) // 2, -len(patch), sorted(patch), behind))
        gates.sort(key=lambda g: g[:3])          # un bras avant le couloir d'entrée ; la plus grande plaque d'abord
        for entry, _, cells, behind in gates:
            patch = set(cells)
            if len(pieces(w.earth)) >= (1 if entry else 1 + len(floor) // 400): break
            if grown(patch, 3) & w.earth: continue
            w.earth |= patch
            probe = w.probe()
            if any(line.startswith(('sol :', 'paroi :')) for line in probe['warn']): w.earth -= patch          # le constructeur n'y trouve pas la place des bords
            elif stranded(probe): w.earth -= patch          # on y glisse : il faut pouvoir la traverser dans les deux sens, sans y rester coincé
            elif not entry: guarded |= behind
        # Sur une grande plaque, un ou deux **cailloux ronds** : c'est sur le verglas qu'ils servent (Ludovic, 18/11/2026 :
        # « pour servir d'obstacle pour faire les casse-têtes »). Contre eux on s'arrête, et de là on repart dans un autre
        # sens. On n'en garde un que si l'on traverse toujours, dans les deux sens, sans rester coincé nulle part.
        stones = random.Random(sub('relief') + 91)
        for part in sorted(pieces(w.earth), key=min):
            spots = sorted(part); stones.shuffle(spots)
            put = []
            for c in spots[:8]:
                if len(put) >= (0 if len(part) < 12 else 2 if len(part) >= 30 else 1): break
                if any(max(abs(c[0] - q[0]), abs(c[1] - q[1])) < 3 for q in put): continue
                w.props.append((THEME_TOPS[w.m['theme']][len(put) % 2], c[0], c[1]))
                if stranded(w.probe()): w.props.pop()
                else: put.append(c)
    built = w.probe()
    reach, wall = built['REACH'], built['SOLID']
    walk = set(reach)
    icy = grown(w.earth, 1) if kit else set()
    dry = lambda c: c not in icy          # en glace, rien ne se pose sur le verglas ni contre lui : un caillou au bord d'une plaque change l'endroit où l'on s'arrête
    # 7. les rochers et les stalagmites : le long des parois, un pour quinze à vingt cases de sol, jamais dans un passage
    AROUND = [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]
    def pinch(c):
        ring = [(c[0] + i, c[1] + j) in walk for i, j in AROUND]
        if all(ring) or not any(ring): return not any(ring)
        runs, k0, k = 0, next(k for k in range(8) if not ring[k]), 0
        while k < 8:
            if ring[(k0 + k) % 8]:
                run = []
                while k < 8 and ring[(k0 + k) % 8]: run.append((k0 + k) % 8); k += 1
                if any(q % 2 for q in run): runs += 1
            else: k += 1
        return runs != 1
    placed = []
    edge_ = sorted(c for c in walk if any((c[0] + i, c[1] + j) in wall for i, j in NEIGH4) and c not in w.lanes and c not in grown(w.lanes, 1) and dry(c))
    rng.shuffle(edge_)
    for c in edge_:
        if len(placed) >= len(walk) // 18: break
        if any(abs(c[0] - p[0]) + abs(c[1] - p[1]) < 4 for p in placed) or pinch(c): continue
        kind = rng.choice(THEME_ROCKS[w.m['theme']])
        w.props.append((kind, c[0], c[1])); placed.append(c); walk.discard(c)
    open_ = sorted(c for c in walk if all((c[0] + i, c[1] + j) in walk for i in range(-2, 4) for j in range(-3, 3)) and c not in grown(w.lanes, 2))
    rng.shuffle(open_)
    big = []
    for c in open_:          # et un ou deux gros blocs au milieu d'une salle
        if kit: break          # (pas en glace : au sol, il n'y a que le caillou et le pic foncés)
        if len(big) >= len(walk) // 220: break
        if any(abs(c[0] - p[0]) + abs(c[1] - p[1]) < 10 for p in big): continue
        if kit and any((c[0] + i, c[1] - j) in w.earth for i in (-1, 0, 1, 2) for j in (-1, 0, 1, 2)): continue          # pas sur une plaque de glace lisse, qu'il cacherait à moitié
        w.props.append(('boulder', c[0], c[1])); big.append(c)
        walk -= {(c[0] + i, c[1] - j) for i in (0, 1) for j in (0, 1)}
    # 7 bis. Les cailloux ronds et pâles de la glace : **sur le dessus du grand plateau**, là où le petit ne le couvre pas
    # — le dessus uni d'un éperon, d'un massif épais, d'un redan de la paroi. La carte d'exemple en a quatorze, tous là.
    # On ne choisit que des cases de dessus plein : paroi tout autour, et deux rangées de paroi encore au sud (plus près
    # du bord, la case porte un flanc, un pli ou une rangée de face, et le caillou serait posé sur une arête).
    if THEME_TOPS.get(w.m['theme']):
        M = built['MOUNTAIN']
        flat = sorted(c for c in M - built['UPPER'] if all((c[0] + i, c[1] + j) in M for i in (-1, 0, 1) for j in (-1, 0, 1, 2)))
        tops_, lot = [], random.Random(sub('decor') + 83)
        lot.shuffle(flat)
        for c in flat:
            if len(tops_) >= 1 + len(flat) // 8: break
            if any(max(abs(c[0] - p[0]), abs(c[1] - p[1])) < 3 for p in tops_): continue
            w.props.append((THEME_TOPS[w.m['theme']][len(tops_) % 2], c[0], c[1])); tops_.append(c)
        # Et **sur le tour de la grotte** (Ludovic, 19/11/2026 : « là il n'y en a aucun sur le tour »). La paroi du bord
        # porte le petit plateau jusqu'à son flanc : le caillou s'y pose dans la colonne du bord du petit plateau, qui
        # s'écarte d'une case (le constructeur fait l'encoche) — entre lui et le vide il reste le liseré et un bord.
        U, dark = built['UPPER'], {c for c in CELLS if w.ground[c] == '#'}
        def ledge(c):
            if c not in U or not all((c[0] + i, c[1] + j) in M for i in (-1, 0, 1) for j in (-1, 0, 1, 2)): return False
            if (c[0], c[1] - 1) not in U or (c[0], c[1] + 1) not in U: return False          # une encoche dans le bord, pas son bout
            return any((c[0] + s, c[1]) not in U and (c[0] - s, c[1]) in U and (c[0] - 2 * s, c[1]) in U and ((c[0] - 3 * s, c[1]) in dark or (c[0] - 4 * s, c[1]) in dark) for s in (1, -1))
        rim = sorted(c for c in U if ledge(c))
        lot.shuffle(rim)
        around_ = []
        for c in rim:
            if len(around_) >= 2 + len(rim) // 12: break
            if any(max(abs(c[0] - p[0]), abs(c[1] - p[1])) < 6 for p in tops_ + around_): continue
            w.props.append((THEME_TOPS[w.m['theme']][(len(tops_) + len(around_)) % 2], c[0], c[1])); around_.append(c)
    # 8. les objets : au fond, loin de l'entrée, dans un renfoncement de la paroi
    far, ring_ = {w.start: 0}, [w.start]
    while ring_:
        nxt = []
        for c in ring_:
            for i, j in NEIGH4:
                n = (c[0] + i, c[1] + j)
                if n in walk and n not in far: far[n] = far[c] + 1; nxt.append(n)
        ring_ = nxt
    nooks = sorted((c for c in far if sum((c[0] + i, c[1] + j) in wall for i, j in NEIGH4) >= 2 and c not in w.lanes and dry(c)), key=lambda c: (c not in guarded, -far[c], c))          # d'abord derrière le verglas : c'est ce qu'il garde
    found = []
    for c in nooks:
        if len(found) >= G['items']: break
        if any(abs(c[0] - f[0]) + abs(c[1] - f[1]) < 10 for f in found) or pinch(c) or any(abs(c[0] - p[0]) + abs(c[1] - p[1]) < 2 for p in placed): continue
        item = ITEMS[len(found) % len(ITEMS)]
        found.append(c); walk.discard(c)
        w.tables.append(('item', dict(mark=w.mark([c]), name='Item%d' % len(found), item=item[0], text='Vous trouvez %s !|Vous rangez %s dans la poche %s.' % (item[1], item[2], item[3]), exact=True)))
    # 9. les échelles (docs/mapping.md, « Grotte » : « au bout des bras, chacune dans un cul-de-sac »). Deux à quatre,
    # adossées au **haut** d'une paroi — leur dessin monte d'une case dans la roche —, jamais sur un passage ni devant
    # la sortie. Elles n'arrêtent pas : on monte dessus. Elles ne mènent nulle part tant qu'une grotte n'a qu'un étage,
    # comme ses sorties, qui n'ont pas encore de scène où aller : c'est le même manque, pas un décor posé pour faire joli.
    # Un couloir de grotte fait deux cases au moins : un bout de bras n'est donc pas une case à voisin unique, mais un
    # **renfoncement** — de la roche au-dessus, de la roche sur au moins un autre côté — et le plus loin possible de l'entrée.
    climbs = sorted((c for c in walk if (c[0], c[1] - 1) in wall and c in far
                     and sum((c[0] + i, c[1] + j) in wall for i, j in NEIGH4) >= 2 and c not in grown(w.lanes, 2) and dry(c)),
                    key=lambda c: (-far[c], c))
    ladders = []
    for c in climbs:
        if ladders: break          # une seule qui monte : le nombre d'échelles suit le nombre d'étages, et il n'y en a qu'un
        if any(abs(c[0] - f[0]) + abs(c[1] - f[1]) < 3 for f in found): continue
        if any(abs(c[0] - p[0]) + abs(c[1] - p[1]) < 2 for p in placed): continue          # pas contre un rocher déjà posé
        w.props.append(('ladder', c[0], c[1])); ladders.append(c); walk.discard(c)
    if not ladders: w.notes.append('aucune echelle qui monte : pas de renfoncement adosse a une paroi')
    # Et **une seule qui descend** : un trou dans le sol, vu de dessus, qui tient sur deux cases de côté. Le décor de la
    # grotte brune n'en a pas (sa planche de falaises n'a aucun trou à échelle) ; il n'y en a donc que dans la glace.
    if 'hole' in THEME_DECOR.get(w.m['theme'], ()):
        def roomy(c): return c in far and all((c[0] + i, c[1] - j) in walk and dry((c[0] + i, c[1] - j)) for i in (-1, 0, 1) for j in (0, 1)) and c not in grown(w.lanes, 2)
        def clear(c): return not (any(abs(c[0] - p[0]) + abs(c[1] - p[1]) < 10 for p in ladders) or any(abs(c[0] - f[0]) + abs(c[1] - f[1]) < 3 for f in found) or any(abs(c[0] - p[0]) + abs(c[1] - p[1]) < 3 for p in placed))
        nooks_ = sorted((c for c in walk if roomy(c) and sum((c[0] + i, c[1] + j) in wall for i, j in NEIGH4) >= 1), key=lambda c: (-far[c], c))
        anywhere = sorted((c for c in walk if roomy(c)), key=lambda c: (-far[c], c))          # une petite grotte n'a pas toujours de recoin assez large
        for c in [q for q in nooks_ if clear(q)] + [q for q in anywhere if clear(q)]:
            w.props.append(('hole', c[0], c[1])); walk -= {(c[0] + i, c[1] - j) for i in (-1, 0, 1) for j in (0, 1)}
            break
        else: w.notes.append('aucune echelle qui descend : pas de place de deux cases au fond d un bras')
    # Les **fissures** du sol (docs/mapping.md, principe 9 : pas de motif qui se répète). La carte d'exemple en sème
    # seize sur ses 255 cases de sol (tools/maps/ice_cave/survey.json) : une pour seize cases — une tache de deux cases
    # de côté, à plat, sans collision — pour que le sol ne soit pas partout le même carreau. On en met une pour dix-huit
    # cases de sol nu. Jamais sur la glace lisse, ni sous un rocher, ni devant la sortie.
    if 'crack' in THEME_DECOR.get(w.m['theme'], ()):
        plain = walk - w.earth - grown(w.lanes, 1)
        spots = sorted(c for c in plain if all((c[0] + i, c[1] - j) in plain for i in (0, 1) for j in (0, 1)))
        rng.shuffle(spots)
        cracks = []
        for c in spots:
            if len(cracks) >= len(plain) // 18: break
            if any(max(abs(c[0] - p[0]), abs(c[1] - p[1])) < 3 for p in cracks): continue          # jamais deux qui se touchent
            w.props.append(('crack', c[0], c[1])); cracks.append(c)
    if kit and w.earth:          # tout est posé : on glisse toujours d'un bord à l'autre, et l'on revient
        stuck = stranded(w.probe())
        if stuck: w.notes.append('verglas : %d cases qu on n atteint pas en glissant, ou d ou l on ne revient pas — %s' % (len(stuck), stuck[:5]))
    if len(masses) < 2: w.notes.append('seulement %d massif de roche : la salle est trop petite' % len(masses))
    return w


def generate(world, source='monde'):
    w = World(world, source)
    if w.S['cavern']: return generate_cave(w)
    W, H, S, CELLS, inb, sub = w.W, w.H, w.S, w.CELLS, w.inb, w.sub
    R, C, V, G = S['relief'], S['climate'], S['vegetation'], S['gameplay']
    FRAME = G['frame']

    seam, seam_high = world.get('seam') or {}, set()          # la couture avec la carte du sud (écrite par neighbor.py)
    if seam and seam.get('side') != 'south': raise SystemExit('[seam] : seul side = "south" est fait (la carte voisine est au sud)')
    # ============================================================ 1. le relief : un bruit, mêlé à la forme demandée, découpé par des seuils
    height = {c: fractal(sub('relief'), c[0], c[1], R['scale'], R['octaves'], R['persistence'], R['lacunarity']) for c in CELLS}
    lo, hi = min(height.values()), max(height.values())
    height = {c: (h - lo) / (hi - lo or 1) for c, h in height.items()}          # de 0 à 1 : les seuils veulent dire la même chose d'une graine à l'autre
    weight = S['shape']['weight']
    if weight: height = {c: h * (1 - weight) + mask(S['shape'], c[0], c[1], W, H, FRAME) * weight for c, h in height.items()}
    # Le cadre (docs/mapping.md, A) : la terre va jusqu'au bord, la mer ne le touche pas. Une ceinture de terre fait le
    # tour de la carte ; la forêt la couvrira, et l'on n'y marchera jamais.
    for c in CELLS:          # (sa profondeur ondule : jamais plus de six cases en ligne droite — C)
        d = w.edge(c) - fractal(sub('relief') + 5, c[0], c[1], 4.0, 2) * 6.0 + 2.0
        if d < FRAME + (4 if w.open else 0): height[c] = max(height[c], R['sand'] + 0.10)          # (sur une plage, quatre cases de plus : la place d'un chemin entre la lisière et le sable)          # (pas de pente douce vers elle : sa falaise tombe dans l'eau, et la mer garde sa place)
    if w.open:          # une plage : de ce côté la mer va jusqu'au bord, sur toute sa longueur — plus loin que la marge, pour qu'aucun sable ne s'y avance
        for c in CELLS:
            if w.offshore(c) < 6: height[c] = 0.0
    for sh in world.get('shore', []):          # l'eau de la carte voisine arrive à ce bord (`[[shore]]` : side, from, to, depth) : elle continue ici, colonne pour colonne, puis le relief reprend la main
        for c in CELLS:
            along, across = (c[0], H - 1 - c[1] if sh['side'] == 'south' else c[1]) if sh['side'] in ('north', 'south') else (c[1], c[0] if sh['side'] == 'west' else W - 1 - c[0])
            if sh['from'] <= along <= sh['to'] and across < sh.get('depth', 12) + (fractal(sub('relief') + 13, along, 0, 6.0, 2) - 0.5) * 6: height[c] = 0.0
    ground = w.ground
    for c, h in height.items(): ground[c] = '~' if h < R['water'] else ':' if h < R['sand'] else '.'
    band = R.get('beach', 3)          # une plage est une bande le long de l'eau : au-delà de quelques cases, le sable redevient de l'herbe
    wet = {c for c in CELLS if ground[c] == '~'}
    for c in CELLS:
        if ground[c] == ':' and not any((c[0] + i, c[1] + j) in wet for i in range(-band, band + 1) for j in range(-band, band + 1)): ground[c] = '.'
    for _ in range(R['smooth']):          # pas de confettis : une case isolée prend le terrain de ses voisines
        nxt = {}
        for c in CELLS:
            around = [ground[(c[0] + i, c[1] + j)] for i in (-1, 0, 1) for j in (-1, 0, 1) if inb((c[0] + i, c[1] + j))]
            nxt[c] = max('~:.', key=around.count) if around.count(ground[c]) < 4 else ground[c]
        ground.update(nxt)

    def clean():
        for piece in pieces({c for c in CELLS if ground[c] == '.'}):          # un îlot d'herbe trop petit pour une falaise redevient du sable
            if len(piece) < 40:
                for c in piece: ground[c] = ':'
        for piece in pieces({c for c in CELLS if ground[c] == '~'}):          # une flaque : de l'herbe (un étang fait douze cases au moins — O)
            if len(piece) < 12:
                for c in piece: ground[c] = '.'
        for piece in pieces({c for c in CELLS if ground[c] == ':'}):          # une tache de sable loin de l'eau : de l'herbe
            if not any(ground.get((c[0] + i, c[1] + j)) == '~' for c in piece for i in (-1, 0, 1) for j in (-1, 0, 1)):
                for c in piece: ground[c] = '.'
    def widen():
        """Un creux — eau ou sable — a la place de ses deux falaises : cinq cases de large au moins (une paroi et son liseré
        de chaque côté, de l'eau au milieu). Plus étroit, le constructeur n'y verrait que de la roche et du sable sec."""
        low = {c for c in CELLS if ground[c] != '.'}
        core = {c for c in low if all((c[0] + i, c[1] + j) in low for i in range(-2, 3) for j in range(-2, 3))}
        keep = {(c[0] + i, c[1] + j) for c in core for i in range(-2, 3) for j in range(-2, 3)}
        for c in low - keep: ground[c] = '.'
    widen()
    clean()
    if S['kind'] == 'beach':          # le relief d'une plage : une ou deux buttes posées sur le sable ou au bord de l'eau, cernées de falaise — la forêt les couvrira
        mound = random.Random(sub('relief') + 3)
        low = {c for c in CELLS if ground[c] != '.'}
        sand0 = {c for c in CELLS if ground[c] == ':'}
        roomy = sorted(c for c in low if w.edge(c) >= FRAME + 8 and w.offshore(c) >= 14 and all((c[0] + i, c[1] + j) in low for i in range(-9, 10) for j in range(-8, 9))
                       and any((c[0] + i, c[1] + j) in sand0 for i in range(-5, 6) for j in range(-4, 5)))
        mound.shuffle(roomy)
        tops = []
        for c in roomy:
            if len(tops) >= 2: break
            if any(abs(c[0] - t[0]) + abs(c[1] - t[1]) < 22 for t in tops): continue
            rx, ry = mound.uniform(4.0, 5.0), mound.uniform(3.2, 3.8)
            for i in range(-6, 7):
                for j in range(-5, 6):
                    if (i / rx) ** 2 + (j / ry) ** 2 <= 1.0 + (lattice(sub('relief') + 11, c[0] + i, c[1] + j) - 0.5) * 0.5: ground[(c[0] + i, c[1] + j)] = '.'
            tops.append(c)
        clean()

    def roughen():
        """Jamais plus de six cases en ligne droite pour un bord de plateau (C) : une encoche de deux cases dans tout bord trop long."""
        cut = random.Random(sub('relief') + 9)
        changed = 0
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):          # le côté où est le vide
            ax = (1, 0) if dx == 0 else (0, 1)
            rim = {c for c in CELLS if ground[c] == '.' and inb((c[0] + dx, c[1] + dy)) and ground[(c[0] + dx, c[1] + dy)] != '.' and w.edge(c) >= 2}
            for c in sorted(rim):
                if (c[0] - ax[0], c[1] - ax[1]) in rim: continue
                run, q = [], c
                while q in rim: run.append(q); q = (q[0] + ax[0], q[1] + ax[1])
                k = cut.randint(2, 4)
                while len(run) > 6 and k < len(run) - 2:
                    for q in run[k:k + 2]: ground[q] = ground[(q[0] + dx, q[1] + dy)]; changed += 1
                    k += cut.randint(5, 7)
        return changed
    for _ in range(3):
        if not roughen(): break
        clean()
    for _ in range(12):          # une plage fait deux cases de large (G). Le pied de la falaise prend la case de sable qui touche l'herbe : ce qui reste doit tenir dans des carrés de deux cases
        core = {c for c in CELLS if ground[c] == ':' and not any(ground.get((c[0] + i, c[1] + j)) == '.' for i in (-1, 0, 1) for j in (-1, 0, 1))}
        wide = {q for c in core if all((c[0] + i, c[1] + j) in core for i in (0, 1) for j in (0, 1)) for q in ((c[0] + i, c[1] + j) for i in (0, 1) for j in (0, 1))}
        if not core - wide: break
        for c in core - wide: ground[c] = '~'
        clean()
    for _ in range(14):          # et ce que le constructeur, lui, voit encore de trop étroit
        built = w.probe()
        beach = built['BEACH'] - built['RING']
        thin = {c for c in beach if ((c[0] - 1, c[1]) not in beach and (c[0] + 1, c[1]) not in beach) or ((c[0], c[1] - 1) not in beach and (c[0], c[1] + 1) not in beach)}
        thin = {c for c in thin if w.edge(c) >= FRAME}
        small = {c for p in pieces(beach) if len(p) < 12 for c in p if w.edge(c) >= FRAME}          # et une plage de quelques cases n'en est pas une
        dry = {c for p in pieces(beach) if not any((c[0] + i, c[1] + j) in built['SEA'] for c in p for i in (-1, 0, 1) for j in (-1, 0, 1)) for c in p}          # du sable sans eau : un bras trop étroit, que la roche a bouché
        lost = {c for c in CELLS if ground[c] == '.' and c in built['SEA']}          # une miette de plateau que le constructeur a laissée à la mer
        puddle = {c for p in pieces(built['SEA']) if len(p) < 12 for c in p}          # une mare que la roche a réduite à quelques cases (O)
        if not thin and not small and not dry and not lost and not puddle: break
        for c in lost: ground[c] = '~'
        for c in puddle:
            for i in range(-2, 3):
                for j in range(-2, 3):
                    if ground.get((c[0] + i, c[1] + j)) == '~': ground[(c[0] + i, c[1] + j)] = '.'
        for c in thin | small: ground[c] = '~' if ground[c] == ':' else '.'          # (un liseré que le sable a cerné, au creux d'une falaise : le creux se comble)
        for c in dry:
            for i in range(-2, 3):
                for j in range(-2, 3):
                    if inb((c[0] + i, c[1] + j)): ground[(c[0] + i, c[1] + j)] = '.'
        clean()

    # Les étangs (O) : une eau dans les terres n'est pas un lac au fond d'une falaise. Elle est au niveau de l'herbe, avec sa
    # berge, et son sable redevient de la pelouse. Seule une très grande eau (près de deux fois `pond_max`) garde ses falaises,
    # sa plage et son escalier.
    def settle():
        """Ce que le constructeur ne garde pas d'un étang (trop étroit pour sa berge, sur un bord de plateau) redevient de l'herbe."""
        kept = w.probe()['POND']
        for c in CELLS:
            if ground[c] == 'o' and c not in kept: ground[c] = '.'
    for water in sorted(pieces({c for c in CELLS if ground[c] == '~'}), key=min):
        if not 12 <= len(water) <= R['pond_max'] * 1.9 or any(w.edge(c) < FRAME or w.offshore(c) < 8 for c in water): continue
        basin = set(water)
        if len(water) > R['pond_max']:          # une eau plus grande perd sa case de rive — celle que la falaise lui aurait prise : elle reste un étang, pas une mer
            water = {c for c in water if all((c[0] + i, c[1] + j) in basin for i, j in NEIGH8)}
            for c in basin - water: ground[c] = '.'
            if len(water) < 12: continue
        shore_, todo = set(), list(water)
        while todo:          # sa plage : le sable qui le touche, de proche en proche, à trois cases de l'eau au plus
            c = todo.pop()
            for i, j in NEIGH8:
                n = (c[0] + i, c[1] + j)
                if ground.get(n) == ':' and n not in shore_ and any((n[0] + a, n[1] + b) in water for a in range(-4, 5) for b in range(-4, 5)): shore_.add(n); todo.append(n)
        for c in water: ground[c] = 'o'
        for c in shore_: ground[c] = '.'
    if any(v == 'o' for v in ground.values()): settle(); clean()

    def deep(c, n): return all(ground.get((c[0] + i, c[1] + j), '.') == '.' for i in range(-n, n + 1) for j in range(-n, n + 1))          # loin du bord du plateau (le hors-carte compte pour de l'herbe)
    grass = {c for c in CELLS if ground[c] == '.'}
    rocky = {c for c in grass if height[c] >= R['mountain'] and deep(c, 2) and w.edge(c) >= FRAME}
    core = {c for c in rocky if all((c[0] + i, c[1] + j) in rocky for i in (-2, -1, 0, 1, 2) for j in (-2, -1, 0, 1, 2))}          # un massif, pas une arête ni un ruban : on ne garde que ce qui a cinq cases d'épaisseur
    for massif in pieces({(c[0] + i, c[1] + j) for c in core for i in (-2, -1, 0, 1, 2) for j in (-2, -1, 0, 1, 2)} & rocky):
        if len(massif) >= 70: w.mountain |= massif
    # Du relief (D) : quelques buttes — des terrasses d'un cran, que la forêt couvrira. Ni trop petites pour leur
    # falaise, ni si grandes qu'elles coupent la carte.
    # ============================================================ 2. les points d'intérêt : sorties et maisons
    def nearest(wish, among): return min(among, key=lambda c: (abs(c[0] - wish[0]) + abs(c[1] - wish[1]), c)) if among else None
    asked = list(world.get('exit', []))
    if not asked:          # une carte a des sorties : sans consigne, deux, sur des bords de terre
        shape, sea, axis = S['shape']['name'], S['shape']['sea'], S['shape']['axis']
        sides = ['west', 'east'] if shape == 'corridor' and axis == 'horizontal' else ['north', 'south']
        if S['hamlet']: sides = ['south', 'east']          # un village : on y entre par le sud, face à son bâtiment repère ; une seconde sortie sur le côté
        if shape in ('coast', 'bay'): sides = [{'south': 'north', 'north': 'south', 'west': 'east', 'east': 'west'}[sea], 'east' if sea in ('north', 'south') else 'north']
        asked = [dict(side=side, at=0.5, name={'north': 'Nord', 'south': 'Sud', 'west': 'Ouest', 'east': 'Est'}[side]) for side in sides]
    for e in asked:          # une sortie qui prolonge une autre carte se donne à la case près (`cell`) : la terre s'y fait, plutôt que la sortie ne se déplace
        if 'cell' not in e: continue
        side = e['side']
        inward = (0, 1) if side == 'north' else (0, -1) if side == 'south' else (1, 0) if side == 'west' else (-1, 0)
        c0 = (e['cell'], 0 if side == 'north' else H - 1) if side in ('north', 'south') else (0 if side == 'west' else W - 1, e['cell'])
        for k in range(0, FRAME + 6):
            for i in range(-3, 4):
                q = (c0[0] + inward[0] * k + i * abs(inward[1]), c0[1] + inward[1] * k + i * abs(inward[0]))
                if inb(q): ground[q] = '.'; w.mountain.discard(q)
    if any('cell' in e for e in asked) and any(v == 'o' for v in ground.values()): settle()          # un couloir imposé a pu entamer un étang
    grass = {c for c in CELLS if ground[c] == '.'}
    dry0 = w.probe()['INSIDE']          # le dessus des plateaux tel que le constructeur le voit : un couloir de sortie n'aboutit pas sur un bord de falaise
    for e in asked:
        side, at = e['side'], e.get('at', 0.5)
        inward = (0, 1) if side == 'north' else (0, -1) if side == 'south' else (1, 0) if side == 'west' else (-1, 0)
        line = [(x, 0 if side == 'north' else H - 1) for x in range(FRAME + 2, W - FRAME - 2)] if side in ('north', 'south') else [(0 if side == 'west' else W - 1, y) for y in range(FRAME + 2, H - FRAME - 2)]
        for depth in (FRAME + 4, FRAME + 1, 5):          # un couloir bien enfoncé dans la carte ; à défaut, celui que la lisière permet — un pont fera le reste
            def lane(c, depth=depth): return [(c[0] + inward[0] * k + i * abs(inward[1]), c[1] + inward[1] * k + i * abs(inward[0])) for k in range(0, depth) for i in (-1, 0, 1)]
            ok = [c for c in line if all(inb(q) and ground[q] == '.' and q in dry0 and q not in w.mountain and q not in w.levels and deep(q, 1 if w.edge(q) > 1 else 0) for q in lane(c))]
            ok = [c for c in ok if all(abs(c[0] - x[2][1][0]) + abs(c[1] - x[2][1][1]) >= 14 for x in w.exits)]          # pas deux sorties au même endroit
            if ok: break
        wish = line[int(at * (len(line) - 1))] if 'cell' not in e else ((e['cell'], line[0][1]) if side in ('north', 'south') else (line[0][0], e['cell']))
        c = nearest(wish, ok)
        if c is not None and 'cell' in e and c != wish: w.notes.append('sortie %s : demandée à la case %d, posée en %s — elle ne prolonge plus la carte voisine' % (e.get('name', side), e['cell'], c))
        if c is None and not e.get('moved'):          # pas de place sur ce bord : on essaie les autres, avant de renoncer
            asked.extend(dict(e, side=other, moved=True) for other in ('north', 'south', 'west', 'east') if other != side and not any(x[0].get('name') == e.get('name') for x in w.exits))
            continue
        if c is None or any(x[0].get('name') == e.get('name') for x in w.exits): continue
        span = [(c[0] + i * abs(inward[1]), c[1] + i * abs(inward[0])) for i in (-1, 0, 1)]
        m = w.mark(span)
        if e.get('moved'): w.notes.append('sortie %s : déplacée sur le bord %s, faute de place sur celui qu on demandait' % (e.get('name', side), side))
        w.exits.append((e, m, span, inward)); w.trail |= set(lane(c)); w.lanes |= {(q[0] + i, q[1] + j) for q in lane(c) for i in (-1, 0, 1) for j in (-1, 0, 1)}
        w.pois.append((c[0] + inward[0] * (depth - 1), c[1] + inward[1] * (depth - 1)))
        w.tables.append(('exit', dict(mark=m, **{k: e[k] for k in ('name', 'scene', 'door') if k in e})))
    if S['deep']:          # une forêt profonde : une dizaine de clairières sur une grille bousculée, chacune avec sa plaque de terre ; une sur trois avec sa mare
        glade = random.Random(sub('paths') + 31)
        pad_ = FRAME + 2
        cols_, rows_ = max(2, (W - 2 * pad_) // 11), max(2, (H - 2 * pad_) // 9)          # onze cases sur neuf par clairière : la place d'un mur d'arbres entre deux
        def blob(cx, cy, rx, ry, salt): return {(cx + i, cy + j) for i in range(-6, 7) for j in range(-5, 6) if (i / rx) ** 2 + (j / ry) ** 2 <= 1.0 + (lattice(sub('relief') + salt, cx + i, cy + j) - 0.5) * 0.7}
        grid_ = [(i, j) for i in range(cols_) for j in range(rows_)]
        glade.shuffle(grid_)
        for i, j in sorted(grid_[len(grid_) // 8:]):          # une case de la grille sur huit reste du bois
            if True:
                cx = pad_ + int((i + 0.5 + glade.uniform(-0.25, 0.25)) * (W - 2 * pad_) / cols_)
                cy = pad_ + int((j + 0.5 + glade.uniform(-0.25, 0.25)) * (H - 2 * pad_) / rows_)
                room = {q for q in blob(cx, cy, glade.uniform(2.6, 3.4), glade.uniform(2.0, 2.6), 31) if inb(q) and w.edge(q) >= FRAME + 3 and ground[q] == '.'}
                if len(room) < 14 or (cx, cy) not in room: continue
                w.glades |= room; w.hearts.append((cx, cy))
                w.earth |= {q for q in blob(cx, cy, glade.uniform(2.0, 2.6), glade.uniform(1.5, 2.0), 37) if q in room}
        for (cx, cy) in glade.sample(w.hearts, max(1, len(w.hearts) // 3)):          # les mares : contre la clairière, de douze à quarante cases
            dx_ = (1 if cx < W // 2 else -1) * glade.randint(5, 6)          # du côté du milieu de la carte : pas dans la lisière
            pool = {q for q in blob(cx + dx_, cy + glade.choice((-1, 0, 1)), glade.uniform(2.4, 3.4), glade.uniform(1.8, 2.6), 41) if inb(q)}
            if len(pool) >= 12 and (cx, cy) not in pool and all(ground[q] == '.' and w.edge(q) >= FRAME + 1 and q not in w.trail and q not in w.hearts for q in pool):
                w.earth -= {(q[0] + a, q[1] + b) for q in pool for a in (-1, 0, 1) for b in (-1, 0, 1)}          # la terre s'arrête à une case de la berge
                for q in pool: ground[q] = 'o'
                w.glades |= {(q[0] + a, q[1] + b) for q in pool for a in (-1, 0, 1) for b in (-1, 0, 1) if inb((q[0] + a, q[1] + b)) and w.edge((q[0] + a, q[1] + b)) >= FRAME + 3}
        if any(v == 'o' for v in ground.values()): settle()
        w.glades = {q for q in w.glades if ground[q] == '.'}
        order = list(w.hearts); glade.shuffle(order)
        w.pois[1:1] = order          # chaque clairière se relie au réseau par son plus court couloir : un arbre de couloirs, d'une sortie à l'autre
    if S['shape']['name'] == 'corridor' and len(w.pois) == 2:          # une route en couloir serpente : un ou deux détours, de part et d'autre de la ligne droite entre ses sorties — ce seront ses poches
        a_, b_ = w.pois
        wig, upright = random.Random(sub('paths') + 2), abs(w.pois[1][1] - w.pois[0][1]) >= abs(w.pois[1][0] - w.pois[0][0])
        swing, count = wig.choice((1, -1)), (2 if max(W, H) >= 50 else 1)
        roomy = {c for c in CELLS if ground[c] == '.' and c not in w.mountain and deep(c, 3) and w.edge(c) >= FRAME + 4}
        for k in range(1, count + 1):
            t, off = k / (count + 1.0), swing * wig.uniform(0.18, 0.28) * (W if upright else H)
            wish = (int(a_[0] + (b_[0] - a_[0]) * t + (off if upright else 0)), int(a_[1] + (b_[1] - a_[1]) * t + (0 if upright else off)))
            c = nearest(wish, roomy)
            if c is not None: w.waypoints.append(c)
            swing = -swing
        w.pois[1:1] = w.waypoints
        if w.waypoints and R['pond_max']:          # une mare dans une poche, à côté du détour : de quoi s'arrêter
            p_ = w.waypoints[wig.randrange(len(w.waypoints))]
            dx_, dy_ = ((wig.choice((-5, 5)), wig.choice((-1, 0, 1))) if upright else (wig.choice((-1, 0, 1)), wig.choice((-5, 5))))
            cx_, cy_, rx_, ry_ = p_[0] + dx_, p_[1] + dy_, wig.uniform(2.0, 2.8), wig.uniform(1.8, 2.4)
            blob = {(cx_ + i, cy_ + j) for i in range(-4, 5) for j in range(-3, 4) if (i / rx_) ** 2 + (j / ry_) ** 2 <= 1.0 + (lattice(sub('relief') + 17, cx_ + i, cy_ + j) - 0.5) * 0.6}
            if all(inb(q) and ground[q] == '.' and w.edge(q) >= FRAME + 2 and q not in w.mountain and q not in w.trail and abs(q[0] - p_[0]) + abs(q[1] - p_[1]) >= 2 for q in blob):
                for q in blob: ground[q] = 'o'
                settle()
    # Une route de montagne monte (Johto 45, 46) : la vallée est coupée de terrasses, d'un mur à l'autre, de plus en plus hautes
    # vers le nord. On passe de l'une à l'autre par un escalier de pierre, face au sud, sur le trajet — jamais deux dans la même colonne.
    ups = [x for x in w.exits if x[3] == (0, 1)]
    downs = [x for x in w.exits if x[3] == (0, -1)]
    if S['terraces'] and ups and downs:
        climb = random.Random(sub('relief') + 21)
        count, lo, hi = (2 if H < 56 else 3), FRAME + 8, H - FRAME - 9
        count = min(count, max(0, hi - lo) // 9)          # neuf rangées par terrasse au moins : une petite carte n'en a qu'une, ou aucune
        column = downs[0][2][1][0] - 2
        for k in range(1, count + 1):
            b = int(hi - (hi - lo) * (k - 0.5 + climb.uniform(-0.15, 0.15)) / count)          # la rangée du bord sud de la terrasse k
            def fits(x): return all(inb(q) and ground[q] == '.' and deep(q, 1) and w.edge(q) >= FRAME + 3 for q in ((x + i, b + j) for i in range(-1, 6) for j in (-2, -1, 0, 1, 2)))
            wish = max(FRAME + 4, min(W - FRAME - 9, column + climb.choice((-1, 1)) * climb.randint(6, 12)))
            spots = sorted((x for x in range(FRAME + 3, W - FRAME - 8) if fits(x)), key=lambda x: (abs(x - wish), x))
            if not spots: continue
            column = spots[0]
            profile, x, off = {}, 0, 0
            while x < W:          # le bord ondule par crans d'une case, tous les quatre à sept pas…
                run = climb.randint(4, 7)
                for q in range(x, min(W, x + run)): profile[q] = b + off
                x += run; off = max(-2, min(2, off + climb.choice((-1, 1))))
            for q in range(column - 2, column + 7): profile[q] = b          # …et file droit sous l'escalier
            for c in CELLS:
                if c[1] <= profile[c[0]]: w.tier[c] = k
            m = w.mark([(column, b)]); w.tables.append(('terrace_stairs', dict(mark=m))); w.climbs.append((column, b))
        rim_ = {c for c in CELLS if any(w.tier.get((c[0] + i, c[1] + j), 0) != w.tier.get(c, 0) for i, j in NEIGH8 if inb((c[0] + i, c[1] + j)))}
        for pond in pieces({c for c in CELLS if ground[c] == 'o'}):          # un étang ne s'étale pas sur deux niveaux
            if pond & rim_:
                for c in pond: ground[c] = '.'
        w.rim = rim_
    for a, z in seam.get('high', []):          # les terres hautes de la carte du sud continuent ici sur huit ou neuf rangées, puis se referment en crans : ses falaises ne s'arrêtent pas net
        for x in range(a, z + 1):
            for k in range(8 + (x // 4) % 2):
                c = (x, H - 1 - k)
                if ground[c] == '.' and c not in w.trail: seam_high.add(c)
    w.levels |= seam_high
    homes_ = list(world.get('house', []))
    if S['hamlet']:
        cx_, cy_ = W // 2, H // 2 + 1
        w.plaza = {(cx_ + i, cy_ + j) for i in range(-3, 4) for j in range(-2, 3) if ground.get((cx_ + i, cy_ + j)) == '.'}          # la placette : sept cases sur cinq, dallée, au milieu
        w.marks.setdefault('%', []).extend(sorted(w.plaza))
        w.pois.append((cx_, cy_))
        if not homes_:          # sans consigne : le repère en haut de l'axe, une rangée de trois en haut, deux en bas — chacune à sa hauteur (B)
            homes_ = [dict(name='Mairie', kind='hall', near=[0.50, 0.30]), dict(name='MaisonOuest', kind='hut_left', near=[0.24, 0.36]), dict(name='MaisonEst', kind='hut_right', near=[0.76, 0.33]),
                      dict(name='MaisonSudOuest', kind='hut_right', near=[0.25, 0.72]), dict(name='MaisonSudEst', kind='hut_left', near=[0.74, 0.76])]
    for h in homes_:
        wish = (int(h.get('near', [0.5, 0.5])[0] * (W - 1)), int(h.get('near', [0.5, 0.5])[1] * (H - 1)))
        taken = [d for _, _, d in w.houses]
        high_ground = w.levels | w.mountain | w.rim
        def flat(c): return not any((c[0] + i, c[1] + j) in high_ground for i in range(-7, 8) for j in range(-8, 6))          # ni sur une butte, ni contre elle
        ok = [c for c in grass - w.mountain - w.levels if deep((c[0], c[1] - 3), 4) and deep(c, 3) and w.edge(c) >= FRAME + 4 and abs(c[0] - W // 2) + abs(c[1] - 3 - H // 2) > 4 and all(abs(c[0] - d[0]) + abs(c[1] - d[1]) >= 12 for d in taken)]
        ok = [c for c in ok if flat(c)] or ok
        if S['hamlet']:          # ni sur la placette, ni sur un couloir de sortie, ni dans l'axe qui monte du sud
            keep_ = {(q[0] + i, q[1] + j) for q in w.plaza for i in range(-2, 3) for j in range(-2, 3)} | w.lanes
            ok = [c for c in ok if not any((c[0] + i, c[1] - j) in keep_ for i in range(-5, 6) for j in range(-2, 7))]
        door = nearest(wish, ok)
        if door is None: w.notes.append('maison %s : pas de place sur l herbe' % h['name']); continue
        m = w.mark([door]); w.houses.append((h, m, door)); w.pois.append((door[0], door[1] + 1))
        w.tables.append(('house', dict(mark=m, **{k: h[k] for k in ('name', 'kind', 'scene', 'door') if k in h})))
    house_area = {(d[0] + i, d[1] - j) for _, _, d in w.houses for i in range(-5, 6) for j in range(0, 7)}
    if S['farm']:
        # Les champs : on en pose jusqu'à six, à cinq cases au moins les uns des autres — la place d'un chemin et de ses bords.
        # Chacun : une clôture sur son pourtour, de la terre dedans, du blé par bandes de deux ou trois rangées séparées d'allées
        # d'une case ; chaque bande a une trouée, d'un côté puis de l'autre : on serpente. Le bout d'une allée, passé la trouée,
        # est un cul-de-sac — un champ sur deux y garde un objet.
        farm = random.Random(sub('paths') + 41)
        def blocked(q): return not inb(q) or ground[q] != '.' or q in w.lanes or q in house_area or w.edge(q) < FRAME - 1 or any(abs(q[0] - p[0]) <= 3 and abs(q[1] - p[1]) <= 3 for p in w.pois)
        # Une grille bousculée : des cases d'une vingtaine sur quinze, un champ par case — parfois un grand sur deux cases voisines.
        pad_ = FRAME + 1
        cols_, rows_ = max(1, (W - 2 * pad_) // 19), max(1, (H - 2 * pad_) // 16)
        cw_, ch_ = (W - 2 * pad_) / float(cols_), (H - 2 * pad_) / float(rows_)
        cells_left = [(i, j) for j in range(rows_) for i in range(cols_)]
        farm.shuffle(cells_left)
        used_ = set()
        for (i, j) in cells_left:
            if (i, j) in used_: continue
            span = 2 if (i + 1, j) not in used_ and i + 1 < cols_ and farm.random() < 0.3 else 1
            ax0, ay0, ax1, ay1 = int(pad_ + i * cw_) + 2, int(pad_ + j * ch_) + 2, int(pad_ + (i + span) * cw_) - 4, int(pad_ + (j + 1) * ch_) - 4          # la place du champ dans sa case : cinq cases de marge en tout
            placed_ = False
            for _ in range(40):
                bands, room_ = [], ay1 - ay0 + 1 - farm.randint(0, 2)
                while 3 + sum(bands) + len(bands) + 4 <= room_ and len(bands) < 4: bands.append(farm.choice((2, 3, 3, 4)))          # des bandes de trois rangées surtout : les allées font un quart du champ          # autant de bandes que la case en porte
                if not bands: break
                tall = 3 + sum(bands) + len(bands)          # (une allée en haut, une sous chaque bande, la clôture autour)
                wide = farm.randint(max(9, ax1 - ax0 - 6), max(9, ax1 - ax0 + 1))
                if tall > ay1 - ay0 + 1 or wide > ax1 - ax0 + 1: continue
                x0, y0 = farm.randint(ax0, ax1 - wide + 1), farm.randint(ay0, ay1 - tall + 1)
                x1, y1 = x0 + wide - 1, y0 + tall - 1
                if any(blocked((x, y)) for x in range(x0 - 2, x1 + 3) for y in range(y0 - 2, y1 + 3)) or min(w.edge((x0, y0)), w.edge((x1, y1))) < FRAME + 1: continue
                placed_ = True; break
            if not placed_: continue
            used_.update((i + k, j) for k in range(span))
            inner = [(x, y) for x in range(x0 + 1, x1) for y in range(y0 + 1, y1)]
            w.earth.update(inner)
            y, side, gaps, alleys = y0 + 2, farm.choice((0, 1)), [], [y0 + 1]
            for band in bands:
                gap = farm.randint(x0 + 3, x0 + 4) if side else farm.randint(x1 - 4, x1 - 3)          # la trouée : à trois ou quatre cases d'un bord, d'un côté puis de l'autre
                w.wheat.update((x, y + j) for x in range(x0 + 1, x1) for j in range(band) if x != gap)
                gaps.append(gap); y += band + 1; alleys.append(y - 1); side = 1 - side
            south = (y0 + y1) / 2.0 < H / 2.0          # le portillon regarde le milieu de la carte : c'est par là que passent les chemins
            gx = max(x0 + 1, min(x1 - 2, (gaps[-1] if south else gaps[0]) + farm.choice((-4, 3))))
            gate = [(gx, y1 if south else y0), (gx + 1, y1 if south else y0)]
            ring_ = [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1) if (x in (x0, x1) or y in (y0, y1)) and (x, y) not in gate]
            w.marks.setdefault('f', []).extend(ring_)
            w.pois.append((gx, y1 + 2 if south else y0 - 2))
            if len(w.fields) % 2 == 0:          # l'objet : au fond de l'allée la plus loin du portillon, du côté opposé à sa trouée
                row, g_ = (alleys[0], gaps[0]) if south else (alleys[-1], gaps[-1])
                spot = (x0 + 1, row) if g_ - x0 > x1 - g_ else (x1 - 1, row)
                item = ITEMS[(len(w.fields) // 2 + 3) % len(ITEMS)]
                w.tables.append(('item', dict(mark=w.mark([spot]), name='ItemChamp%d' % (len(w.fields) // 2 + 1), item=item[0], text='Vous trouvez %s !|Vous rangez %s dans la poche %s.' % (item[1], item[2], item[3]), exact=True)))
            w.fields.append((x0, y0, x1, y1))
            cells_ = {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
            w.spots |= cells_
            house_area |= {(q[0] + i, q[1] + j) for q in cells_ for i in (-1, 0, 1) for j in (-1, 0, 1)}          # ni chemin, ni arbre, ni fleur dans un champ ni contre sa clôture
        if len(w.fields) < 2: w.notes.append('seulement %d champ : la carte est trop petite, ou trop encombrée' % len(w.fields))
    if (S['hamlet'] or S['farm']) and R['pond_max']:          # deux étangs de vingt-cinq à trente-cinq cases, au contact du bâti (O) : à côté d'une maison, loin de sa porte
        pool_ = random.Random(sub('relief') + 51)
        def blob(cx, cy, rx, ry, salt): return {(cx + i, cy + j) for i in range(-6, 7) for j in range(-5, 6) if (i / rx) ** 2 + (j / ry) ** 2 <= 1.0 + (lattice(sub('relief') + salt, cx + i, cy + j) - 0.5) * 0.6}
        walls_ = set()          # l'emprise des maisons : leurs murs et leur toit
        for h, _, d in w.houses:
            model = builder.THEME['buildings'].get(h.get('kind', 'hut_left'), dict(door=1, size=[5, 6]))
            walls_ |= {(d[0] - model['door'] + i, d[1] - j) for i in range(model['size'][0]) for j in range(model['size'][1])}
        walls_ |= {(x, y) for fx0, fy0, fx1, fy1 in w.fields for x in range(fx0, fx1 + 1) for y in range(fy0, fy1 + 1)}          # et celle des champs
        shut_ = ({(p[0] + i, p[1] + j) for p in w.pois for i in range(-3, 4) for j in range(-3, 4)} if S['farm'] else set()) | {(q[0] + i, q[1] + j) for q in walls_ for i in (-1, 0, 1) for j in (-1, 0, 1)} | w.lanes | {(q[0] + i, q[1] + j) for q in w.plaza for i in range(-2, 3) for j in range(-2, 3)} \
            | {(d[0] + i, d[1] + j) for _, _, d in w.houses for i in range(-2, 3) for j in range(1, 5)}
        near_walls = {(q[0] + i, q[1] + j) for q in walls_ for i in range(-2, 3) for j in range(-2, 3)}
        spots_ = sorted(c for c in CELLS if ground[c] == '.' and w.edge(c) >= FRAME + 5)
        pool_.shuffle(spots_)
        made, ponds_ = 0, []
        for c in spots_:
            if made >= 2: break
            if any(abs(c[0] - o[0]) + abs(c[1] - o[1]) < 14 for o in ponds_): continue
            pool = blob(c[0], c[1], pool_.uniform(2.9, 3.6), pool_.uniform(2.2, 2.7), 53 + made)
            if 20 <= len(pool) <= 40 and pool & near_walls and all(inb(q) and ground[q] == '.' and q not in shut_ and w.edge(q) >= FRAME + 2 for q in pool):
                for q in pool: ground[q] = 'o'
                made += 1; ponds_.append(c)
        if made: settle()
    if S['hamlet']:
        # Les massifs clôturés (Q, R) : cinq cases sur quatre contre le flanc d'une maison, trois grandes fleurs en rang dedans.
        beds = 0
        for h, _, d in w.houses:
            if beds >= 2: break
            model = builder.THEME['buildings'].get(h.get('kind', 'hut_left'))
            if not model or model['size'][0] > 6: continue
            x0_, x1_ = d[0] - model['door'], d[0] - model['door'] + model['size'][0] - 1
            for gx0 in (x1_ + 1, x0_ - 5):
                bed = [(gx0 + i, d[1] - j) for i in range(5) for j in range(4)]
                if all(inb(q) and ground[q] == '.' and q not in w.lanes and q not in w.plaza and w.edge(q) >= FRAME + 2 and q not in w.spots for q in bed):
                    w.marks.setdefault('f', []).extend(bed); w.spots.update(bed)
                    for i in (1, 2, 3): w.props.append(('bloom%d' % ((beds + i) % 4), gx0 + i, d[1] - 1))
                    house_area |= {(q[0] + i, q[1] + j) for q in bed for i in (-1, 0, 1) for j in (-1, 0, 1)}
                    beds += 1
                    break
        # Les lampadaires (K) : aux quatre coins de la placette, et de part et d'autre de l'entrée du sud — sur l'herbe, au bord du chemin.
        lamps = [(min(q[0] for q in w.plaza) - 1, min(q[1] for q in w.plaza) - 1), (max(q[0] for q in w.plaza) + 1, min(q[1] for q in w.plaza) - 1),
                 (min(q[0] for q in w.plaza) - 1, max(q[1] for q in w.plaza) + 1), (max(q[0] for q in w.plaza) + 1, max(q[1] for q in w.plaza) + 1)] if w.plaza else []
        for e, m_, span, inward in w.exits:
            if inward == (0, -1): lamps += [(span[1][0] - 3, span[1][1] - FRAME - 2), (span[1][0] + 3, span[1][1] - FRAME - 2)]
        for n_, c in enumerate(lamps):
            if inb(c) and ground[c] == '.' and c not in house_area:
                w.tables.append(('lamp', dict(mark=w.mark([c]), name='Lamp%d' % (n_ + 1)))); w.spots.add(c)

    # Du relief (D) : deux ou trois buttes — des terrasses d'un cran, que la forêt couvrira.
    hill = random.Random(sub('relief') + 2)
    def stout(butte):
        """Une butte est trapue : on n'en garde que ce qui tient dans des blocs de cinq cases sur quatre — de quoi porter un arbre
        et sa falaise. Ni bras d'une case, ni pointe : une terrasse nue où l'on ne monte pas ne ressemble à rien."""
        blocks = [[(c[0] + i, c[1] + j) for i in range(5) for j in range(4)] for c in butte]
        kept = {q for block in blocks if all(q in butte for q in block) for q in block}
        return max(pieces(kept), key=len) if kept else set()
    busy = w.lanes | {(c[0] + i, c[1] + j) for c in w.rim for i in (-3, -2, -1, 0, 1, 2, 3) for j in (-3, -2, -1, 0, 1, 2, 3)} | {(d[0] + i, d[1] + j) for _, _, d in w.houses for i in range(-8, 9) for j in range(-9, 7)} | {(p[0] + i, p[1] + j) for p in w.pois for i in range(-3, 4) for j in range(-3, 4)}          # ni sur une sortie, ni contre une maison
    tops = sorted((c for c in grass - w.mountain - busy if deep(c, 5) and w.edge(c) >= FRAME + 5), key=lambda c: -height[c])
    for top in tops:          # deux ou trois, sur les points hauts, loin les unes des autres ; chacune d'une vingtaine à une quarantaine de cases
        if R['terrace'] > 1.0 or len(pieces(w.levels - seam_high)) + len(pieces(w.mountain)) >= 3: break
        if any(abs(top[0] - c[0]) + abs(top[1] - c[1]) < 14 for c in w.levels) or any(abs(top[0] - c[0]) + abs(top[1] - c[1]) < 8 for c in w.mountain): continue
        size, butte, front = hill.randint(30, 60), {top}, [top]
        while len(butte) < size and front:
            c = front.pop(hill.randrange(len(front)))
            for i, j in NEIGH4:
                n = (c[0] + i, c[1] + j)
                if n not in butte and n in grass and n not in busy and n not in w.mountain and deep(n, 3) and w.edge(n) >= FRAME + 3 and len(butte) < size: butte.add(n); front.append(n)
        butte = stout(butte)
        if len(butte) >= 24: w.levels |= butte
    for top in sorted((c for c in grass - w.mountain - busy if deep(c, 3) and w.edge(c) >= FRAME + 3), key=lambda c: -height[c]):          # la place manque (un anneau, un couloir) : une butte plus petite, plutôt qu'une carte plate
        if R['terrace'] > 1.0 or len(pieces(w.levels - seam_high)) + len(pieces(w.mountain)) >= 2: break
        if any(abs(top[0] - c[0]) + abs(top[1] - c[1]) < 10 for c in w.levels | w.mountain): continue
        size, butte, front = hill.randint(18, 30), {top}, [top]
        while len(butte) < size and front:
            c = front.pop(hill.randrange(len(front)))
            for i, j in NEIGH4:
                n = (c[0] + i, c[1] + j)
                if n not in butte and n in grass and n not in busy and n not in w.mountain and deep(n, 2) and w.edge(n) >= FRAME + 2 and len(butte) < size: butte.add(n); front.append(n)
        butte = stout(butte)
        if len(butte) >= 20: w.levels |= butte

    if S['wall']:          # une route de montagne : la ceinture est de roche, au bord intérieur en crans ; elle s'ouvre aux sorties
        for c in CELLS:
            d = w.edge(c) - fractal(sub('relief') + 5, c[0], c[1], 4.0, 2) * 5.0 + 1.0
            if d < FRAME - 1 and ground[c] == '.' and c not in w.trail and c not in house_area and c not in w.levels: w.mountain.add(c)          # (la roche serre le couloir de sortie : pas de pelouse perdue entre eux)
    if not w.pois: w.pois.append(nearest((W // 2, H // 2), {c for c in grass - w.levels - w.mountain if deep(c, 2)} or grass))          # une carte sans sortie : on part du milieu, et rien ne s'y plante
    w.start = w.pois[0]

    # ============================================================ 3. les chemins, et de quoi tout relier : escaliers et ponts
    half = G['path_width'] // 2
    loose = [False]          # en dernier recours, un chemin peut longer la lisière, de l'autre côté de l'eau
    first = w.probe()
    firm = [first['PLATEAU'] - first['SOLID']]          # là où l'on marche vraiment sur un plateau, tel que le constructeur le voit : ni langue de terre trop mince pour sa falaise, ni flanc de falaise (le bord du haut, lui, se foule)
    def walkable(c): return ground[c] == '.' and c in firm[0] and c not in w.mountain and c not in w.levels and c not in house_area and w.edge(c) >= (5 if loose[0] else FRAME)
    def cost(c):
        if c in w.marks.get('=', ()): return 1.0          # un pont déjà posé se traverse : d'île en île, le chemin continue de l'autre côté
        if not walkable(c) and c not in w.trail: return None
        return 1.0 + (0.0 if c in w.trail else 0.6) + (6.0 if not deep(c, half + 1) else 0.0) + (5.0 if any((c[0] + i, c[1] + j) in w.levels for i in (-2, 0, 2) for j in (-2, 0, 2)) else 0.0) + lattice(sub('paths'), *c) * 1.5          # un peu de hasard : un chemin qui serpente, pas une règle
    def route(a, goals):
        """Le trajet le moins cher de `a` à la première case de `goals` atteinte, ou None."""
        best, queue, came = {a: 0.0}, [(0.0, a)], {}
        while queue:
            d, c = heapq.heappop(queue)
            if c in goals:
                path = [c]
                while c != a: c = came[c]; path.append(c)
                return path
            if d > best.get(c, 1e9): continue
            for i, j in NEIGH4:
                n = (c[0] + i, c[1] + j)
                if not inb(n): continue
                step = cost(n)
                if step is None: continue
                if d + step < best.get(n, 1e9): best[n] = d + step; came[n] = c; heapq.heappush(queue, (d + step, n))
        return None
    def carve(path):
        w.routes.append(list(path))
        for c in path: w.trail |= {(c[0] + i, c[1] + j) for i in range(-half, half + 1) for j in range(-half, half + 1) if inb((c[0] + i, c[1] + j)) and walkable((c[0] + i, c[1] + j))}
    def pad(c): return {q for q in ((c[0] + i, c[1] + j) for i in (-1, 0, 1) for j in (-1, 0, 1)) if inb(q) and walkable(q)}
    def network():
        """Le réseau : ce qui, de la piste, tient au départ. Le couloir d'une autre sortie n'en est pas tant qu'aucun chemin ne l'y mène."""
        seen, todo = {w.start}, [w.start]
        while todo:
            c = todo.pop()
            for i, j in NEIGH4:
                n = (c[0] + i, c[1] + j)
                if n in w.trail and n not in seen: seen.add(n); todo.append(n)
        return seen
    def join(point, net=None):
        """Relie `point` au réseau de chemins, s'il y a de la terre ferme entre eux. Vrai si c'est fait."""
        net = net or network()
        if point in net: return True
        path = route(point, net)
        if path: carve(path)
        return bool(path)
    def footing(built):
        """Ce qu'on atteindra une fois la lisière plantée. Le constructeur, lui, voit encore la ceinture comme une pelouse
        ouverte : par elle, deux terres que l'eau sépare auraient l'air de se toucher."""
        free = {c for c in built['REACH'] if w.edge(c) >= FRAME or c in w.trail}
        seen, todo = set(), [c for c in [w.start] if c in free]
        seen.update(todo)
        while todo:
            c = todo.pop()
            for i, j in NEIGH4:
                n = (c[0] + i, c[1] + j)
                if n in free and n not in seen: seen.add(n); todo.append(n)
        return seen
    waiting = [p for p in w.pois[1:] if not join(p)]
    if S['deep'] and len(w.hearts) >= 4:          # et deux ou trois couloirs de plus, en équerre, pour qu'on tourne en rond : un labyrinthe a des boucles
        loop = random.Random(sub('paths') + 33)
        pairs = [(a_, b_) for k, a_ in enumerate(w.hearts) for b_ in w.hearts[k + 1:] if 10 <= abs(a_[0] - b_[0]) + abs(a_[1] - b_[1]) <= 24]
        loop.shuffle(pairs)
        for a_, b_ in pairs[:2 + len(w.hearts) // 5]:
            corner = (b_[0], a_[1]) if loop.random() < 0.5 else (a_[0], b_[1])
            def leg(p_, q_): return [(x, p_[1]) for x in range(min(p_[0], q_[0]), max(p_[0], q_[0]) + 1)] + [(p_[0] if p_[0] == q_[0] else q_[0], y) for y in range(min(p_[1], q_[1]), max(p_[1], q_[1]) + 1)]
            carve(leg(a_, corner) + leg(corner, b_))
    works = {(x + i, r + j) for x, r in w.climbs for i in range(-1, 6) for j in (-2, -1, 0, 1, 2)}          # les cases des escaliers et des ponts, et leurs abords
    causeway = []
    redo = set()          # les points que le tracé disait reliés et que la carte assemblée ne relie pas
    for _ in range(10 + W * H // 1500):          # tant qu'un grand morceau de terre reste coupé du départ : un pont, ou un escalier vers sa plage
        built = w.probe()
        firm[0] = built['PLATEAU'] - built['SOLID']
        reach, inside, beach = footing(built), built['INSIDE'], built['BEACH'] - built['RING']
        for p in w.pois[1:]:          # ce qu'on croyait relié et que le constructeur, lui, n'atteint pas (une langue de terre devenue trop mince pour qu'on y marche) : à relier de nouveau
            if p not in reach and p not in waiting and p not in redo: waiting.append(p); redo.add(p)
        for p in list(waiting):          # ce qui attendait se relie peut-être, depuis le dernier ouvrage
            if p not in redo and join(p): waiting.remove(p)
            elif p in redo and p in reach: waiting.remove(p)
        lands = [p for p in pieces({c for c in inside if walkable(c)}) if len(p) >= 50 and not p & reach]
        shores = [p for p in pieces(beach) if len(p) >= 24 and not p & reach]
        if not lands and not shores and not waiting: break
        done = False
        # --- un pont : trois cases de large, tout droit, du dessus d'un plateau à l'autre, au plus court (O)
        target = {c for p in lands for c in p}
        firmland = inside - built['POND']          # un pont enjambe un étang comme un bras de mer
        best = None
        for span in (G['bridge_max'],):          # (pas de pont plus long : passé cette portée, une langue de terre vaut mieux qu'un tablier de trente cases)
            if best: break
            for vertical in (True, False):
                if not target: break
                for a in range(FRAME, (W if vertical else H) - FRAME - 2):
                    for first in range(4, (H if vertical else W) - 4):
                        def at(k, i): return (a + i, k) if vertical else (k, a + i)
                        if not all(at(first, i) in reach and at(first, i) in firmland for i in range(3)): continue
                        for way in (1, -1):
                            k, length = first + way, 0
                            while 0 <= k < (H if vertical else W) and length <= span and not any(at(k, i) in firmland for i in range(3)) and not any(at(k, i) in house_area for i in range(3)): k += way; length += 1
                            if 3 <= length <= span and 0 <= k < (H if vertical else W) and all(at(k, i) in target for i in range(3)) and (best is None or length < best[0]):
                                best = (length, [at(q, i) for q in range(min(first, k) + 1, max(first, k)) for i in range(3)], at(first, 1), at(k, 1))
        if best:
            length, cells, near_, far_ = best
            w.marks.setdefault('=', []).extend(cells); works |= {(c[0] + i, c[1] + j) for c in cells for i in range(-2, 3) for j in range(-2, 3)}
            w.trail |= pad(near_) | pad(far_)
            join(near_); w.far.append(far_); done = True
        # --- un escalier : sur un bord du bas tout droit, cinq cases, de la plage au plateau (D)
        if not done and shores:
            ring, rock = built['ring_shape'], built['rock_shape']
            for (x, r) in sorted(ring, key=lambda c: (abs(c[0] - W // 2) + abs(c[1] - H // 2), c)):
                if not all(ring.get((x + i, r)) == '2' for i in range(5)) or not all(rock.get((x + i, r + 1)) == '2' for i in (1, 2, 3)): continue
                if not all((x + i, r + 2) in beach for i in (1, 2, 3)) or w.edge((x, r)) < FRAME + 1: continue
                top, foot = (x + 2, r - 1), (x + 2, r + 2)
                if (top in reach) == (foot in reach) or not (top in inside and walkable(top)): continue
                if any(abs(x - sx) < 8 and abs(r - sr) < 6 for sx, sr in w.stairs): continue
                m = w.mark([(x, r)]); w.tables.append(('stairs', dict(mark=m))); w.stairs.append((x, r))
                works |= {(x + i, r + j) for i in range(-1, 6) for j in range(-3, 5)}
                w.trail |= {q for q in ((top[0] + i, top[1] - j) for i in (-1, 0, 1) for j in (0, 1, 2)) if inb(q) and walkable(q)}
                if top in reach: join(top)
                else: w.far.append(top)
                done = True; break
        if not done and shores:          # pas de bord droit ? On en taille un : cinq cases de plateau au cordeau, la plage dessous
            tries = 0
            for (bx, by) in sorted((c for p in shores for c in p), key=lambda c: (abs(c[0] - W // 2) + abs(c[1] - H // 2), c)):
                if tries >= 8: break          # (chaque essai fait relire toute la carte : on n'insiste pas)
                x, r = bx - 2, by - 2          # la plage commencera en r + 2
                cols = list(range(x - 1, x + 6))
                block = [(cx, r - k) for cx in cols for k in range(0, 4)]
                sand = [(cx, r + k) for cx in cols for k in range(1, 5)]
                if not all(inb(q) and w.edge(q) >= FRAME + 1 for q in block + sand): continue
                if any(ground[q] == 'o' for q in block + sand) or (x + 2, r - 3) not in reach or any(q in w.levels or q in w.mountain or q in house_area or q in works for q in block + sand) or any(q in w.trail for q in sand): continue          # (jamais de sable sous un chemin déjà tracé)
                if sum(ground[q] == '.' for q in block) < len(block) * 0.7 or sum(ground[q] == ':' for q in sand) < len(sand) * 0.5: continue
                if any(abs(x - sx) < 10 and abs(r - sr) < 8 for sx, sr in w.stairs): continue
                before = {q: ground[q] for q in block + sand}
                tries += 1
                for q in block: ground[q] = '.'
                for q in sand: ground[q] = ':'
                again = w.probe()
                ring2, rock2, beach2 = again['ring_shape'], again['rock_shape'], again['BEACH'] - again['RING']
                if all(ring2.get((x + i, r)) == '2' for i in range(5)) and all(rock2.get((x + i, r + 1)) == '2' for i in (1, 2, 3)) and all((x + i, r + 2) in beach2 for i in (1, 2, 3)) and (x + 2, r - 1) in again['REACH']:
                    m = w.mark([(x, r)]); w.tables.append(('stairs', dict(mark=m))); w.stairs.append((x, r))
                    works |= {(x + i, r + j) for i in range(-1, 6) for j in range(-3, 5)}
                    w.trail |= {q for q in (((x + 2) + i, (r - 1) - j) for i in (-1, 0, 1) for j in (0, 1, 2)) if inb(q) and walkable(q)}
                    join((x + 2, r - 1)); done = True; break
                ground.update(before)          # le bord n'est pas sorti droit : on remet tout comme avant
        # --- un escalier de côté : la plage est à l'ouest ou à l'est du plateau (ou au nord : on la rejoint par un flanc). Trois marches sur un flanc droit de cinq cases
        def flank_fits(b_, side, gx, y0):
            s, flank = (-1, '4') if side == 'W' else (1, '6')
            sand_ = b_['BEACH'] - b_['RING']
            return all(b_['ring_shape'].get((gx, y0 + j)) == flank and b_['rock_shape'].get((gx + s, y0 + j)) == flank for j in range(-1, 4)) and all((gx + 2 * s, y0 + j) in sand_ for j in range(-1, 4))
        def side_stairs(side, gx, y0, top):
            m = w.mark([(gx, y0)]); w.tables.append(('side_stairs', dict(mark=m, side=side))); w.stairs.append((gx, y0))
            works.update((gx + i, y0 + j) for i in range(-4, 5) for j in range(-3, 6))
            w.trail |= {q for q in ((top[0] + i, top[1] + j) for i in (-1, 0, 1) for j in (-1, 0, 1)) if inb(q) and walkable(q) and q[0] != gx}
        if not done and shores:
            for side, s in (('W', -1), ('E', 1)):
                for (gx, y0) in sorted(built['ring_shape'], key=lambda c: (abs(c[0] - W // 2) + abs(c[1] - H // 2), c)):
                    if done: break
                    top, foot = (gx - s, y0 + 1), (gx + 2 * s, y0 + 1)
                    if not flank_fits(built, side, gx, y0) or w.edge((gx, y0)) < FRAME + 1 or (top in reach) == (foot in reach) or not (top in inside and walkable(top)): continue
                    if any(abs(gx - sx) < 8 and abs(y0 - sr) < 8 for sx, sr in w.stairs) or any(q in works for q in (top, foot)): continue
                    side_stairs(side, gx, y0, top)
                    if top in reach: join(top)
                    else: w.far.append(top)
                    done = True
        if not done and shores:          # pas de flanc droit ? On en taille un : quatre cases de plateau au cordeau sur sept rangées, le sable à côté
            tries = 0
            for (bx, by) in sorted((c for p in shores for c in p), key=lambda c: (abs(c[0] - W // 2) + abs(c[1] - H // 2), c)):
                if done or tries >= 8: break
                for side, s in (('W', -1), ('E', 1)):
                    gx, y0 = bx - 2 * s, by - 1
                    block = [(gx - s * k, y0 + j) for k in range(0, 4) for j in range(-2, 5)]
                    sand = [(gx + s * k, y0 + j) for k in range(1, 5) for j in range(-2, 5)]
                    top = (gx - s, y0 + 1)
                    if not all(inb(q) and w.edge(q) >= FRAME + 1 and w.offshore(q) >= 7 for q in block + sand): continue
                    if any(ground[q] == 'o' for q in block + sand) or (gx - 3 * s, y0 + 1) not in reach or any(q in w.levels or q in w.mountain or q in house_area or q in works for q in block + sand) or any(q in w.trail for q in sand): continue
                    if sum(ground[q] == '.' for q in block) < len(block) * 0.7 or sum(ground[q] == ':' for q in sand) < len(sand) * 0.5: continue
                    if any(abs(gx - sx) < 10 and abs(y0 - sr) < 8 for sx, sr in w.stairs): continue
                    before = {q: ground[q] for q in block + sand}
                    tries += 1
                    for q in block: ground[q] = '.'
                    for q in sand: ground[q] = ':'
                    again = w.probe()
                    if flank_fits(again, side, gx, y0) and top in again['REACH']:
                        firm[0] = again['PLATEAU'] - again['SOLID']
                        side_stairs(side, gx, y0, top); join(top); done = True; break
                    ground.update(before)          # le flanc n'est pas sorti droit : on remet tout comme avant
        if not done and shores and beach & reach:          # deux plages qu'un cap sépare, l'une déjà atteinte : on rogne le cap, le sable passe — trois cases de large (J)
            landed = beach & reach
            def shut(q): return not inb(q) or ground[q] == 'o' or w.edge(q) < FRAME + 1 or w.offshore(q) < 7 or q in works or q in w.levels or q in w.mountain or q in house_area or q in w.trail
            for piece in sorted(shores, key=len, reverse=True)[:3]:
                came, layer, hit = {c: None for c in piece}, list(piece), None
                for _ in range(12):
                    nxt = []
                    for c in layer:
                        for i, j in NEIGH4:
                            n = (c[0] + i, c[1] + j)
                            if n in came or shut(n): continue
                            came[n] = c; nxt.append(n)
                            if n in landed: hit = n
                        if hit: break
                    if hit or not nxt: break
                    layer = nxt
                if not hit: continue
                path, c = [], hit
                while c is not None: path.append(c); c = came[c]
                strip = {(c[0] + i, c[1] + j) for c in path for i in (-1, 0, 1) for j in (-1, 0, 1)}
                strip = {q for q in strip if not shut(q) and ground[q] != ':'}
                before = {q: ground[q] for q in strip}
                for q in strip: ground[q] = ':'
                again = w.probe()
                if piece & again['REACH']: firm[0] = again['PLATEAU'] - again['SOLID']; works.update(strip); done = True; break
                ground.update(before)
        if not done and shores:          # la plage est au nord du plateau, et aucun escalier ne monte face au nord : on creuse une anse dans la terre, on descend par son flanc
            tries = 0
            for (bx, by) in sorted((c for p in shores for c in p), key=lambda c: (abs(c[0] - W // 2) + abs(c[1] - H // 2), c)):
                if done or tries >= 8: break
                yb = by
                while ground.get((bx, yb + 1)) == ':' and yb - by < 3: yb += 1
                if ground.get((bx, yb + 1)) != '.': continue
                cove = [(bx + i, yb + j) for i in range(-2, 3) for j in range(1, 10)]          # cinq cases de large — une paroi de chaque côté, trois de sable —, neuf de profondeur
                banks = [(bx + i, yb + j) for i in (-6, -5, -4, -3, 3, 4, 5, 6) for j in range(1, 12)] + [(bx + i, yb + j) for i in range(-2, 3) for j in (10, 11)]
                if not all(inb(q) and w.edge(q) >= FRAME + 1 and ground[q] == '.' and q not in w.levels and q not in w.mountain and q not in house_area and q not in works and q not in w.trail for q in cove + banks): continue
                y0 = yb + 4
                if any(abs(bx - sx) < 12 and abs(y0 - sr) < 10 for sx, sr in w.stairs): continue
                before = {q: ground[q] for q in cove}
                tries += 1
                for q in cove: ground[q] = ':'
                again = w.probe()
                for side, gx in (('E', bx - 3), ('W', bx + 3)):
                    top = (gx - 1, y0 + 1) if side == 'E' else (gx + 1, y0 + 1)
                    if flank_fits(again, side, gx, y0) and top in again['REACH'] and top in reach:
                        firm[0] = again['PLATEAU'] - again['SOLID']
                        side_stairs(side, gx, y0, top); works.update(cove); join(top); done = True; break
                if not done: ground.update(before)
        for far_ in w.far:          # de l'autre côté d'un pont, en haut d'un escalier : le chemin continue jusqu'à ce qui attendait
            for p in list(waiting):
                path = route(p, {far_} | pad(far_))
                if path: carve(path); waiting.remove(p)
        if not done and (lands or waiting):          # un étang barre le passage : on ne jette pas un pont sur une mare, on la comble
            for pond in pieces({c for c in CELLS if ground[c] == 'o'}):
                rim = {(c[0] + i, c[1] + j) for c in pond for i in range(-2, 3) for j in range(-2, 3)} - pond
                if rim & reach and any(inb(q) and walkable(q) and q not in reach for q in rim):
                    for c in pond: ground[c] = '.'
                    done = True
        if not done and waiting:          # ni pont ni escalier : le chemin fait le tour par la lisière, plutôt qu'une sortie où l'on n'arrive pas
            loose[0] = True
            for p in list(waiting):
                if p in redo: continue
                path = route(p, network())
                if path:
                    carve(path); waiting.remove(p); done = True
                    w.notes.append('le chemin vers %s longe la lisière, faute de pont ou d escalier : la ceinture de forêt y est plus mince' % (p,))
        if not done and waiting and w.tier:          # les terrasses coupent la route : on y renonce, la carte reste à plat
            w.tier.clear(); w.climbs.clear(); w.rim = set()
            w.tables = [t for t in w.tables if t[0] != 'terrace_stairs']
            w.notes.append('les terrasses ont été retirées : leur escalier ne reliait pas les deux sorties')
            done = True
        if not done and waiting:          # rien n'y fait : on jette une langue de terre, cinq cases de large, au plus court en préférant la terre — une carte se joue
            p = waiting[0]
            net = (reach & firm[0]) if p in redo else network()          # (pour un point que le tracé croyait relié : jusqu'à ce qu'on atteint vraiment)
            keep = {(c[0] + i, c[1] + j) for c in works for i in (-2, -1, 0, 1, 2) for j in (-2, -1, 0, 1, 2)}          # à l'écart des escaliers et des ponts déjà posés : on ne leur retire ni leur plage ni leur eau
            best, queue, came, hit = {p: 0.0}, [(0.0, p)], {}, None
            while queue:
                d, c = heapq.heappop(queue)
                if c in net: hit = c; break
                if d > best.get(c, 1e9): continue
                for i, j in NEIGH4:
                    n = (c[0] + i, c[1] + j)
                    if not inb(n) or w.edge(n) < 4 or w.offshore(n) < 8 or n in house_area or (n in keep and n not in net and p not in redo): continue          # (pour un point mal relié, on repasse où il faut : c'est souvent au ras d'un escalier que la terre s'est amincie)
                    step = 1.0 if ground[n] == '.' and n not in w.mountain and n not in w.levels else 8.0
                    if d + step < best.get(n, 1e9): best[n] = d + step; came[n] = c; heapq.heappush(queue, (d + step, n))
            if hit is not None and len(causeway) < 2:
                causeway.append(p)
                c = hit
                while True:
                    for i in range(-2, 3):
                        for j in range(-2, 3):
                            q = (c[0] + i, c[1] + j)
                            if inb(q) and w.edge(q) >= 2 and q not in house_area and q not in works: ground[q] = '.'; w.mountain.discard(q); w.levels.discard(q)
                    if c == p: break
                    c = came[c]
                w.notes.append('une langue de terre a été jetée jusqu à %s : ni pont, ni escalier, ni détour ne le reliait' % (p,))
                done = True
        if not done: break
    def ripple(seed_):
        """Des bords de chemin ondulés (N) : un décrochement de deux cases dans tout bord droit de plus de sept."""
        bump = random.Random(sub('paths') + seed_)
        def near_poi(q): return any(abs(q[0] - p[0]) <= 2 and abs(q[1] - p[1]) <= 2 for p in w.pois + w.far)
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):          # le côté où déborder
            ax = (1, 0) if dx == 0 else (0, 1)
            side = {c for c in w.trail if (c[0] + dx, c[1] + dy) not in w.trail and c not in w.lanes and c not in works}
            for c in sorted(side):
                if (c[0] - ax[0], c[1] - ax[1]) in side: continue
                run, q = [], c
                while q in side: run.append(q); q = (q[0] + ax[0], q[1] + ax[1])
                k = bump.randint(2, 4)
                while len(run) > 7 and k < len(run) - 2:
                    out = [(q[0] + dx, q[1] + dy) for q in run[k:k + 2]]
                    if all(inb(q) and walkable(q) and deep(q, 1) and q not in works for q in out): w.trail |= set(out)
                    elif all((q[0] - dx * n, q[1] - dy * n) in w.trail for q in run[k:k + 2] for n in (1, 2)) and not any(near_poi(q) for q in run[k:k + 2]): w.trail -= set(run[k:k + 2])          # pas la place de déborder (une falaise, une eau) : le bord rentre, le chemin garde deux cases
                    k += bump.randint(4, 6)
    ripple(4)
    for p in waiting: w.notes.append('le point %s reste coupé du départ : ni pont ni escalier possible jusqu à lui' % (p,))
    w.trail = {c for c in w.trail if ground[c] == '.' and c not in w.mountain and c not in house_area}

    # ============================================================ 4. la végétation, sur la géographie que le constructeur en déduit
    built = w.probe()
    inside, ring, beach = built['INSIDE'] - built['POND'], built['RING'], built['BEACH'] - built['RING']          # (un étang est sur le plateau, mais rien n'y pousse)
    def near(c, cells, n): return any((c[0] + i, c[1] + j) in cells for i in range(-n, n + 1) for j in range(-n, n + 1))
    way = set(w.trail)          # par où l'on passe, bord de plateau compris : rien ne s'y plante
    butte = {c for c in built['high'] if c in w.levels}          # les terrasses où l'on ne monte pas ; les autres (`w.tier`) se foulent, et il y pousse de tout
    brink = {c for c, k in built['high_shape'].items() if k != '5'}          # toute petite falaise, de butte ou de terrasse : rien n'y pousse, rien ne la chevauche
    level_ = built['tier']
    def same_level(cells): return len({level_.get(c, 0) for c in cells if inb(c)}) == 1 and not any(c in brink for c in cells)
    w.trail -= w.plaza          # la placette est dallée : le chemin s'arrête à son bord
    if G['path'] == 'none': w.trail = set()          # une forêt profonde n'a pas de chemin : ce qui guide, ce sont ses plaques de terre
    if G['path'] == 'dotted':          # le chemin n'est dessiné qu'aux bouts, devant ce qui compte, et par tronçons (N) : entre eux, on marche dans l'herbe
        dots = random.Random(sub('paths') + 12)
        deck_ = set(w.marks.get('=', []))
        anchors = [d for _, _, d in w.houses] + list(w.far) + [(x + 2, r - 1) for x, r in w.stairs] + [(x, r) for x, r in w.stairs] + [(x + 2, r + j) for x, r in w.climbs for j in (-1, 1)]
        def matters(c): return c in w.lanes or near(c, deck_, 4) or any(abs(c[0] - a[0]) + abs(c[1] - a[1]) <= 7 for a in anchors)
        # D'abord où les herbes barreront le trajet : là, le chemin ne se dessine pas, neuf cases durant.
        spots = [(route_, i) for route_ in w.routes for i in range(4, len(route_) - 4) if not any(matters(route_[k]) for k in range(i - 3, i + 4))]
        dots.shuffle(spots)
        for route_, i in spots:
            if len(w.bars) >= G['grass_bars'] + W * H // 3000: break
            if all(abs(route_[i][0] - r_[k][0]) + abs(route_[i][1] - r_[k][1]) >= 12 for r_, k in w.bars): w.bars.append((route_, i))
        bare = {route_[k] for route_, i in w.bars for k in range(i - 4, i + 5)}
        painted = set()
        for route_ in w.routes:
            left, on = dots.randint(3, 6), False          # (on commence par un blanc : le tronçon du bout est celui de la sortie)
            for c in route_:
                if left <= 0: on = not on; left = dots.randint(5, 8) if on else dots.randint(4, 7)
                left -= 1
                if (on or matters(c)) and c not in bare: painted.add(c)
        halo = {(c[0] + i, c[1] + j) for c in painted for i in (-2, -1, 0, 1, 2) for j in (-2, -1, 0, 1, 2)}
        w.trail = {c for c in w.trail if c in halo or c in w.lanes or near(c, deck_, 2)}
        for piece in pieces(w.trail):          # un bout de piste de quelques cases ne ressemble à rien
            if len(piece) < 9: w.trail -= piece
        ripple(14)          # les tronçons ont de nouveaux bords droits : ils ondulent aussi
        w.trail -= {c for c in w.trail if any(c in r_[max(0, i - 4):i + 5] for r_, i in w.bars)}
        way |= w.trail
    w.way = way          # (le même ensemble : ce qui s'y ajoute plus bas y est aussi)
    w.trail -= w.trail - inside - built['DECK']          # une piste ne se dessine pas sur le bord d'un plateau : elle s'arrête au pied du pont, en haut de l'escalier
    fronts = {(d[0] + i, d[1] + j) for _, _, d in w.houses for i in (-2, -1, 0, 1, 2) for j in (1, 2, 3)}
    clear = {(c[0] + i, c[1] + j) for c in way for i in (-1, 0, 1) for j in (-1, 0, 1)} | w.lanes | works | house_area | fronts \
        | {(p[0] + i, p[1] + j) for p in w.pois for i in range(-G['poi_radius'], G['poi_radius'] + 1) for j in range(-G['poi_radius'], G['poi_radius'] + 1)}
    clear |= {(c[0] + i, c[1] + j) for c in w.spots for i in (-1, 0, 1) for j in (-1, 0, 1)} | w.plaza
    floor = (way | w.glades) & inside if S['deep'] else set()          # le sol d'une forêt profonde : ses couloirs et ses clairières
    if S['deep']: clear = floor | w.lanes | works          # et rien d'autre : les arbres serrent les couloirs, sans marge — ce sont des murs
    meadow0 = inside - w.mountain - clear
    moist = {c: fractal(sub('climate'), c[0], c[1], C['scale'], 3) for c in CELLS}
    forest = {c for c in meadow0 if moist[c] >= C['forest']}
    if S['deep']: forest = set(meadow0)          # tout ce qui n'est pas le sol est du bois
    forest |= {c for c in meadow0 if w.edge(c) < FRAME}          # la ceinture : trois arbres d'épaisseur, tout le tour (A)
    forest |= {c for c in meadow0 if c in butte}          # les buttes sont boisées (D)
    forest |= {c for p in pieces(meadow0 - footing(built) - butte - brink) if len(p) >= 12 for c in p}          # une terre où ni pont ni escalier ne mène : un bois, pas une pelouse qu'on regarde sans pouvoir y aller
    if S['shape']['name'] == 'corridor':          # une route est un couloir entre deux murs de forêt, qui ne s'élargit qu'en poches (Johto)
        far_, ring_ = {c: 0 for c in way}, list(way)
        while ring_:          # la distance de chaque case au trajet
            nxt = []
            for c in ring_:
                for i, j in NEIGH8:
                    n = (c[0] + i, c[1] + j)
                    if inb(n) and n not in far_ and far_[c] < 12: far_[n] = far_[c] + 1; nxt.append(n)
            ring_ = nxt
        def room(c):          # ce que le couloir laisse de chaque côté du trajet : deux cases, sept dans une poche — autour d'un détour, ou là où le bruit le veut
            if any(abs(c[0] - p[0]) <= 7 and abs(c[1] - p[1]) <= 6 for p in w.waypoints): return 8
            return 2 + int(4 * max(0.0, min(1.0, (fractal(sub('paths') + 8, c[0], c[1], 9.0, 2) - 0.62) / 0.10)))
        forest = {c for c in forest if c not in far_ or far_[c] > room(c) or moist[c] >= C['forest'] + 0.16 or w.edge(c) < FRAME or c in butte}          # dans le couloir, la forêt ne garde que ses bosquets
        forest |= {c for c in meadow0 if far_.get(c, 99) > room(c)}
    rng = random.Random(sub('trees'))
    step = max(4, int(V['tree_spacing']))
    trees = {}
    # La couture avec la carte du sud (`[seam]`, écrit par neighbor.py) : sa trame d'arbres continue ici, zone par zone, et
    # les arbres que son bord coupe ont ici leur autre moitié. Aucun autre arbre n'est coupé par ce bord.
    zones = seam.get('phases', [])
    def phase(x):
        if not zones: return 0
        a, z, p = min(zones, key=lambda zn: 0 if zn[0] <= x <= zn[1] else min(abs(x - zn[0]), abs(x - zn[1])))
        return p
    def foot(x, r): return {(x + i, r - j) for i in range(3) for j in (0, 1)}
    def plant():
        for r in range(0, H + (0 if seam else 1)):          # en quinconce (E) : à 4 la forêt est fermée, au-delà on passe entre les troncs
            for x in range(-2, W):
                if (x - phase(x) - (step // 2) * ((r - H) % 2 if seam else r % 2)) % step or (x, r) in trees: continue
                feet = [(x + i, r - j) for i in range(3) for j in (0, 1) if inb((x + i, r - j))]
                if not feet or any(c not in inside or c in clear or c in w.mountain or c in butte for c in feet) or not same_level(feet + [(x + i, r - 2) for i in range(3)]): continue          # jamais à cheval sur un bord de plateau ni de butte (D)
                if sum(1 for c in feet if c in forest) * 3 >= len(feet) * 2: trees[(x, r)] = 'treeB' if rng.random() < V['tree_dark'] else 'treeA'
    plant()
    if S['deep']:          # entre deux clairières, la trame laisse des vides : on y serre des arbres, où qu'ils tiennent — c'est un mur
        taken_ = {c for (x, r) in trees for c in foot(x, r)}
        for r in range(1, H):
            for x in range(0, W - 2):
                feet = [(x + i, r - j) for i in range(3) for j in (0, 1)]
                if all(c in forest and c not in clear and c not in taken_ and c in inside for c in feet) and same_level(feet):
                    trees[(x, r)] = 'treeB' if rng.random() < V['tree_dark'] else 'treeA'; taken_.update(feet)
    ahead = footing(built)
    for _ in range(3):          # une clairière que les arbres ont refermée : la forêt la reprend, plutôt qu'une pelouse où l'on n'ira jamais
        trunks = {c for (x, r) in trees for c in foot(x, r)}
        seen, todo = {w.start}, [w.start]
        while todo:
            c = todo.pop()
            for i, j in NEIGH4:
                n = (c[0] + i, c[1] + j)
                if n in ahead and n not in trunks and n not in seen: seen.add(n); todo.append(n)
        closed = {c for p in pieces((meadow0 & ahead) - trunks - seen) if len(p) >= 12 for c in p}
        if not closed: break
        forest |= closed; plant()
    crown = {c for c, k in built['high_shape'].items() if k == '5' and c in butte}          # le dessus d'une butte, hors de son bord
    for kind, x, r in seam.get('trees', []): trees[(x, H + r)] = kind          # l'autre moitié des arbres de la carte du sud
    held, perched = set(), {(x, H + r) for _, x, r in seam.get('trees', [])}          # (les arbres d'une butte : à leur place quel que soit leur nombre, l'élagage des bosquets ne les touche pas)
    for r in range(0, H):          # sur les terres hautes de la couture, la forêt garde la trame de la carte du sud
        for x in range(-2, W):
            if not seam_high or (x - phase(x) - 2 * ((r - H) % 2)) % 4: continue
            feet = [(x + i, r - j) for i in range(3) for j in (0, 1) if inb((x + i, r - j))]
            if feet and all(c in crown and c in seam_high and c not in clear for c in feet) and all((x + i, r - 2) in butte for i in range(3) if inb((x + i, r - 2))):
                trees[(x, r)] = 'treeB' if rng.random() < V['tree_dark'] else 'treeA'; perched.add((x, r))
    for r in range(0, H):          # une butte est boisée (D) : ses arbres tiennent tout entiers sur son dessus, serrés, d'un rang sur l'autre décalés
        for x in range(0, W):
            feet = [(x + i, r - j) for i in range(3) for j in (0, 1)]
            if all(c in crown and c not in seam_high and c not in held for c in feet) and (x - 1, r) not in held and all((x + i, r - 2) in butte for i in range(3)):          # tout le dessin tient sur la butte, cime comprise
                trees[(x, r)] = 'treeB' if rng.random() < V['tree_dark'] else 'treeA'; held.update(feet); perched.add((x, r))
    lone = 0
    for grove in sorted(pieces(set(trees), [(i, j) for i in range(-4, 5) for j in range(-3, 4) if (i, j) != (0, 0)]), key=min):          # les arbres bordent ou font des bosquets : pas de semis (E)
        if len(grove) >= 4 or grove & perched: continue
        if len(grove) == 1 and lone < 2: lone += 1; continue
        for c in grove: del trees[c]
    wood = {c for (x, r) in trees for c in foot(x, r)}
    shade = {(x + i, r - j) for (x, r) in trees for i in range(3) for j in (0, 1, 2)}
    occupied = set(wood) | w.spots | w.plaza
    meadow = meadow0 - shade - butte - brink
    obstacle = wood | ring | built['SEA'] | built['POND'] | built['ROCK'] | w.mountain | {c for c in built['high_shape'] if built['high_shape'][c] != '5'}
    homes = fronts | house_area

    # --- les allées de côté (P, Johto) : deux arbres font un îlot ; derrière lui, une allée de trois cases contre un mur d'arbres,
    # barrée d'un rebord. On y saute dans un sens, on fait le tour de l'îlot dans l'autre : le rebord ne ferme rien.
    aside, sites = random.Random(sub('paths') + 9), []
    def vacant(q): return q in inside and q in ahead and q not in occupied and q not in butte and q not in brink and q not in works and q not in fronts and q not in house_area and w.edge(q) >= FRAME + 1 and q not in w.lanes
    def plantable(x, r): return same_level(list(foot(x, r)) + [(x + k, r - 2) for k in range(3)]) and all(vacant(q) and q not in way and not any(abs(q[0] - p[0]) <= 2 and abs(q[1] - p[1]) <= 2 for p in w.pois) for q in foot(x, r))
    def looped(a_, b_, shut_):
        """Vrai si l'on va de `a_` à `b_` à pied sans passer par `shut_` : l'allée fait bien le tour."""
        seen, todo = {a_}, [a_]
        while todo:
            c = todo.pop()
            if c == b_: return True
            for i, j in NEIGH4:
                n = (c[0] + i, c[1] + j)
                if n not in seen and n in ahead and n in inside and n not in wood and n not in shut_ and abs(n[0] - a_[0]) + abs(n[1] - a_[1]) <= 26: seen.add(n); todo.append(n)
        return False
    spots = sorted(c for c in ahead if c in inside and w.edge(c) >= FRAME + 3)
    aside.shuffle(spots)
    for (x0, y) in spots:
        if len(sites) >= min(G['ledges'], max(1, len(ahead) // 200)): break
        if any(abs(x0 - o[0]) + abs(y - o[1]) < 13 for o in sites): continue
        shapes = [  # l'îlot, l'allée, le mur (ses arbres, les cases qui doivent arrêter), le rebord et son signe
            ([(x0, y), (x0, y + 2)], [(x0 + i, y + j) for i in (3, 4, 5) for j in range(-2, 4)], [(x0 + 6, y), (x0 + 6, y + 2)], [(x0 + 6, y + j) for j in range(-1, 3)], [(x0 + i, y) for i in (3, 4, 5)], 'v'),
            ([(x0, y), (x0, y + 2)], [(x0 - i, y + j) for i in (1, 2, 3) for j in range(-2, 4)], [(x0 - 6, y), (x0 - 6, y + 2)], [(x0 - 4, y + j) for j in range(-1, 3)], [(x0 - i, y) for i in (3, 2, 1)], 'v'),
            ([(x0, y), (x0 + 3, y)], [(x0 + i, y + j) for i in range(-1, 7) for j in (1, 2, 3)], [(x0, y + 5), (x0 + 3, y + 5)], [(x0 + i, y + 4) for i in range(0, 6)], [(x0 + 2, y + j) for j in (1, 2, 3)], '>'),
        ]
        aside.shuffle(shapes)
        for island, lane, wall, facing, ledge, mark in shapes:
            if not all(plantable(x, r) for x, r in island) or not all(vacant(q) and q not in way for q in lane): continue
            planted = list(island)
            if not all(q in obstacle for q in facing):
                if not all(plantable(x, r) for x, r in wall): continue
                planted += wall
            shut_ = set(ledge) | {q for x, r in planted for q in foot(x, r)}
            before, after = ((ledge[1][0], ledge[1][1] - 1), (ledge[1][0], ledge[1][1] + 1)) if mark == 'v' else ((ledge[1][0] - 1, ledge[1][1]), (ledge[1][0] + 1, ledge[1][1]))
            if not looped(before, after, shut_) or not looped(w.start, before, shut_): continue
            for x, r in planted:
                trees[(x, r)] = 'treeB' if aside.random() < V['tree_dark'] else 'treeA'; perched.add((x, r))
                wood |= foot(x, r); occupied |= foot(x, r) | {(x + k, r - 2) for k in range(3)}; obstacle |= foot(x, r)
            occupied |= set(lane)          # l'allée reste nue : ni herbes hautes ni bosquet n'y poussent
            meadow -= set(lane) | {q for x, r in planted for q in foot(x, r) | {(x + k, r - 2) for k in range(3)}}
            w.hops.append((mark, ledge)); sites.append((x0, y))
            break

    # --- les hautes herbes (M) : par plaques de 10 à 40, adossées à un bosquet, une eau ou une falaise, au contour déchiqueté
    grow = random.Random(sub('grass'))
    if S['deep']:          # les hautes herbes sont le sol (M) : quatre cases sur cinq de ce qu'on foule, hors des plaques de terre et des trouées de sortie
        w.tall |= {c for c in ahead & inside if c not in w.earth and w.edge(c) >= 5 and c not in occupied and c not in works and c not in brink and lattice(sub('grass') + 3, c[0], c[1]) > 0.08}
    wanted, patches = (0 if S['deep'] else int(max(len(meadow) * V['tall_grass'], len(ahead & inside) * 0.15 if G['path'] == 'dotted' else 0))), []          # (sur une route, les herbes font un sixième de ce qu'on foule, au moins)
    if G['path'] == 'dotted' and G['grass_bars']:          # des herbes en travers du trajet, d'un mur à l'autre (M, Johto) : on les traverse, là où le chemin n'est pas dessiné
        bar, bars = random.Random(sub('grass') + 4), []
        def wall(q): return not inb(q) or q in obstacle or q not in inside or q in occupied or q in butte or q in works
        for route_, i in w.bars:
            c = route_[i]
            if near(c, homes, 6) or near(c, works, 1): continue
            dx, dy = route_[i + 3][0] - route_[i - 3][0], route_[i + 3][1] - route_[i - 3][1]
            along = (1, 0) if abs(dx) >= abs(dy) else (0, 1)
            across, depth, cells, shut_ = (along[1], along[0]), bar.randint(3, 6), set(), True
            for a in range(-(depth // 2), depth - depth // 2):
                base = (c[0] + along[0] * a, c[1] + along[1] * a)
                for sign_ in (1, -1):
                    k = 0 if sign_ == 1 else 1
                    while k <= 8:
                        q = (base[0] + across[0] * k * sign_, base[1] + across[1] * k * sign_)
                        if wall(q): break
                        cells.add(q); k += 1
                    else: shut_ = False          # pas de mur à huit cases : ce n'est pas un couloir, ici
            cells -= fronts | w.trail
            if shut_ and 9 <= len(cells) <= 60:
                holes = {q for q in cells if bar.random() < 0.10 and q not in way}          # quelques trous sur les bords, jamais dans le passage : il n'y aurait plus à traverser
                kept = max(pieces(cells - holes), key=len)
                if len(kept) == (max(q[0] for q in kept) - min(q[0] for q in kept) + 1) * (max(q[1] for q in kept) - min(q[1] for q in kept) + 1):          # jamais un rectangle plein : deux angles en moins, hors du passage
                    kept -= {q for q in (min(kept), max(kept)) if q not in way}
                w.tall |= kept; patches.append(kept); bars.append(c)
    seeds_ = sorted(c for c in meadow if near(c, obstacle, 2) and not near(c, homes, 6) and (not S['hamlet'] or w.edge(c) <= FRAME + 5))          # (dans un village : en lisière seulement, jamais au centre — M)
    grow.shuffle(seeds_)
    big = 40 if V['tall_grass'] >= 0.18 else 30
    for seed in seeds_:
        if sum(len(p) for p in patches) >= wanted: break
        if any(near(seed, p, 3) for p in patches): continue
        size, patch, front = grow.randint(11, big), {seed}, [seed]
        while len(patch) < size and front:
            c = front.pop(grow.randrange(len(front)))
            for i, j in NEIGH4:
                n = (c[0] + i, c[1] + j)
                if n in meadow and n not in patch and len(patch) < size and not any(near(n, p, 2) for p in patches) and not near(n, homes, 6) and (not S['hamlet'] or w.edge(n) <= FRAME + 7): patch.add(n); front.append(n)
        holes = {c for c in patch if grow.random() < 0.16 and c != seed}          # une case manquante sur cinq ou six
        kept = max(pieces(patch - holes), key=len)
        if len(kept) == (max(c[0] for c in kept) - min(c[0] for c in kept) + 1) * (max(c[1] for c in kept) - min(c[1] for c in kept) + 1):          # jamais un rectangle plein : on lui casse deux angles
            kept -= {min(kept), max(kept)}
        if len(kept) >= 10: patches.append(kept)
    for p in patches: w.tall |= p
    occupied |= w.tall

    # --- les fleurs (Q) : par touffes de deux ou trois, en diagonale ou en L, au bord d'un chemin, au pied d'un arbre
    decor = random.Random(sub('decor'))
    lawn = meadow - w.tall
    tufts = []
    open_ = inside - w.mountain - butte - brink - house_area - fronts - w.lanes - works          # toute la pelouse, abords des chemins compris
    FORMS = ([(0, 0), (1, 1)], [(0, 0), (1, 1), (2, 2)], [(0, 0), (1, 0), (1, 1)], [(0, 0), (0, 1), (1, 1)], [(0, 0), (1, -1)], [(0, 0), (1, 1), (2, 0)])
    cap = max(3, len((built['REACH'] & inside) - wood - w.mountain) // (80 if S['deep'] else 19))          # une touffe pour 15 à 60 cases où l'on marche : jamais plus serré
    flowerable = inside - w.mountain - butte - brink - fronts - works - built['SOLID']          # là où une fleur peut pousser : jusque contre une maison, jusque sur le trajet
    def tuft(c, forced=False):
        if len(tufts) >= cap and not forced: return False
        cells = [(c[0] + i, c[1] + j) for i, j in FORMS[decor.randrange(len(FORMS))]]
        if any(q not in (flowerable if forced else open_) or q in w.trail or q in w.tall or q in occupied for q in cells) or any(near(q, set(t), 2) for q in cells for t in tufts): return False
        colour = decor.randint(1, 5)
        for q in cells: w.props.append(('fl%d' % (colour if decor.random() < 0.75 else decor.randint(1, 5)), q[0], q[1]))
        occupied.update(cells); tufts.append(cells); return True
    spots = sorted(c for c in lawn if near(c, w.trail | wood | ring, 2)); decor.shuffle(spots)
    quota = max(3, int(len(lawn) * V['decorations'] / 2.4), len(open_) // 36)
    for c in spots:
        if len(tufts) >= quota: break
        tuft(c)
    spots = sorted(open_ - w.trail); decor.shuffle(spots)
    for c in spots:          # et s'il en manque encore, ailleurs sur la pelouse
        if len(tufts) >= max(3, len(open_) // 50): break
        tuft(c)
    beds, spots = [], sorted(lawn); decor.shuffle(spots)
    for c in spots:          # les grandes fleurs, par deux, décalées, jamais en rang
        if len(beds) >= V['blooms']: break
        pair = [c, (c[0] + 2, c[1] + 1)]
        if all(q in lawn and q not in occupied and (q[0], q[1] - 1) in lawn and (q[0], q[1] - 1) not in occupied for q in pair) and all(abs(c[0] - b[0]) + abs(c[1] - b[1]) >= 8 for b in beds):
            for k, q in enumerate(pair): w.props.append(('bloom%d' % ((len(beds) + k) % 4), q[0], q[1])); occupied |= {q, (q[0], q[1] - 1)}
            beds.append(c)

    # --- aucune pelouse nue de plus de 4 × 4 (B) : un bosquet, une touffe d'herbes ou de fleurs dans chaque étendue vide
    fill = random.Random(sub('decor') + 3)
    for _ in range(400):
        bare = flowerable - occupied - w.trail - w.tall
        squares = sorted((x, y) for x, y in bare if all((x + i, y + j) in bare for i in range(5) for j in range(5)))
        if not squares: break
        x, y = squares[fill.randrange(len(squares))]
        centre, kind, placed = (x + 2, y + 2), fill.random(), False
        if kind < 0.45:          # un bosquet de quatre ou cinq arbres : il fera un dos pour des herbes
            spots = [(tx, tr) for (tx, tr) in [(x, y + 2), (x + 2, y + 3), (x + 4, y + 2), (x + 2, y + 1), (x + 6, y + 3)]
                     if all(q in lawn and q not in w.tall and q not in clear and (q not in occupied or q in wood) for q in foot(tx, tr))]
            if len(spots) >= 4:
                for (tx, tr) in spots:
                    trees[(tx, tr)] = 'treeB' if fill.random() < V['tree_dark'] else 'treeA'
                    wood |= foot(tx, tr); occupied |= foot(tx, tr) | {(tx + i, tr - 2) for i in range(3)}
                placed = True
        if not placed and kind < 0.88 and not S['hamlet'] and not S['farm']:          # une touffe d'herbes hautes, de trois à six cases (pas dans un village)
            n, cells, tries = fill.randint(3, 6), [centre], 0
            while len(cells) < n and tries < 60:
                c = cells[fill.randrange(len(cells))]; d = fill.choice(NEIGH4); q = (c[0] + d[0], c[1] + d[1]); tries += 1          # (côte à côte, pas en diagonale : une touffe est d'un seul tenant)
                if q in bare and q in lawn and q not in cells and not near(q, w.tall - set(cells), 1): cells.append(q)
            if len(cells) >= 3 and centre in lawn and not near(centre, w.tall, 1): w.tall |= set(cells); occupied |= set(cells); placed = True
        on_way = near(centre, way, 1) or centre not in open_          # sur le trajet, là où le chemin n'est pas dessiné, et aux abords d'une maison : des fleurs, jamais rien qui arrête
        if not placed and not tuft(centre, on_way):          # à défaut : des fleurs, ou une seule
            if centre in flowerable and centre not in w.trail and centre not in occupied:
                if len(tufts) < cap or on_way: w.props.append(('fl%d' % fill.randint(1, 5), centre[0], centre[1])); tufts.append([centre])
                else: w.props.append((fill.choice(('rock_s', 'sapling', 'pebbleA')), centre[0], centre[1]))          # assez de fleurs : un caillou, une pousse
            occupied.add(centre)
    lone = 0
    for grove in sorted(pieces(set(trees), [(i, j) for i in range(-4, 5) for j in range(-3, 4) if (i, j) != (0, 0)]), key=min):
        if len(grove) >= 4 or grove & perched: continue
        if len(grove) == 1 and lone < 2: lone += 1; continue
        for c in grove: del trees[c]
    wood = {c for (x, r) in trees for c in foot(x, r)}
    for (x, r), kind in sorted(trees.items(), key=lambda kv: (kv[0][1], kv[0][0])): w.props.append((kind, x, r))

    # --- la montagne, le rivage
    stone = random.Random(sub('relief') + 1)
    for c in sorted(w.mountain):
        if stone.random() < V['boulders'] and all((c[0] + i, c[1] + j) in w.mountain or not inb((c[0] + i, c[1] + j)) for i in range(-3, 5) for j in range(-4, 4)) and not any((c[0] + i, c[1] + j) in occupied for i in (-2, -1, 0, 1, 2) for j in (-2, -1, 0, 1, 2)):          # (sur le dessus du dernier gradin, pas à cheval sur un bord)
            w.props.append(('boulder', c[0], c[1])); occupied |= {(c[0] + i, c[1] - j) for i in (0, 1) for j in (0, 1)}
    shore = random.Random(sub('shore'))
    dry = sorted(c for c in beach if all((c[0] + i, c[1] + j) in beach for i in (-1, 0, 1) for j in (-1, 0, 1)) and c not in works)          # du sable sec, à l'écart de l'eau et de la falaise
    palms = []
    for strand in sorted(pieces(set(dry)), key=min):
        spots, mine = sorted(strand), 0
        shore.shuffle(spots)
        for c in spots:
            if mine < V['palms'] and all(abs(c[0] - p[0]) + abs(c[1] - p[1]) >= V['palm_gap'] for p in palms): palms.append(c); mine += 1          # à cinq cases les uns des autres (E) ; deux à quatre sur une plage
    for c in palms: w.props.append(('palm', c[0], c[1])); occupied.add(c)
    shells, spots = [], list(dry)
    shore.shuffle(spots)
    for c in spots:
        if V['shells'] and len(shells) < len(dry) // V['shells'] and c not in occupied and all(abs(c[0] - o[0]) + abs(c[1] - o[1]) >= 5 for o in shells): w.props.append(('shell%d' % (1 + len(shells) % 4), c[0], c[1])); shells.append(c)
    if V['sand_rocks']:          # une plage se garnit : un rocher pour quinze à vingt cases de sable, et jamais de sable nu sur plus de 8 × 8
        stones, spots = [], [c for c in dry if c not in occupied and c not in shells]
        shore.shuffle(spots)
        drys = set(dry)
        for c in spots:          # par grappes — un gros bloc et un ou deux petits, ou deux petits — jamais en grille (F)
            if len(stones) >= len(dry) // V['sand_rocks']: break
            if not all(abs(c[0] - o[0]) + abs(c[1] - o[1]) >= 6 for o in stones + palms): continue
            block = [(c[0] + i, c[1] - j) for i in (0, 1) for j in (0, 1)]
            if shore.random() < 0.55 and all(q in drys and q not in occupied and q not in shells for q in block):
                w.props.append(('boulder', c[0], c[1])); occupied.update(block); stones.append(c)
                around = [(c[0] + i, c[1] + j) for i, j in ((-1, 0), (2, 0), (2, -1), (-1, 1), (0, 1), (1, 1))]
            else:
                w.props.append(('rock_s', c[0], c[1])); occupied.add(c); stones.append(c)
                around = [(c[0] + i, c[1] + j) for i, j in ((1, 1), (-1, 1), (2, 0), (-2, 0), (1, -1))]
            for q in shore.sample(around, shore.randint(1, 2)):
                if q in drys and q not in occupied and q not in shells: w.props.append(('rock_s', q[0], q[1])); occupied.add(q); stones.append(q)
        for _ in range(200):
            bare = beach - occupied - set(shells) - works
            squares = sorted((x, y) for x, y in bare if all((x + i, y + j) in bare for i in range(9) for j in range(9)))
            if not squares: break
            x, y = squares[shore.randrange(len(squares))]
            c = (x + 4, y + 4)
            w.props.append(('shell%d' % (1 + len(shells) % 4), c[0], c[1])); shells.append(c)
    lily = random.Random(sub('shore') + 3)
    for pond in sorted(pieces(built['POND']), key=min):          # un à trois nénuphars par étang moyen ou grand, sur l'eau pleine, loin d'un pont (O)
        full = sorted(c for c in pond if all((c[0] + i, c[1] + j) in pond for i in (-1, 0, 1) for j in (-1, 0, 1)) and not near(c, set(w.marks.get('=', [])), 1))
        lily.shuffle(full)
        pads = []
        for c in full:
            if len(pads) >= (0 if len(pond) < 20 else 1 if len(pond) < 40 else 2 if len(pond) < 90 else 3): break
            if all(abs(c[0] - p[0]) + abs(c[1] - p[1]) >= 3 for p in pads): w.props.append(('lily%d' % lily.randint(1, 3), c[0], c[1])); pads.append(c)
    deck = set(w.marks.get('=', []))
    sea = built['SEA'] - deck
    coast = sorted(c for c in sea if near(c, built['LAND'], 4) and not near(c, built['LAND'], 2) and not near(c, deck, 2))
    rocks, groups = set(), []
    shore.shuffle(coast)
    for c in coast:          # les rochers décorent (F) : par grappes d'un gros et de deux ou trois petits, en mer près des côtes
        if len(groups) >= max(1, int(len(sea) * V['sea_rocks'] / 3)) or any(abs(c[0] - g[0]) + abs(c[1] - g[1]) < 9 for g in groups): continue
        if not all((c[0] + i, c[1] + j) in sea for i in (0, 1) for j in (0, 1)): continue
        w.props.append(('riverrock', c[0], c[1])); rocks.add(c); groups.append(c)
        for k, (i, j) in enumerate(shore.sample([(-2, 1), (2, -1), (3, 1), (-1, -2), (1, 2), (-2, -1)], shore.randint(2, 3))):
            q = (c[0] + i, c[1] + j)
            if q in sea and not near(q, built['LAND'], 1) and q not in rocks: w.props.append((('spire', 'pebbleB', 'pebbleA')[k % 3], q[0], q[1])); rocks.add(q)

    if S['chain'] and w.open:          # la chaîne de rochers d'une route côtière (F) : elle suit la côte à quatre cases au large, un rocher tous les deux pas, gros et petits mêlés
        def at(t, d): return {'west': (d, t), 'east': (W - 1 - d, t), 'north': (t, d), 'south': (t, H - 1 - d)}[w.open]
        span, last, k = (H if w.open in ('west', 'east') else W), None, 0
        for t in range(2, span - 2, 2):
            depth = next((d for d in range(0, 40) if at(t, d) not in sea), 40)
            if depth < 8: last = None; continue
            d = depth - 4 if last is None else max(last - 1, min(last + 1, depth - 4))
            c = at(t, max(2, d)); last = max(2, d); k += 1
            if near(c, deck, 2) or near(c, rocks, 0): continue
            big = k % 3 != 0 and all((c[0] + i, c[1] - j) in sea and (c[0] + i, c[1] - j) not in rocks for i in (0, 1) for j in (0, 1))
            w.props.append(('riverrock' if big else ('spire', 'pebbleB')[k % 2], c[0], c[1])); rocks.add(c)
            if big: rocks.update({(c[0] + 1, c[1]), (c[0], c[1] - 1), (c[0] + 1, c[1] - 1)})

    # ============================================================ 5. ce qui récompense le curieux et ce qui renseigne : objets et panneaux (K)
    built = w.probe()
    reach = built['REACH']
    taken = set(w.spots) | w.plaza
    veil = {(x + i, r - 2) for (x, r) in trees for i in range(3)} | {(c[0] + i, c[1] - j) for c in palms for i in (-1, 0, 1) for j in (1, 2)}          # derrière une cime ou une palme, on ne voit rien (K)
    AROUND = [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]
    def pinch(c):
        """Vrai si un objet posé là couperait le passage : ses voisines libres ne se rejoignent pas en le contournant."""
        ring = [(c[0] + i, c[1] + j) in reach and (c[0] + i, c[1] + j) not in taken for i, j in AROUND]
        if all(ring): return False
        runs, k0 = 0, next(k for k in range(8) if not ring[k])
        k = 0
        while k < 8:
            if ring[(k0 + k) % 8]:
                run = []
                while k < 8 and ring[(k0 + k) % 8]: run.append((k0 + k) % 8); k += 1
                if any(q % 2 for q in run): runs += 1          # (une case en coin ne compte que si elle tient à une voisine de côté)
            else: k += 1
        return runs != 1
    # Les rebords (P) : un raccourci qu'on saute vers le bas, en travers d'un couloir à l'écart du chemin, ses deux bouts contre un
    # arbre ou une falaise. Jamais sur le seul passage : sans lui, tout se rejoint encore.
    hop = random.Random(sub('paths') + 6)
    def flood(free):
        seen, todo = {w.start}, [w.start]
        while todo:
            c = todo.pop()
            for i, j in NEIGH4:
                n = (c[0] + i, c[1] + j)
                if n in free and n not in seen: seen.add(n); todo.append(n)
        return seen
    lawn_ = {c for c in reach if c in inside and c not in way and c not in w.tall and c not in fronts and c not in works          # (une fleur n'arrête pas un rebord : on l'ôte)
             and w.edge(c) >= FRAME + 1}          # (pas sur le trajet : un rebord barre une allée de côté, d'un mur à l'autre)
    solid_, gone, heads = built['SOLID'], set(), []
    for mark, run in w.hops:          # d'abord ceux des allées de côté, prévus pour ça
        dx, dy = (0, 1) if mark == 'v' else (1, 0)
        if not all(q in reach and q not in way and q not in gone and (q[0] + dx, q[1] + dy) in reach and (q[0] - dx, q[1] - dy) in reach for q in run): continue
        rest = reach - gone - set(run)
        if len(flood(rest)) != len(rest): continue
        w.marks.setdefault(mark, []).extend(run); gone.update(run); heads.append(run[0])
        taken.update(run); taken.update((q[0] + k * dx, q[1] + k * dy) for q in run for k in (-1, 1)); occupied.update(run)
    spots = sorted(lawn_); hop.shuffle(spots)
    for c in spots:
        if len(heads) >= min(G['ledges'], len(reach) // 90): break
        if (c[0] - 1, c[1]) not in solid_ or any(abs(c[0] - l[0]) + abs(c[1] - l[1]) < 9 for l in heads): continue
        run, q = [], c
        while q in lawn_ and len(run) < 9: run.append(q); q = (q[0] + 1, q[1])
        if not 3 <= len(run) <= 8 or q not in solid_: continue
        if not all(n in reach and n not in gone for x, y in run for n in ((x, y - 1), (x, y + 1))): continue
        rest = reach - gone - set(run)
        if len(flood(rest)) != len(rest): continue          # ce serait un sens unique sans retour
        w.marks.setdefault('v', []).extend(run); gone.update(run); heads.append(c)
        taken.update(run); taken.update((x, y + j) for x, y in run for j in (-1, 1)); occupied.update(run)
    reach = reach - gone
    w.props = [p_ for p_ in w.props if not ((p_[1], p_[2]) in gone and p_[0].startswith(('fl', 'bloom')))]

    # Les petits sapins sont de la variété, pas un bouche-trou (Ludovic, 18/11/2026) : un pour huit gros arbres au plus, au
    # bord d'un bois, seuls ou par deux — jamais empilés, jamais dans un passage.
    deco = random.Random(sub('trees') + 5)
    fringe = sorted(c for c in reach if c in inside and c not in way and c not in occupied and c not in taken and c not in veil and near(c, wood, 1) and not near(c, way, 1) and c not in fronts and w.edge(c) >= FRAME + 1)
    deco.shuffle(fringe)
    firs = []
    for c in fringe:
        if len(firs) >= min(len(trees) // 8, max(2, len(reach) // 70)): break
        if any(abs(c[0] - f[0]) + abs(c[1] - f[1]) < 7 for f in firs) or pinch(c): continue
        w.props.append((deco.choice(('conif', 'conif', 'sapling')), c[0], c[1])); firs.append(c); taken.add(c); occupied.add(c)
        q = (c[0] + deco.choice((-1, 1)), c[1])
        if deco.random() < 0.3 and q in fringe and q not in taken and not pinch(q): w.props.append(('conif', q[0], q[1])); firs.append(q); taken.add(q); occupied.add(q)
    veil |= {(c[0], c[1] - 1) for c in firs}
    for e, m, span, inward in w.exits:          # un panneau à chaque entrée : à une case du chemin, adossé aux arbres
        c = (span[1][0] + inward[0] * 4, span[1][1] + inward[1] * 4)
        side = [(c[0] + inward[0] * d + k * abs(inward[1]) * s, c[1] + inward[1] * d + k * abs(inward[0]) * s) for d in (0, 1, 2, -1, 3, 4) for k in (2, 3) for s in (-1, 1)]          # (au nord d'un chemin d'abord : un panneau se lit d'en dessous)
        spot = next((q for q in side if q in reach and q not in way and q not in occupied and q not in taken and q not in veil and not pinch(q)), None)
        if spot is None: continue
        mk = w.mark([spot]); taken.add(spot)
        w.tables.append(('sign', dict(mark=mk, name='Sign%s' % e.get('name', m), text=e.get('sign', '%s.|Sortie %s.' % (w.m.get('location', w.m['name']), e.get('name', m))), exact=True)))
    treasure = random.Random(sub('decor') + 7)
    nooks = sorted(c for c in reach if c in inside and c not in way and c not in occupied and not near(c, way, 3) and near(c, obstacle | wood, 1) and c not in fronts and c not in veil and w.edge(c) >= FRAME + 2 and sum((c[0] + i, c[1] + j) in reach for i, j in NEIGH4) >= 2)          # (pas dans une trouée de la lisière, que la fermeture des bords bouchera)
    treasure.shuffle(nooks)
    found = []
    spare = sorted(c for c in reach if c in inside and c not in way and c not in occupied and near(c, obstacle | wood, 1) and c not in fronts and c not in veil and w.edge(c) >= FRAME + 2 and sum((c[0] + i, c[1] + j) in reach for i, j in NEIGH4) >= 2)
    treasure.shuffle(spare)
    for gap, pool in ((10, nooks), (6, spare)):          # un objet au bout d'un recoin ou d'un détour, loin du chemin ; sur une petite carte, plus près s'il le faut : il en faut trois (K)
        for c in pool:
            if len(found) >= (G['items'] if pool is nooks else min(3, G['items'])): break
            if any(abs(c[0] - f[0]) + abs(c[1] - f[1]) < gap for f in found) or c in taken or pinch(c): continue          # (jamais dans un goulet : un objet est un obstacle)
            item = ITEMS[len(found) % len(ITEMS)]
            mk = w.mark([c]); found.append(c); taken.add(c)
            w.tables.append(('item', dict(mark=mk, name='Item%d' % len(found), item=item[0], text='Vous trouvez %s !|Vous rangez %s dans la poche %s.' % (item[1], item[2], item[3]), exact=True)))
    for name in ('sign', 'lamp', 'item', 'npc', 'flyers'):          # ce que le monde nomme déjà par un repère passe tel quel
        for entry in world.get(name, []): w.tables.append((name, dict(entry)))
    return w


def close_edges(path, keep=(), limit=8):
    """Le bord de la carte et sa marge ne s'atteignent qu'aux sorties. Là où la lisière laisse passer, on y plante un arbre
    de plus — un vrai, quitte à serrer ses voisins ; un caillou sur le sable. Les petits sapins ne servent pas à ça."""
    import check as checker
    added = 0
    for _ in range(limit):
        built = builder.build(builder.Plan(path))
        W, H = built['W'], built['H']
        lanes = set()
        for c in built['GATES']:
            dx, dy = (0, 1) if c[1] == 0 else (0, -1) if c[1] == H - 1 else (1, 0) if c[0] == 0 else (-1, 0)
            lanes |= {(c[0] + dx * k + i * abs(dy), c[1] + dy * k + i * abs(dx)) for k in range(0, 12) for i in (-2, -1, 0, 1, 2)}
        mx, my = checker.MARGIN
        loose = sorted(c for c in built['REACH'] if (c[0] < mx or c[0] >= W - mx or c[1] < my or c[1] >= H - my) and c not in lanes and c not in built['GATES'])
        loose += [c for c in built['edge'] if c not in loose]
        if not loose: break
        trunks = {(x + i, r - j) for k, x, r in built['sprites'] if k.startswith('tree') for i in range(3) for j in (0, 1)}
        shut = built['TRAIL'] | built['GATES'] | built['high'] | built['STEPS'] | built['DECK'] | built['house_area'] | set(built['stairs']) | set(keep)          # (`keep` : le trajet, même là où le chemin n'est pas dessiné)
        def room(x, r):          # un arbre tient-il là ? Ses pieds sur le dessus du plateau, hors de tout chemin (ce qui dépasse de la carte ne compte pas)
            feet = [(x + i, r - j) for i in range(3) for j in (0, 1)]
            seen = [q for q in feet if 0 <= q[0] < W and 0 <= q[1] < H]
            return r <= H - 1 and seen and all(q in built['INSIDE'] and q not in shut for q in seen) and feet          # (jamais un arbre coupé par le bord du bas)
        extra, left = [], set(loose)
        while left:
            c = min(left)
            options = [(len(set(f) & left), -len(set(f) & trunks), x, r, f) for x in (c[0] - 2, c[0] - 1, c[0]) for r in (c[1], c[1] + 1) for f in [room(x, r)] if f]
            if options:
                _, _, x, r, feet = max(options)
                extra.append('treeA %d %d' % (x, r)); left -= set(feet); trunks |= set(feet)
            else:
                extra.append('%s %d %d' % ('rock_s' if c in built['BEACH'] else 'conif', c[0], c[1])); left.discard(c)
        src = open(path, encoding='utf-8').read()
        i = src.index('props = ' + Q3) + len('props = ' + Q3)
        open(path, 'w', encoding='utf-8').write(src[:i] + '\n' + '\n'.join(extra) + src[i:]); added += len(extra)
    return added


if __name__ == '__main__':
    import check as checker
    args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and sys.argv[i - 1] not in ('--preview', '--plan')]
    if not args: sys.exit(__doc__)
    with open(args[0], 'rb') as f: world = tomllib.load(f)
    w = generate(world, args[0])
    out = sys.argv[sys.argv.index('--plan') + 1] if '--plan' in sys.argv else os.path.join(HERE, 'plans', world['map']['name'] + '.toml')
    w.write(out)
    closed = close_edges(out, w.way) if w.S['gameplay']['close_edges'] else 0
    results, built = checker.check(builder.Plan(out))
    done = [r for r in results if r[2] is not None]
    print('%s : %d × %d, %d choses posées, %d pour fermer les bords — %d cases atteintes à pied — composition : %.0f %% (%d règles sur %d)'
          % (world['map']['name'], w.W, w.H, len(w.props), closed, len(built['REACH']), checker.rate(results), sum(1 for r in done if r[2]), len(done)))
    stuck = checker.blocking(built)
    if stuck: print('  INJOUABLE en l état — %d blocages :' % len(stuck))
    for line in stuck: print('  !! ' + line)
    for note in w.notes: print('  !! ' + note)
    for section, text, ok, measure, cells in results:
        if ok is False: print('  !! %s %s — %s%s' % (section, text, measure, ('  ex. %s' % cells) if cells else ''))
    for line in built['warn']: print('     constructeur : ' + line)
    print('plan : ' + os.path.relpath(out))
    if '--preview' in sys.argv:
        target = sys.argv[sys.argv.index('--preview') + 1]; builder.preview(built, target); print('aperçu : ' + target)
