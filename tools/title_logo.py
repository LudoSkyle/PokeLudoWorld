#!/usr/bin/env python3
"""Fabrique le logo de l'écran titre : l'emblème ailé, le logo Pokémon bleuté, le mot MIRAGE.

    python3 tools/title_logo.py

Sort assets/ui/title/logo.png, sur fond transparent, au double de sa taille à l'écran pour
rester net quand l'écran titre l'anime. Trois morceaux :

- **l'emblème**, pris trait pour trait dans assets/ui/title/sources/emblem_reference.png : son
  dessin n'est pas retouché. Son fond est retiré, ses traits noirs passent au bleu nuit, ses
  gris et ses jaunes aux bleus du ciel (voir `recolour`) ; seul son centre est refait : un
  disque de ciel et un nuage à la place de la bille dorée ;
- **le logo Pokémon**, pris tel quel dans assets/ui/title/sources/pokemon_logo.png : sa forme
  n'est jamais retouchée, seules ses couleurs changent — le jaune devient blanc, son ombre
  dorée bleu ciel, le cerne bleu reste (voir `tint`). L'emblème passe un peu dessous ;
- **le mot MIRAGE**, en Gill Sans UltraBold (police livrée avec macOS) : du ciel dans les
  lettres, des nuages à leur pied.

Chacun des trois est aussi gardé à part dans assets/ui/title/parts/ (emblem.png, pokemon.png,
mirage.png), sur la même toile que le logo : posés l'un sur l'autre dans cet ordre, ils le
redonnent, et l'on peut en animer ou en remplacer un seul.

Le mot et le centre de l'emblème sont décrits en SVG, le tout est rendu par `rsvg-convert`
(`brew install librsvg`). Le logo est indépendant du fond et du texte du bas
(title_background.py, title_prompt.py) : n'importe quelle image à fond transparent
peut le remplacer.
"""
import base64
import math
import os
import subprocess
import tempfile
from collections import deque

from island_tiles import ROOT, load, save

TITLE = os.path.join(ROOT, 'src/main/kotlin/fr/skyle/pokeludoworld/assets/ui/title')
LOGO_SOURCE = os.path.join(TITLE, 'sources/pokemon_logo.png')
EMBLEM_SOURCE = os.path.join(TITLE, 'sources/emblem_reference.png')
OUT = os.path.join(TITLE, 'logo.png')

# Dessiné sur 1140×460, rendu au double de la taille d'affichage.
WIDTH, HEIGHT, SCALE = 1140, 460, 1.6

NAVY = (27, 42, 99)
NAVY_HEX = '#1b2a63'
WHITE = '#ffffff'
PALE = '#c3e1fb'

# L'emblème : son coin et sa largeur (sa hauteur suit). Il est posé bas, à cheval entre les
# deux mots, et dessiné AVANT eux : le logo Pokémon et MIRAGE le recouvrent là où ils se croisent.
EMBLEM_X, EMBLEM_Y, EMBLEM_W = 14, 94, 372

# Le logo Pokémon : où il se pose, et à quelle largeur (sa hauteur suit).
LOGO_X, LOGO_Y, LOGO_W = 344, 20, 672

# Les couleurs que prend le jaune du logo : sa face, et l'ombre dorée de son relief.
FACE = (247, 251, 255)
RELIEF = (150, 200, 245)

# Les teintes de l'emblème, de la plus claire à la plus sombre de son dessin d'origine :
# le blanc reste blanc, le gris clair devient bleu pâle, le gris moyen bleu ciel, et ainsi
# jusqu'au noir des traits, qui devient bleu nuit.
SHADES = ((0.97, (255, 255, 255)), (0.80, (198, 226, 251)), (0.62, (116, 184, 246)), (0.40, (74, 141, 231)), (0.0, NAVY))

FONT = "font-family='Gill Sans' font-weight='900' font-size='200'"
# Chaque lettre : son décalage d'encre et sa largeur à 200 px de corps (relevés sur le rendu),
# sa rotation, son décalage vertical — à peine : le mot flotte, il ne danse pas — et de
# combien elle se rapproche de la lettre d'avant. Le G se glisse sous la jambe du A : sans
# cela c'est la seule lettre du mot qui ne touche pas sa voisine.
LETTERS = [
    ('M', 14, 183, -2.0, 0, 0),
    ('I', 15, 66, 1.5, 3, 0),
    ('R', 14, 165, -1.0, -1, 0),
    ('A', 0, 198, 1.5, 2, 0),
    ('G', 10, 156, -1.5, -2, 20),
    ('E', 14, 125, 2.0, 2, 0),
]
SIZE = 0.74          # le mot, par rapport aux lettres relevées à 200 px de corps
CAP = 149 * SIZE
WORD_CENTRE, BASELINE, GAP = LOGO_X + LOGO_W / 2 + 12, 388, 9
DEPTH = 8            # épaisseur du relief du mot, vers le bas à droite


def luminance(pixel):
    return 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]


def tint(pixel):
    """Bleuit un pixel du logo : plus il est jaune, plus il part vers le blanc ou le bleu ciel."""
    r, g, b, a = pixel
    if a == 0: return pixel
    yellow = min(max((min(r, g) - b + 20) / 80.0, 0.0), 1.0)
    if yellow == 0.0: return pixel
    # La face (jaune vif) devient blanche, l'ombre (doré) bleu ciel ; entre les deux, un fondu.
    bright = min(max((r - 205) / 45.0, 0.0), 1.0)
    target = [RELIEF[i] + (FACE[i] - RELIEF[i]) * bright for i in range(3)]
    return tuple(round(pixel[i] + (target[i] - pixel[i]) * yellow) for i in range(3)) + (a,)


def tinted_logo(path):
    width, height, rows = load(LOGO_SOURCE)
    save(path, [[tint(pixel) for pixel in row] for row in rows])
    return width, height


def shade(value):
    """La teinte de l'emblème pour une clarté de 0 à 1 (voir SHADES)."""
    for (high, bright), (low, dark) in zip(SHADES, SHADES[1:]):
        if value >= low:
            t = min((value - low) / (high - low), 1.0)
            return tuple(dark[i] + (bright[i] - dark[i]) * t for i in range(3))
    return NAVY


def recolour(pixel):
    """La couleur de remplissage d'un pixel de l'emblème, une fois passé aux teintes du ciel."""
    value = max(pixel[:3]) / 255.0
    colour = shade(value)
    # Les ailes étaient jaune pâle : elles gardent un soupçon de bleu, pour ne pas se
    # confondre avec le blanc du médaillon.
    yellow = min(max((max(pixel[:3]) - pixel[2]) / max(pixel[:3], default=1) / 0.36, 0.0), 1.0) if max(pixel[:3]) else 0.0
    return tuple(colour[i] + ((232, 244, 255)[i] - colour[i]) * 0.5 * yellow * (1.0 if value > 0.9 else 0.0) for i in range(3))


def recoloured_emblem(path):
    """Détoure l'emblème et le recolore, sans toucher à son dessin. Renvoie aussi son centre doré."""
    width, height, rows = load(EMBLEM_SOURCE)
    light = [[luminance(pixel) for pixel in row] for row in rows]

    # Le fond : tout ce qu'on atteint depuis les bords sans traverser un trait noir.
    outside = [[False] * width for _ in range(height)]
    queue = deque((x, y) for x in range(width) for y in (0, height - 1)) + deque((x, y) for y in range(height) for x in (0, width - 1))
    while queue:
        x, y = queue.popleft()
        if not (0 <= x < width and 0 <= y < height) or outside[y][x] or light[y][x] < 120: continue
        outside[y][x] = True
        queue.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))

    # La bille dorée du centre : on la repère pour dessiner autre chose à sa place.
    gold = [(x, y) for y in range(int(height * 0.3), int(height * 0.75)) for x in range(int(width * 0.35), int(width * 0.7))
            if not outside[y][x] and max(rows[y][x][:3]) > 130 and (max(rows[y][x][:3]) - rows[y][x][2]) / max(rows[y][x][:3]) > 0.38]
    centre = (sum(x for x, _ in gold) / len(gold), sum(y for _, y in gold) / len(gold))
    radius = math.sqrt(len(gold) / math.pi) + 2.0

    out = []
    for y in range(height):
        row = []
        for x in range(width):
            here = light[y][x]
            if outside[y][x]:
                # Le bord extérieur du trait : du bleu nuit, d'autant plus léger que le fond domine.
                near = any(0 <= x + dx < width and 0 <= y + dy < height and not outside[y + dy][x + dx] for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2))
                alpha = min(max((222 - here) / 100.0, 0.0), 1.0) if near else 0.0
                row.append(NAVY + (round(alpha * 255),))
            elif here >= 110:
                row.append(tuple(round(v) for v in recolour(rows[y][x])) + (255,))
            else:
                # Sous le trait : la couleur d'à côté, recouverte d'autant d'encre que le pixel est sombre.
                best, fill = here, rows[y][x]
                for dy in range(-4, 5):
                    for dx in range(-4, 5):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height and not outside[ny][nx] and light[ny][nx] > best: best, fill = light[ny][nx], rows[ny][nx]
                ink = 1.0 if best < 110 else min(max((best - here) / (best - 12.0), 0.0), 1.0)
                base = recolour(fill)
                row.append(tuple(round(base[i] + (NAVY[i] - base[i]) * ink) for i in range(3)) + (255,))
        out.append(row)
    save(path, out)
    return width, height, centre, radius


def word():
    """Les six lettres, chacune posée et à peine tournée autour de son centre."""
    total = sum(width * SIZE - kern for _, _, width, _, _, kern in LETTERS) + GAP * (len(LETTERS) - 1)
    out, x = [], WORD_CENTRE - total / 2
    left = x
    for letter, ink, width, angle, drop, kern in LETTERS:
        x -= kern
        cx, cy = x + width * SIZE / 2, BASELINE - CAP / 2 + drop
        tx, ty = cx - (ink + width / 2), cy + 149 / 2
        out.append(f"<text {FONT} x='{tx:.1f}' y='{ty:.1f}' transform='translate({cx:.1f} {cy:.1f}) rotate({angle}) "
                   f"scale({SIZE}) translate({-cx:.1f} {-cy:.1f})'>{letter}</text>")
        x += width * SIZE + GAP
    return '\n'.join(out), left, x - GAP


def clouds(x0, x1, y, scale=1.0):
    """Une rangée de nuages : des arcs accolés, de tailles inégales."""
    path, x, index = f"M{x0 - 20:.0f},{y + 80} L{x0 - 20:.0f},{y}", x0 - 20, 0
    while x < x1 + 20:
        radius = (17, 25, 14, 21, 28, 16, 23)[index % 7] * scale
        lift = (0, -7, 3, -3, -9, 2, -5)[index % 7] * scale
        path += f" A{radius:.1f},{radius:.1f} 0 0 1 {x + radius * 2:.1f},{y + lift:.1f}"
        x += radius * 2
        index += 1
    return path + f" L{x:.0f},{y + 80} Z"


def emblem_centre(centre, radius, zoom):
    """Ce qui remplace la bille dorée : un disque de ciel, un nuage, un reflet."""
    cx, cy, r = EMBLEM_X + centre[0] * zoom, EMBLEM_Y + centre[1] * zoom, radius * zoom
    return f"""<g clip-path='url(#core)'>
  <circle cx='{cx:.1f}' cy='{cy:.1f}' r='{r:.1f}' fill='url(#coreSky)'/>
  <path d='{clouds(cx - r, cx + r, cy + r * 0.42, 0.42)}' fill='{PALE}'/>
  <path d='{clouds(cx - r - 9, cx + r, cy + r * 0.66, 0.42)}' fill='{WHITE}'/>
  <ellipse cx='{cx - r * 0.38:.1f}' cy='{cy - r * 0.42:.1f}' rx='{r * 0.2:.1f}' ry='{r * 0.34:.1f}' transform='rotate(35 {cx - r * 0.38:.1f} {cy - r * 0.42:.1f})' fill='{WHITE}' opacity='0.9'/>
</g>""", (cx, cy, r)


def svg(logo_data, logo_height, emblem_data, emblem_height, centre, radius, only=None):
    """Le logo entier, ou un seul de ses morceaux ([only] : 'emblem', 'pokemon' ou 'mirage'), sur la même toile."""
    letters, left, right = word()
    top = BASELINE - CAP
    relief = '\n'.join(f"<use href='#word' x='{k * 0.8:.1f}' y='{k}'/>" for k in range(DEPTH, -1, -1))
    core, (cx, cy, r) = emblem_centre(centre, radius, EMBLEM_W / 318.0)
    head = f"""<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' width='{WIDTH * SCALE:.0f}' height='{HEIGHT * SCALE:.0f}' viewBox='0 0 {WIDTH} {HEIGHT}'>
<defs>
  <g id='word'>{letters}</g>
  <clipPath id='inWord'>{letters}</clipPath>
  <clipPath id='core'><circle cx='{cx:.1f}' cy='{cy:.1f}' r='{r:.1f}'/></clipPath>
  <linearGradient id='coreSky' x1='0' y1='0' x2='0' y2='1'>
    <stop offset='0' stop-color='#3f86e6'/><stop offset='1' stop-color='#8cc6f8'/>
  </linearGradient>
  <linearGradient id='face' gradientUnits='userSpaceOnUse' x1='0' y1='{top:.0f}' x2='0' y2='{BASELINE}'>
    <stop offset='0' stop-color='#3f86e6'/><stop offset='0.55' stop-color='#6db5f5'/><stop offset='1' stop-color='#a9d6fb'/>
  </linearGradient>
  <linearGradient id='side' gradientUnits='userSpaceOnUse' x1='0' y1='{top:.0f}' x2='0' y2='{BASELINE + 12}'>
    <stop offset='0' stop-color='#2c4f9e'/><stop offset='1' stop-color='#223a80'/>
  </linearGradient>
  <filter id='soft' x='-10%' y='-20%' width='120%' height='150%'><feGaussianBlur stdDeviation='7'/></filter>
  <!-- un halo clair autour d'une image : elle se détache alors du ciel, sans qu'on touche à sa forme -->
  <filter id='halo' x='-8%' y='-12%' width='116%' height='124%'>
    <feMorphology in='SourceAlpha' operator='dilate' radius='7'/><feGaussianBlur stdDeviation='4' result='spread'/>
    <feFlood flood-color='#ffffff' flood-opacity='0.95'/><feComposite in2='spread' operator='in' result='light'/>
    <feMerge><feMergeNode in='light'/><feMergeNode in='SourceGraphic'/></feMerge>
  </filter>
  <!-- le même, plus fin, pour l'emblème : son trait épais doit rester ce qu'on voit d'abord -->
  <filter id='rim' x='-8%' y='-12%' width='116%' height='124%'>
    <feMorphology in='SourceAlpha' operator='dilate' radius='3'/><feGaussianBlur stdDeviation='1.6' result='spread'/>
    <feFlood flood-color='#ffffff' flood-opacity='0.9'/><feComposite in2='spread' operator='in' result='light'/>
    <feMerge><feMergeNode in='light'/><feMergeNode in='SourceGraphic'/></feMerge>
  </filter>
</defs>

"""
    emblem = f"""<!-- l'emblème, trait pour trait, et son nouveau centre -->
<g filter='url(#rim)'>
  <image x='{EMBLEM_X}' y='{EMBLEM_Y}' width='{EMBLEM_W}' height='{emblem_height:.1f}' href='data:image/png;base64,{emblem_data}'/>
  {core}
</g>

"""
    pokemon = f"""<!-- le logo Pokémon, bleuté, à sa forme exacte : il passe par-dessus l'emblème -->
<image x='{LOGO_X}' y='{LOGO_Y}' width='{LOGO_W}' height='{logo_height:.1f}' filter='url(#halo)' href='data:image/png;base64,{logo_data}'/>

"""
    mirage = f"""<!-- l'ombre portée du mot : elle le détache de n'importe quel fond -->
<g filter='url(#soft)' opacity='0.3' fill='#16245c' stroke='#16245c' stroke-width='26' stroke-linejoin='round'><use href='#word' x='4' y='14'/></g>

<!-- MIRAGE : liseré blanc, cerne bleu nuit, relief, puis la face -->
<g fill='{WHITE}' stroke='{WHITE}' stroke-width='32' stroke-linejoin='round'>{relief}</g>
<g fill='{NAVY_HEX}' stroke='{NAVY_HEX}' stroke-width='18' stroke-linejoin='round'>{relief}</g>
<g fill='url(#side)' stroke='url(#side)' stroke-width='2.5' stroke-linejoin='round'>{relief}</g>
<g fill='{NAVY_HEX}' stroke='{NAVY_HEX}' stroke-width='4' stroke-linejoin='round'><use href='#word'/></g>
<g fill='url(#face)'><use href='#word'/></g>
<g clip-path='url(#inWord)'>
  <path d='{clouds(left, right, BASELINE - 28, 1.25)}' fill='{PALE}'/>
  <path d='{clouds(left - 30, right, BASELINE - 13, 1.25)}' fill='{WHITE}'/>
  <path d='M{left - 30:.0f},{top - 20:.0f} H{right + 30:.0f} V{top + 18:.0f} Q{(left + right) / 2 + 140:.0f},{top + 38:.0f} {(left + right) / 2:.0f},{top + 22:.0f} T{left - 30:.0f},{top + 28:.0f} Z' fill='#ffffff' opacity='0.28'/>
</g>
"""
    # L'emblème d'abord : les deux mots passent par-dessus.
    pieces = {'emblem': emblem, 'pokemon': pokemon, 'mirage': mirage}
    return head + ''.join(piece for name, piece in pieces.items() if only in (None, name)) + '</svg>\n'



def encoded(path):
    return base64.b64encode(open(path, 'rb').read()).decode('ascii')


if __name__ == '__main__':
    os.makedirs(os.path.join(TITLE, 'parts'), exist_ok=True)
    with tempfile.TemporaryDirectory() as work:
        logo, emblem = os.path.join(work, 'pokemon_logo.png'), os.path.join(work, 'emblem.png')
        logo_w, logo_h = tinted_logo(logo)
        emblem_w, emblem_h, centre, radius = recoloured_emblem(emblem)
        pieces = (encoded(logo), LOGO_W * logo_h / logo_w, encoded(emblem), EMBLEM_W * emblem_h / emblem_w, centre, radius)
        # Le logo entier, puis chacun de ses morceaux seul, sur la même toile : posés l'un sur
        # l'autre dans cet ordre (emblem, pokemon, mirage), ils redonnent logo.png.
        for only, target in ((None, OUT), ('emblem', os.path.join(TITLE, 'parts/emblem.png')),
                             ('pokemon', os.path.join(TITLE, 'parts/pokemon.png')), ('mirage', os.path.join(TITLE, 'parts/mirage.png'))):
            source = os.path.join(work, 'logo.svg')
            with open(source, 'w') as handle:
                handle.write(svg(*pieces, only=only))
            subprocess.run(['rsvg-convert', source, '-o', target], check=True)
    print('logo.png ecrit dans', os.path.relpath(TITLE, ROOT), '(et parts/emblem.png, parts/pokemon.png, parts/mirage.png)')
