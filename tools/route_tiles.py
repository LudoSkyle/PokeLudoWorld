#!/usr/bin/env python3
"""Fabrique assets/levels/route.png : les tuiles de la route du nord.

    python3 tools/route_tiles.py

La carte d'exemple de la route (`tools/maps/route_1/reference.png`) est faite des tuiles
de `assets/levels/sources/town_compilation.png`. Cette planche-là, le jeu ne la lit jamais :
ce script y découpe ce dont la route a besoin, sur la grille de 16, sans rien redessiner, et
relancer le script redonne le même fichier. Les ombres translucides de la planche (arbres,
falaises) sont gardées telles quelles.

Ce catalogue sert deux fois : `survey.py` y lit **quelles tuiles chercher** dans l'exemple,
et le TileSet y lit **où elles sont** dans route.png (source 11, cases de 16 px, sans marge).

Une matière à bords est un bloc 3 x 3 — nommé par ses cases comme un pavé numérique,
`rock7` en haut à gauche, `rock5` au centre, `rock3` en bas à droite — suivi de ses quatre
coins rentrants `i j / k l`.

Ce que la planche n'a pas est découpé dans l'exemple lui-même (`REFERENCE_PIECES`) : le
centre de la piste, les ponts, les rochers de la rivière… Le fond connu (pelouse, eau) en
est retiré pixel à pixel.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import island_tiles  # noqa: E402
from island_tiles import load, save, LEVELS  # noqa: E402

OUTPUT = os.path.join(LEVELS, 'route.png')
REFERENCE = os.path.join(HERE, 'maps', 'route_1', 'reference.png')
CLEAR = (0, 0, 0, 0)

# nom : (bloc 3 x 3 sur la planche, ses coins rentrants ou None, (colonne, rangée) dans route.png, idem pour les coins)
BLOCKS = {
    'sand':   ((64, 400), (64, 448), (0, 0), (3, 0)),        # sable bordé d'eau claire : le liseré au pied des falaises
    'deep':   ((160, 400), None, (5, 0), None),              # eau profonde, bords fondus dans l'eau claire
    'trail':  ((64, 240), (64, 288), (9, 0), (12, 0)),       # le contour d'herbe d'une piste (centre vide)
    'paved':  ((944, 240), None, (11, 6), None),             # dallage en chevrons bordé d'herbe
    'rock':   ((112, 512), (112, 560), (0, 3), (3, 3)),      # falaise à dessus de roche
    'grass':  ((208, 512), (208, 560), (5, 3), (8, 3)),      # falaise à dessus d'herbe
    'hollow': ((160, 512), (160, 560), (10, 3), (13, 3)),    # la même falaise, dessus vide : se pose sur n'importe quel sol
    'stair':  ((384, 976), None, (6, 13), None),              # escalier de pierre à poteaux : sa rangée du milieu est celle des marches
    'pond':   ((720, 400), (720, 448), (8, 16), (11, 16)),    # l'étang : une eau au niveau de l'herbe, sa berge brune en haut et sur les côtés — pas une falaise
    'earth':  ((256, 240), (256, 288), (0, 19), (3, 19)),      # la terre nue bordée d'herbe : la plaque d'une clairière, d'un carrefour — on y marche
}
# nom : ((x, y) sur la planche, (colonne, rangée) dans route.png)
SINGLES = {
    'water': ((96, 448), (3, 2)), 'lawn': ((16, 320), (4, 2)), 'lawn2': ((32, 320), (8, 0)),
    'tall': ((48, 320), (6, 6)),             # les hautes herbes : colonnes 6, 7, 8 comme dans l'atlas (TallGrass.kt), ses deux états foulés sont dérivés
    'fl1': ((160, 320), (0, 6)), 'fl2': ((176, 320), (1, 6)), 'fl3': ((192, 320), (2, 6)), 'fl4': ((176, 336), (3, 6)), 'fl5': ((192, 336), (4, 6)),
}
# ce qui est debout — nom : (x, y sur la planche, largeur, hauteur en cases) ; SPRITE_AT : sa case haut-gauche dans route.png
TOWN_SPRITES = {'treeA': (16, 0, 3, 3), 'treeB': (64, 0, 3, 3), 'conif': (160, 192, 1, 2), 'sapling': (128, 192, 1, 2), 'rock_s': (352, 592, 1, 1), 'boulder': (352, 656, 2, 2)}
SPRITE_AT = {'treeA': (0, 9), 'treeB': (3, 9), 'conif': (6, 7), 'sapling': (7, 7), 'rock_s': (8, 11), 'boulder': (9, 10), 'treeAB': (0, 13), 'treeBA': (3, 13)}
# Sur la planche, l'ombre du sapin et de l'arbuste déborde d'une rangée de pixels sous leur pied. L'exemple la coupe
# presque partout (il pose ces arbres sur deux cases) ; le jeu, lui, la dessine en entier : une rangée de plus sous le pied.
SHADOW_ROW = ('conif', 'sapling')
# L'exemple a aussi des arbres faits de deux essences : la cime de l'une sur le pied de l'autre (nom : cime, pied).
# Chaque arbre est une seule tuile de 3 x 3 dans le jeu : ces deux-là sont recomposés ici, rangée par rangée.
# Le jeu, lui, n'en veut pas — un arbre à deux teintes a l'air d'une erreur (Ludovic, 17/11/2026) : ils ne servent
# qu'au relevé (`cells(survey=True)`), et `layout.py` plante à leur place l'essence de leur cime.
MIXED_TREES = {'treeAB': ('treeA', 'treeB'), 'treeBA': ('treeB', 'treeA')}
# L'escalier de la planche ne monte que face au sud. Tourné d'un quart, le même bloc monte par le flanc d'un plateau :
# `stairW…` descend vers l'ouest, `stairE…` vers l'est. Leurs poteaux sont en haut et en bas, leurs marches au milieu.
SIDE_STAIRS = {'W': (9, 13), 'E': (0, 16)}          # quatre colonnes sur trois rangées : le bas, la volée du bas, celle du haut, le haut
# Une falaise à deux étages se monte par une volée double. Empiler deux fois la rangée de marches ne marche pas (Ludovic,
# 17/11/2026 : « ça ne fonctionne pas d'empiler 2 simples ») : ses deux rangées du haut sont vides, la falaise s'y voit,
# et chaque poteau a son pied au milieu. Deux rangées faites pour aller ensemble : celle du haut (`stairU…`) n'a pas de
# pied de poteau, celle du bas (`stairL…`) a l'ombre d'une contremarche à la place du vide.
DOUBLE_STAIRS = {'stairU4': (4, 16), 'stairU5': (7, 14), 'stairU6': (5, 16), 'stairL4': (4, 17), 'stairL5': (5, 17), 'stairL6': (6, 17)}          # (les colonnes 0 à 5 des rangées 13 à 15 sont aux arbres du relevé)
# La jetée : des planches en travers, étroites, entre deux longerons à pieux — un ponton, pas le tablier d'un pont.
# `pier4/5/6` : bord gauche, milieu, bord droit ; `pier1/2/3` : le dernier rang, avec son chant.
PIER = {'pier4': (12, 12), 'pier5': (13, 12), 'pier6': (14, 12), 'pier1': (15, 12), 'pier2': (15, 13), 'pier3': (15, 14),
        'pierT4': (13, 13), 'pierT5': (14, 13), 'pierT6': (13, 14), 'pierU4': (14, 14), 'pierU5': (13, 15), 'pierU6': (14, 15)}          # `pierT…` : le premier rang, que le sable recouvre par endroits — la jetée sort de la plage, elle n'est pas posée dessus
BRIDGE_END = (720, 267)          # dans environments.png : le coin du bout gauche du grand pont de bois, là où son tablier commence ; 48 pixels en travers, 32 le long
# Le dallage n'a que ses bords et ses coins sortants ; pour une place qui n'est pas un rectangle, ses quatre coins
# rentrants sont faits ici : le pavé plein, et dans le coin le bout de liseré d'herbe qui raccorde les deux bords voisins.
PAVED_INNER = {'pavedl': (14, 7), 'pavedk': (15, 7), 'pavedj': (14, 8), 'pavedi': (15, 8)}
# Des coquillages pour le sable : rien n'en avait dans ce style, ils sont dessinés ici, cernés d'un brun de sable mouillé.
# Une clôture de bois, aux teintes du pont : un poteau par case, deux lisses. `fence7…3` : coins et côtés d'un enclos
# (7 8 9 / 4 6 / 1 2 3), dessinés ici — la planche de la Route 1 n'en a pas.
FENCE = {'fence7': (8, 7), 'fence8': (9, 7), 'fence9': (10, 7), 'fence4': (8, 8), 'fence6': (10, 8), 'fence1': (8, 9), 'fence2': (9, 9), 'fence3': (10, 9)}
SHELLS = {'shell1': (13, 5), 'shell2': (14, 5), 'shell3': (15, 5), 'shell4': (14, 6)}
SHELL_ART = {
    'shell1': (4, 5, ['.oo.oo.', 'opwopwo', 'opwpwpo', 'opwpwpo', '.opwpo.', '..opo..', '..ooo..']),           # une coquille Saint-Jacques, en éventail
    'shell2': (5, 5, ['...oo..', '..occo.', '.ocdcco', 'ocdccdo', 'occddo.', '.oooo..']),                      # un bigorneau, en spirale
    'shell3': (5, 4, ['...r...', '..rsr..', 'rrrsrrr', 'rsssssr', '.rsssr.', '.rsrsr.', '.rr.rr.']),           # une étoile de mer
    'shell4': (2, 3, ['.oo........', 'opwo.......', '.oo........', '...........', '...........', '.......ooo.', '......ocdco', '.......ooo.']),
}
SHELL_INK = {'o': (150, 104, 84), 'w': (255, 240, 232), 'p': (240, 150, 140), 'c': (206, 168, 120), 'd': (150, 112, 78), 'r': (196, 110, 66), 's': (238, 156, 96)}          # un sable clair mange le blanc et le crème : il faut du rose et du brun
# Les nénuphars : sur la planche ils sont peints sur l'eau d'un autre étang, plus sombre. On retire cette eau, teinte par
# teinte (celles de sa case pleine, `LILY_WATER`) : il reste la feuille, la fleur et leur ombre, à poser sur n'importe quel étang.
LILIES = {'lily1': ((624, 480), (13, 16)), 'lily2': ((640, 480), (14, 16)), 'lily3': ((656, 480), (15, 16))}
LILY_WATER = (640, 416)
TRAIL_CENTRE = (15, 4)            # une case de l'exemple où la piste est nue : son centre n'est pas sur la planche
TRAIL_AT = (8, 1)
KEYS, CORNERS = '789456123', 'ijkl'


def block_names(name):
    """{nom de tuile: (dx, dy) dans son bloc}, coins rentrants compris (dx à partir de 3)."""
    out = {name + KEYS[j * 3 + i]: (i, j) for j in range(3) for i in range(3)}
    if BLOCKS[name][1]: out.update({name + CORNERS[j * 2 + i]: (3 + i, j) for j in range(2) for i in range(2)})
    return out


def family(name):
    """La matière d'une tuile : `rock7` et `rockj` sont de la famille `rock`."""
    for block in BLOCKS:
        if name.startswith(block) and len(name) == len(block) + 1: return block
    return name.rstrip('0123456789')


def blocks(name):
    """Cette tuile arrête-t-elle le pas ? L'eau, l'étang et sa berge, le sable du pied des falaises, les parois, les rebords de roche.

    Un rebord est plein, et se saute dans un seul sens (`jump`) : on ne s'y tient jamais.

    Deux coins rentrants de la falaise d'herbe ne l'arrêtent pas : `grassk` et `grassl` sont de la
    pelouse du plateau, avec un bout de lisière dans leurs quatre rangées du haut. On s'y tient, et
    ils ne touchent le vide que par leur pointe : on n'en tombe pas. Les mêmes coins de la falaise
    de roche restent pleins — leur dessus est le gradin de roche, où rien ne mène.

    Le bord du haut (`grass8`) est de la même herbe, et bloque ici : sur la Route 1 il donne sur
    le vide. Une carte où ce qui est derrière se foule — la plage, sur l'île de départ — le pose
    dans sa variante sans collision.
    """
    if name is None: return False
    if name == 'water' or family(name) in ('deep', 'sand', 'pond'): return True
    if name in ('grassk', 'grassl'): return False
    if family(name) in ('rock', 'grass', 'hollow'): return name[-1] != '5'
    return name.startswith('ledge') or name.startswith('fence')


def jump(name):
    """Le sens dans lequel un rebord de roche se saute, (dx, dy), ou None : du haut vers le bas de sa marche.

    Son ombre dit où est le bas : sous `ledgeL/M/R`, à l'est de `ledgeV…`, à l'ouest de `ledgeW…`.
    """
    if name is None or not name.startswith('ledge'): return None
    return (1, 0) if name.startswith('ledgeV') else ((-1, 0) if name.startswith('ledgeW') else (0, 1))


def town_tiles():
    """{nom: (x, y) sur la planche} pour toutes les tuiles d'une case."""
    out = {name: xy for name, (xy, _) in SINGLES.items()}
    for name, (at, inner, _, _) in BLOCKS.items():
        for tile, (i, j) in block_names(name).items():
            out[tile] = (at[0] + 16 * i, at[1] + 16 * j) if i < 3 else (inner[0] + 16 * (i - 3), inner[1] + 16 * j)
    return out


def atlas():
    """{nom: (colonne, rangée) dans route.png} — tuiles d'une case et, pour ce qui est debout, la case haut-gauche."""
    out = {name: at for name, (_, at) in SINGLES.items()}
    for name, (_, inner, at, inner_at) in BLOCKS.items():
        for tile, (i, j) in block_names(name).items():
            out[tile] = (at[0] + i, at[1] + j) if i < 3 else (inner_at[0] + i - 3, inner_at[1] + j)
    out['trailC'] = TRAIL_AT
    out['tall_pressing'], out['tall_pressed'] = (7, 6), (8, 6)
    out['ledgeVB'] = (15, 2)
    out.update({'shore' + k: at for k, at in zip('789461230ijkl'.replace('0', ''), [(c, r) for r in (7, 8) for c in range(6)])})
    for side, (c0, r0) in SIDE_STAIRS.items(): out.update({'stair%s%d%d' % (side, i, j): (c0 + i, r0 + j) for j in range(3) for i in range(4)})
    out.update(DOUBLE_STAIRS); out.update(PIER); out.update(SHELLS); out.update(FENCE); out.update(PAVED_INNER)
    out.update({name: at for name, (_, at) in LILIES.items()})
    out.update(SPRITE_AT)
    out.update({name: at for name, (at, _) in REFERENCE_PIECES.items()})
    return out


def drop(name):
    """Le nombre de rangées qu'une tuile dessine sous la case de son pied : l'ombre qui déborde."""
    return 1 if name in SHADOW_ROW else 0


def sizes():
    """{nom: (largeur, hauteur) en cases} de ce qui tient sur plus d'une case, du pied vers le haut (sans `drop`)."""
    out = {name: (w, h) for name, (_, _, w, h) in TOWN_SPRITES.items()}
    out.update({name: (3, 3) for name in MIXED_TREES})
    out.update({name: (w, h) for name, (_, (_, _, w, h, _)) in REFERENCE_PIECES.items() if (w, h) != (1, 1)})
    return out


# Ce qui vient de l'exemple — nom : ((colonne, rangée) dans route.png, (x, y en pixels dans l'exemple, largeur, hauteur en cases, fond à retirer))
# Le fond est le nom d'une tuile unie (`lawn`, `water`, `deep5`), `any` pour l'eau quelle qu'elle soit, ou None pour tout garder.
REFERENCE_PIECES = {
    'ledgeL': ((12, 2), (240, 128, 1, 1, 'lawn')), 'ledgeM': ((13, 2), (256, 128, 1, 1, 'lawn')), 'ledgeR': ((14, 2), (272, 128, 1, 1, 'lawn')),      # le rebord de roche qu'on saute
    'ledgeVT': ((15, 0), (736, 560, 1, 1, 'lawn')), 'ledgeVM': ((15, 1), (736, 576, 1, 1, 'lawn')),      # le même rebord, tourné vers l'est ; son bout du bas : `ledgeVB`, plus bas
    'ledgeWT': ((15, 3), (832, 704, 1, 1, 'lawn')), 'ledgeWB': ((15, 4), (832, 720, 1, 1, 'lawn')),      # et vers l'ouest, sur deux cases
    'riverrock': ((11, 9), (608, 0, 2, 3, 'deep5')),        # le gros rocher de la rivière, cerné d'écume
    'spire': ((13, 10), (288, 368, 1, 2, 'deep5')),         # le rocher pointu
    'pebbleA': ((14, 11), (640, 16, 1, 1, 'deep5')), 'pebbleB': ((15, 11), (592, 0, 1, 1, 'deep5')),      # les deux petits
    # les ponts de planches : trois cases de large, opaques
    'bridgeV4': ((0, 12), (224, 288, 1, 1, None)), 'bridgeV5': ((1, 12), (240, 288, 1, 1, None)), 'bridgeV6': ((2, 12), (256, 288, 1, 1, None)),
    'bridgeV1': ((3, 12), (224, 464, 1, 1, None)), 'bridgeV3': ((4, 12), (256, 464, 1, 1, None)),
    'bridgeH8': ((5, 12), (400, 560, 1, 1, None)), 'bridgeH5': ((6, 12), (400, 576, 1, 1, None)), 'bridgeH2': ((7, 12), (400, 592, 1, 1, None)), 'bridgeH1': ((8, 12), (384, 592, 1, 1, None)),
    # le dessous du pont horizontal, qui déborde sur la rangée d'en dessous : une case courante, puis ses deux bouts en biseau
    'lip': ((9, 12), (480, 608, 1, 1, 'any')), 'lipL': ((10, 12), (384, 608, 1, 1, 'lip')), 'lipR': ((11, 12), (560, 608, 1, 1, 'lip')),
}
STANDING = set(TOWN_SPRITES) | set(MIXED_TREES) | {'riverrock', 'spire', 'pebbleA', 'pebbleB'}       # ce qui est debout : posé dans World, trié en Y


def pressed(tile, by, lighter):
    """La touffe de hautes herbes qu'on foule : tassée de `by` pixels vers le sol, et éclaircie de `lighter` teintes.

    Rien n'est inventé : la touffe a cinq verts, du plus sombre au plus clair ; l'éclaircir, c'est
    faire monter chaque pixel d'autant de crans dans cette gamme. La tasser, c'est en retirer
    des rangées, le pied restant où il est.
    """
    ramp = sorted({p for row in tile for p in row if p[3]}, key=lambda p: p[0] + p[1] + p[2])
    out = [[CLEAR] * 16 for _ in range(16)]
    for y in range(by, 16):
        for x in range(16):
            p = tile[(y - by) * 16 // (16 - by)][x]
            if p[3]: out[y][x] = ramp[min(len(ramp) - 1, ramp.index(p) + lighter)]
    return out


def ledge_bottom(top):
    """Le bout du bas du rebord tourné vers l'est : celui du haut, retourné.

    L'exemple ne le montre jamais en entier — un arbre en cache toujours la moitié — mais ce
    qu'on en voit est, au pixel près, le bout du haut retourné, à un pixel de son ombre près.
    """
    out = [list(row) for row in reversed(top)]
    out[14][4] = (130, 130, 124, 255)
    return out


def cells(survey=False):
    """{(colonne, rangée): image 16 x 16} de toute la planche ; avec `survey`, les arbres à deux essences de l'exemple en plus."""
    town = island_tiles.source_sheet(island_tiles.TOWN)
    def cut(sheet, x, y): return [[tuple(sheet[y + j][x + i]) if sheet[y + j][x + i][3] else CLEAR for i in range(16)] for j in range(16)]
    made, where = {}, atlas()
    for name, (x, y) in town_tiles().items(): made[where[name]] = cut(town, x, y)
    for name, (x, y, w, h) in TOWN_SPRITES.items():
        for j in range(h + drop(name)):
            for i in range(w): made[(where[name][0] + i, where[name][1] + j)] = cut(town, x + 16 * i, y + 16 * j)
    for name, (crown, foot) in MIXED_TREES.items() if survey else ():
        for j in range(3):
            for i in range(3):
                src = where[crown] if j < 2 else where[foot]
                made[(where[name][0] + i, where[name][1] + j)] = made[(src[0] + i, src[1] + j)]
    water = {tuple(town[LILY_WATER[1] + j][LILY_WATER[0] + i]) for j in range(16) for i in range(16)}
    for name, ((x, y), at) in LILIES.items(): made[at] = [[CLEAR if p in water else p for p in row] for row in cut(town, x, y)]
    made[where['tall_pressing']], made[where['tall_pressed']] = pressed(made[where['tall']], 2, 0), pressed(made[where['tall']], 3, 1)
    reference = load(REFERENCE)[2]
    made[TRAIL_AT] = cut(reference, TRAIL_CENTRE[0] * 16, TRAIL_CENTRE[1] * 16)
    plain = {name: made[where[name]] for name in ('lawn', 'water', 'deep5', 'sand5')}
    for name, (at, (x, y, w, h, ground)) in REFERENCE_PIECES.items():
        for j in range(h):
            for i in range(w):
                tile = cut(reference, x + 16 * i, y + 16 * j)
                if ground == 'lip':          # un bout du dessous de pont : on ne garde que les couleurs de sa case courante
                    colours = {p[:3] for row in made[where['lip']] for p in row if p[3]}
                    tile = [[tile[b][a] if b < 8 and tile[b][a][:3] in colours else CLEAR for a in range(16)] for b in range(16)]
                elif ground == 'lawn':       # sur la pelouse : toutes ses teintes s'en vont, où qu'elles tombent (son grain change d'une case à l'autre)
                    colours = {p[:3] for row in plain['lawn'] for p in row}
                    tile = [[CLEAR if tile[b][a][:3] in colours else tile[b][a] for a in range(16)] for b in range(16)]
                elif ground:                 # sur l'eau : pixel à pixel, l'écume d'un rocher a les teintes des reflets
                    grounds = [plain[g] for g in (('water', 'deep5') if ground == 'any' else (ground,))]
                    tile = [[CLEAR if any(g[b][a][:3] == tile[b][a][:3] for g in grounds) else tile[b][a] for a in range(16)] for b in range(16)]
                made[(at[0] + i, at[1] + j)] = tile
    made[where['ledgeVB']] = ledge_bottom(made[where['ledgeVT']])
    # la volée double : la rangée de marches en deux variantes qui se suivent
    STEP_SHADE, POST, POST_FOOT = made[where['stair2']][0][0], made[where['stair4']][0][9], made[where['stair4']][15][9]
    for k in '456':
        up = [row[:] for row in made[where['stair' + k]]]
        up = [[POST if p == POST_FOOT else p for p in row] for row in up]                                # le poteau continue : pas de pied au milieu
        low = [row[:] for row in made[where['stair' + k]]]
        for b in (0, 1):                                                                                 # l'ombre de la contremarche, là où la rangée simple est vide
            for a in range(16):
                if low[b][a][3] == 0 and (k == '5' or (k == '4' and a >= 13) or (k == '6' and a <= 2)): low[b][a] = STEP_SHADE
        if k != '5': made[where['stairU' + k]] = up
        made[where['stairL' + k]] = low
    # les escaliers de côté : le bloc de l'escalier double (le haut, ses deux volées, le bas), tourné d'un quart de tour
    block = [[CLEAR] * 48 for _ in range(64)]
    for j, names in enumerate((('stair7', 'stair8', 'stair9'), ('stairU4', 'stairU5', 'stairU6'), ('stairL4', 'stairL5', 'stairL6'), ('stair1', 'stair2', 'stair3'))):
        for i, name in enumerate(names):
            tile = made.get(where[name])
            for b in range(16):
                for a in range(16):
                    if tile: block[j * 16 + b][i * 16 + a] = tile[b][a]
    turned = {'W': [[block[63 - x][y] for x in range(64)] for y in range(48)],          # le bas de l'escalier passe à gauche
              'E': [[block[x][47 - y] for x in range(64)] for y in range(48)]}          # ou à droite
    for side, (c0, r0) in SIDE_STAIRS.items():
        for j in range(3):
            for i in range(4): made[(c0 + i, r0 + j)] = [[turned[side][j * 16 + b][i * 16 + a] for a in range(16)] for b in range(16)]
    # la jetée : quatre planches par case, aux teintes du pont
    ink = {p[:3]: None for row in made[where['bridgeV4']] for p in row}
    DARK, SIDE, GAP, WOOD, LIGHT, SHADE = [c + (255,) for c in ((132, 97, 57), (165, 130, 82), (189, 146, 99), (222, 178, 123), (231, 195, 140), (206, 170, 115))]
    assert all(c[:3] in ink for c in (DARK, SIDE, GAP, WOOD, LIGHT, SHADE)), 'les teintes du pont ont changé'
    def planks(last):
        tile = []
        for b in range(16):
            tone = (LIGHT, WOOD, SHADE, SIDE)[b % 4]
            row = [tone] * 16
            if b % 4 != 3: row[(5, 12, 2, 9)[b // 4]] = GAP                    # le joint entre deux planches, décalé d'un rang à l'autre
            tile.append(row)
        if last: tile[13], tile[14], tile[15] = [SHADE] * 16, [SIDE] * 16, [DARK] * 16          # le chant du dernier rang
        return tile
    def edged(tile, right):
        tile = [row[:] for row in tile]
        for b in range(16):
            tile[b][0], tile[b][1] = DARK, SIDE                                # le longeron
        for b, row in enumerate(('DDDD', 'DLLD', 'DSSD', 'DSSD', 'DSSD', 'DDDD')):          # la tête d'un pieu, un par case
            for a, k in enumerate(row): tile[5 + b][a] = {'D': DARK, 'L': LIGHT, 'S': SIDE}[k]
        return [row[::-1] for row in tile] if right else tile
    for last, names in ((False, ('pier4', 'pier5', 'pier6')), (True, ('pier1', 'pier2', 'pier3'))):
        made[where[names[0]]], made[where[names[1]]], made[where[names[2]]] = edged(planks(last), False), planks(last), edged(planks(last), True)
    # La jetée sort du sable comme le pont de l'atlas sort de l'herbe : **le même découpage, au pixel près** (Ludovic,
    # 17/11/2026 : « reproduis à l'identique »). On lit, au bout gauche du pont de `environments.png`, où l'herbe recouvre
    # le tablier — son bord en dents inégales et ses touffes posées sur les planches — et l'on reporte ce masque sur le
    # haut de la jetée, tourné d'un quart de tour (le long du pont devient le long de la jetée), l'herbe changée en sable.
    game_atlas = load(os.path.join(LEVELS, 'environments.png'))[2]
    ex, ey = BRIDGE_END
    def grassy(along, across):
        p = game_atlas[ey + across][ex + along]
        return p[3] > 0 and p[1] > p[0] + 25 and p[1] > p[2] + 25
    sand, lip = made[where['sand5']], (214, 198, 156, 255)
    for row, flight in enumerate('TU'):                          # deux rangs de planches : les touffes vont jusqu'au second
        for n, k in enumerate('456'):
            tile = [line[:] for line in made[where['pier' + k]]]
            for b in range(16):
                for a in range(16):
                    along, across = row * 16 + b, n * 16 + a
                    if not grassy(along, across): continue
                    bare = any(0 <= along + i < 32 and 0 <= across + j < 48 and not grassy(along + i, across + j) for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                    tile[b][a] = lip if bare else sand[b][a]          # le bord du sable, plus sombre, contre le bois
            made[where['pier' + flight + k]] = tile
    # les coins rentrants du dallage
    border = next(b for b in range(16) if made[where['paved5']][b][8] == made[where['paved8']][b][8] and b > 0)          # l'épaisseur du liseré d'herbe
    for name, (side, top) in {'pavedl': ('4', True), 'pavedk': ('6', True), 'pavedj': ('4', False), 'pavedi': ('6', False)}.items():
        tile = [row[:] for row in made[where['paved5']]]
        edge = made[where['paved' + side]]
        for b in (range(border) if top else range(16 - border, 16)):
            for a in (range(border) if side == '4' else range(16 - border, 16)): tile[b][a] = edge[b][a]
        made[where[name]] = tile
    # la clôture : les lisses d'abord, vers les voisins que dit la forme, puis le poteau par-dessus
    for name in FENCE:
        k = name[-1]
        east, west, north, south = k in '7812', k in '8923', k in '4613', k in '4679'
        tile = [[CLEAR] * 16 for _ in range(16)]
        for y, tone in ((6, WOOD), (7, DARK), (10, WOOD), (11, DARK)):
            for x in range(16):
                if (x >= 8 and east) or (x < 8 and west): tile[y][x] = tone
        for y in range(16):
            if (y < 8 and north) or (y >= 8 and south): tile[y][7], tile[y][8] = WOOD, SIDE
        for y in range(2, 14):
            for x in range(6, 10): tile[y][x] = DARK if x in (6, 9) or y in (2, 13) else (LIGHT if y == 3 else SIDE)
        made[where[name]] = tile
    # les coquillages
    for name, (x0, y0, art) in SHELL_ART.items():
        tile = [[CLEAR] * 16 for _ in range(16)]
        for b, row in enumerate(art):
            for a, k in enumerate(row):
                if k != '.': tile[y0 + b][x0 + a] = SHELL_INK[k] + (255,)
        made[where[name]] = tile
    # Le rivage sans son eau : le bord du sable seul, à poser par-dessus une case d'eau. C'est ce qui laisse un reflet
    # passer dessous au lieu de s'étaler sur le sable (l'île de départ ; la Route 1 garde le bord d'une seule pièce).
    for name in [n for n in where if n.startswith('shore')]:
        edge = made[where['sand' + name[5:]]]          # l'eau s'en va : tout ce qui est bleu et pas clair (l'écume, elle, reste au bord du sable)
        made[where[name]] = [[CLEAR if edge[b][a][2] > edge[b][a][0] + 25 and edge[b][a][0] < 190 else edge[b][a] for a in range(16)] for b in range(16)]
    return {c: t for c, t in made.items() if any(p[3] for row in t for p in row)}


if __name__ == '__main__':
    made = cells()
    columns, lines = max(c for c, _ in made) + 1, max(r for _, r in made) + 1
    sheet = [[CLEAR] * (columns * 16) for _ in range(lines * 16)]
    for (c, r), img in made.items():
        for y in range(16):
            for x in range(16): sheet[r * 16 + y][c * 16 + x] = img[y][x]
    save(OUTPUT, sheet)
    print('%d tuiles dans %s (%d x %d cases)' % (len(made), os.path.relpath(OUTPUT, os.path.dirname(HERE)), columns, lines))
