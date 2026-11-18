#!/usr/bin/env python3
"""Le contrôleur de composition : un plan en entrée, la liste des règles qu'il enfreint en sortie.

    python3 tools/mapgen/check.py tools/mapgen/plans/<carte>.toml          le détail, règle par règle
    python3 tools/mapgen/check.py <plan> <plan> ...                        une ligne par carte

Le constructeur vérifie qu'une carte **s'assemble** (un escalier a sa plage, une porte s'atteint). Lui vérifie qu'elle
est **bien composée** : les règles chiffrées de `docs/mapping.md`, celles qui se mesurent sur un plan. Chaque règle
porte la lettre de sa section dans ce document. Une règle qui ne concerne pas la carte (pas de maison, pas de mer)
ne compte ni pour ni contre.

Le **taux** d'une carte est la part des règles applicables qu'elle respecte. Ce qui ne se mesure pas — « une carte a
un but », « le décor guide » — reste à juger à l'œil : un taux de 100 % dit qu'aucune faute connue n'a été trouvée,
pas que la carte est bonne.

**Chaque carte a un style** (`docs/mapping.md`, « Les styles de carte ») : `style = "route"`, `forest`, `fields`,
`beach`, `village` ou `city` dans la table `[map]` du plan — sans cela, une route, ou un village s'il y a trois
maisons. Le tableau `STYLES` dit ce que chaque style change aux seuils : une plage n'a pas de chemin à faire passer
dans ses sorties, la mer y touche le bord, et son sable doit s'atteindre.

Le taux ne dit pas tout : une carte où une sortie, une porte ou un objet ne s'atteint pas, où un escalier ne se
franchit pas, où le bord s'atteint ailleurs qu'à une sortie, est **INJOUABLE** quel que soit son taux. C'est dit à
part, et la commande sort alors en erreur (comme pour un plan sous 85 %).

Un plan littéral (`[[layer]]` : la Route 1, l'île de départ) donne ses tuiles, pas sa géographie : le relief, la
ceinture de forêt, les objets et le point de départ ne s'y lisent pas, et ces règles-là ne lui sont pas appliquées.
Son taux ne porte donc que sur une dizaine de règles.

Il sert à une carte écrite à la main comme à une carte inventée ; le générateur (`worldgen.py`) le lance sur ce qu'il
vient d'écrire, et `sweep.py` sur des dizaines de mondes d'un coup.
"""
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as builder  # noqa: E402

NEIGH4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
NEIGH8 = [(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i, j) != (0, 0)]
MARGIN = (4, 3)          # la marge où l'on ne marche jamais : cases depuis les bords gauche/droite, haut/bas (A, la mesure de l'île)
BELT = 6                 # l'épaisseur de la ceinture de forêt : trois arbres (A)
STRAIGHT = 6             # jamais plus de tant de cases en ligne droite pour une côte ou un bord de plateau (C)
BARE = 5                 # un carré de pelouse nue de ce côté est de trop : « aucune pelouse nue de plus de 4 × 4 » (B)

# Les styles de carte (docs/mapping.md, « Les styles de carte ») : ce que chacun change aux seuils. Un plan dit le
# sien dans `[map] style = "..."` ; sans cela, c'est un village s'il a trois maisons, une route sinon.
#   size      le petit et le grand côté admis, en cases
#   belt      l'épaisseur de la ceinture de forêt, en cases pleines (None : pas de ceinture, la mer fait le tour)
#   open_sea  la mer touche le bord largement, au lieu de passes étroites barrées de rochers ; `sea` : la part du bord qu'elle prend au moins
#   paths     un chemin traverse chaque sortie (une forêt profonde et une plage n'ont pas de chemin)
#   relief    le nombre de plateaux, buttes ou massifs qu'il faut au moins
#   palms     l'écart entre deux palmiers, en cases
#   tall      la taille d'une plaque de hautes herbes ; None : elles sont le sol (forêt profonde), on mesure leur part
#   flowers   une touffe pour tant à tant de cases praticables (None : pas de fleurs à compter)
#   items     le nombre d'objets à ramasser
#   sand      le côté du plus grand carré de sable nu admis
STYLES = {
    'route':   dict(name='une route', size=(30, 115), belt=6, open_sea=False, paths=True, relief=2, palms=5, tall=(10, 48), flowers=(15, 60), items=(3, 8), sand=None),
    'seaside': dict(name='une route côtière', size=(30, 115), belt=6, open_sea=True, sea=0.10, paths=True, relief=2, palms=5, tall=(10, 48), flowers=(15, 60), items=(3, 8), sand=None),
    'mountain': dict(name='une route de montagne', size=(30, 115), belt=None, open_sea=False, paths=True, relief=2, palms=5, tall=(10, 48), flowers=(15, 80), items=(3, 8), sand=None),
    'forest':  dict(name='une forêt profonde', size=(35, 80), belt=8, open_sea=False, paths=False, relief=0, palms=5, tall=None, flowers=None, items=(2, 8), sand=None),
    'fields':  dict(name='des champs', size=(40, 60), belt=6, open_sea=False, paths=True, relief=0, palms=5, tall=(3, 12), flowers=(15, 60), items=(2, 6), sand=None),
    'beach':   dict(name='une plage', size=(40, 70), belt=6, open_sea=True, sea=0.12, paths=False, relief=2, palms=2, tall=(10, 40), flowers=None, items=(3, 6), sand=8),
    'village': dict(name='un village', size=(30, 60), belt=6, open_sea=False, paths=True, relief=0, palms=5, tall=(10, 40), flowers=(8, 60), items=(1, 3), sand=None),
    'cave':    dict(name='une grotte', size=(30, 66), belt=None, open_sea=False, paths=False, relief=0, palms=5, tall=(3, 12), flowers=None, items=(1, 4), sand=None, signs=False, bare=False),
    'city':    dict(name='une ville côtière', size=(30, 60), belt=None, open_sea=True, sea=0.5, paths=True, relief=1, palms=1, tall=(3, 15), flowers=None, items=(1, 3), sand=None),
}


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


def runs(cells):
    """Les suites de cases alignées (horizontales puis verticales) d'un ensemble : leurs longueurs et leur première case."""
    out = []
    for dx, dy in ((1, 0), (0, 1)):
        for c in cells:
            if (c[0] - dx, c[1] - dy) in cells: continue
            n, q = 0, c
            while q in cells: n += 1; q = (q[0] + dx, q[1] + dy)
            out.append((n, c, (dx, dy)))
    return out


def thin(cells):
    """Les cases d'une matière qui n'a qu'une case de large à cet endroit, dans un sens ou dans l'autre."""
    return {c for c in cells if ((c[0] - 1, c[1]) not in cells and (c[0] + 1, c[1]) not in cells) or ((c[0], c[1] - 1) not in cells and (c[0], c[1] + 1) not in cells)}


def check(plan):
    """Les règles, une par une : (section, intitulé, respectée ou None si elle ne s'applique pas, ce qu'on a mesuré, quelques cases)."""
    b = builder.build(plan)
    W, H = b['W'], b['H']
    CELLS = [(x, y) for y in range(H) for x in range(W)]
    def inb(c): return 0 <= c[0] < W and 0 <= c[1] < H
    REACH, SOLID, SEA, BEACH, INSIDE, RING = b['REACH'], b['SOLID'], b['SEA'], b['BEACH'], b['INSIDE'], b['RING']
    TRAIL, TALL, GATES, doors = b['TRAIL'], b['TALL'], b['GATES'], b['doors']
    L = b['L']
    trees = [(k, x, r) for k, x, r in b['sprites'] if k.startswith('tree')]
    tree_cells = {(x + i, r - j) for _, x, r in trees for i in range(3) for j in (0, 1)}
    low = {c for c in L['Decorations'] if c not in b['fence']}          # les petites fleurs et les coquillages
    flowers = {c for c in low if c in INSIDE and c not in b['POND']}          # (les nénuphars d'un étang ne sont pas des fleurs de pelouse)
    blooms = {c for c, t in L['Props'].items() if t[0] == builder.FLOWER_SOURCE and t[2] == builder.THEME['sources'].get('blooms', {}).get('foot')}
    props = {(x, r) for _, x, r in b['sprites']}
    lanes = {(c[0] + i, c[1] + j) for c in GATES for i in range(-2, 3) for j in range(-2, 3)}
    for c in list(GATES):          # le couloir d'une sortie traverse la marge : il en est exempté
        dx, dy = (0, 1) if c[1] == 0 else (0, -1) if c[1] == H - 1 else (1, 0) if c[0] == 0 else (-1, 0)
        lanes |= {(c[0] + dx * k + i * abs(dy), c[1] + dy * k + i * abs(dx)) for k in range(0, BELT + 3) for i in (-2, -1, 0, 1, 2)}
    margin = {c for c in CELLS if c[0] < MARGIN[0] or c[0] >= W - MARGIN[0] or c[1] < MARGIN[1] or c[1] >= H - MARGIN[1]}
    out = []
    # Un plan littéral (`[[layer]]`) donne ses tuiles, pas sa géographie : relief, ceinture, objets et point de départ ne
    # s'y lisent pas. Ces règles-là ne s'appliquent pas à lui — sinon une carte validée passerait pour fautive.
    BLIND = ('la ceinture de forêt', 'du relief', 'la carte s assemble') if b['literal'] else ()
    def rule(section, text, ok, measure='', cells=()): out.append((section, text, None if text.startswith(BLIND) else ok, measure, sorted(cells)[:4]))
    kind = plan.map.get('style') or ('route' if len(doors) < 3 else 'village')          # (une cabane au bord du chemin ne fait pas un village)
    if kind not in STYLES: raise SystemExit('style inconnu : %r (connus : %s)' % (kind, ', '.join(STYLES)))
    Y = STYLES[kind]
    b['style'] = kind

    # ---------------------------------------------------------------- A. bords et marge
    bad = (REACH & margin) - lanes
    rule('A', "aucune case de la marge ne s'atteint à pied", not bad, '%d cases atteintes dans la marge' % len(bad), bad)
    bad = {c for c in REACH if (c[0] in (0, W - 1) or c[1] in (0, H - 1))} - GATES
    rule('A', "le bord de la carte ne s'atteint qu'aux sorties", not bad, '%d cases de bord atteintes' % len(bad), bad)
    border = [c for c in CELLS if c[0] in (0, W - 1) or c[1] in (0, H - 1)]
    wet = {c for c in border if c in SEA}
    rocks = {(x, r) for k, x, r in b['sprites'] if k in ('riverrock', 'spire', 'pebbleA', 'pebbleB', 'rock_s')}
    # L'eau qui touche le bord de la carte ne gêne que si elle baigne une plage où l'on marche : le jour où l'on
    # nagera, on sortirait par là. Une rivière encaissée entre deux falaises ne s'atteint jamais : elle peut filer
    # jusqu'au bord. Les rochers arrêtent l'eau du bord.
    seen, todo = set(), list(wet)
    while todo:
        c = todo.pop()
        if c in seen or c not in SEA or c in rocks: continue
        seen.add(c); todo += [(c[0] + i, c[1] + j) for i, j in NEIGH4]
    bathed = {c for c in seen if any((c[0] + i, c[1] + j) in REACH for i in (-2, -1, 0, 1, 2) for j in (-2, -1, 0, 1, 2))}
    passes = pieces(wet, NEIGH8)
    wide = [p for p in passes if len(p) > 7 and p & {q for c in bathed for q in [c]} or (len(p) > 7 and bathed and any(c in seen for c in p))]
    if Y['open_sea']:          # une plage, une ville côtière : le bord de la carte est la limite de la mer
        rule('A', 'la mer touche le bord largement : %d %% du pourtour au moins' % round(Y['sea'] * 100), len(wet) >= len(border) * Y['sea'], '%d cases de bord dans l eau sur %d' % (len(wet), len(border)))
    else:
        rule('A', 'la mer qui baigne une plage ne touche le bord qu à des passes étroites (4 à 7 cases)', not wide if wet and bathed else (True if wet else None),
             '%d cases de bord dans l eau, en %d morceaux dont %d trop larges' % (len(wet), len(passes), len(wide)), [min(p) for p in wide])
        rule('F', 'chaque passe est barrée de rochers : l eau du bord ne baigne aucune plage où l on marche', not bathed if wet else None, '%d cases d eau du bord au contact d une plage praticable' % len(bathed), bathed)
    land_border = [c for c in border if c not in SEA and c not in lanes]
    def depth(c):          # combien de cases pleines de suite, du bord vers le dedans
        dx, dy = (1, 0) if c[0] == 0 else (-1, 0) if c[0] == W - 1 else (0, 1) if c[1] == 0 else (0, -1)
        n, q = 0, c
        while inb(q) and q in SOLID and n < BELT + 6: n += 1; q = (q[0] + dx, q[1] + dy)
        return n
    def doubled(c):          # une falaise ou de l'eau juste derrière : deux arbres suffisent
        dx, dy = (1, 0) if c[0] == 0 else (-1, 0) if c[0] == W - 1 else (0, 1) if c[1] == 0 else (0, -1)
        return any((c[0] + dx * k, c[1] + dy * k) in RING or (c[0] + dx * k, c[1] + dy * k) in SEA or (c[0] + dx * k, c[1] + dy * k) in b['ROCK'] for k in range(1, BELT + 3))
    belt = Y['belt'] or BELT
    shallow = [c for c in land_border if depth(c) < (4 if doubled(c) else belt)]
    rule('A', 'la ceinture de forêt fait au moins %s arbres d épaisseur' % {6: 'trois', 8: 'quatre'}.get(belt, belt // 2), len(shallow) <= len(land_border) * 0.15 if land_border and Y['belt'] else None,
         '%d cases de bord sur %d ont moins de %d cases pleines derrière elles' % (len(shallow), len(land_border), belt), shallow)
    gates = pieces(GATES, NEIGH8)
    bad = [g for g in gates if not 2 <= len(g) <= 4]
    rule('A', 'une sortie est une trouée de 2 à 4 cases', not bad if gates else None, '%d sorties, larges de %s' % (len(gates), sorted(len(g) for g in gates)), [min(g) for g in bad])
    bad = [g for g in gates if not (g & TRAIL or {(c[0] + i, c[1] + j) for c in g for i, j in NEIGH4} & TRAIL)]
    rule('A', 'un chemin traverse chaque sortie', not bad if gates and Y['paths'] else None, '%d sorties sans chemin' % len(bad), [min(g) for g in bad])

    # ---------------------------------------------------------------- B. taille et agencement
    lo, hi = Y['size']
    rule('B', 'la taille convient : %s de %d à %d cases de côté' % (Y['name'], lo, hi), lo <= min(W, H) and max(W, H) <= hi, '%d × %d' % (W, H))
    centre = (W // 2, H // 2)
    rule('B', 'aucun bâtiment au centre exact de la carte', centre not in b['house_area'] if doors else None, 'centre %s' % (centre,))
    bad = [d for d in doors.values() if not ({(d[0], d[1] + 1), (d[0], d[1] + 2)} & (TRAIL | b['PAVED']))]
    rule('B', 'chaque porte donne sur un chemin ou une placette', not bad if doors else None, '%d portes sans chemin devant elles' % len(bad), bad)
    bare = (REACH & INSIDE) - TRAIL - TALL - flowers - b['flower_cells'] - props - b['PAVED'] - set(b['stairs']) - margin - b['MOUNTAIN'] - b['EARTH']          # (une plaque de terre nue est une respiration voulue ; une terrasse où l'on monte est une pelouse comme une autre ; le dessus d'une butte ne s'atteint pas)
    squares = [(x, y) for x, y in bare if all((x + i, y + j) in bare for i in range(BARE) for j in range(BARE))]
    voids = pieces({(x + i, y + j) for x, y in squares for i in range(BARE) for j in range(BARE)})
    rule('B', 'aucune pelouse nue de plus de 4 × 4 (une respiration permise)', len(voids) <= 1 if Y.get('bare', True) else None, '%d étendues nues, la plus grande de %d cases' % (len(voids), max([len(v) for v in voids] or [0])), [min(v) for v in voids])
    if Y['sand']:          # sur une plage, le sable garni tient plus large que la pelouse — mais pas nu
        strand = BEACH - RING
        rule('B', 'le sable est le sol : un dixième de la carte au moins', len(strand) >= W * H * 0.10, '%d cases de sable sur %d : %.0f %%' % (len(strand), W * H, 100.0 * len(strand) / (W * H)))
        rule('B', 'on marche sur la plage : la moitié du sable au moins s atteint', len(strand & REACH) >= len(strand) * 0.5 if strand else False, '%d cases de sable atteintes sur %d' % (len(strand & REACH), len(strand)))
        n = Y['sand'] + 1
        dry = (REACH & BEACH) - RING - low - props - TALL - set(b['stairs'])
        squares = [(x, y) for x, y in dry if all((x + i, y + j) in dry for i in range(n) for j in range(n))]
        rule('B', 'aucun sable nu de plus de %d × %d : un rocher, un coquillage, des herbes' % (Y['sand'], Y['sand']), not squares if REACH & BEACH else None, '%d carrés de sable nu' % len(squares), squares)

    # ---------------------------------------------------------------- C. lignes droites
    inner = {c for c in CELLS if min(c[0], c[1], W - 1 - c[0], H - 1 - c[1]) >= 2}
    edges = collections.defaultdict(set)
    for c, k in b['ring_shape'].items():
        if k in '2468' and c in inner: edges[k].add(c)
    long_ = [(n, c) for k in edges for n, c, d in runs(edges[k]) if n > STRAIGHT and ((d[0] == 1) == (k in '28'))]
    near_work = {(c[0] + i, c[1] + j) for c in set(b['stairs']) | b['DECK'] for i in range(-3, 4) for j in range(-3, 4)}
    long_ = [(n, c) for n, c in long_ if c not in near_work]
    rule('C', 'jamais plus de %d cases en ligne droite pour un bord de plateau' % STRAIGHT, not long_ if RING else None, '%d bords trop droits, le plus long de %d cases' % (len(long_), max([n for n, _ in long_] or [0])), [c for _, c in long_])

    # ---------------------------------------------------------------- D. relief
    tier = b['tier']          # le niveau de chaque case en terrasse ; un relief par morceau de chaque niveau
    relief = sum(len(pieces({c for c, k in tier.items() if k >= n})) for n in range(1, max(tier.values(), default=0) + 1)) + len(pieces(b['MOUNTAIN'])) + max(0, len([p for p in pieces(b['PLATEAU']) if len(p) >= 12]) - 1)
    rule('D', 'du relief : au moins %d plateaux, terrasses, buttes ou massifs' % Y['relief'], relief >= Y['relief'] if Y['relief'] else None, '%d reliefs' % relief)
    bad = {(x, r) for k, x, r in b['sprites'] if (x, r) in TRAIL}
    rule('D', 'rien ne se pose sur une piste', not bad, '%d choses sur une piste' % len(bad), bad)
    bad = {(x, r) for k, x, r in b['sprites'] if k.startswith('tree') and any((x + i, r) in RING for i in range(3)) and any((x + i, r) in INSIDE for i in range(3))}
    rule('D', "rien à cheval sur un bord de plateau", len(bad) <= len(trees) * 0.03 if trees else None, '%d arbres à cheval sur un bord' % len(bad), bad)
    high = b['high']          # une butte : l'arbre qui y pousse y tient tout entier, cime comprise ; celui d'en bas n'y pose pas un pied
    bad = set()
    for _, x, r in trees:
        feet = {(x + i, r - j) for i in range(3) for j in (0, 1)}
        if len({tier.get(c, 0) for c in feet | {(x + i, r - 2) for i in range(3)} if inb(c)}) > 1: bad.add((x, r))          # (ce qui dépasse de la carte tient à la carte voisine)
    rule('D', 'un arbre tient tout entier sur sa butte ou sa terrasse, cime comprise', not bad if high and trees else None, '%d arbres qui dépassent d une butte' % len(bad), bad)

    # ---------------------------------------------------------------- E. arbres
    groves = pieces({(x, r) for _, x, r in trees}, [(i, j) for i in range(-4, 5) for j in range(-3, 4) if (i, j) != (0, 0)])
    small_top = set()          # le dessus d'une butte — une terrasse de moins de 80 cases — est une place d'arbre à lui seul
    for n in range(1, max(tier.values(), default=0) + 1):
        for top in pieces({c for c, k in tier.items() if k >= n}):
            if len(top) < 80: small_top |= top
    groves = [g for g in groves if not any((x, r) in small_top for x, r in g)]
    ends = {(c[0] + i, c[1] + j) for c in b['ledges'] for i, j in NEIGH4}          # (deux arbres qui tiennent le bout d'un rebord servent à quelque chose : ce n'est pas un semis)
    groves = [g for g in groves if not any((x + i, r - j) in ends for x, r in g for i in range(3) for j in (0, 1))]
    lone = [g for g in groves if len(g) == 1]
    small = [g for g in groves if 2 <= len(g) <= 3]
    rule('E', 'les arbres bordent ou font des bosquets de 4 arbres au moins (un ou deux isolés permis)', len(lone) <= 2 and len(small) <= 1 if trees else None,
         '%d bosquets, dont %d arbres seuls et %d de deux ou trois' % (len(groves), len(lone), len(small)), [min(g) for g in lone + small])
    firs = {(x, r) for k, x, r in b['sprites'] if k in ('conif', 'sapling')}          # les petits sapins décorent : ils ne font ni pile ni rang, et restent rares
    stacks = [p for p in pieces(firs) if len(p) > 2]
    rule('E', 'les petits sapins sont un décor : jamais empilés ni en rang, un pour quatre gros arbres au plus', not stacks and len(firs) * 4 <= max(8, len(trees)) if firs else None,
         '%d petits sapins pour %d arbres, %d piles ou rangs' % (len(firs), len(trees), len(stacks)), [min(p) for p in stacks])
    palms = [(x, r) for k, x, r in b['sprites'] if k.startswith('palm')]
    close = [p for i, p in enumerate(palms) for q in palms[i + 1:] if abs(p[0] - q[0]) + abs(p[1] - q[1]) < Y['palms']]
    rule('E', 'les palmiers sont à %d cases au moins les uns des autres' % Y['palms'], not close if palms else None, '%d palmiers, %d trop proches' % (len(palms), len(close)), close)
    fronts = {(d[0] + i, d[1] + j) for d in doors.values() for i in (-1, 0, 1) for j in (1, 2)}
    bad = tree_cells & fronts
    rule('E', 'aucun arbre devant une porte', not bad if doors else None, '%d cases d arbre devant une porte' % len(bad), bad)

    # ---------------------------------------------------------------- G. raccords
    shores = {c for p in pieces(BEACH - RING) if len(p) >= 6 for c in p}          # (quelques cases de sable au creux d'une falaise : c'est son liseré, pas une plage)
    bad = thin(shores)
    rule('G', 'une plage fait au moins deux cases de large', len(bad) <= len(BEACH) * 0.08 if BEACH else None, '%d cases de plage larges d une seule case, sur %d' % (len(bad), len(BEACH)), bad)
    bad = thin(TRAIL)
    rule('G', "aucun chemin d'une seule case de large", not bad if TRAIL else None, '%d cases de chemin trop étroites' % len(bad), bad)

    # ---------------------------------------------------------------- M. hautes herbes
    patches = pieces(TALL)
    def box(p): return (max(c[0] for c in p) - min(c[0] for c in p) + 1) * (max(c[1] for c in p) - min(c[1] for c in p) + 1)
    if Y['tall'] is None:          # en forêt profonde, les hautes herbes sont le sol : on mesure leur part, pas leurs plaques
        floor = REACH & INSIDE
        rule('M', 'les hautes herbes sont le sol : la moitié au moins de ce qu on foule', len(TALL & floor) >= len(floor) * 0.5 if floor else None, '%d cases d herbes sur %d praticables' % (len(TALL & floor), len(floor)))
    else:
        top = max(48, Y['tall'][1])
        odd = [p for p in patches if len(p) < 3 or len(p) > top]          # (les fourchettes sont des repères : la Route 1 a une plaque de 8 et une de 48)
        big = [p for p in patches if len(p) > top]
        rule('M', 'les hautes herbes vont par plaques de %d à %d cases (touffes de 3 à 6 permises, une grande étendue au plus)' % Y['tall'], len(odd) - min(1, len(big)) <= 1 if patches else None,
             '%d plaques, de %s cases' % (len(patches), sorted(len(p) for p in patches)), [min(p) for p in odd])
        full = [p for p in patches if len(p) >= 10 and len(p) == box(p)]
        rule('M', 'jamais un rectangle plein : un contour déchiqueté, des trous', not full if patches else None, '%d plaques en rectangle plein' % len(full), [min(p) for p in full])
    obstacles = tree_cells | RING | SEA | b['POND'] | b['MOUNTAIN'] | b['ROCK'] | {c for c in SOLID if c in INSIDE}
    alone = [p for p in patches if len(p) > 6 and not any((c[0] + i, c[1] + j) in obstacles for c in p for i in range(-2, 3) for j in range(-2, 3))]
    rule('M', 'chaque plaque est adossée à un bosquet, une eau ou une falaise', not alone if patches else None, '%d plaques seules au milieu d un espace ouvert' % len(alone), [min(p) for p in alone])
    if kind in ('route', 'seaside', 'mountain'):          # sur une route, on traverse des herbes : assez pour qu'elles comptent, pas au point de tout couvrir (Johto : un cinquième à un quart)
        floor = REACH & INSIDE
        share = 100.0 * len(TALL & floor) / max(1, len(floor))
        rule('M', 'sur une route, les hautes herbes font 8 à 35 % de ce qu on foule', 8 <= share <= 35 if not b['literal'] else None, '%.0f %% (%d cases sur %d)' % (share, len(TALL & floor), len(floor)))
    bad = {c for c in TALL if any(abs(c[0] - d[0]) + abs(c[1] - d[1]) <= 5 for d in doors.values())}
    rule('M', 'aucune haute herbe au pied d une maison', not bad if doors and TALL else None, '%d cases à moins de six cases d une porte' % len(bad), bad)

    # ---------------------------------------------------------------- N. chemins
    side = {c for c in TRAIL if any((c[0] + i, c[1] + j) not in TRAIL for i, j in NEIGH4)}
    v = {c for c in side if (c[0] - 1, c[1]) not in TRAIL or (c[0] + 1, c[1]) not in TRAIL}
    h = {c for c in side if (c[0], c[1] - 1) not in TRAIL or (c[0], c[1] + 1) not in TRAIL}
    stiff = [(n, c) for n, c, d in runs(v) if d == (0, 1) and n > 8] + [(n, c) for n, c, d in runs(h) if d == (1, 0) and n > 8]
    near_built = {(c[0] + i, c[1] + j) for c in b['GARDEN'] for i in range(-3, 4) for j in range(-3, 4)}          # le long d'une clôture, un chemin file droit : le construit est droit
    stiff = [(n, c) for n, c in stiff if c not in lanes and c not in near_work and c not in near_built]
    rule('N', 'des bords de chemin ondulés : pas plus de 8 cases sans décrochement', len(stiff) <= 2 if TRAIL else None, '%d bords raides, le plus long de %d cases' % (len(stiff), max([n for n, _ in stiff] or [0])), [c for _, c in stiff])
    goals = fronts | GATES | {(c[0] + i, c[1] + j) for c in set(b['stairs']) | b['DECK'] for i, j in NEIGH8}
    trail_pieces = pieces(TRAIL)
    def dotted(p):          # un chemin en pointillés : un tronçon à une douzaine de cases d'un autre au plus (la place d'une barre de hautes herbes)
        return any(q is not p and any(abs(c[0] - d[0]) + abs(c[1] - d[1]) <= 12 for c in list(p)[::3] for d in list(q)[::3]) for q in trail_pieces)
    lost = [p for p in trail_pieces if not {(c[0] + i, c[1] + j) for c in p for i, j in NEIGH8 + [(0, 0)]} & goals and not dotted(p)]
    rule('N', 'un chemin mène quelque part : une porte, un escalier, un pont, une sortie', not lost if TRAIL else None, '%d tronçons qui ne mènent nulle part' % len(lost), [min(p) for p in lost])

    # ---------------------------------------------------------------- O. eau
    open_sea = set()
    todo = [c for c in border if c in SEA]
    while todo:
        c = todo.pop()
        if c in open_sea or c not in SEA: continue
        open_sea.add(c); todo += [(c[0] + i, c[1] + j) for i, j in NEIGH4]
    sunk = [p for p in pieces(SEA - open_sea) if len(p) < 60]          # une petite eau au fond d'une falaise
    ponds = sunk + pieces(b['POND'])
    tiny = [p for p in ponds if len(p) < 12]
    rule('O', 'un étang fait 12 cases au moins', not tiny if ponds else None, '%d étangs, de %s cases' % (len(ponds), sorted(len(p) for p in ponds)), [min(p) for p in tiny])
    rule('O', 'un étang est au niveau de l herbe, avec sa berge — pas au fond d une falaise', not sunk if ponds and not b['literal'] else None, '%d petites eaux encaissées, de %s cases' % (len(sunk), sorted(len(p) for p in sunk)), [min(p) for p in sunk])

    # ---------------------------------------------------------------- P. rebords
    ledges = pieces(set(b['ledges']))
    bad = [l for l in ledges if not 2 <= len(l) <= 10]
    rule('P', 'un rebord est un segment droit de 3 à 10 cases', not bad if ledges else None, '%d rebords' % len(ledges), [min(l) for l in bad])

    # ---------------------------------------------------------------- Q. fleurs
    tufts = pieces(flowers, NEIGH8)
    walk = len(REACH & INSIDE)
    per = walk / len(tufts) if tufts else 0
    lo, hi = Y['flowers'] or (0, 0)
    rule('Q', 'une touffe de fleurs pour %d à %d cases praticables' % (lo, hi), lo <= per <= hi if walk >= 60 and Y['flowers'] else None, '%d touffes pour %d cases : une pour %d' % (len(tufts), walk, per))
    heavy = [t for t in tufts if len(t) > 3]
    single = [t for t in tufts if len(t) == 1]
    rule('Q', 'par touffes de deux ou trois, une seule de temps en temps', not heavy and len(single) <= max(2, len(tufts) * 0.4) if tufts else None,
         '%d touffes : %d d une seule fleur, %d de plus de trois' % (len(tufts), len(single), len(heavy)), [min(t) for t in heavy])
    rows = [c for c in blooms if (c[0] + 1, c[1]) in blooms]
    rule('Q', 'les grandes fleurs ne sont jamais côte à côte en rang (hors massif clôturé)', not [c for c in rows if c not in b['GARDEN'] and c not in {(q[0], q[1]) for q in b['fence']}] if blooms else None, '%d paires côte à côte' % len(rows), rows)
    bad = (flowers | blooms) & TRAIL
    rule('Q', 'jamais de fleur sur un chemin', not bad if flowers | blooms else None, '%d fleurs sur un chemin' % len(bad), bad)

    # ---------------------------------------------------------------- K. objets
    items = [t for t in plan.table('item')]
    rule('K', '%d à %d objets à ramasser dans %s' % (Y['items'] + (Y['name'],)), Y['items'][0] <= len(items) <= Y['items'][1] if not b['literal'] else None, '%d objets' % len(items))
    signs = [plan.at(t['mark'], 'panneau') for t in plan.table('sign') if len(plan.marks.get(t['mark'], [])) == 1]
    bad = [g for g in gates if not any(min(abs(s[0] - c[0]) + abs(s[1] - c[1]) for c in g) <= 10 for s in signs)]
    rule('K', 'un panneau à chaque entrée', not bad if gates and Y.get('signs', True) else None, '%d sorties sans panneau' % len(bad), [min(g) for g in bad])

    veil = set()          # ce qu'un grand dessin couvre au-dessus de son pied : sa cime, ses palmes
    for k, x, r in b['sprites']:
        model = builder.THEME['props'].get(k)
        if not model or model['size'][1] < 3 or not model['feet']: continue
        top = max(-f[1] for f in model['feet'])
        veil |= {(x + i, r - j) for i in range(model['size'][0]) for j in range(top + 1, model['size'][1])}
    things = signs + [plan.at(t['mark'], 'objet') for t in items if len(plan.marks.get(t['mark'], [])) == 1]
    bad = [c for c in things if c in veil]
    rule('K', 'ni panneau ni objet derrière une cime ou une palme', not bad if things else None, '%d cachés' % len(bad), bad)

    # ---------------------------------------------------------------- une route n'est pas un couloir vide
    if kind in ('route', 'seaside', 'mountain') and not b['literal']:
        inner_groves = [g for g in pieces({(x, r) for _, x, r in trees}, [(i, j) for i in range(-4, 5) for j in range(-3, 4) if (i, j) != (0, 0)])
                        if all(min(x, r, W - 1 - x, H - 1 - r) >= BELT + 3 for x, r in g)]
        motifs = {'des hautes herbes en deux plaques au moins': len(patches) >= 2, 'de l eau': bool(SEA or b['POND']), 'du relief': relief >= 1, 'un rebord': bool(b['ledges']),
                  'un bosquet au milieu': bool(inner_groves), 'trois objets': len(items) >= 3, 'une maison': bool(doors), 'un pont ou un escalier': bool(b['DECK'] or b['stairs'])}
        have = [name for name, there in motifs.items() if there]
        rule('B', 'une route a de quoi s y arrêter : quatre motifs au moins sur huit', len(have) >= 4,          # (les routes de Johto en ont de trois à six)
             '%d motifs : %s — il manque : %s' % (len(have), ', '.join(have), ', '.join(n for n in motifs if n not in have)))

    # ---------------------------------------------------------------- une grotte
    if kind == 'cave' and not b['literal']:
        void, wall_ = b['VOID'], b['MOUNTAIN']
        foot = set(CELLS) - void
        floor = foot - wall_
        rim = [c for c in border if c not in void and not any(abs(c[0] - g[0]) + abs(c[1] - g[1]) <= 6 for g in GATES)]          # (la paroi du couloir de sortie va jusqu'au bord avec lui)
        rule('A', 'une grotte est une tache posée sur du noir : le vide touche tout le bord, hors des sorties', not rim, '%d cases de bord qui ne sont pas du vide' % len(rim), rim)
        rule('B', 'le sol fait 35 à 60 % de la tache, le reste est de la roche', 0.35 <= len(floor) / max(1.0, len(foot)) <= 0.60, '%d cases de sol sur %d : %.0f %%' % (len(floor), len(foot), 100.0 * len(floor) / max(1, len(foot))))
        masses = [m for m in pieces(wall_) if not any((c[0] + i, c[1] + j) in void for c in m for i, j in NEIGH4)]
        rule('D', 'des massifs de roche au milieu de la salle : deux au moins, de 12 à 70 cases', len(masses) >= 2 and all(12 <= len(m) <= 70 for m in masses), '%d massifs, de %s cases' % (len(masses), sorted(len(m) for m in masses)))
        narrow = thin(floor - b['POND'])
        rule('N', 'aucun couloir d une seule case de large', len(narrow) <= 2, '%d cases de sol trop étroites' % len(narrow), narrow)
        pools = pieces(b['POND'])
        rule('O', 'un à trois bassins', 1 <= len(pools) <= 3, '%d bassins, de %s cases' % (len(pools), sorted(len(p) for p in pools)))
        stones = len(b['sprites'])
        per_ = len(REACH) / max(1.0, stones)
        rule('F', 'des rochers et des stalagmites le long des parois : un pour 10 à 30 cases de sol', 10 <= per_ <= 30 if stones else False, '%d rochers pour %d cases : un pour %.0f' % (stones, len(REACH), per_))
        alive = len(trees) + len(TALL) + len(flowers) + len(blooms)
        rule('E', 'rien de vivant dans une grotte : ni arbre, ni herbes, ni fleurs', not alive, '%d' % alive)

    # ---------------------------------------------------------------- des champs
    if kind == 'fields' and not b['literal']:
        wheat, plots = b['WHEAT'], pieces(b['GARDEN'])
        rule('B', 'les champs sont la matière de la carte : trois au moins, et le blé couvre 8 % de la carte', len(plots) >= 3 and len(wheat) >= W * H * 0.08, '%d champs, %.0f %% de blé' % (len(plots), 100.0 * len(wheat) / (W * H)))
        rule('R', 'chaque champ est clôturé : pas de blé hors d un enclos', wheat <= b['GARDEN'], '%d cases de blé hors enclos' % len(wheat - b['GARDEN']), wheat - b['GARDEN'])
        alleys = b['EARTH'] - wheat - {plan.marks[t['mark']][0] for t in items if len(plan.marks.get(t['mark'], [])) == 1}          # (un objet posé au fond d'une allée en occupe la case)
        rule('R', 'un champ est un labyrinthe : ses allées s atteignent toutes, et font un cinquième à la moitié du champ', bool(alleys) and alleys <= REACH and 0.2 <= len(alleys) / max(1.0, len(b['EARTH'])) <= 0.5,
             '%d cases d allée sur %d atteintes, %.0f %% du champ' % (len(alleys & REACH), len(alleys), 100.0 * len(alleys) / max(1, len(b['EARTH']))), alleys - REACH)
        hidden_ = [t for t in items if len(plan.marks.get(t['mark'], [])) == 1 and plan.marks[t['mark']][0] in b['GARDEN']]
        rule('K', 'un objet au fond d une allée de blé', bool(hidden_), '%d objets dans les champs' % len(hidden_))
        rule('M', 'pas de hautes herbes dans les champs : le blé en tient lieu', len(TALL) <= 12, '%d cases de hautes herbes' % len(TALL))

    # ---------------------------------------------------------------- un village
    if kind == 'village' and not b['literal']:
        rule('B', 'un village a quatre maisons au moins', len(doors) >= 4, '%d maisons' % len(doors))
        lamps = len(plan.table('lamp'))
        rule('K', 'quatre à huit lampadaires dans un village, aux entrées et aux coins de la place', 4 <= lamps <= 8, '%d lampadaires' % lamps)
        net = pieces(TRAIL | b['PAVED'])
        rule('N', 'le réseau de chemins est d un seul tenant et relie chaque porte', len(net) == 1 and all({(d[0], d[1] + 1), (d[0], d[1] + 2)} & net[0] for d in doors.values()) if net else False,
             '%d morceaux de chemin' % len(net), [min(n_) for n_ in net[1:]])
        centre_ = {c for c in CELLS if abs(c[0] - W // 2) <= W // 5 and abs(c[1] - H // 2) <= H // 5}
        rule('M', 'aucune haute herbe au centre d un village', not TALL & centre_, '%d cases d herbes au centre' % len(TALL & centre_), TALL & centre_)

    # ---------------------------------------------------------------- une forêt profonde
    if kind == 'forest' and not b['literal']:
        wooded = {c for c in tree_cells if inb(c)}
        rule('E', 'en forêt profonde, les arbres sont les murs : la moitié de la carte au moins', len(wooded) >= W * H * 0.5, '%.0f %% de la carte sous les arbres' % (100.0 * len(wooded) / (W * H)))
        rule('N', 'une forêt profonde n a pas de chemin', not TRAIL, '%d cases de chemin' % len(TRAIL))
        earths = pieces(b['EARTH'])
        rule('N', 'ce qui guide, ce sont des plaques de terre nue : trois au moins, de 4 à 30 cases', len(earths) >= 3 and all(4 <= len(e) <= 30 for e in earths), '%d plaques, de %s cases' % (len(earths), sorted(len(e) for e in earths)))

    # ---------------------------------------------------------------- le constructeur, lui, ne signale rien
    import re
    def minor(line):          # une clairière de quelques cases qu'on n'atteint pas, au fond d'un bois : ce n'est pas une faute
        m = re.match(r'(\d+) cases libres hors d atteinte', line)
        return bool(m) and int(m.group(1)) < 40
    serious = [line for line in b['warn'] if not minor(line)]
    rule('—', 'la carte s assemble sans avertissement du constructeur', not serious, '%d avertissements : %s' % (len(serious), ' ; '.join(l[:90] for l in serious[:2])))
    return out, b


BLOCKING = ('n est pas atteinte', 'hors d atteinte', 'on ne peut pas s en approcher', 'on ne passe pas', 'la case est pleine', 'est prise ou hors', 'le bord de la carte s atteint')


def blocking(built):
    """Ce qui empêche de jouer la carte, quel que soit son taux : une sortie, une porte, un objet qu'on n'atteint pas, un
    escalier qu'on ne franchit pas, un bord de carte ouvert. (Une clairière perdue au fond d'un bois n'en est pas.)"""
    if built['literal']: return []          # un plan littéral ne dit pas d'où l'on part
    return [line for line in built['warn'] if any(k in line for k in BLOCKING) and 'cases libres hors d atteinte' not in line]


def rate(results):
    done = [r for r in results if r[2] is not None]
    return 100.0 * sum(1 for r in done if r[2]) / len(done) if done else 0.0


if __name__ == '__main__':
    paths = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not paths: sys.exit(__doc__)
    worst = 100.0
    for path in paths:
        results, built = check(builder.Plan(path))
        score = rate(results); worst = min(worst, score)
        done = [r for r in results if r[2] is not None]
        stuck = blocking(built)
        if stuck: worst = 0.0
        print('%-22s %-8s %3.0f %%   %d règles respectées sur %d (%d ne s appliquent pas)%s' % (os.path.basename(path)[:-5], built['style'], score, sum(1 for r in done if r[2]), len(done), len(results) - len(done),
                                                                                      '   INJOUABLE : %d blocages' % len(stuck) if stuck else ''))
        if len(paths) == 1 or '--detail' in sys.argv:
            for section, text, ok, measure, cells in results:
                if ok is None: continue
                print('   %s %s  %s%s' % ('ok ' if ok else '!! ', section, text, '' if ok else '  — %s%s' % (measure, ('  ex. %s' % cells) if cells else '')))
            for line in built['warn']: print('      constructeur : ' + line)
    sys.exit(0 if worst >= 85.0 else 1)
