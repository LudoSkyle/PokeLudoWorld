#!/usr/bin/env python3
"""Tire d'une carte qui existe le plan qui la refait à l'identique.

    python3 tools/mapgen/scene_to_plan.py <scène.tscn> <nom du plan> [décor]

Lit les calques de tuiles de la scène et écrit `plans/<nom>.toml` : un calque par `[[layer]]`, chaque tuile sous le
signe que lui donne la légende du calque, et tout ce qui est debout (arbres, rochers) dans `props`. Le constructeur
(`build.py`) refait la carte à partir de ce plan ; `compare.py` compte les cases qui diffèrent — il n'en reste aucune.

Ce qui n'est pas une tuile (panneaux, personnages, portes) n'est pas repris : ce sont des tables du plan, à écrire.
"""
import base64
import os
import re
import struct
import sys
import tomllib

HERE = os.path.dirname(os.path.abspath(__file__))
SIGNS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*/=%&#@$!?<>()[]{}^~:;,_|'


def layers(path):
    """Les calques de tuiles d'une scène, dans l'ordre : (nom, parent, {(x, y): (source, colonne, rangée, variante)})."""
    text = open(path, encoding='utf-8').read()
    out = []
    for name, parent, data in re.findall(r'\[node name="(\w+)" type="TileMapLayer" parent="([^"]*)"[^\]]*\]\n(?:[a-z_]+ = [^\n]*\n)*?tile_map_data = PackedByteArray\("([^"]*)"\)', text):
        raw = base64.b64decode(data)
        cells = {}
        for i in range(2, len(raw), 12):
            x, y, source, ax, ay, alt = struct.unpack('<hhHHHH', raw[i:i + 12])
            cells[(x, y)] = (source, ax, ay, alt)
        out.append((name, parent, cells))
    return out


if __name__ == '__main__':
    if len(sys.argv) < 3: sys.exit(__doc__)
    scene, name, theme_name = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else 'coast')
    with open(os.path.join(HERE, 'themes', theme_name + '.toml'), 'rb') as f: theme = tomllib.load(f)
    main, buildings = theme['sources']['main']['id'], theme['sources']['buildings']['id']
    tall, blooms = theme['sources']['tall_grass'], theme['sources']['blooms']
    tiles = {(main, t[0], t[1]): n for n, t in theme['tiles'].items()}
    props = {(main if p['source'] == 'main' else buildings, p['at'][0], p['at'][1]): (n, p) for n, p in theme['props'].items()}
    found = layers(scene)
    W = 1 + max(c[0] for _, _, cells in found for c in cells); H = 1 + max(c[1] for _, _, cells in found for c in cells)
    out, listed, unknown = [], [], {}
    for lname, parent, cells in found:
        if lname in ('Trees', 'Props', 'Houses'):          # ce qui est debout : une ligne par chose
            for (x, y), t in sorted(cells.items(), key=lambda kv: (kv[0][1], kv[0][0])):
                if t[0] == blooms['id']:
                    if t[2] == blooms['foot']: listed.append('bloom%d %d %d' % (t[1], x, y))
                elif t[:3] in props and props[t[:3]][1]['layer'] == lname: listed.append('%s %d %d' % (props[t[:3]][0], x + props[t[:3]][1]['anchor'], y))
                else: listed.append('@%d:%d,%d %d %d %s' % (t[0], t[1], t[2], x, y, lname)); unknown.setdefault(lname, set()).add(t[:3])          # pas de nom dans le décor : sa planche et sa case
            continue
        legend, grid = {}, [['.'] * W for _ in range(H)]
        for (x, y), t in sorted(cells.items(), key=lambda kv: (kv[0][1], kv[0][0])):
            if not (0 <= x < W and 0 <= y < H): continue
            tname = 'tall_grass' if (t[0], t[1], t[2]) == (tall['id'], *tall['at']) else tiles.get(t[:3]) or (props[t[:3]][0] if t[:3] in props else None)
            if tname is None: tname = '@%d:%d,%d' % t[:3]; unknown.setdefault(lname, set()).add(t[:3])
            key = (tname, t[3])
            if key not in legend:
                if len(legend) >= len(SIGNS): sys.exit('calque %s : plus de %d tuiles différentes' % (lname, len(SIGNS)))
                legend[key] = SIGNS[len(legend)]
            grid[y][x] = legend[key]
        out += ['', '[[layer]]', 'name = "%s"' % lname, "grid = '''", *(''.join(r) for r in grid), "'''", '[layer.legend]']
        out += ['"%s" = %s' % (sign.replace('\\', '\\\\').replace('"', '\\"'), ('"%s"' % key[0]) if key[1] == 0 else '["%s", %d]' % key) for key, sign in legend.items()]
    head = ['# Le plan de %s, relevé tuile par tuile par tools/mapgen/scene_to_plan.py.' % os.path.basename(scene),
            '# Chaque calque est une grille de signes ; sa légende dit quelle tuile du décor chaque signe pose.', '',
            "props = '''", *listed, "'''", '', '[map]', 'name = "%s"' % name, 'theme = "%s"' % theme_name]
    meta = dict(re.findall(r'metadata/(\w+) = "?([^"\n]*)"?', open(scene, encoding='utf-8').read()))
    for key in ('location', 'banner', 'music', 'wild'):
        if key in meta: head.append('%s = "%s"' % (key, meta[key]))
    target = os.path.join(HERE, 'plans', name + '.toml')
    open(target, 'w', encoding='utf-8').write('\n'.join(head + out) + '\n')
    print('%s : %d x %d, %d calques, %d choses posées -> %s' % (os.path.basename(scene), W, H, len(found), len(listed), os.path.relpath(target)))
    for lname, what in unknown.items(): print('  (calque %s : %d tuiles sans nom dans le décor %s, reprises par leur planche et leur case)' % (lname, len(what), theme_name))
