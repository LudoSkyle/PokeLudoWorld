# Plan de l'île : terrains, relief, pontons. Tout est en cases.
#
# Le plan est dessiné dans un cadre de 66 x 50 cases (les coordonnées « de dessin »). Pour
# tenir la taille d'une petite carte, on en retire quelques colonnes et rangées — là où il
# n'y a que de la lisière, de la pelouse ou de l'eau —, puis on l'entoure d'une case de marge
# qui prolonge le bord. P() et R() traduisent une case ou un rectangle de dessin en cases
# de la carte finale.
import math

SEA, SAND, GRASS = '~', '.', 'g'
def noise(x, y): return math.sin(x * 0.7 + 1.3) * math.cos(y * 0.9 + 0.4) + 0.5 * math.sin((x + y) * 0.45)

DW, DH = 66, 50
DROP_X = {2, 7, 22, 43, 58, 63}
DROP_Y = {16, 19, 46}
KX = [x for x in range(DW) if x not in DROP_X]
KY = [y for y in range(DH) if y not in DROP_Y]
OX, OY = 1, 1
W, H = len(KX) + 2 * OX, len(KY) + OY + 1
PAD_X, PAD_Y = 6, 5                      # la marge boisée : 6 cases à gauche et à droite, 5 en bas
def inb(x, y): return 0 <= x < W and 0 <= y < H
def in_padding(x, y): return x < PAD_X or x >= W - PAD_X or y >= H - PAD_Y
def in_hard(x, y): return x < PAD_X - 2 or x >= W - (PAD_X - 2) or y >= H - (PAD_Y - 2)   # là où le joueur ne va jamais
def _lo(v, kept): return next(i for i, k in enumerate(kept) if k >= v)      # première case gardée à partir de v
def _hi(v, kept): return max(i for i, k in enumerate(kept) if k <= v)       # dernière case gardée jusqu'à v
def PX(x): return _lo(x, KX) + OX
def PY(y): return _lo(y, KY) + OY
def P(x, y): return (PX(x), PY(y))
def R(x0, y0, x1, y1): return (_lo(x0, KX) + OX, _lo(y0, KY) + OY, _hi(x1, KX) + OX, _hi(y1, KY) + OY)

# --- relief : des plateaux d'herbe à falaise basse. Chacun est une réunion de rectangles,
# rognée ensuite là où la mer est trop proche et aux cases de NIBBLES (pour casser les
# angles droits). Du relief partout, y compris sous la place. ---
PLATEAUS_D = [
    [(6, 3, 19, 11), (19, 3, 26, 6)],          # 0 nord-ouest : Ludo, la maison orange — adossé à la falaise ; il s'allonge vers l'est sous les arbres du pied du mur
    [(45, 3, 60, 13)],                         # 1 nord-est, premier étage : la terrasse du laboratoire, adossée à la falaise
    [(46, 33, 57, 41), (52, 32, 56, 34)],      # 2 sud-est : la grande maison orange
    [(25, 20, 39, 30)],                        # 3 le centre : la place
    [(5, 25, 13, 31)],                         # 4 ouest : la bibliothèque
    [(15, 40, 21, 45)],                        # 5 une butte boisée, au sud-ouest
    [],                                        # 6 (retiré : le cap du nord-est est pris par la terrasse du labo)
    [(0, 11, 4, 15)],                          # 7 une butte boisée, dans la lisière de l'ouest
    [(47, 3, 58, 10)],                         # 8 nord-est, second étage : le laboratoire, un étage plus haut, contre le mur
]
PLATEAUS = [[R(*r) for r in rects] for rects in PLATEAUS_D]
NIBBLES = [P(*c) for c in [(6, 11), (46, 33), (57, 41), (56, 32), (25, 30), (39, 30), (39, 29), (5, 25), (13, 25), (5, 31),
                           (15, 40), (21, 45), (21, 44), (4, 11), (0, 15), (60, 13), (45, 13)]]
# escaliers : (plateau, côté, première des deux voies). Des planches posées sur le bord du
# plateau — en bas, mais aussi sur les côtés et en haut. La position exacte du bord est
# trouvée par le générateur.
STAIRS = [(0, 'B', PX(9)), (1, 'B', PX(51)), (8, 'B', PX(51)), (2, 'B', PX(51)),
          (3, 'B', PX(32)), (3, 'L', PY(24)), (3, 'R', PY(24)),      # la place : par l'ouest, l'est et le sud — pas par le nord
          (4, 'B', PX(8)), (4, 'R', PY(27))]

# --- pontons : des bandes de deux cases de large. Chaque rectangle dépasse sur la terre aux
# deux bouts : seules ses cases d'eau deviennent ponton. ---
DECKS_D = [(11, 15, 12, 22), (11, 21, 30, 22), (53, 15, 54, 22), (36, 21, 54, 22), (12, 27, 28, 28), (32, 40, 33, 44)]
DECKS = [R(*d) for d in DECKS_D]

# --- falaise haute du nord : rangées 0..3, sauf la trouée de la route ---
CLIFF_ROWS = 4
# Le mur tient dans ces quatre rangées (la carte ne grandit pas) : sa hauteur vient de gradins posés les uns
# sur les autres — voir gen.py.
ROCK = [(0, PX(29)), (PX(36), W - 1)]
# sentiers de sable sur l'herbe (rectangles)
TRAILS = []          # plus de sentier de sable au pied des escaliers : de l'herbe (Ludovic, 15/11/2026)
# pelouses : la place et son tour restent en herbe (le dallage a une frange d'herbe)
LAWNS = [R(26, 21, 38, 29)]
# embouchures : la ligne que suit la chaîne de rochers. ('v', colonne, y0, y1) ou ('h', rangée, x0, x1)
BARRIERS = [('v', PX(4), PY(18), PY(22)), ('v', PX(4), PY(34), PY(37)), ('v', PX(61), PY(22), PY(27)), ('h', PY(48), PX(30), PX(36))]


# --- le mobilier, en cases de la carte : (sorte, nom, arguments). Revu à la main sur chaque version. ---
FURNITURE = [
    ('bench', 'BenchSquare', (32, 19)),           # au fond de la place, face à la cloche
    ('bench', 'BenchCove', (33, 7)),              # dans la crique, face à la baie, au bord de la route du nord
    ('bench', 'BenchLudo', (10, 13)),             # au pied du plateau de Ludo, le long du sentier
    ('bench', 'BenchLab', (52, 12)),              # sur la terrasse du labo, entre les deux escaliers
    ('bench', 'BenchOrange', (44, 41)),           # au pied du plateau du sud-est
    ('parasol', 'ParasolCove', (22, 9, 1)), ('towel', 'TowelCove', (24, 9, 1)),       # la plage de la crique
    ('parasol', 'ParasolSouth', (37, 37, 0)), ('towel', 'TowelSouth', (39, 37, 0)),   # la plage du sud
]
# --- les objets à ramasser : nom -> case ---
ITEMS = {'ItemPotion': (55, 32), 'ItemBall': (5, 40)}      # au fond du recoin de la pointe de l'est ; au bord des hautes herbes
# --- hautes herbes en plus des deux premières (rectangles, en cases de la carte) ---
TALL_MORE = [(26, 6, 28, 7)]                                 # une touffe au bord de la route du nord


# --- les Pokémon qui volent au-dessus de la carte : nom -> (espèce, zone de 10 × 10 cases : x, y, largeur, hauteur) ---
FLYERS = {
    'WingullBayWest': ('wingull', (19, 9, 10, 10)),      # la baie, côté ouest
    'WingullBayEast': ('wingull', (31, 8, 10, 10)),      # la baie, côté est
    'WingullWest': ('wingull', (13, 28, 10, 10)),        # le bras de mer de l'ouest
    'WingullSouth': ('wingull', (26, 36, 10, 10)),       # la plage du sud et la jetée
    'PelipperEast': ('pelipper', (44, 19, 10, 10)),      # la mer de l'est
    'PelipperStrait': ('pelipper', (1, 16, 10, 10)),     # la passe du nord-ouest
}


def distances_of(t):
    dist = [[99] * W for _ in range(H)]
    cur = [(x, y) for y in range(H) for x in range(W) if t[y][x] == SEA]
    for (x, y) in cur: dist[y][x] = 0
    d = 0
    while cur:
        d += 1; nxt = []
        for (x, y) in cur:
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    X, Y = x + i, y + j
                    if inb(X, Y) and dist[Y][X] > d: dist[Y][X] = d; nxt.append((X, Y))
        cur = nxt
    return dist


def build():
    t = [[SEA] * DW for _ in range(DH)]
    def rrect(x0, y0, x1, y1, r=2, v=GRASS):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                dx = max(x0 + r - x, x - (x1 - r), 0); dy = max(y0 + r - y, y - (y1 - r), 0)
                if dx * dx + dy * dy <= r * r + 0.5 and 0 <= x < DW and 0 <= y < DH: t[y][x] = v
    def ell(cx, cy, rx, ry, v=GRASS):
        for y in range(DH):
            for x in range(DW):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0: t[y][x] = v
    rrect(0, 0, 65, 6, 0)                                    # bande nord, sous la falaise
    rrect(-4, 3, 22, 17, 3); ell(13, 17.3, 6.5, 2.2)         # nord-ouest
    rrect(43, 3, 69, 17, 3); ell(52, 17.3, 6.5, 2.2)         # nord-est
    rrect(58, 14, 69, 21, 3)                                 # cap du nord-est
    ell(32.5, 6.0, 10.5, 4.8)                                # la crique du nord : la plage où débouche la trouée. Elle ne touche pas l'île du centre.
    ell(32.5, 25.5, 11.6, 8.8)                               # île centrale
    rrect(-4, 23, 15, 33, 3)                                 # ouest
    rrect(-4, 38, 23, 53, 3); ell(19, 40, 4, 2.5)            # sud-ouest
    rrect(44, 31, 69, 53, 4); ell(49, 31.5, 5, 2.4); rrect(53, 28, 69, 34, 3)   # sud-est
    rrect(-4, 44, 29, 53, 1); rrect(37, 45, 69, 53, 1)       # deux avancées resserrent la passe du sud
    rrect(27, 31, 38, 42, 3, SAND)                           # plage du sud
    rrect(22, 39, 29, 43, 2, SAND); rrect(37, 36, 44, 41, 2, SAND)   # langues de sable

    # rien de droit : on fait onduler toutes les côtes, d'une case, sur une période de sept ou huit
    t0 = t
    def wob(v, k): return int(round(math.sin(v * k[0] + k[1]) + 0.35 * math.sin(v * k[2] + k[3])))
    t = [[t0[min(max(y + wob(x, (0.83, 0.4, 0.37, 1.9)), 0), DH - 1)][min(max(x + wob(y, (0.91, 1.3, 0.41, 0.2)), 0), DW - 1)] for x in range(DW)] for y in range(DH)]
    for y in range(0, 7):
        for x in range(DW): t[y][x] = t0[y][x]            # la bande nord garde sa falaise droite
    # ...sauf autour des pontons : là, la côte garde son tracé, pour qu'un ponton ne touche la
    # terre que par ses deux bouts, jamais par le flanc
    for (x0, y0, x1, y1) in DECKS_D:
        for y in range(max(y0 - 2, 0), min(y1 + 3, DH)):
            for x in range(max(x0 - 2, 0), min(x1 + 3, DW)): t[y][x] = t0[y][x]
    # ...et autour de la passe du sud : ses deux berges tombent droit, pour qu'un seul rocher
    # suffise à fermer chacune
    for y in range(43, DH):
        for x in range(22, 47): t[y][x] = t0[y][x]
    # un ponton est large de deux cases d'un bout à l'autre : là où la côte n'en laisse qu'une
    # à l'eau, on comble l'autre
    for (x0, y0, x1, y1) in DECKS_D:
        vertical = (x1 - x0) == 1
        for k in range(y0, y1 + 1) if vertical else range(x0, x1 + 1):
            pair = [(x0, k), (x1, k)] if vertical else [(k, y0), (k, y1)]
            kinds = [t[c[1]][c[0]] for c in pair]
            if SEA in kinds and kinds[0] != kinds[1]:
                for c in pair: t[c[1]][c[0]] = GRASS

    # on retire les colonnes et rangées en trop, et on pose le tout au milieu de la carte :
    # la case de marge prolonge le bord
    t = [[t[KY[min(max(y - OY, 0), len(KY) - 1)]][KX[min(max(x - OX, 0), len(KX) - 1)]] for x in range(W)] for y in range(H)]

    # plages : toute terre à moins de trois cases de l'eau. Deux cases au moins, pour
    # que la tuile de rivage (au contact de l'eau) ne touche jamais l'herbe.
    dist = distances_of(t)
    for y in range(H):
        for x in range(W):
            if t[y][x] == GRASS and (dist[y][x] <= 2 or (dist[y][x] == 3 and noise(x, y) > 0.55 and not in_padding(x, y))): t[y][x] = SAND
    for (x0, y0, x1, y1) in LAWNS:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if t[y][x] == SAND and dist[y][x] >= 3: t[y][x] = GRASS
    for (x0, y0, x1, y1) in TRAILS:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if t[y][x] == GRASS: t[y][x] = SAND
    t = clean(t)
    for _ in range(8):
        if not square_decks(t): break
        t = clean(t)
    # dans la marge, la plage ne fait que ses deux cases : la lisière descend jusqu'à elle
    dist = distances_of(t)
    for y in range(H):
        for x in range(W):
            if in_padding(x, y) and t[y][x] == SAND and dist[y][x] >= 3: t[y][x] = GRASS
    t = clean(t)
    return t, distances_of(t)


def square_decks(t):
    """Un ponton ne touche la terre que par ses bouts. Là où la rive longe son flanc, ou ne
    laisse à l'eau qu'une de ses deux voies, on comble : la rive vient à sa rencontre."""
    changed = False
    for di, (x0, y0, x1, y1) in enumerate(DECKS):
        vertical = (x1 - x0) == 1
        others = [d for j, d in enumerate(DECKS) if j != di]
        def other(c): return any(a <= c[0] <= b and u <= c[1] <= v for (a, u, b, v) in others)
        for k in (range(y0, y1 + 1) if vertical else range(x0, x1 + 1)):
            pair = [(x0, k), (x1, k)] if vertical else [(k, y0), (k, y1)]
            kinds = [t[c[1]][c[0]] for c in pair]
            if SEA not in kinds or any(other(c) for c in pair): continue
            flank = [(x0 - 1, k), (x1 + 1, k)] if vertical else [(k, y0 - 1), (k, y1 + 1)]
            if kinds[0] != kinds[1] or any(inb(*f) and t[f[1]][f[0]] != SEA and not other(f) for f in flank):
                for c in pair: t[c[1]][c[0]] = SAND
                changed = True
    return changed


def clean(t):
    """Retire ce que les raccords ne savent pas dessiner : une matière d'une seule case de large."""
    for _ in range(40):
        changed = False
        for y in range(H):
            for x in range(W):
                v = t[y][x]
                def at(i, j): return t[y + j][x + i] if inb(x + i, y + j) else v
                if v == SEA:
                    if (at(-1, 0) != SEA and at(1, 0) != SEA) or (at(0, -1) != SEA and at(0, 1) != SEA): t[y][x] = SAND; changed = True
                elif v == SAND:
                    if (at(-1, 0) == GRASS and at(1, 0) == GRASS) or (at(0, -1) == GRASS and at(0, 1) == GRASS): t[y][x] = GRASS; changed = True
                    # une langue de sable d'une case entre deux eaux : la mer la reprend
                    elif (at(-1, 0) == SEA and at(1, 0) == SEA) or (at(0, -1) == SEA and at(0, 1) == SEA): t[y][x] = SEA; changed = True; continue
                    # deux eaux en diagonale autour d'une case de sable : on comble
                    elif SEA not in (at(-1, 0), at(1, 0), at(0, -1), at(0, 1)):
                        diag = [(i, j) for i in (-1, 1) for j in (-1, 1) if at(i, j) == SEA]
                        if len(diag) >= 2:
                            for (i, j) in diag[1:]:
                                if inb(x + i, y + j): t[y + j][x + i] = SAND; changed = True
                    # une case de plage ne touche pas à la fois l'eau et l'herbe
                    near = [at(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1)]
                    if t[y][x] == SAND and SEA in near and GRASS in near:
                        for i in (-1, 0, 1):
                            for j in (-1, 0, 1):
                                if inb(x + i, y + j) and t[y + j][x + i] == GRASS: t[y + j][x + i] = SAND; changed = True
                elif v == GRASS:
                    if (at(-1, 0) != GRASS and at(1, 0) != GRASS) or (at(0, -1) != GRASS and at(0, 1) != GRASS): t[y][x] = SAND; changed = True
        if not changed: break
    return t


if __name__ == '__main__':
    t, dist = build()
    show = [row[:] for row in t]
    for (x0, y0, x1, y1) in DECKS:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if t[y][x] == SEA: show[y][x] = '='
    for rects in PLATEAUS:
        for (x0, y0, x1, y1) in rects:
            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    if (x, y) not in NIBBLES and t[y][x] != SEA and dist[y][x] >= 2 and show[y][x] != '=': show[y][x] = 'P'
    print('carte %d x %d' % (W, H))
    print('    ' + ''.join(str(i // 10) for i in range(W))); print('    ' + ''.join(str(i % 10) for i in range(W)))
    for y in range(H): print('%2d  %s' % (y, ''.join(show[y])))
