# Pokémon

Tout ce dossier est **copié tel quel** du pack de données de Pokémon Studio,
[GameDataPacks](https://github.com/PokemonWorkshop/GameDataPacks) de **Pokémon
Workshop**, pack `Gen 9/scarlet-violet` (copié dans `vendor/GameDataPacks`),
par `tools/gamedata.py` :

| Dossier | Contenu | Dans le pack |
|---|---|---|
| `overworld/` | le sprite de chaque espèce sur la carte | `graphics/characters/` |
| `icons/` | l'icône de chaque espèce | `graphics/pokedex/pokeicon/` |
| `front/` | le portrait de face de chaque espèce, 96 × 96 | `graphics/pokedex/pokefront/` |

Un fichier par espèce, à son nom (`wingull.png`). Rien n'est retouché : seul le
nom du fichier change (le numéro du pack devient le nom de l'espèce).

**Licence** : [Licence d'utilisation de Pokémon Studio](https://github.com/PokemonWorkshop/PokemonStudio/blob/develop/LICENSE-FR.md)
— attribution, usage non commercial, partage dans les mêmes conditions. Les
Pokémon eux-mêmes appartiennent à Nintendo, Creatures Inc., GAME FREAK inc. et
The Pokémon Company.

Les données des espèces (`resources/pokedex/national.tsv`) et leurs cris
(`assets/audio/cries/`) viennent du même pack, aux mêmes conditions. Le format
des fichiers est décrit dans [docs/pokedex.md](../../../../../../../docs/pokedex.md).
