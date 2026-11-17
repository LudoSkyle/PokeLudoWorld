#!/usr/bin/env python3
"""Fabrique l'île de départ : scenes/levels/start_island.tscn.

    python3 tools/maps/start_island/generate.py                 # contrôle seulement, n'écrit rien
    python3 tools/maps/start_island/generate.py --write         # écrit la scène, et la source des maisons dans le TileSet
    python3 tools/maps/start_island/generate.py --preview a.png # la carte telle que le jeu la dessinera (terrain, arbres, maisons)
    python3 tools/maps/start_island/generate.py --map           # ~ mer, # plein, = ponton, S marche, . atteignable, ? libre mais coupé du reste

La chaîne, dans l'ordre où on la relance quand quelque chose change :

    tools/route_tiles.py, tools/village_tiles.py   découpent route.png et village.png dans la planche de la Route 1
    geography.py --read      relit reference.png (la carte d'exemple de l'île) -> classes.json
    geography.py             en tire la mer, les plages, les plateaux ; porte les retouches
    layout.py                pose le terrain, les pontons, les escaliers, la forêt, les maisons ; calcule ce qui bloque
    generate.py              pose la place, les panneaux, les personnages, la quête de la cloche ; contrôle ; écrit

L'île ne reproduit pas son exemple tuile pour tuile (voir geography.py) : elle en a la
géographie, dans le style de la Route 1. Relancer ce script écrase la scène : une retouche
faite dans l'éditeur se refait ici.
"""
import base64
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as lay  # noqa: E402
from layout import L, W, H, ROOT, DOORS, PLAZA, LOOP, LOOP_CELLS, ROAD, GUARD_Y, DECK, STEPS, STAIRS, PIER_END, BEACH, INSIDE, rect, village_tiles  # noqa: E402

B = os.path.join(ROOT, 'src', 'main', 'kotlin', 'fr', 'skyle', 'pokeludoworld') + os.sep
RES = 'res://src/main/kotlin/fr/skyle/pokeludoworld/'
LEVELS = RES + 'scenes/levels/'
TS = B + 'resources/tilesets/level.tres'
def px(c): return (c[0] * 16 + 8, c[1] * 16 + 8)
def polygon(x0, y0, x1, y1):
    """Le rectangle qui couvre ces cases, rentré d'un pixel : trois rectangles bord à bord, le moteur les soude et y laisse des trous."""
    return 'PackedVector2Array(%d, %d, %d, %d, %d, %d, %d, %d)' % (x0 * 16 - 7, y0 * 16 - 7, x1 * 16 + 7, y0 * 16 - 7, x1 * 16 + 7, y1 * 16 + 7, x0 * 16 - 7, y1 * 16 + 7)


# ------------------------------------------------------------------ TileSet : la source des maisons
def village_source():
    out = ['[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_village"]', 'resource_name = "village"', 'texture = ExtResource("9_village")']
    for name, at in sorted(village_tiles.atlas().items(), key=lambda kv: kv[1]):
        (w, h), below, d = village_tiles.sizes()[name], village_tiles.drop(name), village_tiles.door(name)
        key = '%d:%d' % at
        out += ['%s/size_in_atlas = Vector2i(%d, %d)' % (key, w, h + below), '%s/0 = 0' % key, '%s/0/texture_origin = Vector2i(%d, %d)' % (key, -8 * (w - 1), 8 * (h - below - 1)),
                '%s/0/y_sort_origin = -1' % key]          # qui se tient sur la case de la porte passe devant ; qui passe derrière le toit passe derrière
        # une maison : les murs et le bas du toit, quatre rangées, sauf la case de la porte ; une plante : son tronc
        parts = [p for p in ((0, -3, d - 1, 0), (d, -3, d, -1), (d + 1, -3, w - 1, 0)) if p[0] <= p[2]] if name in village_tiles.HOUSES else [(d, 0, d, 0)]
        for k, p in enumerate(parts): out.append('%s/0/physics_layer_0/polygon_%d/points = %s' % (key, k, polygon(*p)))
    return '\n'.join(out) + '\n'


def patch_tileset(write):
    s = open(TS).read()
    s = re.sub(r'\[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_village"\]\n(?:[^\[\n][^\n]*\n)*\n?', '', s)
    s = re.sub(r'^sources/14 = [^\n]*\n', '', s, flags=re.M)
    texture = '[ext_resource type="Texture2D" path="%sassets/levels/village.png" id="9_village"]' % RES
    if texture not in s:
        route = '[ext_resource type="Texture2D" path="%sassets/levels/route.png" id="8_route"]' % RES
        assert s.count(route) == 1
        s = s.replace(route, route + '\n' + texture)
    assert s.count('\n[resource]') == 1
    s = s.replace('\n[resource]', '\n' + village_source() + '\n[resource]')
    s = s.rstrip('\n') + '\nsources/14 = SubResource("TileSetAtlasSource_village")\n'
    changed = s != open(TS).read()
    if write and changed: open(TS, 'w').write(s)
    return changed


for w_ in lay.WARN: print('  !!', w_)
print('TileSet :', 'source des maisons à réécrire' if patch_tileset('--write' in sys.argv) else 'à jour')

# ------------------------------------------------------------------ poser sans gêner
SOLID = set(lay.SOLID)
REACH0 = set(lay.REACH)
CXP, TOP = (PLAZA[0] + PLAZA[2]) // 2, PLAZA[1]
STAND = {(CXP, TOP + 1), (CXP - 1, TOP + 2), (CXP, TOP + 2), (CXP + 1, TOP + 2), (CXP - 1, TOP + 3), (CXP + 1, TOP + 3)}          # le socle de la cloche, vide puis garni
STATUES = {'StatueWest': (CXP - 3, TOP + 1), 'StatueEast': (CXP + 3, TOP + 1)}
SOLID |= STAND | set(STATUES.values())
FRONTS = {(d[0], d[1] + j) for d in DOORS.values() for j in (1, 2)} | {(x + i, r + j) for x, r in STAIRS.values() for i in range(5) for j in (-2, -1, 0, 1, 2)}
CLEAR = FRONTS | DECK | LOOP_CELLS | STEPS | {(x, y) for x in ROAD for y in range(0, GUARD_Y + 3)} | {(c[0] + i, c[1] + j) for c in DECK for i, j in lay.NEIGH4}
placed = {}
nodes = []
# Les cases choisies à la main : un lampadaire se met dans un angle — au coin de deux pistes, contre un coin de falaise —,
# et rien ne se pose sur une piste (Ludovic, 17/11/2026). Ce qui est ici n'est pas déplacé par `settle`.
FIXED = {(11, 14), (7, 13), (19, 10), (47, 37), (12, 31), (1, 29), (39, 13), (19, 38)}
def node(text): nodes.append(text)
def pinches(c):
    ring = [(c[0] + i, c[1] + j) for i, j in ((-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0))]
    open_ = [lay.inb(r) and r not in SOLID for r in ring]; group = list(range(8))
    def find(i):
        while group[i] != i: i = group[i]
        return i
    for i in range(8):
        if open_[i] and open_[(i + 1) % 8]: group[find(i)] = find((i + 1) % 8)
    return len({find(i) for i in range(8) if open_[i] and i % 2 == 1}) > 1
def fix(name, c, solid=True):
    """Pose quelque chose sur une case choisie à la main (par Ludovic, sur capture) : on ne la déplace pas, on prévient si elle ne convient pas."""
    if c in SOLID or c not in REACH0: print('  !! %s : la case %s est prise ou hors d atteinte' % (name, c))
    if c in lay.TRAIL: print('  !! %s : la case %s est sur une piste' % (name, c))
    placed[name] = c
    if solid: SOLID.add(c)
    return c
def settle(name, wish, solid=True, apart=2, among=None, tight=False):
    """La case libre la plus proche de `wish` où poser quelque chose sans gêner : ni devant une porte ou un escalier, ni sur un ponton ou une piste, ni dans un passage étroit, ni derrière un arbre."""
    if wish in FIXED: return fix(name, wish, solid)
    for q in sorted(((wish[0] + i, wish[1] + j) for i in range(-6, 7) for j in range(-6, 7)), key=lambda q: (abs(q[0] - wish[0]) + abs(q[1] - wish[1]), q)):
        if q in (among or REACH0) and q not in SOLID and q not in CLEAR and q not in lay.WOODS and q not in lay.HOUSE_AREA and q not in lay.TALL and q not in lay.TRAIL and (q in lay.PAVED or tight or not pinches(q)) \
                and all(abs(q[0] - o[0]) + abs(q[1] - o[1]) >= apart for o in placed.values()):
            placed[name] = q
            if solid: SOLID.add(q)
            if q != wish: print('  (%s : %s -> %s)' % (name, wish, q))
            return q
    print('  !! %s : aucune case convenable près de %s' % (name, wish)); placed[name] = wish; return wish

# ------------------------------------------------------------------ mobilier (tuiles de island.png, source 10)
TOWELS = {}
def bench(name, wish, side=None):
    if side:          # de profil, une case de large et deux de long : `side` est le côté vers lequel on s'y assoit ('west' ou 'east')
        c = fix(name, wish); SOLID.add((c[0], c[1] - 1)); placed[name + '+'] = (c[0], c[1] - 1)
        for j in range(3): L['Props'][(c[0], c[1] - 2 + j)] = (10, 9 if side == 'west' else 8, 3 + j, 0)
        return c
    c = settle(name, wish); SOLID.add((c[0] + 1, c[1])); placed[name + '+'] = (c[0] + 1, c[1])          # de face, deux cases : l'assise est pleine, le dossier dépasse sur la case du dessus
    for i in range(2):
        for j in range(2): L['Props'][(c[0] + i, c[1] - 1 + j)] = (10, 4 + i, 5 + j, 0)
    return c
def parasol(name, wish, kind):  # deux cases de large, trois de haut. Rien n'y arrête : on passe sous la toile, derrière le mât
    c = settle(name, wish, solid=False); placed[name + '+'] = (c[0] + 1, c[1])
    for i in range(2):
        for j in range(3): L['Props'][(c[0] + i, c[1] - 2 + j)] = (10, (11, 13)[kind] + i, 3 + j, 0)
    return c
def towel(name, wish, kind):    # une case de large, deux de haut : on marche dessus
    c = settle(name, wish, solid=False); TOWELS[name] = c
    L['Decorations'][(c[0], c[1] - 1)] = (10, 15, 3 + 2 * kind, 0); L['Decorations'][c] = (10, 15, 4 + 2 * kind, 0)
    return c
BENCH_LUDO, BENCH_SOUTH, BENCH_SQUARE = bench('BenchLudo', (11, 14)), bench('BenchSouth', (49, 31), side='west'), bench('BenchSquare', (CXP + 3, TOP - 2))
parasol('ParasolCove', (29, 16), 1); towel('TowelCove', (32, 16), 1)
parasol('ParasolSouth', (25, 36), 0); towel('TowelSouth', (28, 36), 0)

# ------------------------------------------------------------------ panneaux, lampadaires, lueurs, objets
def sign(name, wish, text):
    c = settle(name, wish)
    if c in L['Decorations']: L['Decorations'][(c[0], c[1] - 1)] = L['Decorations'].pop(c)          # la fleur qui était là remonte d'une case
    node('[node name="%s" parent="World" instance=ExtResource("3_sign")]\nposition = Vector2(%d, %d)\ntext = "%s"\n' % (name, *px(c), text))
def lamp(name, wish):
    c = settle(name, wish); node('[node name="%s" parent="World" instance=ExtResource("10_lamp")]\nposition = Vector2(%d, %d)\n' % (name, *px(c)))
sign('SignLudo', (DOORS['ludo'][0] + 2, DOORS['ludo'][1] + 1), "Maison de Ludo.|La porte n'est jamais fermée, entrez donc.")
sign('SignLibrary', (1, 29), "Bibliothèque de Bourg-Ludo.|Entrée libre. On parle à voix basse.")
sign('SignLab', (DOORS['lab'][0] + 2, DOORS['lab'][1] + 1), "Laboratoire du Professeur.|Les Pokémon blessés y sont soignés.")
sign('SignNorth', (ROAD[-1] + 1, GUARD_Y + 7), "Route 1.|Elle quitte l'île par la falaise.")
sign('SignPier', (PIER_END[0] - 2, 42), "Jetée du sud.|Attention : planches glissantes.")
for name, wish in {'LampLudo': (7, 13), 'LampNorth': (19, 10), 'LampLibrary': (12, 31),
                   'LampLab': (39, 13), 'LampSouth': (47, 37), 'LampGarden': (19, 38), 'LampPier': (PIER_END[0] + 2, 42),
                   'LampSquareWest': (PLAZA[0] - 2, PLAZA[1] - 2), 'LampSquareEast': (PLAZA[2] + 2, PLAZA[1] - 2)}.items(): lamp(name, wish)
# une lueur à chaque fenêtre : le milieu des vitres de la maison, mesuré sur son image
SHEET = village_tiles.cells()
for name, (kind, x, r) in sorted(lay.HOUSES.items()):
    (w, h), col = village_tiles.sizes()[kind], village_tiles.atlas()[kind][0]
    panes = [(i, j) for j in range(h * 16 - 34, h * 16) for i in range(w * 16) if SHEET[j][col * 16 + i][3] == 255 and SHEET[j][col * 16 + i][2] > 200 and SHEET[j][col * 16 + i][0] < 170]
    runs = []          # les vitres, par groupes de colonnes voisines
    for i in sorted({p[0] for p in panes}):
        if runs and i - runs[-1][-1] <= 3: runs[-1].append(i)
        else: runs.append([i])
    for k, run in enumerate(runs):
        ys = [j for i, j in panes if run[0] <= i <= run[-1]]
        node('[node name="Glow%s%d" parent="World" instance=ExtResource("11_glow")]\nposition = Vector2(%d, %d)\n' % (name.capitalize(), k, x * 16 + (run[0] + run[-1]) // 2, (r - h + 1) * 16 + (min(ys) + max(ys)) // 2))

node('''[node name="BellStandEmpty" type="StaticBody2D" parent="World"]
position = Vector2(%d, %d)
collision_mask = 0
script = ExtResource("6_readable_script")
text = "Un socle de pierre. Il manque quelque chose dessus."
states = PackedStringArray("bell_ribbon > @flag:bell_hung @take:clear_bell @reload @sound:bell Vous accrochez la cloche. Elle tient.")
ask = "bell_ribbon > Accrocher la Cloche claire ?"
forbidden_flag = "bell_hung"

[node name="Sprite" type="Sprite2D" parent="World/BellStandEmpty"]
position = Vector2(0, 9)
texture = ExtResource("7_stand")
region_enabled = true
region_rect = Rect2(0, 0, 48, 48)

[node name="ColliderBack" type="CollisionShape2D" parent="World/BellStandEmpty"]
position = Vector2(0, -7)
shape = SubResource("RectangleShape2D_statue")

[node name="ColliderPostLeft" type="CollisionShape2D" parent="World/BellStandEmpty"]
position = Vector2(-16, 9)
shape = SubResource("RectangleShape2D_statue")

[node name="ColliderPostRight" type="CollisionShape2D" parent="World/BellStandEmpty"]
position = Vector2(16, 9)
shape = SubResource("RectangleShape2D_statue")

[node name="ColliderLeft" type="CollisionShape2D" parent="World/BellStandEmpty"]
position = Vector2(-16, 25)
shape = SubResource("RectangleShape2D_statue")

[node name="ColliderRight" type="CollisionShape2D" parent="World/BellStandEmpty"]
position = Vector2(16, 25)
shape = SubResource("RectangleShape2D_statue")

[node name="BellStand" type="StaticBody2D" parent="World"]
position = Vector2(%d, %d)
collision_mask = 0
script = ExtResource("6_readable_script")
text = "La cloche est à sa place.|Elle bouge un peu quand le vent passe."
required_flag = "bell_hung"

[node name="Sprite" type="Sprite2D" parent="World/BellStand"]
texture = ExtResource("7_stand")
region_enabled = true
region_rect = Rect2(48, 0, 48, 48)

[node name="Collider" type="CollisionShape2D" parent="World/BellStand"]
shape = SubResource("RectangleShape2D_stand")

[node name="ColliderLeft" type="CollisionShape2D" parent="World/BellStand"]
position = Vector2(-16, 16)
shape = SubResource("RectangleShape2D_statue")

[node name="ColliderRight" type="CollisionShape2D" parent="World/BellStand"]
position = Vector2(16, 16)
shape = SubResource("RectangleShape2D_statue")
''' % (CXP * 16 + 8, TOP * 16 + 31, CXP * 16 + 8, TOP * 16 + 40))
for name, c in STATUES.items():
    node('''[node name="%s" type="StaticBody2D" parent="World"]
position = Vector2(%d, %d)
collision_mask = 0

[node name="Sprite" type="Sprite2D" parent="World/%s"]
position = Vector2(0, -13)
texture = ExtResource("8_environments")
flip_h = %s
region_enabled = true
region_rect = Rect2(1075, 1719, 27, 42)

[node name="Collider" type="CollisionShape2D" parent="World/%s"]
shape = SubResource("RectangleShape2D_statue")
''' % (name, *px(c), name, 'true' if name == 'StatueWest' else 'false', name))

ITEMS = {}
FOUND = {'ItemPotion': ('potion', "Vous trouvez une Potion !|Vous rangez la Potion dans la poche Objets.", 'found_island_potion', (46, 46)),
         'ItemBall': ('poke_ball', "Vous trouvez une Poké Ball !|Vous rangez la Poké Ball dans la poche Poké Balls.", 'found_island_ball', (4, 43)),
         'ItemWater': ('fresh_water', "Vous trouvez une Eau Fraîche !|Vous rangez l'Eau Fraîche dans la poche Objets.", 'found_island_water', (49, 5))}          # derrière le laboratoire
for name, (item, text, flag, wish) in FOUND.items():
    c = ITEMS[name] = settle(name, wish, tight=name == 'ItemWater')          # celui-là est au fond d'un couloir sans issue : il ne coupe le passage de personne
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
node('[node name="Overhead" type="TileMapLayer" parent="."]\ntile_set = ExtResource("1_ian7c")\n')
node('[node name="SpawnPoint" type="Node2D" parent="."]\nposition = Vector2(%d, %d)\n' % px(lay.START))
node('[node name="Doors" type="Node2D" parent="."]\n')
for name, house, scene in [('MaisonLudo', 'ludo', 'ludo_house'), ('Bibliotheque', 'library', 'library'), ('Laboratoire', 'lab', 'lab_house'), ('MaisonNord', 'north', 'orange_house_north'), ('MaisonSud', 'south', 'orange_house_south')]:
    node('[node name="%s" parent="Doors" instance=ExtResource("2_door")]\nposition = Vector2(%d, %d)\ntarget_scene = "%s%s.tscn"\ntarget_door = "Entree"\nentry_direction = Vector2(0, 1)\n' % (name, *px(DOORS[house]), LEVELS, scene))
# la sortie du nord : trois cases, qui mènent aux trois de la Route 1
for i, c in enumerate(lay.NORTH_GATE):
    node('[node name="Nord%d" parent="Doors" instance=ExtResource("2_door")]\nposition = Vector2(%d, %d)\ntarget_scene = "%sroute_1.tscn"\ntarget_door = "Sud%d"\nentry_direction = Vector2(0, 1)\n' % (i, *px(c), LEVELS, i))

# ------------------------------------------------------------------ les personnages
NPCS = []            # (nom, case, drapeau requis, drapeau interdit) des personnages immobiles
PHASES = {'avant': set(), 'pendant': {'bell_hung'}, 'après': {'bell_hung', 'vigil_over'}}
def present(req, forb, flags): return (req is None or req in flags) and (forb is None or forb not in flags)
def stand(name, c, req, forb):
    """La case la plus proche de c où un personnage immobile ne gêne personne, parmi ceux qu'il peut croiser."""
    taken = {q for n, q, r, f in NPCS if any(present(r, f, fl) and present(req, forb, fl) for fl in PHASES.values())}
    for q in sorted(((c[0] + i, c[1] + j) for i in range(-4, 5) for j in range(-4, 5)), key=lambda q: (abs(q[0] - c[0]) + abs(q[1] - c[1]), q)):
        if q in REACH0 and q not in SOLID and q not in taken and q not in CLEAR and q not in lay.WOODS and q not in lay.HOUSE_AREA and q not in lay.TALL and q not in lay.TRAIL and (q in lay.PAVED or not pinches(q)):
            if q != c: print('  (%s : %s -> %s)' % (name, c, q))
            return q
    print('  !! %s : aucune case convenable près de %s' % (name, c)); return c
def npc(name, c, appearance, text, **kw):
    fixed = kw.pop('fixed', False)
    if kw.get('movement') is None and not fixed: c = stand(name, c, kw.get('required_flag'), kw.get('forbidden_flag'))
    if kw.get('movement') is None: NPCS.append((name, c, kw.get('required_flag'), kw.get('forbidden_flag')))
    lines = ['[node name="%s" parent="World/Entities" instance=ExtResource("4_npc")]' % name, 'position = Vector2(%d, %d)' % px(c)]
    for k in ('display_name', 'gender'):
        if k in kw: lines.append('%s = "%s"' % (k, kw[k]))
    lines.append('appearance = "%s"' % appearance)
    if 'facing' in kw: lines.append('facing = Vector2(%d, %d)' % kw['facing'])
    lines.append('text = "%s"' % text)
    if 'states' in kw: lines.append('states = PackedStringArray(%s)' % ', '.join('"%s"' % s for s in kw['states']))
    if 'movement' in kw: lines.append('movement = "%s"' % kw['movement'])
    if 'pace' in kw: lines.append('pace = %s' % kw['pace'])
    if 'wander_layer' in kw: lines.append('wander_layer = "%s"' % kw['wander_layer'])
    if 'wander_zone' in kw: lines.append('wander_zone = Rect2i(%d, %d, %d, %d)' % kw['wander_zone'])
    if 'route' in kw: lines.append('route = PackedVector2Array(%s)' % ', '.join('%d, %d' % p for p in kw['route']))
    for k in ('required_flag', 'forbidden_flag'):
        if k in kw: lines.append('%s = "%s"' % (k, kw[k]))
    node('\n'.join(lines) + '\n')

BEFORE, DURING, AFTER_ALL = dict(forbidden_flag='bell_hung'), dict(required_flag='bell_hung', forbidden_flag='vigil_over'), dict(required_flag='vigil_over')
STAYS = dict(required_flag='bell_hung')      # arrive pour la Veillée, et reste ensuite
LIB_STAIR = STAIRS['bibliotheque']
BELL = (14, 21)          # dans l'eau, contre le ponton de l'ouest : on la repêche depuis la planche du dessous
TALL_SW = sorted(c for c in lay.TALL if c[1] > 30)

# ============ AVANT que la cloche soit accrochée
CLOSED = "Désolé, le passage est fermé.|C'est dangereux par là : la Route 1 n'est pas encore sûre."
npc('GuardWest', (ROAD[0], GUARD_Y), 'dppt_worker', CLOSED, facing=(0, 1), fixed=True, **BEFORE)
npc('GuardEast', (ROAD[-1], GUARD_Y), 'dppt_worker', CLOSED, facing=(0, 1), fixed=True, **BEFORE)
npc('Runner', LOOP[0], 'rse_triathlete_m', "Pff... pff... Je fais le tour de la place tous les matins.|Ne reste pas au milieu du chemin, je perds mon rythme.",
    facing=(0, 1), movement='patrol', pace=3.0, route=LOOP, **BEFORE)
npc('Fisher', PIER_END, 'hgss_fisherman', "Chut... Ça ne mord pas fort aujourd'hui.|Il paraît qu'il y a de gros poissons au large.", facing=(0, 1), fixed=True, **BEFORE)
npc('Roland', (LIB_STAIR[0] + 5, LIB_STAIR[1] + 3), 'frlg_ruinmaniac', "Ces eaux, j'y ai plongé vingt ans.|Elles ont encore des choses à dire, je le sens.", display_name='Roland', gender='male', facing=(1, 0),
    states=["bell_register > @flag:bell_spotted Sous le ponton de l'ouest, là où l'eau est profonde...|...il y a quelque chose qui accroche la lumière.|Moi, je n'y plonge plus. Trop froid, trop de courant.",
            "bell_tarnished > Alors c'était ça qui brillait.|Une cloche. Vingt ans que je passe au-dessus."], **BEFORE)

# ============ TOUJOURS LÀ : chacun près de ce qui l'occupe ; sa réplique change une fois la cloche accrochée
npc('GrassWatcher', TALL_SW[len(TALL_SW) // 2], 'frlg_bugcatcher', "Ces herbes sont si hautes qu'on s'y perd.|Je cherche des insectes, mais je n'ai encore rien trouvé.",
    facing=(0, 1), states=["bell_hung > Il paraît que c'est toi qui as retrouvé la cloche ! Bravo !|Moi, toujours pas le moindre insecte."], movement='wander', pace=2.0, wander_layer='Background/Grass')
npc('BenchLady', (BENCH_LUDO[0] + 2, BENCH_LUDO[1] + 1), 'rse_expert_f', "Je viens m'asseoir ici tous les matins.|D'ici, on voit passer tout le village.", facing=(0, 1),
    states=["bell_hung > Je viens toujours m'asseoir ici le matin.|Maintenant, j'attends que la cloche sonne pour rentrer."])
npc('Sunbather', TOWELS['TowelSouth'], 'hgss_swimmer_f', "Le sable est chaud, l'eau est fraîche.|Je ne bouge plus d'ici avant la nuit.", facing=(0, 1),
    states=["bell_hung > J'ai entendu la cloche depuis ma serviette.|Je n'ai pas bougé pour autant."])
npc('Swimmer', TOWELS['TowelCove'], 'hgss_swimmer_m', "L'eau de la crique est la plus calme de l'île.|Les vagues se cassent sur les rochers avant d'arriver.", facing=(0, 1),
    states=["bell_hung > J'étais dans l'eau quand la cloche a sonné.|J'ai bu la tasse. Ça valait le coup."])
npc('ShellKid', (TOWELS['TowelCove'][0] + 1, TOWELS['TowelCove'][1] - 1), 'hgss_tuber_m', "Je cherche des coquillages.|Pour l'instant, j'ai surtout trouvé des cailloux.", facing=(0, 1),
    states=["bell_hung > J'ai trouvé un coquillage qui fait le bruit de la cloche !|Bon, il faut l'écouter de très près."])
npc('Sailor', (43, 17), 'hgss_sailor', "Tu vois ces rochers, au large ?|Ils ferment toutes les passes.|Aucun bateau n'entre dans la baie, aucun n'en sort.", facing=(0, 1),
    states=["bell_hung > Les rochers ferment toujours les passes.|Mais une cloche, ça s'entend du large.|Les bateaux sauront qu'il y a un village ici."])
# le gamin tourne autour de ses herbes : il y entre, il en sort — un rectangle qui les déborde de deux cases
npc('Youngster', (48, 13), 'hgss_youngster', "Le Professeur dit que des Pokémon vivent dans ces herbes.|Sans le mien, je n'ose pas y mettre un pied.", facing=(1, 0),
    movement='wander', pace=2.0, wander_zone=(47, 11, 7, 6),
    states=["bell_hung > C'est toi qui as rapporté la cloche ? Tout seul ?|Alors moi, je peux bien entrer dans ces herbes. Demain."])
npc('Gardener', (BENCH_SOUTH[0], BENCH_SOUTH[1] + 1), 'hgss_npc_midage_woman', "Ici, les fleurs poussent toutes seules.|Je me contente de les regarder.", facing=(-1, 0), fixed=True,
    states=["bell_hung > Depuis la Veillée, je jardine en fredonnant.|Ma sœur dit que je chante faux. Les fleurs ne se plaignent pas."])

# ============ PENDANT la Veillée : le village autour de la cloche. Elle prend fin dès qu'on quitte l'île (on_leave).
for name, spot, app, text, kw in [
        ('OdileAfter', (CXP - 1, TOP + 4), 'dppt_socialite', "J'ai finalement fait le déplacement. Je voulais l'entendre de près.|Merci.|*Kraak* ...MON DOS !!!", dict(display_name='Mémé Odile', gender='female', facing=(0, -1))),
        ('FisherAfter', (CXP + 1, TOP + 4), 'hgss_fisherman', "J'ai laissé ma canne là-bas. Pour une fois.", dict(facing=(0, -1))),
        ('AlixAfter', (CXP - 2, TOP + 2), 'frlg_aromalady', "J'ai fermé la bibliothèque pour ce soir.|Il y a des choses qu'on n'apprend pas dans les livres.", dict(display_name='Alix', gender='female', facing=(1, 0))),
        ('WorkerAfter', (CXP + 6, TOP + 4), 'dppt_worker', "La Route 1 est ouverte.|On a fini juste à temps pour la Veillée.", dict(facing=(-1, 0))),
        ('WorkerAfter2', (CXP + 4, TOP + 7), 'dppt_worker', "Les outils sont rangés.|Ce soir on ne répare rien : on écoute.", dict(facing=(0, -1))),
        ('VisitorHiker', (CXP + 2, TOP + 4), 'hgss_picnicker', "On l'entendait depuis l'autre rive !", dict(facing=(-1, 0))),
        ('VisitorChild', (CXP - 1, TOP + 7), 'frlg_twins', "Elle est toute petite, la cloche ! Mais elle fait un grand bruit !", dict(facing=(0, -1))),
        ('VisitorWaitress', (CXP - 4, TOP + 2), 'rse_npc_pike_maid', "Si j'avais su, j'aurais apporté de quoi nourrir tout ce monde.", dict(facing=(1, 0))),
        ('VisitorKalos', (ROAD[-1] + 1, GUARD_Y + 10), 'hgss_hiker', "J'ai traversé toute la forêt pour venir. Ça valait la marche.", dict(facing=(0, 1))),
        ('VisitorFestival', (PIER_END[0] - 2, 41), 'hgss_lass', "Une Veillée ! Ma grand-mère m'en parlait tout le temps.", dict(facing=(0, -1))),
        ('VisitorBlackBelt', (ROAD[1], GUARD_Y + 8), 'rse_blackbelt', "Même au dojo, on s'est arrêtés pour écouter.", dict(facing=(0, 1)))]:
    npc(name, spot, app, text, **kw, **DURING)
npc('RolandAfter', (CXP + 2, TOP + 2), 'frlg_ruinmaniac', "Vingt ans que je passais au-dessus sans la voir.", display_name='Roland', gender='male', facing=(-1, 0),
    states=["vigil_over > Je reste encore un peu.|Vingt ans à passer au-dessus : je peux bien la regarder une heure."], **STAYS)
npc('VisitorPainter', (CXP + 4, TOP + 1), 'frlg_painter', "Ne bouge pas... La lumière sur ce bronze est parfaite.", facing=(-1, 0),
    states=["vigil_over > Presque fini. Il me manque le reflet sur le bronze.|Les autres sont repartis. Moi, je reste jusqu'au dernier coup de pinceau."], **STAYS)
npc('RunnerAfter', LOOP[0], 'rse_triathlete_m', "Cette cloche m'a ouvert les yeux !|J'ai couru dans le mauvais sens pendant dix ans !", movement='patrol', pace=3.0, route=[LOOP[0], LOOP[3], LOOP[2], LOOP[1]],
    states=["vigil_over > Je cours dans le bon sens, maintenant. Enfin, je crois.|À chaque tour, je salue la cloche."], **STAYS)

# ============ APRÈS : chacun retourne à ce qu'il faisait. (Mémé Odile et Alix rentrent : voir ludo_house et library.)
npc('FisherLater', PIER_END, 'hgss_fisherman', "Chut... Ça ne mord pas plus qu'avant.|Mais d'ici, maintenant, j'entends la cloche. Les poissons aussi, peut-être.", facing=(0, 1), fixed=True, **AFTER_ALL)
npc('WorkerLater', (ROAD[-1] + 1, GUARD_Y + 8), 'dppt_worker', "La Route 1 est ouverte.|On surveille encore les éboulis, mais tu peux passer.", facing=(-1, 0), **AFTER_ALL)
npc('WorkerLater2', (PIER_END[0] + 3, 41), 'dppt_worker', "On range le matériel du chantier.|Si tu pars vers le nord, bonne route !", facing=(0, 1), **AFTER_ALL)

# ---------- les Pokémon qui volent : des oiseaux de mer, chacun dans sa zone de dix cases sur dix
node('[node name="Sky" type="Node2D" parent="."]\nz_index = 40\n')
FLYERS = {'WingullBayWest': ('wingull', (10, 12, 10, 10)), 'WingullBayEast': ('wingull', (36, 15, 10, 10)), 'WingullWest': ('wingull', (0, 18, 10, 10)), 'WingullSouth': ('wingull', (22, 38, 10, 10)),
          'PelipperEast': ('pelipper', (44, 38, 10, 10)), 'PelipperStrait': ('pelipper', (8, 26, 10, 10))}
for name, (species, (zx, zy, zw, zh)) in FLYERS.items():
    node('[node name="%s" parent="Sky" instance=ExtResource("13_flyer")]\nposition = Vector2(%d, %d)\nspecies = "%s"\nzone = Rect2i(%d, %d, %d, %d)\n' % (name, *px((zx + zw // 2, zy + zh // 2)), species, zx, zy, zw, zh))
node('[node name="Triggers" type="Node2D" parent="."]\n')
for i, x in enumerate(ROAD[1:-1]):
    node('[node name="NorthRoadblock%d" parent="Triggers" instance=ExtResource("5_roadblock")]\nposition = Vector2(%d, %d)\nguard = "%s"\npush_direction = Vector2(0, 1)\nforbidden_flag = "bell_hung"\n' % (i, *px((x, GUARD_Y)), 'GuardWest' if x - ROAD[0] <= ROAD[-1] - x else 'GuardEast'))
node('[node name="Readables" type="Node2D" parent="."]\n')
node('''[node name="Bell" parent="Readables" instance=ExtResource("9_readable")]
position = Vector2(%d, %d)
kind = "item"
text = "Quelque chose brille au fond de l'eau, juste sous le ponton.|@give:tarnished_bell Vous repêchez la Cloche ternie !|Un banc de poissons s'éparpille dans l'eau sombre."
flag = "bell_tarnished"
required_flag = "bell_spotted"

[node name="Glint" type="Polygon2D" parent="Readables/Bell"]
script = ExtResource("14_twinkle")
color = Color(1, 1, 0.85, 0.9)
polygon = PackedVector2Array(0, -3, 1, -1, 3, 0, 1, 1, 0, 3, -1, 1, -3, 0, -1, -1)
''' % px(BELL))
if BELL not in lay.SEA or (BELL[0], BELL[1] + 1) not in DECK: print('  !! la cloche n est pas dans l eau contre un ponton')

# ------------------------------------------------------------------ contrôles : tout se rejoint, dans les trois temps de l'histoire
targets = {'porte ' + k: (v[0], v[1] + 1) for k, v in DOORS.items()}
targets.update({'socle (devant)': (CXP, TOP + 4), 'devant les gardes': (ROAD[1], GUARD_Y + 1), 'derrière les gardes': (ROAD[1], GUARD_Y - 1), 'la sortie du nord': (ROAD[1], 0), 'bout de la jetée': (PIER_END[0], PIER_END[1] - 1),
                'ponton de la cloche': (BELL[0], BELL[1] + 1), 'hautes herbes du sud-ouest': TALL_SW[0]})
def somewhere(x0, y0, x1, y1):
    """Une case de plage libre de ce rectangle : de quoi vérifier qu'on y descend."""
    cells = sorted(c for c in rect(x0, y0, x1, y1) if c in BEACH and c not in SOLID)
    return cells[len(cells) // 2] if cells else (x0, y0)
targets.update({'plage du sud': somewhere(22, 32, 35, 40), 'plage de l ouest': somewhere(2, 34, 8, 45), 'crique du nord': somewhere(19, 10, 31, 17)})
def beside(c, R): return any((c[0] + i, c[1] + j) in R for i, j in lay.NEIGH4)
for phase, flags in PHASES.items():
    there = {c for n, c, req, forb in NPCS if present(req, forb, flags)}
    R = lay.reach_from(lay.START, (SOLID | there) - {lay.START})
    missing = [k for k, c in targets.items() if c not in R and c not in there]
    missing += ['à côté de ' + k for k, c in list(placed.items()) + [(n, c) for n, c, req, forb in NPCS if present(req, forb, flags)] if not k.endswith('+') and c in (SOLID | there) and not beside(c, R)]
    crowd = sum(1 for c in there if PLAZA[0] - 2 <= c[0] <= PLAZA[2] + 2 and PLAZA[1] - 2 <= c[1] <= PLAZA[3] + 2)
    print('%-8s : %d personnages immobiles, %d sur la place, %d cases accessibles%s' % (phase, len(there), crowd, len(R), (' — INACCESSIBLE : %s' % missing) if missing else ''))
    bad = [c for c in LOOP_CELLS if c in SOLID or c in there]
    if bad: print('  !! le tour du coureur est encombré en', sorted(bad), phase)
    edge = [c for c in R if (c[0] in (0, W - 1) or c[1] in (0, H - 1)) and c not in lay.NORTH_GATE]
    if edge: print('  !! bord de carte atteignable :', sorted(edge)[:8])
print('départ', lay.START, '| portes', DOORS, '| objets', ITEMS, '| cloche', BELL)

# ------------------------------------------------------------------ écriture
def encode(cells_):
    raw = struct.pack('<H', 0)
    for (x, y), t in sorted(cells_.items(), key=lambda kv: (kv[0][1], kv[0][0])): raw += struct.pack('<hhHHHH', x, y, t[0], t[1], t[2], t[3] if len(t) > 3 else 0)
    return base64.b64encode(raw).decode()
def layer(name, parent, cells_, ysort=False):
    return '[node name="%s" type="TileMapLayer" parent="%s"]\n%stile_map_data = PackedByteArray("%s")\ntile_set = ExtResource("1_ian7c")\n' % (name, parent, 'y_sort_enabled = true\n' if ysort else '', encode(cells_))
head = '''[gd_scene load_steps=15 format=4]

[ext_resource type="TileSet" uid="uid://c38ht37ho6e3a" path="{R}resources/tilesets/level.tres" id="1_ian7c"]
[ext_resource type="PackedScene" path="{R}scenes/levels/scene_trigger.tscn" id="2_door"]
[ext_resource type="PackedScene" path="{R}scenes/levels/sign.tscn" id="3_sign"]
[ext_resource type="PackedScene" path="{R}scenes/characters/npc.tscn" id="4_npc"]
[ext_resource type="PackedScene" path="{R}scenes/levels/roadblock.tscn" id="5_roadblock"]
[ext_resource type="Script" path="{R}scripts/gameplay/levels/Readable.kt" id="6_readable_script"]
[ext_resource type="Texture2D" path="{R}assets/levels/bell_stand.png" id="7_stand"]
[ext_resource type="Texture2D" path="{R}assets/levels/environments.png" id="8_environments"]
[ext_resource type="PackedScene" path="{R}scenes/levels/readable.tscn" id="9_readable"]
[ext_resource type="PackedScene" path="{R}scenes/levels/street_lamp.tscn" id="10_lamp"]
[ext_resource type="PackedScene" path="{R}scenes/levels/window_glow.tscn" id="11_glow"]
[ext_resource type="Texture2D" path="{R}assets/levels/island.png" id="12_island"]
[ext_resource type="PackedScene" path="{R}scenes/levels/flyer.tscn" id="13_flyer"]
[ext_resource type="Script" path="{R}scripts/gameplay/levels/Twinkle.kt" id="14_twinkle"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_stand"]
size = Vector2(48, 16)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_statue"]
size = Vector2(16, 16)

[node name="Level" type="Node2D"]
metadata/location = "Bourg-Ludo"
metadata/banner = "wood"
metadata/music = "new_bark_town"
metadata/daylight = true
metadata/encounter_rate = 3
metadata/encounter_rate_run = 5
metadata/wild = "mulotin:2-4*50 | piafeuille:2-5*35 | chenibulle:3*15"
metadata/on_leave = "bell_hung > vigil_over"

[node name="Background" type="Node2D" parent="."]
'''.replace('{R}', RES)
parts = [head] + [layer(n, 'Background', L[n]) for n in lay.ORDER]
parts.append('[node name="World" type="Node2D" parent="."]\ny_sort_enabled = true\n')
parts += [layer(n, 'World', L[n], True) for n in ('Trees', 'Props', 'Houses')] + nodes
if '--preview' in sys.argv:
    marks = [(c, (230, 40, 40) if n.startswith('Item') else ((240, 200, 60) if n.startswith('Lamp') else (200, 120, 60))) for n, c in placed.items()] + [(c, (60, 60, 230)) for n, c, r, f in NPCS if r is None]
    lay.write_preview(sys.argv[sys.argv.index('--preview') + 1], marks)
if '--map' in sys.argv: lay.show_map()
if '--grid' in sys.argv:
    open(sys.argv[sys.argv.index('--grid') + 1], 'w').write('\n'.join(''.join('#' if (x, y) in SOLID else '.' for x in range(W)) for y in range(H)))
if '--write' in sys.argv:
    open(B + 'scenes/levels/start_island.tscn', 'w').write('\n'.join(parts))
    print('écrit')
if '--where' in sys.argv:          # où est quoi : de quoi mettre à jour les tests et la documentation
    for n, c in sorted(placed.items()): print('  %-18s %s' % (n, c))
    for n, c, req, forb in NPCS: print('  %-18s %s  %s' % (n, c, ('si ' + req if req else '') + (' sauf ' + forb if forb else '')))
    print('  tour du coureur', LOOP, '| socle', (CXP, TOP + 1), '| statues', STATUES, '| serviettes', TOWELS, '| trouée', ROAD, 'gardes en y', GUARD_Y)
