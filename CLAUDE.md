# Pokémon Mirage

Jeu type Pokémon sous **Godot 4.7** avec **godot-kotlin-jvm** : les scripts sont
des `.kt` compilés vers la JVM, d'où le layout Maven (`src/main/kotlin/...`).
Ce n'est pas du GDScript — ne propose pas de `.gd` pour du code de production.

Le projet suit le tutoriel [joeythelantern/pokemon-godot-csharp](https://github.com/joeythelantern/pokemon-godot-csharp)
(écrit en C#), dont on reprend la structure de dossiers. Les écarts assumés par
rapport à ce tutoriel sont listés dans [docs/architecture.md](docs/architecture.md).

## Documents à lire selon la tâche

| Tu touches à… | Lis d'abord |
|---|---|
| scènes, calques, ordre de dessin, tri Y | [docs/architecture.md](docs/architecture.md) |
| tuiles, collisions, terrains, atlas | [docs/tilesets.md](docs/tilesets.md) |
| composer ou retoucher une carte : bords, relief, arbres, herbes, chemins, eau, fleurs, objets | [docs/mapping.md](docs/mapping.md) |
| le joueur, ses déplacements, sa caméra | [docs/player.md](docs/player.md) |
| dialogues, panneaux, interaction | [docs/dialogue.md](docs/dialogue.md) |
| cartes, portes, changement de scène, bandeau de lieu | [docs/levels.md](docs/levels.md) |
| PNJ, leurs déplacements, passages gardés | [docs/npcs.md](docs/npcs.md) |
| quêtes, drapeaux d'histoire, objets ramassables | [docs/quests.md](docs/quests.md) |
| écran titre, logo, lancement d'une partie | [docs/title.md](docs/title.md) |
| menu de pause, options | [docs/menu.md](docs/menu.md) |
| sac, objets, inventaire | [docs/bag.md](docs/bag.md) |
| Pokémon sauvages, rencontres dans l'herbe | [docs/encounters.md](docs/encounters.md) |
| Pokédex, données des espèces | [docs/pokedex.md](docs/pokedex.md) |
| sons, musiques | [docs/audio.md](docs/audio.md) |
| jour et nuit, teinte du dehors | [docs/daynight.md](docs/daynight.md) |
| pluie, neige, brouillard, le temps qu'il fait | [docs/weather.md](docs/weather.md) |
| textes, traductions | [docs/i18n.md](docs/i18n.md) |
| sauvegarde, reprise au lancement | [docs/save.md](docs/save.md) |
| commits, branches, PRs | [docs/commits.md](docs/commits.md) |
| vérifier un rendu ou une collision, écrire un test, le terrain d'essai | [docs/verification.md](docs/verification.md) |

## Où sont les choses

```
src/main/kotlin/fr/skyle/pokemonmirage/
├── assets/levels/      textures sources (atlas PNG + .import)
├── resources/tilesets/ level.tres — LE TileSet, collisions comprises
├── scenes/core/        game_manager.tscn (point d'entrée)
├── scenes/levels/      une scène par map — une nouvelle partie démarre dans ludo_bedroom
├── scenes/ui/          interface (boîte de dialogue)
└── scripts/
    ├── autoload/       singletons déclarés dans project.godot
    ├── gameplay/       joueur, objets de niveau
    ├── log/            Logger, LogLevel, LogColor
    └── ui/             MessageBox
```

`tools/` (hors Godot) : les scripts qui fabriquent une planche à partir d'une
autre — `island_tiles.py` produit `assets/levels/island.png`,
`route_tiles.py` découpe `assets/levels/route.png` dans la planche de la
carte d'exemple de la route, `village_tiles.py` y découpe les maisons de
`assets/levels/village.png`, `cavern_tiles.py` fabrique `assets/levels/cavern.png` — la roche d'une grotte —
dans la planche des montagnes, `ice_cave_tiles.py` fabrique
`assets/levels/ice_cavern.png` — la grotte de glace, un kit à plateaux qui
se superposent — dans la planche de la grotte de glace,
`gamedata.py` sort du pack de données (`vendor/GameDataPacks`) les sprites,
icônes, cris et données des 1025 espèces, et les icônes des objets,
`weather_sheets.py` les planches de `assets/weather/`. Les trois
`title_*.py` dessinent les images de l'écran titre. **`tools/mapgen/` fait les cartes, en deux programmes** :
`build.py`, **le constructeur**, assemble un plan (`plans/<carte>.toml` : tout
ce qu'il y a sur la carte, case par case) avec un décor (`themes/<décor>.toml` :
quelle tuile dessine quoi) — sans rien décider ni tirer au hasard ;
`worldgen.py`, **le générateur**, invente un plan à partir d'une graine et de
réglages (`worlds/<monde>.toml` : relief, climat, végétation, chemins), en
appliquant les règles de `docs/mapping.md`. À côté d'eux, `check.py`, **le
contrôleur**, mesure ces règles sur un plan (un taux, et « injouable » à
part) avec les seuils du **style** de la carte — route, plage, village… :
elle le dit dans `[map] style` ; `neighbor.py` lit le bord d'une carte pour
que la suivante la prolonge (sortie, eau, talus, trame des arbres), et `sweep.py` le fait sur des dizaines de mondes de graines neuves —
à relancer après toute retouche du générateur. Une
nouvelle carte = un plan ou un monde, jamais un nouveau programme ; une
nouvelle ambiance = un décor. Et la scène écrite ne se refait pas : elle se
retouche dans l'éditeur. `tools/maps/` garde les
anciens générateurs, propres à leur carte : `route_1/` relève une carte d'exemple tuile par
tuile (`survey.py`) et en fabrique la Route 1 (`generate.py`) ;
`start_island/` lit la géographie d'une carte d'exemple (`geography.py`) et en
fabrique l'île de départ, avec les tuiles de la Route 1. `seam.py` colle
le bas de la route et le haut de l'île, pour vérifier qu'elles se suivent. `ice_cave/` garde la carte
d'exemple de la grotte de glace, son relevé tuile par tuile (`survey.py`) et
le juge de paix du décor `cave_ice` (`compare.py` : notre constructeur doit
la refaire à partir de quatre classes de cases).

`vendor/GameDataPacks/` (hors Godot : `vendor/.gdignore`) : le pack
`Gen 9/scarlet-violet` des packs de données de Pokémon Studio, **copié tel
quel dans le dépôt** — pas un sous-module ; son commit d'origine est noté dans
`vendor/GameDataPacks/ORIGINE.md`. **C'est la base du jeu**, la même que PSDK
et Pokémon Studio : données des espèces, objets, capacités, talents, types et
Pokédex (`Data/Studio/*.json`), textes en sept langues
(`Data/Text/Dialogs/*.csv`), cris, sprites sur la carte, icônes d'objets,
sprites de combat et icônes des Pokémon (`graphics/`). Pour tout ce qu'il
contient, on part de lui plutôt que d'une autre source. Le jeu ne lit jamais ce
dossier : `tools/gamedata.py` en sort ce qu'il faut vers `assets/` et
`resources/`. Licence de Pokémon Studio : attribution, usage non commercial,
partage dans les mêmes conditions.

## Règles qui ne se redemandent pas

- **Un `@Export` Kotlin devient du `snake_case` côté Godot.** `targetScene`
  s'écrit `target_scene` dans un `.tscn` ; avec le nom camelCase la valeur est
  silencieusement ignorée et la propriété garde son défaut. Vérifier avec
  `get_property_list()` en cas de doute.
- **Un `.import` se commite toujours avec son asset.** Il porte l'UID ; sans lui
  les références `uid://` cassent sur un clone neuf.
- **Jamais de collision posée à la main sur une map.** Tout se déclare une fois
  par tuile dans `level.tres` — voir [docs/tilesets.md](docs/tilesets.md).
- **Le flou sur du pixel art vient du `SubViewport`**, pas des calques : il
  n'hérite pas du filtre projet. Voir [docs/architecture.md](docs/architecture.md).
- **Ne jamais valider un rendu sur une vue d'ensemble.** Zoomer sur chaque
  jonction — voir [docs/verification.md](docs/verification.md).
- **Que ça ait du sens.** Visuel possible, comportement logique, ensemble
  cohérent, collisions justifiées : les quatre questions de
  [docs/verification.md](docs/verification.md), à se poser avant toute sonde.
- Réponds en français ; les titres de commit restent en anglais.
