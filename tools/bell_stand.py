#!/usr/bin/env python3
"""Adoucit le cerne du socle de la cloche : assets/levels/bell_stand.png.

Le socle vient d'une planche cernée de gris presque noir ; à côté des tuiles de la Route 1,
cernées de brun, il ressort trop (Ludovic, 17/11/2026). Son cerne opaque prend un gris-brun de
pierre ; ses ombres translucides ne bougent pas. Relancer ne change plus rien : la teinte
d'origine n'y est plus.

    python3 tools/bell_stand.py
"""
import os
from island_tiles import load, save

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'main', 'kotlin', 'fr', 'skyle', 'pokeludoworld', 'assets', 'levels', 'bell_stand.png')
SOFT = {(32, 32, 32, 255): (80, 72, 62, 255)}

if __name__ == '__main__':
    _, _, rows = load(PATH)
    changed = sum(1 for row in rows for p in row if tuple(p) in SOFT)
    save(PATH, [[SOFT.get(tuple(p), tuple(p)) for p in row] for row in rows])
    print('%d pixels de cerne adoucis' % changed)
