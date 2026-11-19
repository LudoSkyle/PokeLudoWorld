#!/usr/bin/env python3
"""Fabrique les cartes de test : tests/maps/field.tscn, room.tscn, hall.tscn et ice.tscn.

    python3 tests/maps/build.py

Ces cartes ne font pas partie du jeu : aucune porte du jeu n'y mène. Elles servent aux tests
qui vérifient le **système** — déplacements, dialogues, menus, portes, sons, jour et nuit —
sur un terrain petit, où tout est à quelques pas. Ce qui vérifie une carte ou une quête du
jeu se joue sur cette carte-là (tests/island, tests/quests…).

Le terrain (field), 24 × 16 cases, tient presque dans un écran :

      0         1         2
      012345678901234567890123
    0 ################HHHH####    # clôture   H la maison (sa porte : S)
    1 #G..............HHHHsC.#    G gardes, et entre eux le passage gardé (g)
    2 .g..............HHHH...#    C la porte de la cabane, s un panneau (celui de chez Ludo :
    3 #G..............HHHH...#      son texte a une traduction, de quoi vérifier les langues)
    4 #####...........HSHH...#
    5 #.BB...................#    B un banc
    6 #....hhhhhhh.......rrrr#    h hautes herbes, w le chasseur qui y erre
    7 #....hhhwhhh.......rrrr#    r le chemin du coureur, une boucle à deux voies
    8 #....hhhhhhh.......rrrr#
    9 #..................rrrr#
   10 #..................rrrr#
   11 #.~ooDDD.L.....L...rrrr#    ~ la rive, o l'eau claire où l'on tient debout,
   12 #.~ooDDD...........rrrr#    D l'eau profonde ; F le pêcheur, L un lampadaire
   13 #.~oFDDD...............#
   14 #.~ooDDD...............#
   15 ########################

La cabane (room) a la musique du terrain, la salle (hall) a la sienne : de quoi vérifier
qu'une musique continue d'une carte à l'autre, ou change.

La glacière (ice) est une petite salle de grotte de glace, pour la glissade (tests/moves/ice_slide).
Elle est à part du terrain parce qu'une plaque de verglas y aurait détourné les trajets des autres
tests. Ses cases, dans la carte (la salle est posée en (10, 5)) :

      1111111111222
      0123456789012
    5 #############    # le vide, qui arrête
    6 #...........#    . le sol
    7 #.,,,,,,....#    , le verglas, de (12, 7) à (17, 9)
    8 #.,,,O,,....#    O un caillou rond posé dessus, en (15, 8)
    9 #.,,,,,,#...#    # en (18, 9) : du vide au bout de la rangée du bas
   10 #...........#
   11 #...........#
   12 #############

Relancer le script redonne exactement les mêmes fichiers. Les cases sont celles que les
tests visent : en déplacer une, c'est reprendre les tests qui s'en servent.
"""
import base64
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
RES = 'res://src/main/kotlin/fr/skyle/pokemonmirage/'
MAPS = 'res://tests/maps/'
W, H = 24, 16


def pack(cells):
    raw = struct.pack('<h', 0)
    for (x, y), (source, ax, ay) in sorted(cells.items()):
        raw += struct.pack('<hhhhhh', x, y, source, ax, ay, 0)
    return base64.b64encode(raw).decode()


def pos(x, y):
    return 'Vector2(%d, %d)' % (x * 16 + 8, y * 16 + 8)


def layer(name, parent, cells, extra=''):
    return '[node name="%s" type="TileMapLayer" parent="%s"]\n%stile_map_data = PackedByteArray("%s")\ntile_set = ExtResource("1_tileset")\n' % (name, parent, extra, pack(cells))


# --- le terrain

FENCE = (5, 50, 27)
PATH = (5, 1, 17)
TALL = (5, 6, 0)
SHORE, SHALLOW, DEEP_TOP, DEEP = (5, 17, 32), (5, 9, 31), (5, 6, 34), (5, 6, 35)

# Le coureur : une boucle à deux voies, dans l'ordre où il la parcourt.
ROUTE = [(19, 12), (22, 12), (22, 6), (21, 6), (21, 11), (20, 11), (20, 6), (19, 6)]


def field():
    ground = {(x, y): (5, 1 + (x * 7 + y * 13) % 4, 0) for x in range(W) for y in range(H)}
    for y in range(11, 15):
        ground[(2, y)] = SHORE
        for x in (3, 4): ground[(x, y)] = SHALLOW
        for x in (5, 6, 7): ground[(x, y)] = DEEP_TOP if y == 11 else DEEP

    paths = {(x, y): PATH for x in range(19, 23) for y in range(6, 13)}
    grass = {(x, y): TALL for x in range(5, 12) for y in range(6, 9)}

    props = {}
    for x in range(W):
        if not 16 <= x <= 19: props[(x, 0)] = FENCE
        props[(x, H - 1)] = FENCE
    for y in range(1, H - 1):
        props[(W - 1, y)] = FENCE
        if y != 2: props[(0, y)] = FENCE
    for x in range(1, 5): props[(x, 4)] = FENCE
    props[(2, 5)], props[(3, 5)] = (5, 74, 25), (5, 75, 25)

    houses = {(16 + i, j): (5, 13 + i, 95 + j) for i in range(4) for j in range(5)}

    out = ['[gd_scene load_steps=9 format=4]\n',
           '[ext_resource type="TileSet" path="%sresources/tilesets/level.tres" id="1_tileset"]' % RES,
           '[ext_resource type="PackedScene" path="%sscenes/levels/scene_trigger.tscn" id="2_door"]' % RES,
           '[ext_resource type="PackedScene" path="%sscenes/levels/sign.tscn" id="3_sign"]' % RES,
           '[ext_resource type="PackedScene" path="%sscenes/characters/npc.tscn" id="4_npc"]' % RES,
           '[ext_resource type="PackedScene" path="%sscenes/levels/roadblock.tscn" id="5_roadblock"]' % RES,
           '[ext_resource type="PackedScene" path="%sscenes/levels/street_lamp.tscn" id="6_lamp"]' % RES,
           '[ext_resource type="PackedScene" path="%sscenes/levels/window_glow.tscn" id="7_glow"]\n' % RES,
           '[node name="Level" type="Node2D"]\nmetadata/location = "Terrain d\'essai"\nmetadata/banner = "wood"\nmetadata/music = "new_bark_town"\n'
           'metadata/daylight = true\nmetadata/encounter_rate = 10\nmetadata/wild = "mulotin:2-4*50 | piafeuille:2-5*35 | chenibulle:3*15"\n',
           '[node name="Background" type="Node2D" parent="."]\n',
           layer('Ground', 'Background', ground),
           layer('Paths', 'Background', paths, 'position = Vector2(0, -1)\n'),
           layer('Decorations', 'Background', {}),
           layer('Grass', 'Background', grass),
           '[node name="World" type="Node2D" parent="."]\ny_sort_enabled = true\n',
           layer('Props', 'World', props, 'y_sort_enabled = true\n'),
           layer('Houses', 'World', houses, 'y_sort_enabled = true\n'),
           layer('Trees', 'World', {}, 'y_sort_enabled = true\n'),
           '[node name="Sign" parent="World" instance=ExtResource("3_sign")]\nposition = %s\ntext = "Maison de Ludo.|La porte n\'est jamais fermée, entrez donc."\n' % pos(22, 3),
           '[node name="LampWest" parent="World" instance=ExtResource("6_lamp")]\nposition = %s\n' % pos(9, 11),
           '[node name="LampEast" parent="World" instance=ExtResource("6_lamp")]\nposition = %s\n' % pos(15, 11),
           # La vitre de la maison : 10 × 7 pixels à partir de (294, 67).
           '[node name="GlowHouse" parent="World" instance=ExtResource("7_glow")]\nposition = Vector2(299, 70)\n',
           '[node name="Entities" type="Node2D" parent="World"]\ny_sort_enabled = true\n']

    def npc(name, x, y, lines):
        out.append('[node name="%s" parent="World/Entities" instance=ExtResource("4_npc")]\nposition = %s\n%s\n' % (name, pos(x, y), '\n'.join(lines)))

    guard = 'text = "Désolé, le passage est fermé.|C\'est dangereux par là : la route n\'est pas encore sûre."'
    npc('GuardNorth', 1, 1, ['appearance = "dppt_worker"', 'facing = Vector2(1, 0)', guard])
    npc('GuardSouth', 1, 3, ['appearance = "dppt_worker"', 'facing = Vector2(1, 0)', guard])
    npc('GrassWatcher', 8, 7, ['appearance = "frlg_bugcatcher"', 'facing = Vector2(0, 1)',
                               'text = "Ces herbes sont si hautes qu\'on s\'y perd.|Je cherche des insectes, mais je n\'ai encore rien trouvé."',
                               'movement = "wander"', 'pace = 2.0', 'wander_layer = "Background/Grass"'])
    npc('Runner', ROUTE[-1][0], ROUTE[-1][1], ['appearance = "rse_triathlete_m"', 'facing = Vector2(0, 1)',
                                             'text = "Pff... pff... Je fais le tour du village tous les matins.|Ne reste pas au milieu du chemin, je perds mon rythme."',
                                             'movement = "patrol"', 'pace = 3.0',
                                             'route = PackedVector2Array(%s)' % ', '.join('%d, %d' % c for c in ROUTE)])
    npc('Fisher', 4, 13, ['appearance = "hgss_fisherman"', 'facing = Vector2(1, 0)',
                          'text = "Chut... Ça ne mord pas fort aujourd\'hui.|Il paraît qu\'il y a de gros poissons au fond du lac."'])

    out += ['[node name="Overhead" type="TileMapLayer" parent="."]\ntile_set = ExtResource("1_tileset")\n',
            '[node name="SpawnPoint" type="Node2D" parent="."]\nposition = %s\n' % pos(12, 9),
            '[node name="Doors" type="Node2D" parent="."]\n',
            '[node name="Cabane" parent="Doors" instance=ExtResource("2_door")]\nposition = %s\ntarget_scene = "%sroom.tscn"\ntarget_door = "Entree"\nentry_direction = Vector2(0, 1)\n' % (pos(21, 1), MAPS),
            '[node name="Salle" parent="Doors" instance=ExtResource("2_door")]\nposition = %s\ntarget_scene = "%shall.tscn"\ntarget_door = "Entree"\nentry_direction = Vector2(0, 1)\n' % (pos(17, 4), MAPS),
            '[node name="Triggers" type="Node2D" parent="."]\n',
            '[node name="WestRoadblock" parent="Triggers" instance=ExtResource("5_roadblock")]\nposition = %s\nguard = "GuardNorth"\npush_direction = Vector2(1, 0)\n' % pos(1, 2),
            '[node name="Readables" type="Node2D" parent="."]']
    return '\n'.join(out) + '\n'


# --- les deux intérieurs : une pièce nue, un paillasson, une porte qui ramène au terrain

def interior(location, music, door):
    ground = {(x, y): (5, 65, 49) for x in range(32) for y in range(20)}
    for x in range(12, 19):
        for y in range(10, 15): ground[(x, y)] = (5, 61, 47)
    walls = {}
    for x in range(12, 19):
        for j in range(3): walls[(x, 7 + j)] = (5, 60 if x == 12 else (62 if x == 18 else 61), 44 + j)
    out = ['[gd_scene load_steps=3 format=4]\n',
           '[ext_resource type="TileSet" path="%sresources/tilesets/level.tres" id="1_tileset"]' % RES,
           '[ext_resource type="PackedScene" path="%sscenes/levels/scene_trigger.tscn" id="2_door"]\n' % RES,
           '[node name="Level" type="Node2D"]\nmetadata/location = "%s"\nmetadata/banner = "wood"\nmetadata/music = "%s"\n' % (location, music),
           '[node name="Background" type="Node2D" parent="."]\n',
           layer('Ground', 'Background', ground),
           layer('Walls', 'Background', walls),
           layer('Decor', 'Background', {(15, 14): (7, 16, 7)}),
           '[node name="World" type="Node2D" parent="."]\ny_sort_enabled = true\n',
           layer('Props', 'World', {}, 'y_sort_enabled = true\n'),
           '[node name="Entities" type="Node2D" parent="World"]\ny_sort_enabled = true\n',
           '[node name="Doors" type="Node2D" parent="."]\n',
           '[node name="Entree" parent="Doors" instance=ExtResource("2_door")]\nposition = %s\ntarget_scene = "%sfield.tscn"\ntarget_door = "%s"\nentry_direction = Vector2(0, -1)\nexit_direction = Vector2(0, 1)\n' % (pos(15, 14), MAPS, door),
           '[node name="Readables" type="Node2D" parent="."]']
    return '\n'.join(out) + '\n'


# --- la glacière : une salle de grotte de glace, une plaque de verglas, un caillou dessus

ICE = 16          # la source de la grotte de glace dans le TileSet (tools/ice_cave_tiles.py)
ICE_VOID, ICE_FLOOR, ICE_ROCK = (ICE, 1, 8), (ICE, 1, 12), (ICE, 6, 1)          # le noir qui arrête, le sol, un caillou rond
ICE_ROOM, ICE_PLATE, ICE_STONE, ICE_STOP = (10, 5, 13, 8), (12, 7, 6, 3), (15, 8), (18, 9)


def ice():
    ground = {(x, y): ICE_VOID for x in range(32) for y in range(20)}
    rx, ry, rw, rh = ICE_ROOM
    for x in range(rx + 1, rx + rw - 1):
        for y in range(ry + 1, ry + rh - 1): ground[(x, y)] = ICE_FLOOR
    px, py, pw, ph = ICE_PLATE
    for i in range(pw):
        for j in range(ph):          # la matière `earth…` : son bloc de 3 × 3 est en (5, 13) sur la planche
            ground[(px + i, py + j)] = (ICE, 5 + (0 if i == 0 else 2 if i == pw - 1 else 1), 13 + (0 if j == 0 else 2 if j == ph - 1 else 1))
    ground[ICE_STOP] = ICE_VOID
    out = ['[gd_scene load_steps=2 format=4]\n',
           '[ext_resource type="TileSet" path="%sresources/tilesets/level.tres" id="1_tileset"]\n' % RES,
           '[node name="Level" type="Node2D"]\nmetadata/location = "Glacière"\nmetadata/banner = "cave"\nmetadata/daylight = false\n',
           '[node name="Background" type="Node2D" parent="."]\n',
           layer('Ground', 'Background', ground),
           '[node name="World" type="Node2D" parent="."]\ny_sort_enabled = true\n',
           layer('Props', 'World', {ICE_STONE: ICE_ROCK}, 'y_sort_enabled = true\n'),
           '[node name="Entities" type="Node2D" parent="World"]\ny_sort_enabled = true\n',
           '[node name="SpawnPoint" type="Node2D" parent="."]\nposition = %s\n' % pos(11, 6),
           '[node name="Doors" type="Node2D" parent="."]\n',
           '[node name="Triggers" type="Node2D" parent="."]\n',
           '[node name="Readables" type="Node2D" parent="."]']
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    for name, text in (('field', field()), ('room', interior('Cabane', 'new_bark_town', 'Cabane')), ('hall', interior('Salle', 'sprout_tower', 'Salle')), ('ice', ice())):
        with open(os.path.join(HERE, name + '.tscn'), 'w', encoding='utf-8') as handle:
            handle.write(text)
    print('field.tscn, room.tscn, hall.tscn et ice.tscn ecrits dans tests/maps')
