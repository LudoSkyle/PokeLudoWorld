#!/usr/bin/env python3
"""Fabrique les données du Pokédex national : resources/pokedex/national.tsv et assets/pokemon/icons.png.

    python3 -I tools/pokedex.py <dossier des CSV de PokéAPI> <dossier du kit Pokémon Essentials>

**Les espèces, leurs noms, leur taille, leur poids et leurs descriptions** viennent des CSV du dépôt
PokeAPI/pokeapi (`data/v2/csv/`) : `pokemon_species.csv`, `pokemon_species_names.csv`,
`pokemon_species_flavor_text.csv`, `pokemon.csv`. Français = langue 5, anglais = langue 9. La
description retenue est la plus récente de chaque langue. Les CSV ne sont pas versionnés : ce
fichier-ci, et ce qu'il écrit, le sont.

**Les icônes** viennent du kit Pokémon Essentials (`Graphics/Pokemon/Icons/<ID>.png`, deux images
de 64 x 64 aux pixels doublés) : ramenées à 32 x 32 et rangées dans une seule planche, une case de
64 x 32 par espèce, à sa place d'après son numéro national (25 colonnes). Le kit s'arrête à la
génération 8 : les cases des espèces qu'il n'a pas restent vides, et `national.tsv` le dit.

`national.tsv` : une espèce par ligne, ses champs séparés par des tabulations, dans l'ordre de
`FIELDS` — c'est ce que lit `NationalDex.kt`, sans analyseur. Aucun texte n'a de tabulation ni de
saut de ligne.

Ce qu'il manque est écrit à la fin, et se voit dans la vue de debug du jeu.
"""
import csv
import collections
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from island_tiles import load, save  # noqa: E402

ROOT = os.path.dirname(HERE)
GAME = os.path.join(ROOT, 'src', 'main', 'kotlin', 'fr', 'skyle', 'pokemonmirage')
OUT = os.path.join(GAME, 'resources', 'pokedex', 'national.tsv')
FIELDS = ('number', 'id', 'generation', 'name_fr', 'name_en', 'genus_fr', 'genus_en', 'height', 'weight', 'icon', 'overworld', 'text_fr', 'text_en')
ICONS = os.path.join(GAME, 'assets', 'pokemon', 'icons.png')
OVERWORLD = os.path.join(GAME, 'assets', 'pokemon', 'overworld')
FR, EN = 5, 9
COLUMNS = 25                                  # espèces par rangée de la planche d'icônes


def rows(folder, name):
    with open(os.path.join(folder, name + '.csv'), encoding='utf-8', newline='') as f: return list(csv.DictReader(f))


def clean(text):
    """Une description sur une ligne : les CSV la coupent comme l'écran des jeux d'origine."""
    text = text.replace('­\n', '').replace('­', '').replace('-\n', '-').replace('\f', ' ').replace('\n', ' ')
    return re.sub(r'\s+', ' ', text).strip()


def kit_ids(kit):
    """Les identifiants du kit, dans l'ordre de son pokemon.txt : c'est l'ordre national, de 1 à 898."""
    with open(os.path.join(kit, 'PBS', 'pokemon.txt'), encoding='utf-8-sig') as f:
        return [line.strip()[1:-1] for line in f if line.startswith('[')]


if __name__ == '__main__':
    api, kit = sys.argv[1], sys.argv[2]
    names, genus = collections.defaultdict(dict), collections.defaultdict(dict)
    for r in rows(api, 'pokemon_species_names'):
        names[int(r['pokemon_species_id'])][int(r['local_language_id'])] = r['name']
        genus[int(r['pokemon_species_id'])][int(r['local_language_id'])] = r['genus']
    texts = {}
    for r in rows(api, 'pokemon_species_flavor_text'):
        key, version = (int(r['species_id']), int(r['language_id'])), int(r['version_id'])
        if version >= texts.get(key, (-1, ''))[0]: texts[key] = (version, r['flavor_text'])
    bodies = {int(r['species_id']): r for r in rows(api, 'pokemon') if r['is_default'] == '1'}
    kit_order = kit_ids(kit)
    species, missing = [], collections.defaultdict(list)
    width = COLUMNS * 64
    sheet = None
    for r in sorted(rows(api, 'pokemon_species'), key=lambda r: int(r['id'])):
        n = int(r['id'])
        ident = r['identifier'].replace('-', '_')
        entry = {'number': n, 'id': ident, 'generation': int(r['generation_id']),
                 'name_fr': names[n].get(FR, ''), 'name_en': names[n].get(EN, ''),
                 'genus_fr': genus[n].get(FR, ''), 'genus_en': genus[n].get(EN, ''),
                 'height': int(bodies[n]['height']) / 10 if n in bodies else 0.0,          # en mètres (les CSV sont en décimètres)
                 'weight': int(bodies[n]['weight']) / 10 if n in bodies else 0.0,          # en kilos (hectogrammes)
                 'text_fr': clean(texts.get((n, FR), (0, ''))[1]), 'text_en': clean(texts.get((n, EN), (0, ''))[1])}
        icon = os.path.join(kit, 'Graphics', 'Pokemon', 'Icons', kit_order[n - 1] + '.png') if n <= len(kit_order) else ''
        entry['icon'] = bool(icon) and os.path.exists(icon)
        entry['overworld'] = os.path.exists(os.path.join(OVERWORLD, ident + '.png'))          # un fichier par espèce (tools/pokemon_overworld.py)
        if entry['icon']:
            w, h, art = load(icon)
            if sheet is None: sheet = []
            x0, y0 = ((n - 1) % COLUMNS) * 64, ((n - 1) // COLUMNS) * 32
            while len(sheet) < y0 + 32: sheet.append([(0, 0, 0, 0)] * width)
            for y in range(32):
                for x in range(64): sheet[y0 + y][x0 + x] = tuple(art[2 * y][2 * x]) if 2 * x < w and 2 * y < h else (0, 0, 0, 0)
        for field in ('name_fr', 'name_en', 'genus_fr', 'genus_en', 'text_fr', 'text_en', 'icon', 'overworld'):
            if not entry[field]: missing[field].append(n)
        if not entry['height'] or not entry['weight']: missing['height/weight'].append(n)
        species.append(entry)
    last = ((len(species) - 1) // COLUMNS + 1) * 32
    while len(sheet) < last: sheet.append([(0, 0, 0, 0)] * width)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('# ' + '\t'.join(FIELDS) + '\n')
        for entry in species:
            cells = [('1' if entry[k] else '0') if isinstance(entry[k], bool) else str(entry[k]) for k in FIELDS]
            assert not any('\t' in c or '\n' in c for c in cells), entry['id']
            f.write('\t'.join(cells) + '\n')
    save(ICONS, sheet)
    print('%d espèces dans %s' % (len(species), os.path.relpath(OUT, ROOT)))
    print('icônes : %s (%d x %d)' % (os.path.relpath(ICONS, ROOT), width, len(sheet)))
    for field, numbers in sorted(missing.items()):
        spans, start, prev = [], numbers[0], numbers[0]
        for n in numbers[1:] + [None]:
            if n != prev + 1:
                spans.append('%d' % start if start == prev else '%d-%d' % (start, prev)); start = n
            prev = n
        print('  sans %-13s : %4d — %s' % (field, len(numbers), ', '.join(spans)[:150]))
