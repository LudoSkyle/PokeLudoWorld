#!/usr/bin/env python3
"""Fabrique le fond de l'écran titre : le sommet d'une tour ancienne, au-dessus des nuages.

    python3 tools/title_background.py

Quatre images sortent dans assets/ui/title/, toutes de 320×240 en pixels de jeu (l'écran à
l'échelle 4), à superposer dans cet ordre :

    background.png    le ciel — clair à hauteur d'yeux, plus profond vers le bas, où l'on
                      regarde dans le vide — et les grands nuages lointains, immobiles
    clouds_far.png    quelques nuages sur fond transparent, qui passent derrière la tour
    tower.png         la tour sur fond transparent : pierre usée, mousse, un sceau runique gravé qui luit
    clouds_near.png   la mer de nuages du premier plan, où le pied de la tour se perd

Les deux images de nuages se raccordent d'un bord à l'autre : l'écran titre les fait défiler,
la proche plus vite que la lointaine.

Deux morceaux sont aussi gardés à part dans assets/ui/title/parts/, pour qui voudrait les
animer ou les remplacer séparément : tower_bare.png (la tour sans son sceau) et seal.png (le
sceau seul). Posés l'un sur l'autre, ils redonnent tower.png.

Tout est dessiné par ce script, rien n'est repris d'une autre image : le relancer redonne
exactement les mêmes fichiers. Le fond est indépendant du logo et du texte du bas
(title_logo.py, title_prompt.py).
"""
import math
import os

from island_tiles import ROOT, save

OUT = os.path.join(ROOT, 'src/main/kotlin/fr/skyle/pokemonmirage/assets/ui/title')
W, H = 320, 240
CLEAR = (0, 0, 0, 0)

BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


def rgb(code, alpha=255):
    code = code.lstrip('#')
    return (int(code[0:2], 16), int(code[2:4], 16), int(code[4:6], 16), alpha)


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


def ramp(colours, t, x, y):
    """Une couleur du dégradé, tramée entre deux teintes voisines : pas de mélange lisse."""
    t = min(max(t, 0.0), 1.0) * (len(colours) - 1)
    low = min(int(t), len(colours) - 2)
    # La trame n'occupe que le tiers central de chaque marche : le reste est une bande franche.
    part = min(max((t - low - 0.34) / 0.32, 0.0), 1.0)
    return colours[low + 1] if part * 16 > BAYER[y & 3][x & 3] + 0.5 else colours[low]


def noise(x, y, seed=0):
    n = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0


def smooth(x, y, scale, seed):
    """Un bruit doux, pour les plaques de mousse."""
    gx, gy = x / scale, y / scale
    x0, y0 = math.floor(gx), math.floor(gy)
    fx, fy = gx - x0, gy - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    top = noise(x0, y0, seed) * (1 - fx) + noise(x0 + 1, y0, seed) * fx
    low = noise(x0, y0 + 1, seed) * (1 - fx) + noise(x0 + 1, y0 + 1, seed) * fx
    return top * (1 - fy) + low * fy


# --- le ciel : clair au milieu, profond en haut, et plus profond encore vers le bas

SKY = [rgb(c) for c in ('#3b7ade', '#4384e3', '#4a8de7', '#5598eb', '#5fa2ee', '#6dadf1', '#7ab7f3', '#89c1f5', '#98caf7',
                        '#a7d3f9', '#b6dcfa', '#c3e3fb', '#cfe9fc', '#c9e5fb', '#bcdcf8', '#a9cef4', '#96bdee', '#84ade9',
                        '#739de3', '#648ddc', '#577dd4', '#4c6ecb', '#4562c3')]


def sky(x, y):
    # Le ciel est grand et vide : la trame court d'une teinte à l'autre sans palier, pour qu'on
    # n'y voie pas de bandes.
    t = y / (H - 1) * (len(SKY) - 1)
    low = min(int(t), len(SKY) - 2)
    return SKY[low + 1] if (t - low) * 16 > BAYER[y & 3][x & 3] + 0.5 else SKY[low]


# --- les nuages : des boules accolées, éclairées d'en haut à gauche

CLOUD = [rgb(c) for c in ('#8fb2ea', '#b7d2f5', '#deecfb', '#ffffff')]
LIGHT = (-0.46, -0.72, 0.52)


def cloud_at(balls, x, y):
    """Teinte du nuage (0..3) en ce point, ou None hors du nuage."""
    best, hit = 0.0, None
    for cx, cy, r in balls:
        dx, dy = x - cx, y - cy
        d2 = dx * dx + dy * dy
        if d2 < r * r:
            height = math.sqrt(r * r - d2)
            if height > best: best, hit = height, (dx / r, dy / r, height / r)
    if hit is None: return None
    lit = hit[0] * LIGHT[0] + hit[1] * LIGHT[1] + hit[2] * LIGHT[2]
    if lit > 0.62: return 3
    if lit > 0.34: return 2 if (lit - 0.34) * 57 < BAYER[y & 3][x & 3] else 3
    if lit > 0.02: return 2
    if lit > -0.22: return 1 if (lit + 0.22) * 66 < BAYER[y & 3][x & 3] else 2
    if lit > -0.5: return 1
    return 0 if (-0.5 - lit) * 60 > BAYER[y & 3][x & 3] else 1


def bank(seed, x0, x1, base, peak, count, small=9, big=14):
    """Un amas de cumulus : de grosses boules en bas, de plus petites en haut."""
    balls = []
    for i in range(count):
        u = noise(i, seed, 1)
        cx = x0 + (x1 - x0) * u
        # La silhouette monte vers le milieu de l'amas.
        crest = 1.0 - abs(u - 0.5) * 2.0
        level = noise(i, seed, 2) ** 0.8
        cy = base - (base - peak) * level * (0.25 + 0.75 * crest)
        r = small + big * (1.0 - level) + 5 * noise(i, seed, 3)
        balls.append((cx, cy, r))
    return balls


def wrapped(balls):
    """Trois copies : la boule qui dépasse d'un bord revient par l'autre."""
    return [(cx + offset, cy, r) for cx, cy, r in balls for offset in (-W, 0, W)]


def build_background():
    rows = [[sky(x, y) for x in range(W)] for y in range(H)]

    # Très loin en dessous, des nuages minuscules : c'est eux qui donnent le vertige.
    for index in range(26):
        cx, cy = round(noise(index, 1, 21) * W), 160 + round(noise(index, 2, 21) * 70)
        half = 4 + round(noise(index, 3, 21) * 9)
        for dx in range(-half, half + 1):
            for dy in range(-1, 2):
                if abs(dx) > half - 2 * abs(dy) - (1 if dy < 0 else 0): continue
                x, y = (cx + dx) % W, cy + dy
                if y < H: rows[y][x] = mix(CLOUD[3] if dy < 1 else CLOUD[1], sky(x, y), 0.4)

    # Deux grands amas de part et d'autre ; entre eux, autour de la tour, on voit le vide.
    layers = [
        (bank(11, 238, 356, 232, 100, 50), 0.2),
        (bank(29, -40, 82, 236, 78, 46), 0.2),
    ]
    for balls, haze in layers:
        for y in range(H):
            for x in range(W):
                tone = cloud_at(balls, x, y)
                if tone is not None: rows[y][x] = mix(CLOUD[tone], sky(x, y), haze)
    return rows


def build_far_clouds():
    """Les nuages qui passent derrière la tour."""
    rows = [[CLEAR] * W for _ in range(H)]
    groups = [
        [(40, 118, 9), (52, 113, 13), (67, 117, 11), (80, 121, 8), (30, 122, 6), (58, 122, 10)],
        [(140, 156, 8), (152, 151, 12), (168, 154, 13), (184, 158, 9), (198, 161, 6), (160, 160, 10)],
        [(250, 134, 7), (261, 130, 10), (274, 133, 9), (286, 137, 6), (266, 137, 8)],
        [(300, 176, 6), (310, 172, 9), (322, 175, 8), (333, 179, 5)],
        [(96, 188, 6), (106, 185, 9), (118, 187, 8), (128, 190, 5)],
    ]
    for balls in groups:
        base = max(cy + r * 0.45 for cx, cy, r in balls)
        for y in range(H):
            if y > base: continue
            for x in range(W):
                tone = cloud_at(wrapped(balls), x, y)
                if tone is not None: rows[y][x] = mix(CLOUD[max(tone, 1)] if y < base - 1 else CLOUD[1], SKY[6], 0.12)
    return rows


def build_near_clouds():
    """La mer de nuages du premier plan : des bosses, des creux, et plus bas tout est blanc."""
    rows = [[CLEAR] * W for _ in range(H)]
    balls = []
    for index in range(34):
        level = noise(index, 2, 53)
        balls.append((noise(index, 1, 53) * W, 221 + 22 * level, 9 + 12 * noise(index, 3, 53)))
    balls = wrapped(balls)
    for y in range(170, H):
        for x in range(W):
            tone = cloud_at(balls, x, y)
            # Sous les bosses, le nuage est plein : l'ombre de celles du dessus.
            if tone is None and y >= 234: tone = 1 if (x + y) % 2 or y < 237 else 2
            if tone is not None: rows[y][x] = CLOUD[tone]
    return rows


# --- la tour : un fût rond, vu d'un peu au-dessus, dont on ne voit que le sommet

CX, TOP, RADIUS, FLAT = 160, 128, 45, 11
COURSE = 7
STONE = [rgb(c) for c in ('#f3f7fb', '#d5e0ee', '#b1c2dc', '#8a9cc6', '#677aae', '#4c5c92')]
MOSS = [rgb(c) for c in ('#a6e8bc', '#6cc99a', '#429f88', '#2d7378')]
GRASS = [rgb(c) for c in ('#a6e8bc', '#7bd3a0', '#56b68e')]
GLOW = [rgb(c) for c in ('#ffffff', '#c4fbff', '#74e4f6')]
DARK = rgb('#38467a')

# Le signe de la tour : un sceau runique. Un anneau traversé d'une croix, et quatre branches
# qui portent chacune un peigne de traits — le même dessin tourné d'un quart de tour à chaque
# branche, comme une roue.
def seal():
    """Les points du sceau, autour de (0, 0)."""
    points = set()
    for step in range(48):
        angle = step / 48 * 2 * math.pi
        points.add((round(5.3 * math.cos(angle)), round(5.3 * math.sin(angle))))
    # Une branche, vers le haut : la tige, une barre recourbée près de l'anneau, trois dents au bout.
    branch = {(0, -k) for k in range(0, SEAL_REACH + 1)}
    branch |= {(dx, -8) for dx in range(-3, 4)} | {(-3, -9), (3, -9)}
    branch |= {(dx, -11) for dx in (1, 2, 3, 4)} | {(dx, -13) for dx in (1, 2, 3, 4)} | {(dx, -15) for dx in (1, 2, 3)}
    branch |= {(4, -12), (-1, -15), (-2, -15), (-2, -14)}
    for turn in range(4):
        points |= branch
        branch = {(-y, x) for x, y in branch}
    return points


SEAL_REACH = 15
SEAL = rgb('#35c3ea')
RUNES = (('#.#', '.#.', '#.#'), ('###', '..#', '###'), ('.#.', '###', '.#.'), ('#..', '###', '..#'))


def shade(u):
    """Du flanc éclairé au flanc à l'ombre, de 0 à 1 le long du fût."""
    return 0.14 * (-0.6 - u) / 0.4 + 0.02 if u < -0.6 else 0.02 + (u + 0.6) / 1.6 * 0.86


def stone(u, x, y, darker=0):
    t = min(max(shade(u) + darker * 0.2, 0.0), 1.0)
    return ramp(STONE, t, x, y)


def draw_seal(put):
    """Le sceau, gravé à même les pierres, sans cadre : un sillon qui luit, et sous chaque trait
    l'ombre de la gravure, qui le détache de la pierre claire. Les joints du mur passent derrière."""
    seal_x, seal_y = CX, TOP + 38
    marks = {(seal_x + dx, seal_y + dy) for dx, dy in seal()}
    for x, y in marks:
        if (x, y + 1) not in marks: put(x, y + 1, STONE[4])
    for x, y in marks: put(x, y, SEAL)
    put(seal_x, seal_y, GLOW[1])
    for dx, dy in ((0, -SEAL_REACH), (SEAL_REACH, 0), (0, SEAL_REACH), (-SEAL_REACH, 0)): put(seal_x + dx, seal_y + dy, GLOW[1])


def build_seal():
    """Le sceau seul, à sa place sur l'image : posé sur la tour nue, il redonne la tour."""
    rows = [[CLEAR] * W for _ in range(H)]

    def put(x, y, colour):
        if 0 <= x < W and 0 <= y < H: rows[y][x] = colour

    draw_seal(put)
    return rows


def build_tower(sealed=True):
    rows = [[CLEAR] * W for _ in range(H)]

    def put(x, y, colour):
        if 0 <= x < W and 0 <= y < H: rows[y][x] = colour

    def front(x):
        """Le bord avant du sommet : c'est de là que part le mur."""
        u = (x - CX) / RADIUS
        return TOP + FLAT * math.sqrt(max(0.0, 1.0 - u * u))

    # Le mur : des assises qui suivent la courbe du fût, des joints décalés d'une assise à l'autre.
    for x in range(CX - RADIUS, CX + RADIUS + 1):
        u = (x - CX) / RADIUS
        if abs(u) > 1: continue
        turn = math.asin(u) / math.pi * 13
        before = math.asin(max(-1.0, (x - 1 - CX) / RADIUS)) / math.pi * 13
        for y in range(math.ceil(front(x)), H):
            depth = round(y - front(x))
            course = depth // COURSE
            # Le bord s'est ébréché par endroits.
            if abs(u) > 0.95 and noise(course, 1 if u > 0 else 2, 31) > 0.62 and depth % COURSE < 5: continue
            brick = math.floor(turn + 0.5 * (course % 2))
            darker = 0
            tint = noise(course, brick, 32)
            if tint > 0.84: darker = 1
            elif tint < 0.12: darker = -1
            if depth % COURSE == 0 or brick != math.floor(before + 0.5 * (course % 2)): darker = 1.4
            # La mousse : en plaques, plus dense sous le sommet et du côté de l'ombre.
            cover = smooth(x, y, 10, 33) + 0.2 * max(0.0, 1.0 - depth / 30.0) + 0.1 * max(0.0, u)
            if cover > 0.78 + (0.06 if depth % COURSE == 0 else 0.0):
                put(x, y, ramp(MOSS, shade(u) + (0.22 if noise(x // 2, y // 2, 34) > 0.8 else 0.0), x, y))
            else:
                put(x, y, stone(u, x, y, darker))

    # Une meurtrière, des fissures.
    for dy in range(13):
        for dx in range(-3, 4):
            if dy < 3 and abs(dx) > dy + 1: continue
            put(CX - 26 + dx, TOP + 58 + dy, STONE[5] if dx == -3 or dy == 0 else DARK)
    for start_x, start_y, steps, lean in ((CX + 20, TOP + 16, 22, -1), (CX - 30, TOP + 30, 15, 1), (CX + 9, TOP + 78, 18, 1)):
        x = start_x
        for step in range(steps):
            put(x, start_y + step, STONE[5])
            if noise(step, start_x, 35) > 0.55: x += lean if noise(step, start_x, 36) > 0.35 else -lean

    # Les lianes qui pendent du sommet — avant le signe, qu'elles ne recouvrent pas.
    for index in range(9):
        x = CX - RADIUS + 4 + round(noise(index, 1, 37) * (RADIUS * 2 - 8))
        u = (x - CX) / RADIUS
        length = 8 + round(noise(index, 2, 37) * 34)
        for step in range(length):
            y = round(front(x)) + step
            sway = round(math.sin(step / 5.0 + index) * 0.8)
            put(x + sway, y, MOSS[2] if u < 0.3 else MOSS[3])
            if step % 4 == 1: put(x + sway + (1 if step % 8 == 1 else -1), y, MOSS[1] if u < 0.3 else MOSS[2])

    # Le grand sceau (à part dans parts/seal.png), puis une frise de signes plus petits tout
    # autour du fût.
    if sealed: draw_seal(put)
    for index in range(-5, 6):
        angle = index * 0.27
        x = round(CX + RADIUS * math.sin(angle))
        y = round(front(x)) + 9 * COURSE + 2
        rune = RUNES[(index + 5) % len(RUNES)]
        for row, line in enumerate(rune):
            for column, mark in enumerate(line):
                # Vers les bords le fût tourne : les signes se resserrent.
                if mark == '#' and (abs(index) < 4 or column < 2): put(x - 1 + column, y + row, GLOW[2] if abs(index) > 2 else GLOW[1])

    # Les créneaux du fond, dont plusieurs sont tombés.
    def merlon(angle, tall, wide=7):
        mx = CX + RADIUS * math.cos(math.radians(angle))
        my = TOP + FLAT * math.sin(math.radians(angle))
        for dx in range(-(wide // 2), wide // 2 + 1):
            x = round(mx) + dx
            u = max(-1.0, min(1.0, (x - CX) / RADIUS))
            # Le haut d'un créneau cassé est en dents.
            chip = round(noise(x, round(angle), 38) * 2.4) if tall < 9 else 0
            for dy in range(tall - chip + 1):
                y = round(my) - dy
                edge = dy == tall - chip or dx == -(wide // 2)
                put(x, y, stone(u, x, y, -1 if edge else (1.2 if dx == wide // 2 else 0)))

    for angle, tall in ((198, 6), (216, 11), (236, 5), (252, 9), (291, 4), (308, 11), (326, 7), (344, 10)):
        merlon(angle, tall)

    # Le dessus : une margelle de pierre, de l'herbe au milieu.
    for y in range(TOP - FLAT, TOP + FLAT + 1):
        for x in range(CX - RADIUS, CX + RADIUS + 1):
            u, v = (x - CX) / RADIUS, (y - TOP) / FLAT
            d = u * u + v * v
            if d > 1.0: continue
            if d > 0.74:
                spoke = math.floor(math.atan2(v, u) / math.pi * 11)
                joint = spoke != math.floor(math.atan2(v, (x - 1 - CX) / RADIUS) / math.pi * 11)
                put(x, y, stone(u * 0.7 - 0.3, x, y, 1.3 if joint or d > 0.96 else 0))
            elif d > 0.66:
                put(x, y, STONE[3] if v < 0 else GRASS[2])
            else:
                tuft = noise(x // 2, y, 39)
                put(x, y, GRASS[0] if tuft > 0.8 else (GRASS[2] if tuft < 0.24 else GRASS[1]))
    # Des dalles éparses dans l'herbe, qui mènent au socle.
    for dx, dy in ((-2, 6), (2, 5), (-3, 3), (1, 2), (-12, 1), (11, 4)):
        for ox in range(3):
            put(CX + dx + ox, TOP + dy, STONE[1] if ox < 2 else STONE[3])

    # Deux piliers, l'un brisé, et entre eux un éclat de lumière qui flotte.
    def pillar(x, foot, tall, broken):
        for dy in range(tall + 1):
            y = foot - dy
            for dx in range(-3, 4):
                if broken and dy > tall - 3 and noise(dx, dy, 40) > 0.45 + 0.2 * (tall - dy): continue
                wide = 3 if dy < 2 or (not broken and dy > tall - 3) else 2
                if abs(dx) > wide: continue
                tone = 0 if dx <= -wide + 1 else (2 if dx < wide else 4)
                if dy % 6 == 3 and tone < 4: tone += 1
                put(x + dx, y, STONE[tone])
        if not broken:
            # Un reste de linteau, qui partait vers l'autre pilier.
            for dx in range(-4, 10):
                for dy in range(3):
                    if dx > 6 and noise(dx, dy, 41) > 0.5: continue
                    put(x + dx, foot - tall - 1 - dy, STONE[0] if dy == 2 else (STONE[2] if dx < 8 else STONE[3]))

    pillar(CX - 16, TOP + 1, 34, False)
    pillar(CX + 16, TOP + 1, 20, True)
    for dx, dy, tone in ((20, 3, 1), (21, 3, 3), (22, 4, 2), (-22, 4, 1), (-21, 4, 3)): put(CX + dx, TOP + dy, STONE[tone])
    orb_x, orb_y = CX, TOP - 17
    for dy in range(-13, 14):
        for dx in range(-13, 14):
            d = math.hypot(dx, dy)
            x, y = orb_x + dx, orb_y + dy
            if d <= 3.2: put(x, y, GLOW[0])
            elif d <= 4.6: put(x, y, GLOW[1])
            elif d <= 12.5 and rows[y][x][3] == 0:
                # Le halo : une trame qui s'éclaircit en s'éloignant, sur le ciel seulement.
                if (1.0 - (d - 4.6) / 7.9) * 15 > BAYER[y & 3][x & 3]: put(x, y, rgb('#c4fbff', 150))

    # Les créneaux de devant, sur les côtés seulement : ils ne cachent pas le sommet.
    for angle, tall in ((12, 8), (34, 5), (146, 8), (168, 6)):
        merlon(angle, tall)

    # Des pierres détachées de la tour, qui flottent près d'elle.
    for sx, sy, wide, tall in ((92, 146, 10, 6), (236, 134, 8, 5), (250, 170, 5, 4), (80, 182, 6, 4), (102, 112, 4, 3)):
        for dy in range(tall):
            inset = (1 if dy == 0 else 0) + (dy - tall + 3 if dy > tall - 3 else 0)
            for dx in range(inset, wide - inset):
                tone = 0 if dy == 0 else (1 if dx < wide * 0.6 and dy < tall - 2 else (3 if dy < tall - 1 else 4))
                put(sx + dx, sy + dy, MOSS[1] if dy == 0 and noise(sx + dx, sy, 42) > 0.5 else STONE[tone])
    return rows


if __name__ == '__main__':
    os.makedirs(os.path.join(OUT, 'parts'), exist_ok=True)
    for name, build in (('background', build_background), ('clouds_far', build_far_clouds), ('tower', build_tower), ('clouds_near', build_near_clouds)):
        save(os.path.join(OUT, name + '.png'), build())
    # Les morceaux de la tour, gardés à part : ils se superposent tels quels.
    save(os.path.join(OUT, 'parts/tower_bare.png'), build_tower(sealed=False))
    save(os.path.join(OUT, 'parts/seal.png'), build_seal())
    print('background.png, clouds_far.png, tower.png et clouds_near.png ecrits dans', os.path.relpath(OUT, ROOT), '(et parts/tower_bare.png, parts/seal.png)')
