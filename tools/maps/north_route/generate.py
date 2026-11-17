#!/usr/bin/env python3
"""Fabrique la route du nord : scenes/levels/north_route.tscn.

    python3 tools/maps/north_route/generate.py                 # contrôle seulement, n'écrit rien
    python3 tools/maps/north_route/generate.py --write         # écrit la scène, et les sources de la route dans le TileSet
    python3 tools/maps/north_route/generate.py --preview a.png # la carte telle que le jeu la dessinera, sans passer par Godot
    python3 tools/maps/north_route/generate.py --compare       # les cases qui diffèrent de la carte d'exemple, au pixel près
    python3 tools/maps/north_route/generate.py --map           # ~ eau, # plein, = pont, S marche, o objet, . atteignable, ? libre mais coupé du reste
    python3 tools/maps/north_route/generate.py --grid g.txt    # la grille pleine / libre attendue, à comparer à celle du moteur

La chaîne, dans l'ordre où on la relance quand quelque chose change :

    tools/route_tiles.py     découpe route.png dans la planche de l'exemple (puis réimporter dans Godot)
    survey.py                relève reference.png tuile par tuile -> survey.json
    layout.py                pose chaque tuile relevée dans son calque, ouvre la trouée du sud, calcule ce qui bloque
    generate.py              pose objets, personnages et portes, contrôle, écrit la scène et le TileSet

Les sources 11 (`route`), 12 et 13 (ses hautes herbes) du TileSet sont **réécrites en entier** à
chaque `--write`, à partir du catalogue de `route_tiles.py` : une collision ne se retouche pas
dans l'éditeur, elle se déclare dans `route_tiles.blocks` ou `layout.feet`.

Relancer ce script écrase la scène : une retouche faite dans l'éditeur se refait ici.
"""
import base64
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as gen  # noqa: E402
from layout import L, W, H, ROOT, route_tiles  # noqa: E402

B = os.path.join(ROOT, 'src', 'main', 'kotlin', 'fr', 'skyle', 'pokeludoworld') + os.sep
RES = 'res://src/main/kotlin/fr/skyle/pokeludoworld/'
LEVELS = RES + 'scenes/levels/'
TS = B + 'resources/tilesets/level.tres'
WATER_MATERIAL = 'SubResource("ShaderMaterial_water")'
def px(c): return (c[0] * 16 + 8, c[1] * 16 + 8)
def polygon(cells):
    """Le rectangle qui couvre ces cases, comptées depuis la case où la tuile est posée."""
    xs, ys = [c[0] for c in cells], [c[1] for c in cells]
    x0, x1, y0, y1 = min(xs) * 16 - 8, max(xs) * 16 + 8, min(ys) * 16 - 8, max(ys) * 16 + 8
    return 'PackedVector2Array(%d, %d, %d, %d, %d, %d, %d, %d)' % (x0, y0, x1, y0, x1, y1, x0, y1)


# ------------------------------------------------------------------ TileSet
def route_sources():
    """Le texte des trois sources de la route, d'après le catalogue de route_tiles.py."""
    made, at, sizes = route_tiles.cells(), route_tiles.atlas(), route_tiles.sizes()
    names = {}
    for name, where in at.items(): names.setdefault(where, name)
    inside = {(at[n][0] + i, at[n][1] + j) for n, (w, h) in sizes.items() for i in range(w) for j in range(h + route_tiles.drop(n))}
    grass = {at['tall'], at['tall_pressing'], at['tall_pressed']}
    out = ['[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_route"]', 'resource_name = "route"', 'texture = ExtResource("8_route")']
    for name, (w, h) in sorted(sizes.items(), key=lambda kv: at[kv[0]]):          # ce qui est debout : une seule tuile, posée sur la case en bas à gauche de son pied
        if name in route_tiles.MIXED_TREES: continue          # les arbres à deux essences ne servent qu'au relevé
        key, below = '%d:%d' % at[name], route_tiles.drop(name)          # `below` : les rangées d'ombre dessinées sous la case du pied
        out += ['%s/size_in_atlas = Vector2i(%d, %d)' % (key, w, h + below), '%s/0 = 0' % key, '%s/0/texture_origin = Vector2i(%d, %d)' % (key, -8 * (w - 1), 8 * (h - below - 1)),
                '%s/0/y_sort_origin = %d' % (key, -2 if name.startswith('tree') else -1)]          # un arbre passe derrière ce qui est planté sur sa rangée
        feet = gen.feet(name, 0, 0)
        if feet: out.append('%s/0/physics_layer_0/polygon_0/points = %s' % (key, polygon(feet)))
    for where in sorted(made):
        if where in inside or where in grass: continue
        name, key = names[where], '%d:%d' % where
        wet = name == 'water' or route_tiles.family(name) in ('deep', 'sand')
        if route_tiles.blocks(name): out.append('%s/next_alternative_id = 2' % key)
        out.append('%s/0 = 0' % key)
        if wet: out.append('%s/0/material = %s' % (key, WATER_MATERIAL))
        if route_tiles.jump(name): out.append('%s/0/custom_data_2 = Vector2i(%d, %d)' % ((key,) + route_tiles.jump(name)))          # le sens où ce rebord se saute (CharacterMovement.tryJump)
        if route_tiles.blocks(name):
            out += ['%s/0/physics_layer_0/polygon_0/points = %s' % (key, polygon([(0, 0)])), '%s/1 = 1' % key]          # la variante 1 : le même dessin, sans collision (sous un pont, sous un escalier)
            if wet: out.append('%s/1/material = %s' % (key, WATER_MATERIAL))
    tall = at['tall'][1] * 16
    out += ['', '[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_route_grass"]', 'resource_name = "route_grass"', 'texture = ExtResource("8_route")',
            'margins = Vector2i(0, %d)' % tall, '6:0/0 = 0', '7:0/0 = 0', '8:0/0 = 0',
            '', '[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_route_grass_front"]', 'resource_name = "route_grass_front"', 'texture = ExtResource("8_route")',
            'margins = Vector2i(0, %d)' % (tall + 12), 'separation = Vector2i(0, 12)', 'texture_region_size = Vector2i(16, 4)']
    for column in (6, 7, 8): out += ['%d:0/0 = 0' % column, '%d:0/0/texture_origin = Vector2i(0, -6)' % column, '%d:0/0/y_sort_origin = 2' % column]
    return '\n'.join(out) + '\n'


def patch_tileset(write):
    s = open(TS).read()
    s = re.sub(r'\[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_route[^\n]*\n(?:[^\[\n][^\n]*\n)*\n?', '', s)          # les anciennes sources de la route
    s = re.sub(r'^sources/1[123] = [^\n]*\n', '', s, flags=re.M)
    texture = '[ext_resource type="Texture2D" path="%sassets/levels/route.png" id="8_route"]' % RES
    if texture not in s:
        island = '[ext_resource type="Texture2D" path="%sassets/levels/island.png" id="7_island"]' % RES
        assert s.count(island) == 1
        s = s.replace(island, island + '\n' + texture)
    if 'custom_data_layer_2/name = "jump"' not in s:          # la donnée des rebords qui se sautent : un Vector2i (type 6)
        last = 'custom_data_layer_1/type = 1\n'
        assert s.count(last) == 1
        s = s.replace(last, last + 'custom_data_layer_2/name = "jump"\ncustom_data_layer_2/type = 6\n')
    assert s.count('\n[resource]') == 1
    s = s.replace('\n[resource]', '\n' + route_sources() + '\n[resource]')
    s = s.rstrip('\n') + '\nsources/11 = SubResource("TileSetAtlasSource_route")\nsources/12 = SubResource("TileSetAtlasSource_route_grass")\nsources/13 = SubResource("TileSetAtlasSource_route_grass_front")\n'
    changed = s != open(TS).read()
    if write and changed: open(TS, 'w').write(s)
    return s, changed


for w_ in gen.WARN: print('  !!', w_)
print(gen.summary())
ts, changed = patch_tileset('--write' in sys.argv)
print('TileSet :', 'sources de la route à réécrire' if changed else 'à jour')
declared = set(re.findall(r'^(\d+):(\d+)/0 = 0$', ts[ts.index('id="TileSetAtlasSource_route"]'):ts.index('id="TileSetAtlasSource_route_grass"]')], flags=re.M))
missing = sorted({(n, t) for n, cells_ in L.items() for t in cells_.values() if t[0] == gen.SOURCE and (str(t[1]), str(t[2])) not in declared})
print('tuiles posées mais non déclarées :', missing or 'aucune')

# ------------------------------------------------------------------ objets, personnages, portes
SOLID = set(gen.SOLID)
nodes = []
def node(text): nodes.append(text)
TEXTS = {'SignSouth': "Route du nord.|Au sud : Bourg-Ludo.", 'SignEast': "Route de l'est.|Le chemin n'est pas encore tracé.", 'SignNorth': "Route du nord.|La montagne est droit devant."}
for name, c in gen.SIGNS.items():
    node('[node name="%s" parent="World" instance=ExtResource("3_sign")]\nposition = Vector2(%d, %d)\ntext = "%s"\n' % (name, *px(c), TEXTS[name]))
FOUND = {'ItemRoutePotion': ('potion', "Vous trouvez une Potion !|Vous rangez la Potion dans la poche Objets.", 'found_route_potion'),
         'ItemRouteAntidote': ('antidote', "Vous trouvez un Antidote !|Vous rangez l'Antidote dans la poche Objets.", 'found_route_antidote'),
         'ItemRouteBall': ('poke_ball', "Vous trouvez une Poké Ball !|Vous rangez la Poké Ball dans la poche Poké Balls.", 'found_route_ball'),
         'ItemRouteSuper': ('super_potion', "Vous trouvez une Super Potion !|Vous rangez la Super Potion dans la poche Objets.", 'found_route_super')}
for name, c in gen.ITEMS.items():
    item, text, flag = FOUND[name]
    node('''[node name="%s" parent="World" instance=ExtResource("9_readable")]
position = Vector2(%d, %d)
kind = "item"
text = "@give:%s %s"
flag = "%s"

[node name="Ball" type="Sprite2D" parent="World/%s"]
texture = ExtResource("12_island")
region_enabled = true
region_rect = Rect2(48, 96, 16, 16)
''' % (name, *px(c), item, text, flag, name))
node('[node name="Entities" type="Node2D" parent="World"]\ny_sort_enabled = true\n')

KEEP_CLEAR = gen.STEPS | gen.DECK | gen.GATES | gen.LANE
NPCS = []
def hidden(q): return any(x <= q[0] <= x + 2 and r - 2 <= q[1] <= r - 1 for name, x, r in gen.sprites if name.startswith('tree'))          # derrière une cime
def stand(name, wish):
    def ok(q):
        return q in gen.REACH and q not in SOLID and q not in gen.TALL and q not in gen.TRAIL and q not in L['Paths'] and not gen.pinches(q) and not hidden(q) \
            and not any((q[0] + i, q[1] + j) in KEEP_CLEAR for i in (-1, 0, 1) for j in (-1, 0, 1)) and all(abs(q[0] - n[1][0]) + abs(q[1] - n[1][1]) > 3 for n in NPCS)
    for q in sorted(((wish[0] + i, wish[1] + j) for i in range(-4, 5) for j in range(-4, 5)), key=lambda q: (abs(q[0] - wish[0]) + abs(q[1] - wish[1]), q)):
        if ok(q): return q
    print('  !! %s : aucune case convenable près de %s' % (name, wish)); return wish
def npc(name, wish, appearance, text, **kw):
    c = wish
    if kw.get('movement') is None:
        c = stand(name, wish); NPCS.append((name, c)); SOLID.add(c)
    lines = ['[node name="%s" parent="World/Entities" instance=ExtResource("4_npc")]' % name, 'position = Vector2(%d, %d)' % px(c), 'appearance = "%s"' % appearance]
    if 'facing' in kw: lines.append('facing = Vector2(%d, %d)' % kw['facing'])
    lines.append('text = "%s"' % text)
    for key in ('movement', 'pace', 'wander_layer'):
        if key in kw: lines.append(('%s = "%s"' if key != 'pace' else '%s = %s') % (key, kw[key]))
    node('\n'.join(lines) + '\n')
# Dans une forêt, ni pêcheur ni montagnard (Ludovic, 17/11/2026) : des campeurs, des gamins, des chasseurs d'insectes.
npc('RouteCamper', (21, 34), 'hgss_camper', "La rivière a creusé son lit bien en dessous de nous.|Aucun sentier n'y descend : il faut prendre les ponts.", facing=(0, 1))
npc('RouteLass', (9, 36), 'hgss_lass', "D'ici, on voit les poissons remonter le courant.|Dommage qu'on ne puisse pas descendre jusqu'à l'eau.", facing=(-1, 0))
npc('RoutePicnicker', (49, 29), 'hgss_picnicker', "D'ici, on voit la rivière se séparer en trois.|Par temps clair, on devine même le toit du laboratoire.", facing=(0, 1))
npc('RouteYoungster', (17, 10), 'hgss_youngster', "Ce rebord de roche ne se remonte pas.|Pour aller au nord, il faut faire le tour par les hautes herbes.", facing=(0, 1))
tall = sorted(c for c in gen.TALL if 38 <= c[0] <= 52 and 40 <= c[1] <= 46 and c in gen.REACH)
npc('RouteBugCatcher', tall[len(tall) // 2], 'frlg_bugcatcher', "Les Pokémon de la route sont plus vifs que ceux de l'île.|J'en ai vu un filer entre mes jambes !", facing=(0, 1), movement='wander', pace=2.0, wander_layer='Background/Grass')

node('[node name="Overhead" type="TileMapLayer" parent="."]\ntile_set = ExtResource("1_ian7c")\n')
node('[node name="SpawnPoint" type="Node2D" parent="."]\nposition = Vector2(%d, %d)\n' % px(gen.START))
node('[node name="Doors" type="Node2D" parent="."]\n')
BACK = {0: 1, 1: 3, 2: 4}
for i, c in enumerate(gen.SOUTH_GATE):
    node('[node name="Sud%d" parent="Doors" instance=ExtResource("2_door")]\nposition = Vector2(%d, %d)\ntarget_scene = "%sstart_island.tscn"\ntarget_door = "Nord%d"\nentry_direction = Vector2(0, -1)\n' % (i, *px(c), LEVELS, BACK[i]))
node('[node name="Sky" type="Node2D" parent="."]\nz_index = 40\n')
# Au-dessus d'une forêt, pas d'oiseaux de mer : des Granivol, des Floravol et des Cotovol que le vent porte d'ouest en est,
# par groupes de deux ou trois. Un groupe partage sa graine — même souffle, mêmes ondulations — et chacun y a sa place.
# (nom, espèce, graine, allure en cases par seconde, [(colonne, rangée) de chacun, en cases et fractions de case])
PACKS = [('Hoppip', 'hoppip', 11, 1.3, [(9.0, 7.0), (10.6, 8.2), (11.8, 6.6)]),
         ('Skiploom', 'skiploom', 23, 1.1, [(38.0, 15.0), (40.2, 16.1)]),
         ('Jumpluff', 'jumpluff', 37, 1.5, [(22.0, 27.0), (23.8, 25.8), (25.1, 27.6)]),
         ('HoppipSouth', 'hoppip', 41, 1.2, [(54.0, 39.0), (55.9, 40.3)])]
for name, species, seed, pace, places in PACKS:
    for i, (x, y) in enumerate(places):
        node('[node name="%s%d" parent="Sky" instance=ExtResource("13_flyer")]\nposition = Vector2(%d, %d)\nspecies = "%s"\nzone = Rect2i(0, 0, %d, %d)\npace = %s\nseed = %d\ndrift = 1\n'
             % (name, i, round(x * 16 + 8), round(y * 16 + 8), species, W, H, pace, seed))
node('[node name="Readables" type="Node2D" parent="."]\n')
# L'arbuste de l'exemple se coupe, dans les jeux d'origine. Le nôtre ne sait pas encore : il dit ce qu'ils disent.
for i, (x, r) in enumerate(sorted((x, r) for name, x, r in gen.sprites if name == 'sapling')):
    node('[node name="CutTree%d" parent="Readables" instance=ExtResource("9_readable")]\nposition = Vector2(%d, %d)\ntext = "Cet arbre semble pouvoir être coupé !"\n' % (i, *px((x, r))))
ENDS = {'North': (gen.NORTH_GATE, "La route continue vers la montagne.|Le chemin n'est pas encore tracé au-delà."), 'East': (gen.EAST_GATE, "La route continue vers l'est.|Le chemin n'est pas encore tracé au-delà.")}
for side, (cells_, text) in ENDS.items():
    for i, c in enumerate(cells_):
        node('[node name="RoadEnd%s%d" parent="Readables" instance=ExtResource("9_readable")]\nposition = Vector2(%d, %d)\ntext = "%s"\n' % (side, i, *px(c), text)); SOLID.add(c)

# ------------------------------------------------------------------ contrôles
R = gen.reach_from(gen.START, SOLID - {gen.START})
targets = {'devant ' + n: c for n, c in list(gen.SIGNS.items()) + list(gen.ITEMS.items()) + NPCS}
targets.update({'devant la sortie du nord': (15, 1), 'devant la sortie de l est': (67, 36), 'hautes terres': (50, 25)})
def beside(c): return any((c[0] + i, c[1] + j) in R for i, j in gen.NEIGH4)
locked = {'devant ' + n for n in gen.LOCKED}          # ce qui attend derrière l'arbuste à couper : hors d'atteinte aujourd'hui, à portée une fois l'arbuste coupé
RCUT = gen.reach_from(gen.START, SOLID - {gen.START} - gen.CUT, gen.CUT)
miss = [k for k, c in targets.items() if k not in locked and not (beside(c) if k.startswith('devant ') and c in SOLID else c in R)]
miss += [k + ' (devrait être hors d atteinte)' for k in locked if beside(targets[k])]
miss += [k + ' (hors d atteinte même l arbuste coupé)' for k in locked if not any((targets[k][0] + i, targets[k][1] + j) in RCUT for i, j in gen.NEIGH4)]
miss += ['porte du sud %d' % i for i, c in enumerate(gen.SOUTH_GATE) if c not in R]
print('%d cases accessibles%s' % (len(R), (' — INACCESSIBLE : %s' % miss) if miss else ' ; tous les lieux se rejoignent'))
print('départ', gen.START, '| panneaux', gen.SIGNS, '| objets', gen.ITEMS, '| personnages', NPCS, '| marches', sorted(gen.STEPS))

# ------------------------------------------------------------------ scène
def encode(cells_):
    raw = struct.pack('<H', 0)
    for (x, y), (src, ax, ay, alt) in sorted(cells_.items(), key=lambda kv: (kv[0][1], kv[0][0])): raw += struct.pack('<hhHHHH', x, y, src, ax, ay, alt)
    return base64.b64encode(raw).decode()
def layer(name, parent, cells_, ysort=False):
    return '[node name="%s" type="TileMapLayer" parent="%s"]\n%stile_map_data = PackedByteArray("%s")\ntile_set = ExtResource("1_ian7c")\n' % (name, parent, 'y_sort_enabled = true\n' if ysort else '', encode(cells_))
head = '''[gd_scene load_steps=8 format=4]

[ext_resource type="TileSet" uid="uid://c38ht37ho6e3a" path="{R}resources/tilesets/level.tres" id="1_ian7c"]
[ext_resource type="PackedScene" path="{R}scenes/levels/scene_trigger.tscn" id="2_door"]
[ext_resource type="PackedScene" path="{R}scenes/levels/sign.tscn" id="3_sign"]
[ext_resource type="PackedScene" path="{R}scenes/characters/npc.tscn" id="4_npc"]
[ext_resource type="PackedScene" path="{R}scenes/levels/readable.tscn" id="9_readable"]
[ext_resource type="Texture2D" path="{R}assets/levels/island.png" id="12_island"]
[ext_resource type="PackedScene" path="{R}scenes/levels/flyer.tscn" id="13_flyer"]

[node name="Level" type="Node2D"]
metadata/location = "Route du nord"
metadata/banner = "forest"
metadata/music = "new_bark_town"
metadata/daylight = true
metadata/encounter_rate = 3
metadata/encounter_rate_run = 5
metadata/wild = "mulotin:3-5*45 | piafeuille:3-6*35 | chenibulle:4-5*20"

[node name="Background" type="Node2D" parent="."]
'''.replace('{R}', RES)
parts = [head] + [layer(n, 'Background', L[n]) for n in gen.ORDER]
parts.append('[node name="World" type="Node2D" parent="."]\ny_sort_enabled = true\n')
parts += [layer(n, 'World', L[n], True) for n in ('Trees', 'Props')] + nodes
if '--grid' in sys.argv:
    open(sys.argv[sys.argv.index('--grid') + 1], 'w').write('\n'.join(''.join('#' if (x, y) in SOLID else '.' for x in range(W)) for y in range(H)))
if '--preview' in sys.argv: gen.write_preview(sys.argv[sys.argv.index('--preview') + 1])
if '--map' in sys.argv: gen.show_map()
if '--compare' in sys.argv:
    differ = gen.compare(); ours = gen.LANE | set(gen.OBJECTS.values()) | gen.SHADOWS | gen.RETOUCHED
    print('%d cases sur %d identiques à l exemple, au pixel près' % (W * H - len(differ), W * H))
    print('  diffèrent, hors trouée du sud, objets du jeu, ombres complétées sous les sapins et arbres ramenés à une essence :', sorted(c for c in differ if c not in ours))
if '--write' in sys.argv:
    open(B + 'scenes/levels/north_route.tscn', 'w').write('\n'.join(parts))
    print('écrit')
