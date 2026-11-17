# Pokédex

Deux Pokédex sont prévus (Ludovic, 17/11/2026) :

- **le national** — toutes les espèces qui existent, sans exception. Pour
  l'instant c'est **une vue de debug**, hors du jeu : elle montre tout, vu ou
  non, pour vérifier que chaque espèce est bien renseignée ;
- **le régional** — le seul qu'on ouvrira en jeu : une espèce s'y découvre une
  fois rencontrée, ses détails une fois capturée. **Pas encore fait** ; ses
  espèces seront choisies avec Ludovic. L'écran, lui, attend qu'il ait trouvé
  une interface qui convienne.

## Les données du national

`resources/pokedex/national.tsv` : une espèce par ligne, ses champs séparés par
des tabulations, dans cet ordre —

| Champ | |
|---|---|
| `number`, `id`, `generation` | le numéro national, l'identifiant (`mr_mime`), la génération |
| `name_fr`, `name_en` | le nom |
| `genus_fr`, `genus_en` | la catégorie (« Pokémon Graine ») |
| `height`, `weight` | en mètres, en kilos ; 0 si la donnée manque |
| `icon`, `overworld` | 1 si on a son icône, son sprite de marche |
| `text_fr`, `text_en` | la description, sur une ligne ; vide si elle manque |

`tools/pokedex.py` le fabrique :

```bash
python3 -I tools/pokedex.py <dossier des CSV de PokéAPI> <dossier du kit Pokémon Essentials>
```

- **Noms, catégories, taille, poids, descriptions** : les CSV du dépôt
  [PokeAPI/pokeapi](https://github.com/PokeAPI/pokeapi) (`data/v2/csv/` :
  `pokemon_species`, `pokemon_species_names`, `pokemon_species_flavor_text`,
  `pokemon`), téléchargés le 17/11/2026 (commit `7764ee08de86`). Ils ne sont
  pas versionnés : le `.tsv` l'est. La description retenue est la plus récente
  de chaque langue.
- **Icônes** : `Graphics/Pokemon/Icons/` du kit Essentials, ramenées à 32 × 32
  et rangées dans **une seule planche**, `assets/pokemon/icons.png` — une case
  de 64 × 32 par espèce (ses deux images), 25 espèces par rangée, à la place
  que donne son numéro.
- **Sprites de marche** : un fichier par espèce dans
  `assets/pokemon/overworld/` (`tools/pokemon_overworld.py`).

Côté jeu : `NationalDex.kt` lit le `.tsv` (`NationalDex.all`, `DexEntry`). Ce
n'est pas le catalogue des espèces qu'on rencontre (`Dex`, dans `Species.kt`,
encore provisoire).

## Ce qui manque (17/11/2026)

`tools/pokedex.py` le redit à chaque passage, et la vue de debug le montre
espèce par espèce.

| | Manque à | |
|---|---|---|
| description en français | 127 espèces, n° 899 à 1025 | PokéAPI n'a pas de texte français pour Hisui ni pour la génération 9 |
| icône | 376 espèces, n° 650 à 1025 | le kit n'a d'icônes que jusqu'à la génération 5 |
| sprite de marche | 1017 espèces | seuls les neuf Pokémon du décor sont sortis des planches ; les planches de `sources/` couvrent bien plus, à découper |

Noms (FR et EN), catégories, taille, poids et description anglaise : complets
pour les 1025.

## La vue de debug

Menu de pause → Debug → **Pokédex national** (`PokedexDebug.kt`,
`scenes/ui/pokedex_debug.tscn`). À gauche la liste, quatorze espèces à la fois ;
à droite la fiche : icône, sprite, les deux noms, la catégorie, la génération,
la taille, le poids, les deux descriptions, et en rouge ce qui manque. Une
étoile dans la liste marque une espèce incomplète ; le titre les compte.

Haut/Bas : une espèce (en boucle) ; Gauche/Droite : dix d'un coup ; la touche
du menu referme. `tests/run.sh ui/debug_pokedex`.
