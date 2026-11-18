# D'où vient ce dossier

Copie **non modifiée** du pack `Gen 9/scarlet-violet` du dépôt
[PokemonWorkshop/GameDataPacks](https://github.com/PokemonWorkshop/GameDataPacks)
— les packs de données de Pokémon Studio et de PSDK.

| | |
|---|---|
| Commit d'origine | `d430fb553df98ccde5f9f90ece78e36b07d8083c` (2026-09-07) |
| Copié le | 18/11/2026 |
| Ce qui est pris | le seul dossier `Gen 9/scarlet-violet`, en entier, et le `README.md` du dépôt |
| Modifications | aucune |

**Licence** : [Licence d'utilisation de Pokémon Studio](https://github.com/PokemonWorkshop/PokemonStudio/blob/develop/LICENSE-FR.md)
([English](https://github.com/PokemonWorkshop/PokemonStudio/blob/develop/LICENSE.md)) —
attribution, usage non commercial, partage dans les mêmes conditions. Fourni
tel quel, sans garantie. Les Pokémon appartiennent à Nintendo, Creatures Inc.,
GAME FREAK inc. et The Pokémon Company.

**Pour le mettre à jour** : remplacer `Gen 9/scarlet-violet` par celui d'un
commit plus récent du dépôt d'origine, noter ce commit ici, puis relancer
`python3 tools/gamedata.py`.

Le jeu ne lit jamais ce dossier (`vendor/.gdignore`) : `tools/gamedata.py` en
copie ce qu'il faut vers `assets/` et `resources/`.
