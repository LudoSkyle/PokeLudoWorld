#!/usr/bin/env python3
"""Découpe le lampadaire dans l'atlas et adoucit un peu son cerne : assets/levels/street_lamp.png.

Dans `environments.png`, le lampadaire est cerné de gris presque noir ; à côté des tuiles de la
Route 1, cernées de brun, il ressort un peu trop (Ludovic, 17/11/2026 : « un tout petit peu »).
Ses deux teintes les plus sombres s'éclaircissent d'un cran, rien d'autre ne bouge. L'atlas, lui,
n'est pas retouché : la planche découpée vit à part.

    python3 tools/street_lamp.py
"""
import os
from island_tiles import load, save

LEVELS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'main', 'kotlin', 'fr', 'skyle', 'pokeludoworld', 'assets', 'levels')
REGION = (1362, 279, 14, 36)          # la lanterne de bois, à tête carrée : l'atlas n'en a pas de suspendue, c'est son modèle le plus chaud (le globe gris d'avant est en 1314)
SOFT = {(45, 45, 45): (88, 68, 48)}          # son cerne presque noir prend un brun de bois sombre

if __name__ == '__main__':
    _, _, atlas = load(os.path.join(LEVELS, 'environments.png'))
    x0, y0, w, h = REGION
    art = [[(SOFT.get(tuple(p[:3]), tuple(p[:3])) + (p[3],)) if p[3] else (0, 0, 0, 0) for p in row[x0:x0 + w]] for row in atlas[y0:y0 + h]]
    save(os.path.join(LEVELS, 'street_lamp.png'), art)
    print('street_lamp.png : %d x %d' % (w, h))
