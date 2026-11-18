#!/usr/bin/env python3
"""Le balayage : le générateur tient-il sur des graines qu'on n'a jamais regardées ?

    python3 tools/mapgen/sweep.py 7,64,333              huit formes de route et sept styles (plage, côte, montagne, forêt, village, champs, grotte) × ces graines, tailles et caractères variés
    python3 tools/mapgen/sweep.py 7,64,333 --only cave  un seul style (ou plusieurs, séparés par des virgules)
    python3 tools/mapgen/sweep.py 7,64,333 --keep DIR   garder mondes, plans et aperçus dans DIR (sinon un dossier temporaire)

Pour chaque monde : son taux de composition (`check.py`), s'il est **jouable**, et les règles qu'il enfreint. Rien
n'est écrit dans le dépôt.

À quoi il sert : un réglage du générateur se juge sur des mondes qu'on n'a pas eus sous les yeux en le faisant. Après
une retouche de `worldgen.py`, on balaie des graines **neuves** — celles sur lesquelles on vient de corriger ne
prouvent rien. Sort en erreur si un monde est injouable ou sous 85 %.
"""
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SHAPES = ['free', 'island', 'ring', 'plain', 'coast', 'bay', 'corridor', 'archipelago', 'beach', 'seaside', 'mountain', 'forest', 'village', 'fields', 'cave']          # (les sept derniers sont des styles, pas des formes ; la mer ouverte change de côté avec la graine)
KINDS = ('beach', 'seaside', 'mountain', 'forest', 'village', 'fields', 'cave')
SIDES = ['south', 'west', 'north', 'east']
CHARACTERS = [[], ['rocky'], ['sandy'], ['wooded'], ['wet', 'jagged'], ['flowery', 'open']]
WORLD = '[map]\nname = "%s"\nlocation = "Essai"\ntheme = "coast"\n\n[seed]\nworld = %d\n\n[style]\nsize = "%s"\n%s\ncharacter = [%s]\n'

if __name__ == '__main__':
    args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and sys.argv[i - 1] not in ('--keep', '--only')]
    if not args: sys.exit(__doc__)
    seeds = [int(a) for a in args[0].split(',')]
    folder = sys.argv[sys.argv.index('--keep') + 1] if '--keep' in sys.argv else tempfile.mkdtemp(prefix='mapgen_sweep_')
    os.makedirs(folder, exist_ok=True)
    rows = []
    only = sys.argv[sys.argv.index('--only') + 1].split(',') if '--only' in sys.argv else SHAPES
    for s, shape in enumerate(SHAPES):
        if shape not in only: continue
        for k, seed in enumerate(seeds):
            character = CHARACTERS[(k + s) % len(CHARACTERS)]
            size = ['small', 'medium'][k % 2] if shape == 'corridor' else ['medium', 'small', 'large'][k % 3]
            name = 'sweep_%s_%d' % (shape, seed)
            world = os.path.join(folder, name + '.toml')
            form = 'kind = "%s"\nsea = "%s"' % (shape, SIDES[(k + seed) % 4]) if shape in KINDS else 'shape = "%s"' % shape
            with open(world, 'w', encoding='utf-8') as f: f.write(WORLD % (name, seed, size, form, ', '.join('"%s"' % c for c in character)))
            start = time.time()
            try:
                run = subprocess.run([sys.executable, os.path.join(HERE, 'worldgen.py'), world, '--plan', os.path.join(folder, name + '.plan.toml'),
                                      '--preview', os.path.join(folder, name + '.png')], capture_output=True, text=True, timeout=300)
                out = run.stdout + run.stderr
            except subprocess.TimeoutExpired:
                out = 'trop long : arrêté après cinq minutes'
            found = re.search(r'composition : (\d+) %', out)
            rate, stuck = (int(found.group(1)) if found else None), 'INJOUABLE' in out
            broken = ['%s %s' % b for b in re.findall(r'^  !! (\S) (.{0,44})', out, re.M)]
            rows.append((rate, stuck))
            print('%-26s %-6s %-14s %5s %-9s %3.0f s  %s' % (name, size, ','.join(character) or '-', ('%d %%' % rate) if found else 'ERREUR', 'INJOUABLE' if stuck else '',
                                                              time.time() - start, ' | '.join(broken) if found else (out.strip().splitlines() or [''])[-1][:160]), flush=True)
    rated = [r for r, _ in rows if r is not None]
    good = sum(1 for r, stuck in rows if r is not None and r >= 85 and not stuck)
    print('\n%d mondes : %d jouables à 85 %% ou plus, %d injouables, %d en erreur — taux moyen %.0f %%, le plus bas %d %%'
          % (len(rows), good, sum(1 for _, stuck in rows if stuck), len(rows) - len(rated), sum(rated) / max(1, len(rated)), min(rated or [0])))
    print('mondes, plans et aperçus : ' + folder)
    sys.exit(0 if good == len(rows) else 1)
