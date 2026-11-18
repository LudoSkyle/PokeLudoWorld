#!/usr/bin/env python3
"""Fabrique le texte du bas de l'écran titre : « PRESS ENTER ».

    python3 tools/title_prompt.py

Sort assets/ui/title/prompt.png, en pixels de jeu (affiché à l'échelle 4) : des lettres
blanches dessinées ici même, point par point, cernées de bleu nuit et posées sur une ombre
d'un pixel, pour se lire sur n'importe quel fond.

Le texte est indépendant du fond et du logo (title_background.py, title_logo.py) : n'importe
quelle image à fond transparent peut le remplacer. Pour un autre texte, changer TEXT et
ajouter à GLYPHS les lettres qui manquent.
"""
import os

from island_tiles import ROOT, save

OUT = os.path.join(ROOT, 'src/main/kotlin/fr/skyle/pokemonmirage/assets/ui/title/prompt.png')
TEXT = 'PRESS ENTER'

INK = (255, 255, 255, 255)
SHINE = (207, 232, 252, 255)   # le bas des lettres tire sur le bleu du ciel, comme le logo
OUTLINE = (27, 42, 99, 255)
CLEAR = (0, 0, 0, 0)
SPACING, SPACE = 2, 5

GLYPHS = {
    'P': ('######.',
          '##...##',
          '##...##',
          '##...##',
          '######.',
          '##.....',
          '##.....',
          '##.....',
          '##.....'),
    'R': ('######.',
          '##...##',
          '##...##',
          '##...##',
          '######.',
          '##.##..',
          '##..##.',
          '##...##',
          '##...##'),
    'E': ('#######',
          '##.....',
          '##.....',
          '##.....',
          '######.',
          '##.....',
          '##.....',
          '##.....',
          '#######'),
    'S': ('.#####.',
          '##...##',
          '##.....',
          '##.....',
          '.#####.',
          '.....##',
          '.....##',
          '##...##',
          '.#####.'),
    'T': ('########',
          '...##...',
          '...##...',
          '...##...',
          '...##...',
          '...##...',
          '...##...',
          '...##...',
          '...##...'),
    'N': ('##...##',
          '###..##',
          '###..##',
          '####.##',
          '##.####',
          '##..###',
          '##..###',
          '##...##',
          '##...##'),
    'A': ('..###..',
          '.##.##.',
          '##...##',
          '##...##',
          '##...##',
          '#######',
          '##...##',
          '##...##',
          '##...##'),
}
TALL = 9


def build():
    # Les lettres d'abord, sur une grille qui laisse la place du cerne et de l'ombre.
    width = sum(SPACE if c == ' ' else len(GLYPHS[c][0]) + SPACING for c in TEXT) - SPACING + 2
    height = TALL + 3
    ink = [[False] * width for _ in range(height)]
    x = 1
    for letter in TEXT:
        if letter == ' ':
            x += SPACE
            continue
        for row, line in enumerate(GLYPHS[letter]):
            for column, mark in enumerate(line):
                if mark == '#': ink[1 + row][x + column] = True
        x += len(GLYPHS[letter][0]) + SPACING

    def inked(px, py):
        return 0 <= px < width and 0 <= py < height and ink[py][px]

    rows = [[CLEAR] * width for _ in range(height)]
    for y in range(height):
        for x in range(width):
            if ink[y][x]:
                rows[y][x] = SHINE if y - 1 >= TALL - 3 else INK
            # Le cerne touche la lettre par un côté ou un coin ; l'ombre la prolonge d'un pixel vers le bas.
            elif any(inked(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)) or any(inked(x + dx, y - 2) for dx in (-1, 0, 1)):
                rows[y][x] = OUTLINE
    return rows


if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    save(OUT, build())
    print('prompt.png ecrit dans', os.path.relpath(os.path.dirname(OUT), ROOT))
