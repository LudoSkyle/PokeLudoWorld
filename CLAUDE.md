# PokeLudoWorld

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
| le joueur, ses déplacements, sa caméra | [docs/player.md](docs/player.md) |
| dialogues, panneaux, interaction | [docs/dialogue.md](docs/dialogue.md) |
| cartes, portes, changement de scène, bandeau de lieu | [docs/levels.md](docs/levels.md) |
| PNJ, leurs déplacements, passages gardés | [docs/npcs.md](docs/npcs.md) |
| menu de pause, options | [docs/menu.md](docs/menu.md) |
| sac, objets, inventaire | [docs/bag.md](docs/bag.md) |
| textes, traductions | [docs/i18n.md](docs/i18n.md) |
| sauvegarde, reprise au lancement | [docs/save.md](docs/save.md) |
| commits, branches, PRs | [docs/commits.md](docs/commits.md) |
| vérifier un rendu ou une collision | [docs/verification.md](docs/verification.md) |

## Où sont les choses

```
src/main/kotlin/fr/skyle/pokeludoworld/
├── assets/levels/      textures sources (atlas PNG + .import)
├── resources/tilesets/ level.tres — LE TileSet, collisions comprises
├── scenes/core/        game_manager.tscn (point d'entrée)
├── scenes/levels/      une scène par map
├── scenes/ui/          interface (boîte de dialogue)
└── scripts/
    ├── autoload/       singletons déclarés dans project.godot
    ├── gameplay/       joueur, objets de niveau
    ├── log/            Logger, LogLevel, LogColor
    └── ui/             MessageBox
```

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
