import sys, re, collections
sys.path.insert(0, '/tmp/plw'); sys.path.insert(0, '/tmp/plw/island')
import gen, plan
from gen import L, T, W, H, DECK, PLAT_EDGE, STAIRS, HOUSES, DOORS, BLOCKED, is_land, PINES, BLOOMS, PLZ, BELL, OX, OY, P, LOOP, LOOP_CELLS, LANDINGS
from tmx import encode
from crop import load

ROOT = '/Users/godart/Documents/Projects/Perso/PokeLudoWorld/'
B = ROOT + 'src/main/kotlin/fr/skyle/pokeludoworld/'
RES = 'res://src/main/kotlin/fr/skyle/pokeludoworld/'
opacity = gen.opacity

# ------------------------------------------------------------------ TileSet
FULL = 'PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)'
NO_FLYERS = '--no-flyers' in sys.argv
FACADES = '--facades' in sys.argv          # les deux maisons orange restent des façades (la PR des intérieurs ouvre leurs portes)
def rep1(s, a, b):
    assert s.count(a) == 1, (s.count(a), a)
    return s.replace(a, b)
def patch_tileset():
    p = B + 'resources/tilesets/level.tres'
    s = open(p).read()
    heads = [m.start() for m in re.finditer(r'^\[sub_resource type="TileSetAtlasSource"', s, flags=re.M)] + [s.index('\n[resource]')]
    def block(name):
        for a, b in zip(heads, heads[1:]):
            if 'resource_name = "%s"' % name in s[a:b]: return a, b
        raise KeyError(name)
    def set_tile(name, ax, ay, props, size=None):
        nonlocal s, heads
        a, b = block(name); blk = s[a:b]
        key = '%d:%d/0' % (ax, ay)
        lines = blk.split('\n')
        lines = [l for l in lines if not any(l.startswith('%s/%s' % (key, k)) for k in ('physics_layer_0', 'y_sort_origin', 'material') if k.split('/')[0] in [q.split('/')[0] for q in props] or k == 'physics_layer_0' and props.get('physics_layer_0/polygon_0/points', 1) is None)]
        if (key + ' = 0') not in lines:
            if size: lines.insert(len(lines) - 1 if lines[-1] == '' else len(lines), '%d:%d/size_in_atlas = Vector2i(%d, %d)' % (ax, ay, size[0], size[1]))
            lines.insert(len(lines) - 1 if lines[-1] == '' else len(lines), key + ' = 0')
        i = lines.index(key + ' = 0')
        add = ['%s/%s = %s' % (key, k, v) for k, v in props.items() if v is not None]
        lines[i + 1:i + 1] = add
        s = s[:a] + '\n'.join(lines) + s[b:]
        heads = [m.start() for m in re.finditer(r'^\[sub_resource type="TileSetAtlasSource"', s, flags=re.M)] + [s.index('\n[resource]')]
    if 'ShaderMaterial_sway_top' not in s:
        s = s.replace('[sub_resource type="ShaderMaterial" id="ShaderMaterial_water"]', '[ext_resource type="Shader" path="%sresources/shaders/sway.gdshader" id="6_sway"]\n\n[sub_resource type="ShaderMaterial" id="ShaderMaterial_water"]' % RES, 1)
        mats = '''[sub_resource type="ShaderMaterial" id="ShaderMaterial_sway_bottom"]
shader = ExtResource("6_sway")

[sub_resource type="ShaderMaterial" id="ShaderMaterial_sway_top"]
shader = ExtResource("6_sway")
shader_parameter/base = 1.0

[sub_resource type="ShaderMaterial" id="ShaderMaterial_sway_palm"]
shader = ExtResource("6_sway")
shader_parameter/reach = 1.3
shader_parameter/tile = Vector2(64, 64)
shader_parameter/origin = Vector2(481, 177)

'''
        i = s.index('[sub_resource type="TileSetAtlasSource"'); s = s[:i] + mats + s[i:]
        heads = [m.start() for m in re.finditer(r'^\[sub_resource type="TileSetAtlasSource"', s, flags=re.M)] + [s.index('\n[resource]')]
    if 'TileSetAtlasSource_island' not in s:
        tex = '[ext_resource type="Texture2D" path="%sassets/levels/interiors.png" id="2_interiors"]' % RES
        s = rep1(s, tex, tex + '\n[ext_resource type="Texture2D" path="%sassets/levels/island.png" id="7_island"]' % RES)
        lines = ['[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_island"]', 'resource_name = "island"', 'texture = ExtResource("7_island")']
        def island_props(cx, cy):          # (plein ?, tri) — rien pour ce qui se pose dans le fond
            if cy == 2 and 8 <= cx <= 11: return (True, 8)                                   # petits rochers dans l'eau
            if 11 <= cx <= 14 and cy in (3, 4, 5): return (cy == 5, {3: 40, 4: 24, 5: 8}[cy])   # parasols : seul le pied est plein
            if (cx, cy) in ((0, 5), (2, 5)): return (False, 24)                              # haut des caisses, du pot de fleurs
            if (cx, cy) in ((0, 6), (1, 6), (2, 6)): return (True, 8)                        # caisses, pot de fleurs
            if (cx, cy) in ((4, 5), (5, 5)): return (False, 24)                              # banc de face : le haut du dossier
            if (cx, cy) in ((4, 6), (5, 6)): return (True, 8)                                # banc de face : l'assise
            if cx in (8, 9) and cy in (3, 4, 5): return (cy != 3, {3: 40, 4: 24, 5: 8}[cy])     # banc de profil : deux cases pleines
            return None
        for (cx, cy) in sorted(gen.ISL_IMG):
            lines.append('%d:%d/0 = 0' % (cx, cy))
            pr = island_props(cx, cy)
            if pr:
                if pr[0]: lines.append('%d:%d/0/physics_layer_0/polygon_0/points = %s' % (cx, cy, FULL))
                lines.append('%d:%d/0/y_sort_origin = %d' % (cx, cy, pr[1]))
        s = rep1(s, '\n[resource]', '\n' + '\n'.join(lines) + '\n\n[resource]')
        s = s.rstrip('\n') + '\nsources/10 = SubResource("TileSetAtlasSource_island")\n'
        heads = [m.start() for m in re.finditer(r'^\[sub_resource type="TileSetAtlasSource"', s, flags=re.M)] + [s.index('\n[resource]')]
    WATER = 'SubResource("ShaderMaterial_water")'
    E = 'environments'
    set_tile(E, 6, 32, {'material': WATER, 'physics_layer_0/polygon_0/points': FULL})                 # la mer
    for (ax, ay) in [(x, y) for x in (15, 16, 17) for y in (31, 32, 33)] + [(18, 31), (19, 31), (18, 32), (19, 32)]:
        set_tile(E, ax, ay, {'material': WATER, 'physics_layer_0/polygon_0/points': None})          # le rivage, sur la case de sable
    for (ax, ay) in [(x, y) for x in (10, 11, 12) for y in (13, 14, 15)] + [(13, 13), (14, 13), (13, 14), (14, 14)]:
        set_tile(E, ax, ay, {'physics_layer_0/polygon_0/points': None})                             # la plage
    # plateau : les bords pleins sont ceux où la falaise se voit. Le bord du haut est de l'herbe : on s'y
    # tient, et c'est une bande fine le long du rebord (couche des rebords) qui empêche de le franchir.
    # Deux coins rentrants sont de l'herbe aussi.
    for (ax, ay) in [(38, 24), (40, 24), (38, 25), (40, 25), (38, 26), (39, 26), (40, 26), (41, 24), (43, 24)]:
        set_tile(E, ax, ay, {'physics_layer_0/polygon_0/points': FULL})
    set_tile(E, 39, 24, {'physics_layer_0/polygon_0/points': None, 'physics_layer_1/polygon_0/points': 'PackedVector2Array(-8, -8, 8, -8, 8, -5, -8, -5)'})
    for (ax, ay) in [(41, 26), (43, 26)]: set_tile(E, ax, ay, {'physics_layer_0/polygon_0/points': None})
    if 'physics_layer_1/collision_layer' not in s:
        s = rep1(s, 'physics_layer_0/collision_mask = 1\n', 'physics_layer_0/collision_mask = 1\nphysics_layer_1/collision_layer = 8\nphysics_layer_1/collision_mask = 0\n')
        heads = [m.start() for m in re.finditer(r'^\[sub_resource type="TileSetAtlasSource"', s, flags=re.M)] + [s.index('\n[resource]')]
    for ax in (26, 27, 28):
        for ay in (21, 22, 23): set_tile(E, ax, ay, {'physics_layer_0/polygon_0/points': FULL, 'y_sort_origin': 8})
    for ax in (47, 48, 49):
        for ay in (21, 22, 23, 24): set_tile(E, ax, ay, {'physics_layer_0/polygon_0/points': None})
    for name in HOUSES:
        ax0, ay0, w, h = HOUSES[name][:4]
        for j in range(h):
            for i in range(w):
                o = opacity(ax0 + i, ay0 + j)
                if o == 0: continue
                if (ax0 + i, ay0 + j) in gen.SOFT_ROOF:      # on passe derrière une maison : le haut de son toit se franchit
                    set_tile(E, ax0 + i, ay0 + j, {'physics_layer_0/polygon_0/points': None, 'y_sort_origin': 9})
                elif not name.startswith('orange'): continue   # pour le reste, les maisons de la première carte gardent leurs collisions
                elif (i, j) == (HOUSES[name][5], h - 1) and not FACADES:      # la porte s'ouvre : décor franchissable, trié depuis le haut de la case (sinon elle passe sur le joueur qui entre)
                    set_tile(E, ax0 + i, ay0 + j, {'physics_layer_0/polygon_0/points': None, 'y_sort_origin': -15})
                else:
                    set_tile(E, ax0 + i, ay0 + j, {'physics_layer_0/polygon_0/points': FULL if o >= 0.25 else None, 'y_sort_origin': 9})
    for (ax, ay) in PINES:        # petits sapins : pied solide, cime par-dessus
        set_tile(E, ax, ay, {'physics_layer_0/polygon_0/points': None, 'y_sort_origin': 24})
        set_tile(E, ax, ay + 1, {'physics_layer_0/polygon_0/points': FULL, 'y_sort_origin': 8})
    for (ax, ay) in BLOOMS:       # grandes fleurs : on marche dessus, elles passent sous le joueur
        set_tile(E, ax, ay, {'material': 'SubResource("ShaderMaterial_sway_top")', 'physics_layer_0/polygon_0/points': None, 'y_sort_origin': 1})
        set_tile(E, ax, ay + 1, {'material': 'SubResource("ShaderMaterial_sway_bottom")', 'physics_layer_0/polygon_0/points': None, 'y_sort_origin': -15})
    for (ax, ay) in gen.LAND_ROCKS:   # rochers de plage : pleins, la moitié haute triée avec le pied
        for i in (0, 1):
            set_tile(E, ax + i, ay, {'physics_layer_0/polygon_0/points': FULL, 'y_sort_origin': 24})
            set_tile(E, ax + i, ay + 1, {'physics_layer_0/polygon_0/points': FULL, 'y_sort_origin': 8})
    for (ax, ay) in gen.BUSHES:
        set_tile(E, ax, ay, {'physics_layer_0/polygon_0/points': FULL, 'y_sort_origin': 8})
    for (ax, ay) in gen.STAIR_UNDER:      # le bord de plateau sous un escalier : même dessin, sans collision
        a_, b_ = block(E); lines_ = s[a_:b_].split('\n'); key = '%d:%d/' % (ax, ay)
        i0 = lines_.index(key + '0 = 0'); i1 = max(i for i, l in enumerate(lines_) if l.startswith(key + '0'))
        lines_.insert(i1 + 1, key + '1 = 1'); lines_.insert(i0, key + 'next_alternative_id = 2')
        s = s[:a_] + '\n'.join(lines_) + s[b_:]
        heads = [m.start() for m in re.finditer(r'^\[sub_resource type="TileSetAtlasSource"', s, flags=re.M)] + [s.index('\n[resource]')]
    BT = 'border_environments'
    set_tile(E, gen.ROCKLET[0], gen.ROCKLET[1], {'physics_layer_0/polygon_0/points': FULL, 'y_sort_origin': 8})
    # arbres 3x3 : pied solide sur deux rangées ; triés assez haut pour qu'un personnage
    # debout à côté du tronc passe devant, jamais derrière
    for t in (12, 15, 18, 21, 24, 27, 30):
        set_tile(BT, t, 0, {'physics_layer_0/polygon_0/points': 'PackedVector2Array(-24, -8, 24, -8, 24, 24, -24, 24)', 'y_sort_origin': 14})
    # palmier : son dessin fait 53 px de large, il lui faut quatre cases
    set_tile(BT, 30, 11, {'material': 'SubResource("ShaderMaterial_sway_palm")', 'physics_layer_0/polygon_0/points': 'PackedVector2Array(-8, 8, 8, 8, 8, 24, -8, 24)', 'y_sort_origin': 14}, size=(4, 4))
    missing = []
    names = {5: 'environments', 6: 'border_environments', 10: 'island'}
    for lname, cells_ in L.items():
        for c, t in cells_.items():
            a_, b_ = block(names[t[0]])
            if ('\n%d:%d/0 = 0\n' % (t[1], t[2])) not in s[a_:b_] + '\n': missing.append((lname, c, t))
    if missing: print('  !! tuiles posées mais non déclarées :', len(missing), sorted({m[2] for m in missing})[:30])
    open(p, 'w').write(s)

# ------------------------------------------------------------------ carte
def px(c): return (c[0] * 16 + 8, c[1] * 16 + 8)
SOLID = set(BLOCKED) | {(x, y) for y in range(H) for x in range(W) if T[y][x] == '~' and (x, y) not in DECK}
SOLID -= STAIRS
for d in DOORS.values(): SOLID.discard(d)
if FACADES:
    for c in ('orange_small', 'orange_big'): SOLID.add(DOORS[c])
OBJ = []      # (case, raison) : objets solides posés par la scène
def solid(c, why):
    OBJ.append((c, why))
    if c in SOLID or not is_land(*c): print('  !! %s en %s : case prise ou hors terre' % (why, c))
    SOLID.add(c)

LUDO, LIB, LAB = DOORS['ludo'], DOORS['library'], DOORS['lab']
SPAWN = (LUDO[0], LUDO[1] + 1)
nodes = []
def node(text): nodes.append(text)
LEVELS = RES + 'scenes/levels/'

def sign(name, c, text):
    solid(c, name); node('[node name="%s" parent="World" instance=ExtResource("3_sign")]\nposition = Vector2(%d, %d)\ntext = "%s"\n' % (name, *px(c), text))
def lamp(name, c):
    solid(c, name); node('[node name="%s" parent="World" instance=ExtResource("10_lamp")]\nposition = Vector2(%d, %d)\n' % (name, *px(c)))
def glow(name, x, y): node('[node name="%s" parent="World" instance=ExtResource("11_glow")]\nposition = Vector2(%d, %d)\n' % (name, x, y))

for c in gen.OBJECTS.values(): SOLID.discard(c)
TEXTS = {'SignLudo': "Maison de Ludo.|La porte n'est jamais fermée, entrez donc.", 'SignLibrary': "Bibliothèque de Bourg-Ludo.|Entrée libre. On parle à voix basse.",
         'SignLab': "Laboratoire du Professeur.|Les Pokémon blessés y sont soignés.", 'SignNorth': "Route du nord.|Elle quitte l'île par la falaise.", 'SignPier': "Jetée du sud.|Attention : planches glissantes."}
for name, c in gen.SIGNS.items(): sign(name, c, TEXTS[name])

# --- la place : socle de la cloche, statues ---
CXP = (PLZ[0] + PLZ[2]) // 2; TOP = PLZ[1]
PX0, PY0 = CXP * 16 + 8, TOP * 16          # centre de la place en x, haut de la place en y
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
''' % (PX0, PY0 + 31, PX0, PY0 + 40))
for c in [(CXP - 1, TOP + 1), (CXP, TOP + 1), (CXP + 1, TOP + 1), (CXP - 1, TOP + 2), (CXP + 1, TOP + 2), (CXP - 1, TOP + 3), (CXP + 1, TOP + 3)]: SOLID.add(c)
for name, cx, flip in (('StatueWest', CXP - 3, 'true'), ('StatueEast', CXP + 3, 'false')):
    SOLID.add((cx, TOP + 1))
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
''' % (name, cx * 16 + 8, (TOP + 1) * 16 + 8, name, flip, name))

for name, (c, why) in gen.LAMPS.items(): lamp(name, c)
ox, oy = HOUSES['ludo'][4][0] * 16, HOUSES['ludo'][4][1] * 16
glow('GlowLudoUp', ox + 40, oy + 64); glow('GlowLudoDown', ox + 51, oy + 87)
ox, oy = HOUSES['library'][4][0] * 16, HOUSES['library'][4][1] * 16
glow('GlowLibrary', ox + 43, oy + 70)
ox, oy = HOUSES['lab'][4][0] * 16, HOUSES['lab'][4][1] * 16
glow('GlowLabLeft', ox + 22, oy + 74); glow('GlowLabRight', ox + 58, oy + 74); glow('GlowLabWing', ox + 97, oy + 68)

FOUND = {'ItemPotion': ('potion', "Vous trouvez une Potion !|Vous rangez la Potion dans la poche Objets.", 'found_island_potion'),
         'ItemBall': ('poke_ball', "Vous trouvez une Poké Ball !|Vous rangez la Poké Ball dans la poche Poké Balls.", 'found_island_ball')}
for name, c in gen.ITEMS.items():
    item, text, flag = FOUND[name]
    solid(c, name)
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
node('[node name="SpawnPoint" type="Node2D" parent="."]\nposition = Vector2(%d, %d)\n' % px(SPAWN))
node('[node name="Doors" type="Node2D" parent="."]\n')
OPEN = [('MaisonLudo', LUDO, 'ludo_house'), ('Bibliotheque', LIB, 'library'), ('Laboratoire', LAB, 'lab_house')]
if not FACADES: OPEN += [('MaisonNord', DOORS['orange_small'], 'orange_house_north'), ('MaisonSud', DOORS['orange_big'], 'orange_house_south')]
for name, c, scene in OPEN:
    node('[node name="%s" parent="Doors" instance=ExtResource("2_door")]\nposition = Vector2(%d, %d)\ntarget_scene = "%s%s.tscn"\ntarget_door = "Entree"\nentry_direction = Vector2(0, 1)\n' % (name, *px(c), LEVELS, scene))

NPCS = []            # (nom, case, drapeau requis, drapeau interdit) des personnages immobiles
FRONTS = {(c[0] + d[0], c[1] + d[1]) for c in STAIRS for d in ((1, 0), (-1, 0), (0, 1), (0, -1))} | STAIRS | LANDINGS
PHASES = {'avant': set(), 'pendant': {'bell_hung'}, 'après': {'bell_hung', 'vigil_over'}}
def present(req, forb, flags): return (req is None or req in flags) and (forb is None or forb not in flags)
def stand(name, c, req, forb):
    """La case la plus proche de c où un personnage immobile ne gêne personne."""
    taken = {q for n, q, r, f in NPCS if any(present(r, f, fl) and present(req, forb, fl) for fl in PHASES.values())}      # ceux qu'il peut croiser
    def ok(q):
        return is_land(*q) and q not in SOLID and q not in taken and q not in LOOP_CELLS and q not in FRONTS and (q in L['Plaza'] or not gen.pinches(q)) \
            and all(q != (d[0], d[1] + 1) and q != (d[0], d[1] + 2) for d in DOORS.values()) and not hidden(q)
    cands = sorted(((c[0] + i, c[1] + j) for i in range(-3, 4) for j in range(-3, 4)), key=lambda q: (abs(q[0] - c[0]) + abs(q[1] - c[1]), q))
    for q in cands:
        if ok(q):
            if q != c: print('  (%s : %s -> %s)' % (name, c, q))
            return q
    print('  !! %s : aucune case convenable près de %s' % (name, c)); return c
def hidden(q):
    """Derrière la couronne d'un palmier ou le pied d'un arbre : on ne l'y verrait pas."""
    return any(abs(q[0] - fx) <= 1 and fy - 3 <= q[1] <= fy - 1 for fx, fy in gen.palm_feet) or any(abs(q[0] - x) <= 1 and q[1] == y - 1 for (x, y), t in L['Trees'].items() if t[2] == 0)
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
    for k in ('movement',):
        if k in kw: lines.append('%s = "%s"' % (k, kw[k]))
    if 'pace' in kw: lines.append('pace = %s' % kw['pace'])
    if 'wander_layer' in kw: lines.append('wander_layer = "%s"' % kw['wander_layer'])
    if 'route' in kw: lines.append('route = PackedVector2Array(%s)' % ', '.join('%d, %d' % p for p in kw['route']))
    for k in ('required_flag', 'forbidden_flag'):
        if k in kw: lines.append('%s = "%s"' % (k, kw[k]))
    node('\n'.join(lines) + '\n')

GUARD_Y = gen.GUARD_Y
road = gen.ROAD
PIER_END = max(DECK, key=lambda c: (c[1], c[0]))
BEFORE, DURING, AFTER_ALL = dict(forbidden_flag='bell_hung'), dict(required_flag='bell_hung', forbidden_flag='vigil_over'), dict(required_flag='vigil_over')
STAYS = dict(required_flag='bell_hung')      # arrive pour la Veillée, et reste ensuite

# ============ AVANT que la cloche soit accrochée
CLOSED = "Désolé, le passage est fermé.|C'est dangereux par là : la route du nord n'est pas encore sûre."
npc('GuardWest', (road[0], GUARD_Y), 'dppt_worker', CLOSED, facing=(0, 1), fixed=True, **BEFORE)
npc('GuardEast', (road[-1], GUARD_Y), 'dppt_worker', CLOSED, facing=(0, 1), fixed=True, **BEFORE)
npc('Runner', LOOP[0], 'rse_triathlete_m', "Pff... pff... Je fais le tour de la place tous les matins.|Ne reste pas au milieu du chemin, je perds mon rythme.",
    facing=(0, 1), movement='patrol', pace=3.0, route=LOOP, **BEFORE)
npc('Fisher', PIER_END, 'hgss_fisherman', "Chut... Ça ne mord pas fort aujourd'hui.|Il paraît qu'il y a de gros poissons au large.", facing=(0, 1), fixed=True, **BEFORE)
npc('Roland', (gen.LIB_STAIR[0] + 4, gen.LIB_STAIR[1] + 2), 'frlg_ruinmaniac', "Ces eaux, j'y ai plongé vingt ans.|Elles ont encore des choses à dire, je le sens.", display_name='Roland', gender='male', facing=(1, 0),
    states=["bell_register > Sous le ponton de l'ouest, là où l'eau est profonde...|...il y a quelque chose qui accroche la lumière.|Moi, je n'y plonge plus. Trop froid, trop de courant.",
            "bell_tarnished > Alors c'était ça qui brillait.|Une cloche. Vingt ans que je passe au-dessus."], **BEFORE)

# ============ TOUJOURS LÀ : chacun près de ce qui l'occupe ; sa réplique change une fois la cloche accrochée
npc('GrassWatcher', (gen.TALL[0][0] + 1, gen.TALL[0][1] + 1), 'frlg_bugcatcher', "Ces herbes sont si hautes qu'on s'y perd.|Je cherche des insectes, mais je n'ai encore rien trouvé.",
    facing=(0, 1), states=["bell_hung > Il paraît que c'est toi qui as retrouvé la cloche ! Bravo !|Moi, toujours pas le moindre insecte."], movement='wander', pace=2.0, wander_layer='Background/Grass')
npc('BenchLady', (gen.FURN['BenchLudo'][-1][0] + 1, gen.FURN['BenchLudo'][-1][1]), 'rse_expert_f', "Je viens m'asseoir ici tous les matins.|D'ici, on voit passer tout le village.", facing=(0, 1),
    states=["bell_hung > Je viens toujours m'asseoir ici le matin.|Maintenant, j'attends que la cloche sonne pour rentrer."])
npc('Sunbather', gen.TOWELS['TowelSouth'], 'hgss_swimmer_f', "Le sable est chaud, l'eau est fraîche.|Je ne bouge plus d'ici avant la nuit.", facing=(0, 1),
    states=["bell_hung > J'ai entendu la cloche depuis ma serviette.|Je n'ai pas bougé pour autant."])
npc('Swimmer', gen.TOWELS['TowelCove'], 'hgss_swimmer_m', "L'eau de la crique est la plus calme de l'île.|Les vagues se cassent sur les rochers avant d'arriver.", facing=(0, 1),
    states=["bell_hung > J'étais dans l'eau quand la cloche a sonné.|J'ai bu la tasse. Ça valait le coup."])
npc('ShellKid', (gen.TOWELS['TowelCove'][0] + 4, gen.TOWELS['TowelCove'][1]), 'hgss_tuber_m', "Je cherche des coquillages.|Pour l'instant, j'ai surtout trouvé des cailloux.", facing=(0, 1),
    states=["bell_hung > J'ai trouvé un coquillage qui fait le bruit de la cloche !|Bon, il faut l'écouter de très près."])
npc('Sailor', (gen.LAMPS['LampDeckNE'][0][0] + 4, gen.LAMPS['LampDeckNE'][0][1]), 'hgss_sailor', "Tu vois ces rochers, au large ?|Ils ferment toutes les passes.|Aucun bateau n'entre dans la baie, aucun n'en sort.", facing=(0, 1),
    states=["bell_hung > Les rochers ferment toujours les passes.|Mais une cloche, ça s'entend du large.|Les bateaux sauront qu'il y a un village ici."])
npc('Youngster', (gen.TALL[2][0] - 1, gen.TALL[2][3]), 'hgss_youngster', "Le Professeur dit que des Pokémon vivent dans ces herbes.|Sans le mien, je n'ose pas y mettre un pied.", facing=(1, 0),
    states=["bell_hung > C'est toi qui as rapporté la cloche ? Tout seul ?|Alors moi, je peux bien entrer dans ces herbes. Demain."])
npc('Gardener', (gen.FURN['BenchOrange'][-1][0] + 1, gen.FURN['BenchOrange'][-1][1]), 'hgss_npc_midage_woman', "Ici, les fleurs poussent toutes seules.|Je me contente de les regarder.", facing=(0, 1),
    states=["bell_hung > Depuis la Veillée, je jardine en fredonnant.|Ma sœur dit que je chante faux. Les fleurs ne se plaignent pas."])

# ============ PENDANT la Veillée : le village autour de la cloche. Elle prend fin dès qu'on quitte l'île (on_leave).
for name, spot, app, text, kw in [
        ('OdileAfter', (CXP - 1, TOP + 4), 'dppt_socialite', "J'ai finalement fait le déplacement. Je voulais l'entendre de près.|Merci.|*Kraak* ...MON DOS !!!", dict(display_name='Mémé Odile', gender='female', facing=(0, -1))),
        ('FisherAfter', (CXP + 1, TOP + 4), 'hgss_fisherman', "J'ai laissé ma canne là-bas. Pour une fois.", dict(facing=(0, -1))),
        ('AlixAfter', (CXP - 2, TOP + 2), 'frlg_aromalady', "J'ai fermé la bibliothèque pour ce soir.|Il y a des choses qu'on n'apprend pas dans les livres.", dict(display_name='Alix', gender='female', facing=(1, 0))),
        ('WorkerAfter', (CXP + 6, TOP + 4), 'dppt_worker', "La route du nord est ouverte.|On a fini juste à temps pour la Veillée.", dict(facing=(-1, 0))),
        ('WorkerAfter2', (CXP + 4, TOP + 6), 'dppt_worker', "Les outils sont rangés.|Ce soir on ne répare rien : on écoute.", dict(facing=(0, -1))),
        ('VisitorHiker', (CXP + 2, TOP + 4), 'hgss_picnicker', "On l'entendait depuis l'autre rive !", dict(facing=(-1, 0))),
        ('VisitorChild', (CXP - 1, TOP + 6), 'frlg_twins', "Elle est toute petite, la cloche ! Mais elle fait un grand bruit !", dict(facing=(0, -1))),
        ('VisitorWaitress', (CXP - 4, TOP + 2), 'rse_npc_pike_maid', "Si j'avais su, j'aurais apporté de quoi nourrir tout ce monde.", dict(facing=(1, 0))),
        ('VisitorKalos', (road[3], GUARD_Y + 4), 'hgss_hiker', "J'ai traversé toute la forêt pour venir. Ça valait la marche.", dict(facing=(0, 1))),
        ('VisitorFestival', (gen.PIER[0] + 2, gen.PIER[1] - 2), 'hgss_lass', "Une Veillée ! Ma grand-mère m'en parlait tout le temps.", dict(facing=(0, -1))),
        ('VisitorBlackBelt', (road[1], GUARD_Y + 6), 'rse_blackbelt', "Même au dojo, on s'est arrêtés pour écouter.", dict(facing=(0, 1)))]:
    npc(name, spot, app, text, **kw, **DURING)
# ...et ceux qui restent près de la cloche une fois la Veillée finie
npc('RolandAfter', (CXP + 2, TOP + 2), 'frlg_ruinmaniac', "Vingt ans que je passais au-dessus sans la voir.", display_name='Roland', gender='male', facing=(-1, 0),
    states=["vigil_over > Je reste encore un peu.|Vingt ans à passer au-dessus : je peux bien la regarder une heure."], **STAYS)
npc('VisitorPainter', (CXP + 4, TOP + 1), 'frlg_painter', "Ne bouge pas... La lumière sur ce bronze est parfaite.", facing=(-1, 0),
    states=["vigil_over > Presque fini. Il me manque le reflet sur le bronze.|Les autres sont repartis. Moi, je reste jusqu'au dernier coup de pinceau."], **STAYS)
npc('RunnerAfter', LOOP[0], 'rse_triathlete_m', "Cette cloche m'a ouvert les yeux !|J'ai couru dans le mauvais sens pendant dix ans !", movement='patrol', pace=3.0, route=[LOOP[0], LOOP[3], LOOP[2], LOOP[1]],
    states=["vigil_over > Je cours dans le bon sens, maintenant. Enfin, je crois.|À chaque tour, je salue la cloche."], **STAYS)

# ============ APRÈS : chacun retourne à ce qu'il faisait. (Mémé Odile et Alix rentrent : voir ludo_house et library.)
npc('FisherLater', PIER_END, 'hgss_fisherman', "Chut... Ça ne mord pas plus qu'avant.|Mais d'ici, maintenant, j'entends la cloche. Les poissons aussi, peut-être.", facing=(0, 1), fixed=True, **AFTER_ALL)
npc('WorkerLater', (road[0] - 1, GUARD_Y + 1), 'dppt_worker', "La route du nord est ouverte.|On surveille encore les éboulis, mais tu peux passer.", facing=(1, 0), **AFTER_ALL)
npc('WorkerLater2', (gen.FURN['CratesPier'][0][0], gen.FURN['CratesPier'][0][1] - 2), 'dppt_worker', "On range le matériel du chantier.|Si tu pars vers le nord, bonne route !", facing=(0, 1), **AFTER_ALL)

# ---------- les Pokémon qui volent : du décor, au-dessus de tout, sans corps. Chacun dans sa zone.
if not NO_FLYERS:
    node('[node name="Sky" type="Node2D" parent="."]\nz_index = 40\n')
    for name, (species, (zx, zy, zw, zh)) in plan.FLYERS.items():
        node('[node name="%s" parent="Sky" instance=ExtResource("13_flyer")]\nposition = Vector2(%d, %d)\nspecies = "%s"\nzone = Rect2i(%d, %d, %d, %d)\n' % (name, *px((zx + zw // 2, zy + zh // 2)), species, zx, zy, zw, zh))
node('[node name="Triggers" type="Node2D" parent="."]\n')
for i, x in enumerate(road[1:-1]):
    node('[node name="NorthRoadblock%d" parent="Triggers" instance=ExtResource("5_roadblock")]\nposition = Vector2(%d, %d)\nguard = "%s"\npush_direction = Vector2(0, 1)\nforbidden_flag = "bell_hung"\n' % (i, *px((x, GUARD_Y)), 'GuardWest' if x - road[0] <= road[-1] - x else 'GuardEast'))
node('[node name="Readables" type="Node2D" parent="."]\n')
ENDS = [x for x in range(W) if (x, 0) not in L['Cliffs']]
for i, x in enumerate(ENDS):
    node('[node name="RoadEnd%d" parent="Readables" instance=ExtResource("9_readable")]\nposition = Vector2(%d, %d)\ntext = "La route du nord s\'enfonce dans la montagne.|Le chemin n\'est pas encore tracé au-delà."\n' % (i, *px((x, 0))))
    SOLID.add((x, 0))
node('''[node name="Bell" parent="Readables" instance=ExtResource("9_readable")]
position = Vector2(%d, %d)
kind = "item"
text = "Quelque chose brille au fond de l'eau, juste sous le ponton.|@give:tarnished_bell Vous repêchez la Cloche ternie !|Un banc de poissons s'éparpille dans l'eau sombre."
flag = "bell_tarnished"

[node name="Glint" type="Polygon2D" parent="Readables/Bell"]
color = Color(1, 1, 0.85, 0.9)
polygon = PackedVector2Array(0, -3, 1, -1, 3, 0, 1, 1, 0, 3, -1, 1, -3, 0, -1, -1)
''' % px(BELL))

# ------------------------------------------------------------------ les personnages ne gênent personne
for name, c, req, forb in NPCS:
    why = []
    if c in LOOP_CELLS: why.append('sur le tour de la place')
    if c in FRONTS: why.append('devant un escalier ou sur un débarcadère')
    if c in SOLID and not name.startswith('Guard'): why.append('sur une case prise')
    if not (is_land(*c) or c in DECK): why.append('dans l eau')
    if not name.startswith(('Guard', 'Fisher')) and gen.pinches(c) and c not in L['Plaza']: why.append('étrangle un passage')
    if why: print('  !! %s en %s : %s' % (name, c, ', '.join(why)))
# ------------------------------------------------------------------ accessibilité, dans les trois temps de l'histoire
def reach(start, extra_solid=()):
    seen = {start}; q = collections.deque([start]); solid_now = SOLID | set(extra_solid)
    while q:
        c0 = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            c = (c0[0] + dx, c0[1] + dy)
            if 0 <= c[0] < W and 0 <= c[1] < H and c not in seen and c not in solid_now and frozenset((c0, c)) not in gen.LEDGE: seen.add(c); q.append(c)
    return seen
targets = {'porte ' + k: (v[0], v[1] + 1) for k, v in DOORS.items()}
targets.update(gen.PLACES)
targets.update({'socle (devant)': (CXP, TOP + 4), 'devant les gardes': (road[2], GUARD_Y + 1), 'derrière les gardes': (road[2], GUARD_Y - 1)})
targets.update({'devant ' + k: (c[0], c[1] - 1) for k, c in gen.ITEMS.items()})
for phase, flags in PHASES.items():
    there = [c for n, c, req, forb in NPCS if present(req, forb, flags)]
    R = reach(SPAWN, there)
    missing = [k for k, c in targets.items() if c not in R and c not in there]
    crowd = sum(1 for n, c, req, forb in NPCS if present(req, forb, flags) and PLZ[0] - 2 <= c[0] <= PLZ[2] + 2 and PLZ[1] - 2 <= c[1] <= PLZ[3] + 2)
    print('%-8s : %d personnages immobiles, %d sur la place, %d cases accessibles%s' % (phase, len(there), crowd, len(R), (' — INACCESSIBLE : %s' % missing) if missing else ''))
    for i in range(len(LOOP)):
        a, bb = LOOP[i], LOOP[(i + 1) % len(LOOP)]
        cells = [(x, a[1]) for x in range(min(a[0], bb[0]), max(a[0], bb[0]) + 1)] if a[1] == bb[1] else [(a[0], y) for y in range(min(a[1], bb[1]), max(a[1], bb[1]) + 1)]
        bad = [c for c in cells if c in SOLID or c in there]
        if bad: print('  !! boucle du coureur bloquée en', bad, phase)
R = reach(SPAWN, [c for n, c, req, forb in NPCS if present(req, forb, set())])

# ------------------------------------------------------------------ écriture
def layer(name, parent, cells, ysort=False):
    return '[node name="%s" type="TileMapLayer" parent="%s"]\n%stile_map_data = PackedByteArray("%s")\ntile_set = ExtResource("1_ian7c")\n' % (
        name, parent, 'y_sort_enabled = true\n' if ysort else '', encode({c: (t[0], t[1], t[2], t[3] if len(t) > 3 else 0) for c, t in cells.items()}))
head = '''[gd_scene load_steps=14 format=4]

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
if NO_FLYERS:        # sans oiseaux, la scène ne doit pas citer flyer.tscn (il n'existe pas encore)
    head = head.replace('[ext_resource type="PackedScene" path="' + RES + 'scenes/levels/flyer.tscn" id="13_flyer"]\n', '').replace('load_steps=14', 'load_steps=13')
parts = [head]
for n in ('Ground', 'Paths', 'Relief', 'Plaza', 'Bridges', 'Decorations', 'Grass'): parts.append(layer(n, 'Background', L[n]))
parts.append('[node name="World" type="Node2D" parent="."]\ny_sort_enabled = true\n')
for n in ('Cliffs', 'CliffsMid', 'CliffsTop', 'Props', 'Houses', 'Trees'): parts.append(layer(n, 'World', L[n], True))
parts += nodes
if '--map' in sys.argv:
    for y in range(H):
        print('%2d ' % y + ''.join('~' if T[y][x] == '~' and (x, y) not in DECK else ('#' if (x, y) in SOLID else ('.' if (x, y) in R else '?')) for x in range(W)))
if '--write' in sys.argv:
    open(B + 'scenes/levels/start_island.tscn', 'w').write('\n'.join(parts))
    patch_tileset()
    print('écrit')
