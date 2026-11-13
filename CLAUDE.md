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
| commits, branches, PRs | [docs/commits.md](docs/commits.md) |
| vérifier un rendu ou une collision | [docs/verification.md](docs/verification.md) |

## Où sont les choses

```
src/main/kotlin/fr/skyle/pokeludoworld/
├── assets/levels/      textures sources (atlas PNG + .import)
├── resources/tilesets/ level.tres — LE TileSet, collisions comprises
├── scenes/core/        game_manager.tscn (point d'entrée)
├── scenes/levels/      une scène par map
└── scripts/
    ├── autoload/       singletons déclarés dans project.godot
    └── log/            Logger, LogLevel, LogColor
```

## Règles qui ne se redemandent pas

- **Un `.import` se commite toujours avec son asset.** Il porte l'UID ; sans lui
  les références `uid://` cassent sur un clone neuf.
- **Jamais de collision posée à la main sur une map.** Tout se déclare une fois
  par tuile dans `level.tres` — voir [docs/tilesets.md](docs/tilesets.md).
- **Ne jamais valider un rendu sur une vue d'ensemble.** Zoomer sur chaque
  jonction — voir [docs/verification.md](docs/verification.md).
- Réponds en français ; les titres de commit restent en anglais.
