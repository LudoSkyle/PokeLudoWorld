#!/usr/bin/env python3
"""Assemble les captures entières des cartes du dehors en une seule image : la carte complète.

    python3 tools/maps/world.py <dossier des captures> <sortie.png> [échelle]

Chaque carte est posée à sa place dans le monde, en cases : la Route 1 en haut, l'île de départ
dessous, décalée de `SEAM` colonnes — là où leurs pistes se rejoignent (voir seam.py). Les
captures se prennent dans le jeu, une par carte, à un pixel par pixel (`w_capture_<carte>.png`).
Une nouvelle carte s'ajoute à `PLACES`.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from island_tiles import load, save  # noqa: E402

SEAM = 41                                     # la colonne de la Route 1 sous laquelle tombe la colonne 0 de l'île
PLACES = {'route_1': (0, 0), 'start_island': (SEAM, 50)}          # carte : (colonne, rangée) de son coin haut-gauche dans le monde
VOID = (22, 24, 34, 255)                      # là où il n'y a pas (encore) de carte

if __name__ == '__main__':
    folder, out = sys.argv[1], sys.argv[2]
    scale = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    shots = {name: load(os.path.join(folder, 'w_capture_%s.png' % name)) for name in PLACES}
    width = max(PLACES[n][0] * 16 + shots[n][0] for n in PLACES)
    height = max(PLACES[n][1] * 16 + shots[n][1] for n in PLACES)
    world = [[VOID] * width for _ in range(height)]
    for name, (w, h, rows) in shots.items():
        x0, y0 = PLACES[name][0] * 16, PLACES[name][1] * 16
        for y in range(h): world[y0 + y][x0:x0 + w] = [tuple(p[:3]) + (255,) for p in rows[y]]
    save(out, [[p for p in row for _ in range(scale)] for row in world for _ in range(scale)])
    print('%s : %d x %d cases, %d x %d pixels' % (os.path.basename(out), width // 16, height // 16, width * scale, height * scale))
