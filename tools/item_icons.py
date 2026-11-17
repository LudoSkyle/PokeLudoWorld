#!/usr/bin/env python3
"""Fabrique assets/items/icons/ : une icône par fichier, en quatre dossiers.

    python3 tools/item_icons.py          # -v : détaille ce qui est écarté et pourquoi

    icons/named/      les objets officiels qu'on sait nommer : <nom>.png — potion.png.
    icons/unnamed/    les objets officiels dont on n'a pas le nom, sous leur case :
                      07_F_2_fan.png est la case 07:F:2 de la planche de Kryptonlion.
    icons/invented/   les objets inventés par Kryptonlion (fond sarcelle ou lavande).
    icons/custom/     les icônes faites pour ce jeu, et elles seules : clear_bell.png.

Deux cases de la planche qui portent exactement le même dessin ne donnent qu'un fichier.

**Un nom de fichier dit ce qu'est l'icône, jamais à quoi le jeu l'emploie.** Une icône
sans nom dont le jeu se sert reste dans unnamed/, sous sa case : le catalogue la désigne
par `icon = "unnamed/07_F_2_fan"`. On ne nomme une case dans itemdex.txt que quand on a
identifié l'objet officiel qu'elle représente.

**Toute la planche de Kryptonlion est exportée**, case par case : c'est la source
principale. Les deux autres ne servent qu'à la compléter.

  sources/itemdex_kryptonlion.png + itemdex.txt
        seize blocs de 16 x 16 cases de 32 x 32 ; le fond de chaque case dit sa famille
        (voir LEGEND). Le dessin tient presque toujours dans les 24 x 24 du centre, et
        l'icône fait alors 24 x 24 ; quand il déborde, elle fait 32 x 32. itemdex.txt
        nomme les cases qu'on sait nommer — presque toutes le sont d'après pokesprite
        et PokeAPI, deux jeux d'icônes officielles nommées (voir l'en-tête de la table).
  sources/essentials/
        les 449 icônes de Pokémon Essentials, une image de 48 x 48 par objet, nommée par
        son identifiant du kit (ANTIDOTE.png) ; `items.txt` donne le nom anglais de
        chacun : « Super Repel » devient super_repel. C'est d'elles que viennent les noms.
  sources/frlg.png + frlg.txt, sources/custom.png + custom.txt
        les icônes de Rouge Feu / Vert Feuille et celles faites pour ce jeu, en cases de
        24 x 24 ; la table nomme les cases. Celles de custom.png vont dans icons/custom/.

Ce qu'on garde d'une icône qui ne vient PAS de la planche de Kryptonlion :

  - la planche a exactement ce dessin, sous ce nom ou un autre : on ne la garde pas ;
  - elle porte un nom que la planche n'a pas : on la garde, sous ce nom ;
  - la planche a ce nom, et les deux dessins se ressemblent (même objet, teinte ou
    contour à peine différents) : on ne garde que celui de Kryptonlion, plus récent ;
  - la planche a ce nom, mais c'est un autre dessin (la carte à plat de FRLG, quand celle
    de la planche est pliée) : on garde les deux, la seconde sous <nom>-<origine>.png ;
  - elle n'a pas de nom (une case de FRLG) : on la garde dans unnamed/ si la planche n'a
    pas ce dessin.

« Se ressembler », pour deux icônes du même nom : leurs silhouettes se recouvrent à 80 %
au moins. « Le même dessin », pour une case sans nom : exactement la même silhouette, et
16 d'écart moyen de couleur sur 255 au plus.

Les icônes du kit sont dessinées en pixels doublés — chaque bloc de 2 x 2 est d'une seule
couleur. On en garde un pixel par bloc, sans aucune perte.

Relancer le script redonne exactement les mêmes fichiers, et retire de icons/ ceux qu'il
ne produit plus.
"""
import os
import re
import shutil
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from island_tiles import load, save  # noqa: E402  — les mêmes lecteur et écrivain de PNG

ITEMS = os.path.join(
    os.path.dirname(HERE), 'src', 'main', 'kotlin', 'fr', 'skyle', 'pokeludoworld', 'assets', 'items',
)
SOURCES = os.path.join(ITEMS, 'sources')
KIT = os.path.join(SOURCES, 'essentials')
ICONS = os.path.join(ITEMS, 'icons')
SIZE = 24
CLEAR = (0, 0, 0, 0)

# Les images du kit qu'aucun objet de items.txt ne porte : on les nomme à la main.
UNLISTED = {
    'BLUESCARF': 'blue_scarf', 'GREENSCARF': 'green_scarf', 'PINKSCARF': 'pink_scarf',
    'REDSCARF': 'red_scarf', 'YELLOWSCARF': 'yellow_scarf',
    'CLEVERWING': 'clever_wing', 'GENIUSWING': 'genius_wing', 'HEALTHWING': 'health_wing',
    'MUSCLEWING': 'muscle_wing', 'PRETTYWING': 'pretty_wing', 'RESISTWING': 'resist_wing',
    'SWIFTWING': 'swift_wing', 'STICK': 'stick',
}

# Celles qu'on ne prend pas, et pourquoi.
SKIPPED = {
    '000': 'l\'icône « objet inconnu » du kit : le sac garde celle de FRLG (unnamed/frlg_227.png)',
    'back': 'la flèche de retour du kit : le sac prend celle de la planche (unnamed/00_F_F_special.png)',
    'machine_hm_NORMAL': 'la seule qui ne soit pas en pixels doublés : la réduire l\'abîmerait',
    'THICKCLUB': 'le kit lui donne l\'image de l\'Os Rare, que la planche a déjà (rare_bone.png)',
}

# La légende de la planche de Kryptonlion : la couleur du fond d'une case dit sa famille.
# Les teintes claires sont les « Repeated » : un objet qui reprend l'icône d'un autre.
LEGEND = {
    (245, 218, 38): 'official', (248, 231, 114): 'official',            # jaune : officielle, couleurs récentes
    (255, 115, 39): 'old_colors', (255, 164, 114): 'old_colors',        # orange : officielle, anciennes couleurs
    (34, 109, 181): 'recolored', (111, 160, 207): 'recolored',          # bleu : officielle recolorée
    (212, 146, 75): 'fan', (227, 184, 138): 'fan',                      # brun : objet officiel, dessin d'un fan
    (68, 194, 157): 'invented',                                         # sarcelle : objet et dessin inventés
    (170, 170, 255): 'generic',                                         # lavande : objet inventé, aux couleurs officielles
    (77, 61, 43): 'special', (32, 32, 32): 'special', (255, 255, 255): 'special',   # icônes de poche, flèche
}
# Les cases qui ne sont pas des icônes : vides (vert), ou une simple étiquette en attente
# de dessin (gris, « Work in Progress »).
NOT_AN_ICON = {(112, 160, 96), (195, 195, 195)}

# Seize blocs de 16 x 16 cases, quatre par rangée : un bloc tous les 561 pixels, une case
# tous les 33, la première à 34 pixels du bord. Le dessin est au centre de sa case de 32.
DEX_BLOCK, DEX_PITCH, DEX_FIRST, DEX_CELL = 561, 33, 34, 32

# D'où peut venir une icône nommée, de la première servie à la dernière : la planche de
# Kryptonlion d'abord, par famille, puis le kit, FRLG.
ORIGINS = ['official', 'generic', 'old_colors', 'recolored', 'fan', 'special', 'invented', 'essentials', 'frlg']
FROM_SHEET = ORIGINS[:7]

ALIKE = 0.8      # deux icônes du même nom se ressemblent : recouvrement des silhouettes
SAME = 16.0      # deux cases sont le même dessin : écart moyen de couleur, sur 255


def slug(name):
    """« Poké Ball » -> poke_ball, « King's Rock » -> kings_rock."""
    plain = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode().replace("'", '')
    return re.sub(r'[^a-z0-9]+', '_', plain.lower()).strip('_')


def kit_names():
    """Le nom de fichier de chaque identifiant du kit, d'après son nom anglais."""
    names, taken, current = {}, set(), None
    for line in open(os.path.join(KIT, 'items.txt'), encoding='utf-8', errors='replace'):
        header = re.match(r'^\[(\w+)\]', line)
        if header:
            current = header.group(1)
        elif current and line.startswith('Name') and '=' in line:
            name = slug(line.split('=', 1)[1].strip())
            # Deux objets peuvent porter le même nom : l'état « utilisé » d'un objet de fusion.
            if name in taken and current.endswith('USED'):
                name += '_used'
            assert name not in taken, 'deux objets pour le nom %s' % name
            taken.add(name)
            names[current] = name
            current = None
    return names


def halve(path):
    width, height, rows = load(path)
    assert (width, height) == (SIZE * 2, SIZE * 2), (path, width, height)
    out = []
    for y in range(0, height, 2):
        line = []
        for x in range(0, width, 2):
            block = {p if p[3] > 0 else CLEAR for p in (rows[y][x], rows[y][x + 1], rows[y + 1][x], rows[y + 1][x + 1])}
            assert len(block) == 1, '%s : le bloc (%d, %d) n\'est pas uniforme' % (path, x, y)
            line.append(block.pop())
        out.append(line)
    return out


def from_kit():
    names = kit_names()
    made = {}
    for file in sorted(os.listdir(KIT)):
        if not file.endswith('.png'):
            continue
        key = file[:-4]
        if key in SKIPPED:
            continue
        if key in names:
            name = names[key]
        elif key in UNLISTED:
            name = UNLISTED[key]
        elif key.startswith('machine_'):
            name = key.lower()                 # une image de CT ou de CS par type
        else:
            raise SystemExit('%s : ni dans items.txt, ni nommée à la main' % file)
        assert name not in made, 'deux images pour %s' % name
        made[name] = halve(os.path.join(KIT, file))
    return made


def table(sheet):
    """Les lignes « case  nom [nom…] » de la table d'une planche."""
    path = os.path.join(SOURCES, sheet + '.txt')
    for line in open(path, encoding='utf-8'):
        words = line.split('#')[0].split()
        if words:
            assert len(words) > 1, '%s : la case %s n\'a pas de nom' % (path, words[0])
            yield words[0], words[1:]


def from_numbered(sheet):
    """frlg.png et custom.png, 16 cases par rangée : ({nom: image}, {numéro: image sans nom})."""
    width, height, rows = load(os.path.join(SOURCES, sheet + '.png'))
    names = {int(ref): found for ref, found in table(sheet)}
    named, unnamed = {}, {}
    for number in range((width // SIZE) * (height // SIZE)):
        column, row = number % 16, number // 16
        cell = [list(line[column * SIZE:(column + 1) * SIZE]) for line in rows[row * SIZE:(row + 1) * SIZE]]
        if not any(p[3] > 0 for line in cell for p in line):
            assert number not in names, '%s %d : la case est vide' % (sheet, number)
        elif number in names:
            for name in names[number]:
                assert name not in named, '%s : deux cases pour %s' % (sheet, name)
                named[name] = cell
        else:
            unnamed[number] = cell
    return named, unnamed


def from_itemdex():
    """Toute la planche de Kryptonlion : [(case, famille, noms, image)], un dessin n'y étant qu'une fois."""
    rows = load(os.path.join(SOURCES, 'itemdex_kryptonlion.png'))[2]
    names = dict(table('itemdex'))
    cells = []
    for block in range(16):
        for row in range(16):
            for column in range(16):
                left = DEX_FIRST + (block % 4) * DEX_BLOCK + column * DEX_PITCH
                top = DEX_FIRST + (block // 4) * DEX_BLOCK + row * DEX_PITCH
                ground = rows[top][left][:3]
                if ground in NOT_AN_ICON:
                    continue
                ref = '%02X:%X:%X' % (block, row, column)
                assert ground in LEGEND, 'itemdex %s : fond %s, absent de la légende' % (ref, ground)
                # Tout ce qui n'est pas le fond est le dessin.
                cell = [[CLEAR if p[:3] == ground else p[:3] + (255,) for p in line[left:left + DEX_CELL]]
                        for line in rows[top:top + DEX_CELL]]
                margin = (DEX_CELL - SIZE) // 2
                inside = [line[margin:-margin] for line in cell[margin:-margin]]
                if sum(p[3] > 0 for line in inside for p in line) == sum(p[3] > 0 for line in cell for p in line):
                    cell = inside                      # le dessin tient dans les 24 x 24 du centre
                assert any(p[3] > 0 for line in cell for p in line), 'itemdex %s : rien de dessiné' % ref
                family = LEGEND[ground]
                # Le fond lavande est celui des CT « par type » : Kryptonlion en a inventé
                # pour chaque type, mais celles qui existent vraiment se nomment.
                assert not (family == 'invented' and ref in names), \
                    'itemdex %s : un objet inventé par Kryptonlion, à ne pas utiliser sans sa permission' % ref
                cells.append((ref, family, names.pop(ref, []), cell))
    assert not names, 'itemdex.txt nomme des cases sans icône : %s' % sorted(names)

    # Plusieurs cases portent exactement le même dessin (un objet qui reprend l'icône d'un
    # autre) : on n'en garde qu'une, celle de la première famille, avec tous leurs noms.
    cells.sort(key=lambda found: ORIGINS.index(found[1]))        # tri stable : l'ordre de la planche demeure
    first, unique = {}, []
    for ref, family, found, cell in cells:
        key = tuple(map(tuple, cell))
        if key in first:
            first[key][2].extend(name for name in found if name not in first[key][2])
        else:
            first[key] = (ref, family, list(found), cell)
            unique.append(first[key])
    return unique, len(cells) - len(unique)


def dots(rows):
    """Le dessin d'une icône, calé en haut à gauche : {(x, y): couleur}."""
    found = [(x, y, p[:3]) for y, line in enumerate(rows) for x, p in enumerate(line) if p[3] > 0]
    left, top = min(d[0] for d in found), min(d[1] for d in found)
    return {(x - left, y - top): color for x, y, color in found}


def alike(a, b):
    """Deux icônes du même nom se ressemblent : leurs silhouettes se recouvrent, à deux pixels près."""
    a, b = set(dots(a)), set(dots(b))
    best = 0.0
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            moved = {(x + dx, y + dy) for x, y in b}
            best = max(best, len(a & moved) / float(len(a | moved)))
    return best >= ALIKE


def same(a, b):
    """Deux cases sont le même dessin : même silhouette, couleurs très proches."""
    a, b = dots(a), dots(b)
    if a.keys() != b.keys():
        return False
    return sum(sum(abs(x - y) for x, y in zip(a[k], b[k])) for k in a) / (3.0 * len(a)) <= SAME


def prune(written):
    """Retire de icons/ les icônes qu'on ne produit plus, leur .import, et les dossiers vidés."""
    for folder, _, files in os.walk(ICONS, topdown=False):
        for file in files:
            path = os.path.join(folder, file)
            icon = path[:-len('.import')] if path.endswith('.import') else path
            if icon.endswith('.png') and icon not in written:
                os.remove(path)
        if folder != ICONS and not set(os.listdir(folder)) - {'.DS_Store', '.gdignore'}:
            shutil.rmtree(folder)


if __name__ == '__main__':
    verbose = '-v' in sys.argv
    sheet, repeated = from_itemdex()
    frlg, frlg_unnamed = from_numbered('frlg')
    custom, custom_unnamed = from_numbered('custom')
    assert not custom_unnamed, 'custom.png : des cases sans nom, %s' % sorted(custom_unnamed)

    # --- named/ : pour chaque nom, ses dessins, de la première origine à la dernière
    found = {origin: {} for origin in ORIGINS}
    for ref, family, names, cell in sheet:
        for name in names:
            assert name not in found[family], 'itemdex : deux cases « %s » pour %s' % (family, name)
            found[family][name] = cell
    found['essentials'], found['frlg'] = from_kit(), frlg
    on_sheet = [cell for _, _, _, cell in sheet if len(cell) == SIZE]

    out, kept, dropped, several = {}, {}, {}, []
    for origin in ORIGINS:
        for name, cell in sorted(found[origin].items()):
            mine = kept.setdefault(name, [])
            # Une case de la planche se garde toujours. Une autre icône se garde si la
            # planche n'a pas ce dessin, et si aucun dessin déjà gardé sous ce nom ne lui
            # ressemble.
            if origin in FROM_SHEET or not (any(alike(cell, other) for _, other in mine) or any(same(cell, other) for other in on_sheet)):
                mine.append((origin, cell))
            else:
                dropped.setdefault(origin, []).append(name)
    kept = {name: drawn for name, drawn in kept.items() if drawn}
    for name, drawn in kept.items():
        for rank, (origin, cell) in enumerate(drawn):
            out['named/%s.png' % (name if rank == 0 else '%s-%s' % (name, origin))] = cell
        if len(drawn) > 1:
            several.append('%s (%s)' % (name, ', '.join(origin for origin, _ in drawn)))

    # --- custom/ : nos icônes, à part
    for name, cell in custom.items():
        out['custom/%s.png' % name] = cell

    # --- unnamed/ et invented/ : les cases sans nom
    for ref, family, names, cell in sheet:
        if not names:
            case = ref.replace(':', '_')
            out['invented/%s.png' % case if family in ('invented', 'generic') else 'unnamed/%s_%s.png' % (case, family)] = cell
    twins = []
    for number, cell in sorted(frlg_unnamed.items()):
        if any(same(cell, other) for other in on_sheet):
            twins.append(number)
        else:
            out['unnamed/frlg_%d.png' % number] = cell

    written = set()
    for path, cell in out.items():
        path = os.path.join(ICONS, path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        save(path, cell)
        written.add(path)
    prune(written)
    # Le jeu ne se sert jamais d'un objet inventé : Godot n'a pas à importer ce dossier.
    open(os.path.join(ICONS, 'invented', '.gdignore'), 'w').close()
    if os.path.exists(os.path.join(ICONS, 'unnamed', '.gdignore')):
        os.remove(os.path.join(ICONS, 'unnamed', '.gdignore'))

    count = lambda folder, mark='': sum(1 for path in out if path.startswith(folder + '/') and mark in path)
    print('planche de Kryptonlion : %d cases dessinées, %d dessins différents, dont %d nommés' % (
        len(sheet) + repeated, len(sheet), sum(1 for c in sheet if c[2])))
    print('named/     %4d icônes, %d objets ; dont %d du kit, %d de FRLG' % (
        count('named'), len(kept), sum(1 for d in kept.values() for o, _ in d if o == 'essentials'),
        sum(1 for d in kept.values() for o, _ in d if o == 'frlg')))
    print('unnamed/   %4d icônes ; dont %d de FRLG' % (count('unnamed'), count('unnamed', 'frlg_')))
    print('invented/  %4d icônes' % count('invented'))
    print('custom/    %4d icônes' % count('custom'))
    print('écartées, la planche ayant le même objet : %d du kit, %d de FRLG nommées, %d de FRLG sans nom' % (
        len(dropped.get('essentials', [])), len(dropped.get('frlg', [])), len(twins)))
    print('%d objets ont plusieurs dessins : %s' % (len(several), ', '.join(sorted(several))))
    print('nommées, hors de la planche : %s' % (', '.join(sorted(
        '%s (%s)' % (name, origin) for name, drawn in kept.items() for origin, _ in drawn if origin not in FROM_SHEET)) or 'aucune'))
    if verbose:
        for origin, names in sorted(dropped.items()):
            print('  %s, écartées : %s' % (origin, ' '.join(names)))
        print('  FRLG sans nom, déjà sur la planche : %s' % ' '.join(map(str, twins)))
    for key, why in SKIPPED.items():
        print('  laissée de côté — %s : %s' % (key, why))
