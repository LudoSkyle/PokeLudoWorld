#!/usr/bin/env python3
"""Sort du pack de données ce dont le jeu se sert pour ses Pokémon.

    python3 tools/gamedata.py

Le pack est `vendor/GameDataPacks/Gen 9/scarlet-violet` (copié dans le dépôt, la base de données de Pokémon Studio
et de PSDK ; son origine est dans `vendor/GameDataPacks/ORIGINE.md`). Le jeu ne lit jamais ce dossier : ce script en **copie** ce qu'il faut, sans rien retoucher, sous le nom de
l'espèce (son `dbSymbol` : `wingull`, `ho_oh`) :

    graphics/characters/NNNN.png        -> assets/pokemon/overworld/<espèce>.png   le sprite sur la carte
    graphics/pokedex/pokeicon/NNNN.png  -> assets/pokemon/icons/<espèce>.png       l'icône (deux images de 32 x 32)
    graphics/pokedex/pokefront/NNNN.png -> assets/pokemon/front/<espèce>.png       le portrait de face, 96 x 96 (la fiche du Pokédex)
    audio/se/cries/NNNN.ogg             -> assets/audio/cries/<espèce>.ogg         le cri
    graphics/icons/NNN.png              -> assets/items/icons/<objet>.png          l'icône d'un objet (32 x 32)
    Data/Studio/pokemon/*.json, Data/Text/Dialogs/*.csv -> resources/pokedex/national.tsv

Seule la forme de base de chaque espèce est prise (ni chromatique, ni femelle, ni forme régionale). Un fichier de
ces trois dossiers que le script n'écrit plus est retiré.

Un sprite de carte fait quatre rangées — bas, gauche, droite, haut — de quatre images carrées (32 pixels, plus pour
un gros Pokémon). Colonnes 0 et 2 : les deux dessins ; colonnes 1 et 3 : les mêmes un pixel plus bas. Lues dans
l'ordre, elles donnent le petit saut des jeux d'origine à chaque changement de dessin.
"""
import csv
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(ROOT, 'vendor', 'GameDataPacks', 'Gen 9', 'scarlet-violet')
GAME = os.path.join(ROOT, 'src', 'main', 'kotlin', 'fr', 'skyle', 'pokemonmirage')
OVERWORLD = os.path.join(GAME, 'assets', 'pokemon', 'overworld')
ICONS = os.path.join(GAME, 'assets', 'pokemon', 'icons')
FRONT = os.path.join(GAME, 'assets', 'pokemon', 'front')
CRIES = os.path.join(GAME, 'assets', 'audio', 'cries')
ITEMS = os.path.join(GAME, 'assets', 'items', 'icons')          # ses sous-dossiers (custom/, other/) ne sont pas au pack : on n'y touche pas
NATIONAL = os.path.join(GAME, 'resources', 'pokedex', 'national.tsv')

FIELDS = ('number', 'id', 'generation', 'name_fr', 'name_en', 'genus_fr', 'genus_en', 'height', 'weight', 'icon', 'overworld', 'text_fr', 'text_en', 'front', 'type1', 'type2')
LAST_OF_GENERATION = (151, 251, 386, 493, 649, 721, 809, 905, 1025)          # le dernier numéro de chaque génération
NAMES, GENUS, TEXTS = '100000', '100001', '100002'                             # les fichiers de textes : noms, catégories, descriptions


def texts(name):
    """Les lignes d'un fichier de textes : la ligne d'une espèce est celle de son numéro (la 0 est l'Œuf)."""
    with open(os.path.join(PACK, 'Data', 'Text', 'Dialogs', name + '.csv'), encoding='utf-8', newline='') as f:
        rows = list(csv.reader(f))
    en, fr = rows[0].index('en'), rows[0].index('fr')
    def clean(text): return ' '.join(text.split())          # sur une ligne : ni retour, ni tabulation
    return [(clean(r[fr]), clean(r[en])) for r in rows[1:]]


def kind(symbol):
    """Un type du pack (`grass`), ou rien : une espèce d'un seul type porte `__undef__` en second."""
    return '' if not symbol or symbol.startswith('__') else symbol


def put(source, folder, name):
    """Copie `source` dans `folder` sous `name`, si elle existe. Renvoie vrai si le fichier y est."""
    if not source or not os.path.exists(source): return False
    target = os.path.join(folder, name)
    if not os.path.exists(target) or open(source, 'rb').read() != open(target, 'rb').read(): shutil.copyfile(source, target)
    return True


def sweep(folder, kept, extension):
    """Retire de `folder` les fichiers `extension` qu'on n'a pas écrits, et leur `.import`."""
    gone = 0
    for name in sorted(os.listdir(folder)):
        if name.endswith(extension) and name not in kept:
            for stale in (name, name + '.import'):
                if os.path.exists(os.path.join(folder, stale)): os.remove(os.path.join(folder, stale))
            gone += 1
    return gone


if __name__ == '__main__':
    with open(os.path.join(PACK, 'Data', 'Studio', 'dex', 'national.json'), encoding='utf-8') as f:
        order = [c['dbSymbol'] for c in json.load(f)['creatures']]
    names, genus, descriptions = texts(NAMES), texts(GENUS), texts(TEXTS)
    for folder in (OVERWORLD, ICONS, FRONT, CRIES): os.makedirs(folder, exist_ok=True)

    lines, kept, missing = [], {OVERWORLD: set(), ICONS: set(), FRONT: set(), CRIES: set()}, {'icône': [], 'sprite': [], 'portrait': [], 'cri': []}
    for symbol in order:
        with open(os.path.join(PACK, 'Data', 'Studio', 'pokemon', symbol + '.json'), encoding='utf-8') as f:
            species = json.load(f)
        number = species['id']
        form = next(f for f in species['forms'] if f['form'] == 0)
        files = form['resources']
        has = {
            'sprite': put(files.get('character') and os.path.join(PACK, 'graphics', 'characters', files['character'] + '.png'), OVERWORLD, symbol + '.png'),
            'icône': put(files.get('icon') and os.path.join(PACK, 'graphics', 'pokedex', 'pokeicon', files['icon'] + '.png'), ICONS, symbol + '.png'),
            'portrait': put(files.get('front') and os.path.join(PACK, 'graphics', 'pokedex', 'pokefront', files['front'] + '.png'), FRONT, symbol + '.png'),
            'cri': put(files.get('cry') and os.path.join(PACK, 'audio', 'se', 'cries', files['cry']), CRIES, symbol + '.ogg'),
        }
        if has['sprite']: kept[OVERWORLD].add(symbol + '.png')
        if has['icône']: kept[ICONS].add(symbol + '.png')
        if has['portrait']: kept[FRONT].add(symbol + '.png')
        if has['cri']: kept[CRIES].add(symbol + '.ogg')
        for what, there in has.items():
            if not there: missing[what].append(symbol)
        entry = {'number': number, 'id': symbol, 'generation': next(g + 1 for g, last in enumerate(LAST_OF_GENERATION) if number <= last),
                 'name_fr': names[number][0], 'name_en': names[number][1], 'genus_fr': genus[number][0], 'genus_en': genus[number][1],
                 'height': form['height'], 'weight': form['weight'], 'icon': int(has['icône']), 'overworld': int(has['sprite']),
                 'text_fr': descriptions[number][0], 'text_en': descriptions[number][1], 'front': int(has['portrait']),
                 'type1': kind(form.get('type1')), 'type2': kind(form.get('type2'))}
        lines.append('\t'.join(str(entry[field]) for field in FIELDS))

    with open(NATIONAL, 'w', encoding='utf-8') as f:
        f.write('# Fabriqué par tools/gamedata.py depuis vendor/GameDataPacks (Gen 9/scarlet-violet) : ne pas modifier à la main.\n')
        f.write('# ' + '\t'.join(FIELDS) + '\n')
        f.write('\n'.join(lines) + '\n')

    print('%d espèces dans %s' % (len(lines), os.path.relpath(NATIONAL, ROOT)))
    for folder, extension in ((OVERWORLD, '.png'), (ICONS, '.png'), (FRONT, '.png'), (CRIES, '.ogg')):
        print('%4d fichiers dans %s, %d retirés' % (len(kept[folder]), os.path.relpath(folder, ROOT), sweep(folder, kept[folder], extension)))
    for what, who in missing.items():
        if who: print('sans %s : %d — %s' % (what, len(who), ', '.join(who[:12]) + (' …' if len(who) > 12 else '')))

    # ---------- les objets : l'icône de chacun, sous son nom (`potion.png`)
    os.makedirs(ITEMS, exist_ok=True)
    folder, written, without = os.path.join(PACK, 'Data', 'Studio', 'items'), set(), []
    for name in sorted(os.listdir(folder)):
        with open(os.path.join(folder, name), encoding='utf-8') as f:
            item = json.load(f)
        if put(item.get('icon') and os.path.join(PACK, 'graphics', 'icons', item['icon'] + '.png'), ITEMS, item['dbSymbol'] + '.png'): written.add(item['dbSymbol'] + '.png')
        else: without.append(item['dbSymbol'])
    print('%4d fichiers dans %s, %d retirés' % (len(written), os.path.relpath(ITEMS, ROOT), sweep(ITEMS, written, '.png')))
    if without: print('objets sans icône dans le pack : %d — %s' % (len(without), ', '.join(without[:12]) + (' …' if len(without) > 12 else '')))
