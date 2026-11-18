#!/usr/bin/env python3
"""La carte d'exemple, refaite par notre constructeur : reference.png contre ce que bâtit `tools/mapgen/build.py`.

    python3 tools/maps/ice_cave/compare.py                       # écrit plan.toml, le bâtit, compare
    python3 tools/maps/ice_cave/compare.py --preview /tmp/x.png  # et garde l'image bâtie
    python3 tools/maps/ice_cave/compare.py --map                 # et montre où ça diffère

C'est le juge de paix du décor `cave_ice` (Ludovic, 18/11/2026 : « tu dois être capable de générer la même map que
l'exemple, vu que tu as le même set — tant que tu n'y arrives pas, c'est que tes règles de placement ne sont pas les
bonnes »). On ne donne au constructeur que **quatre classes de cases** lues sur le relevé (`survey.json`) — le vide,
le sol, la glace lisse, la paroi — et il doit en tirer la même image. Aucune tuile ne lui est soufflée.

L'image d'exemple est un JPEG : deux cases identiques y diffèrent de quelques unités. Une case est dite **refaite**
quand son écart moyen par pixel et par canal reste sous `SAME` ; le bruit du JPEG seul en donne 6 ou 7.
Ce que le plan ne dit pas — les rochers, les échelles, les raccords que l'auteur a faits à la main entre deux lobes —
reste en écart, et c'est attendu : on le compte à part.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'mapgen'))
from island_tiles import load  # noqa: E402
import build as builder  # noqa: E402

SAME = 14.0
PLAN = os.path.join(HERE, 'plan.toml')
# les tuiles de la planche qui sont des objets posés : sous elles, on lit la classe de la tuile du dessous
OBJECTS = {(7, 0), (5, 1), (5, 2), (6, 1), (6, 2), (6, 8), (7, 8), (6, 9), (7, 9), (8, 7), (9, 7), (10, 7), (9, 8), (10, 8),
           (7, 1), (8, 1), (7, 2), (8, 2), (12, 4), (12, 5), (7, 3), (8, 3), (6, 4), (7, 4), (8, 4), (6, 5), (7, 5), (8, 5),
           (15, 4), (15, 5), (16, 1), (5, 10), (6, 10), (7, 10)}
# ce qu'un objet cache : lu sur l'image, case par case (x, y) → classe
BY_HAND = {(6, 4): '^', (7, 4): '^', (6, 5): '^', (7, 5): '^', (21, 1): '^', (22, 1): '^', (21, 2): '^', (22, 2): '^'}


def classes():
    survey = json.load(open(os.path.join(HERE, 'survey.json')))
    W, H = survey['size']
    def floor(t): return t is not None and ((t[0] <= 2 and 11 <= t[1] <= 13) or (3 <= t[0] <= 4 and 11 <= t[1] <= 12))
    def slick(t): return t is not None and ((5 <= t[0] <= 7 and 13 <= t[1] <= 15) or (8 <= t[0] <= 9 and 13 <= t[1] <= 14))
    grid = [['#'] * W for _ in range(H)]
    hidden = set()
    for x, y, top, base, _ in survey['cells']:
        top, base = tuple(top) if top else None, tuple(base) if base else None
        if top is None and base is None: continue
        bare = top is None or top in OBJECTS
        grid[y][x] = '.' if bare and floor(base) else ',' if bare and slick(base) else '^'
        if top in OBJECTS: hidden.add((x, y))
    for (x, y), k in BY_HAND.items(): grid[y][x] = k
    return W, H, grid, hidden


def main():
    W, H, grid, hidden = classes()
    start = next((x, y) for y in range(H - 1, -1, -1) for x in range(W) if grid[y][x] == '.')
    objects = [['.'] * W for _ in range(H)]
    objects[start[1]][start[0]] = '*'
    q = "'''"
    with open(PLAN, 'w', encoding='utf-8') as f:
        f.write("# La carte d'exemple de la grotte de glace, réduite à quatre classes de cases. Écrit par compare.py.\n\n")
        f.write('terrain = %s\n%s\n%s\n\nobjects = %s\n%s\n%s\n\nprops = %s\n%s\n\n' % (q, '\n'.join(''.join(r) for r in grid), q, q, '\n'.join(''.join(r) for r in objects), q, q, q))
        f.write('[map]\nname = "exemple_grotte_glace"\ntheme = "cave_ice"\nstyle = "cave"\nstart = "*"\nlocation = "Exemple"\ndaylight = false\ntiers = 1\n')
    built = builder.build(builder.Plan(PLAN))
    out = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else os.path.join('/tmp', 'exemple_grotte_glace.png')
    builder.preview(built, out)
    rw, rh, ref = load(os.path.join(HERE, 'reference.png'))
    mw, mh, mine = load(out)
    cave, same, bad = 0, 0, []
    for y in range(H):
        for x in range(W):
            if grid[y][x] == '#' and max(max(ref[y * 16 + j][x * 16 + i][:3]) for j in range(16) for i in range(16)) < 30: continue
            if (x, y) in hidden: continue
            cave += 1
            d = (sum((ref[y * 16 + j][x * 16 + i][c] - mine[y * 16 + j][x * 16 + i][c]) ** 2 for j in range(16) for i in range(16) for c in range(3)) / 768.0) ** 0.5
            if d <= SAME: same += 1
            else: bad.append((x, y, d))
    print('%d cases comparées (%d sous un objet, laissées) : %d refaites, %d en écart — %.1f %%' % (cave, len(hidden), same, len(bad), 100.0 * same / cave))
    for line in built['warn'][:6]: print('  constructeur : ' + line)
    if '--map' in sys.argv:
        marks = {(x, y) for x, y, _ in bad}
        for y in range(H):
            print('  ' + ''.join('X' if (x, y) in marks else ('o' if (x, y) in hidden else grid[y][x].replace('#', ' ')) for x in range(W)))
    print('image bâtie : ' + out)


main()
