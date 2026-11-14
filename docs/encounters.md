# Pokémon sauvages

Un pas dans les hautes herbes peut faire surgir un Pokémon sauvage. Le
principe vient du projet de référence (`TallGrass.cs` : un tirage quand le
joueur entre sur une case d'herbe, contre le `EncounterRate` de la carte).

**État actuel : la rencontre s'annonce, et c'est tout.** Il n'y a encore ni
espèces, ni table de rencontres, ni combat. `WildEncounters.step` est l'endroit
où ils se brancheront.

## Comment ça marche

`scripts/gameplay/wild/WildEncounters.kt`.

- **Quand** : à l'instant où le **joueur se pose** sur une case, à la fin de
  son pas (`Player._process`). Jamais en cours de pas, jamais à l'arrivée sur
  une carte, jamais en se retournant sur place. Un PNJ qui marche dans l'herbe
  ne déclenche rien.
- **Où** : la case doit porter une tuile du calque `Background/Grass` — le même
  qui dessine l'herbe ([tilesets.md](tilesets.md)). Rien à poser de plus.
- **Combien** : la carte donne la chance par pas, en pour cent, sur son nœud
  `Level` : `metadata/encounter_rate = 10`. Sans ce réglage, ou à 0, ses herbes
  sont vides.
- **Ce qui passe avant** : un passage gardé ou une porte déclenchés par le même
  pas. Boîte ouverte, joueur retenu ou carte qui change : pas de tirage.
- **Ce qui arrive** : le compteur `WildEncounters.count` monte, le journal
  l'écrit, et la boîte de dialogue dit « Un Pokémon sauvage apparaît ! ». Le
  joueur est arrêté le temps de la boîte, même touche tenue.

| Carte | `encounter_rate` |
|---|---|
| `start_town` | 10 |

## Mise au point et tests

Le hasard se court-circuite : `WildEncounters.forced` (true : toujours ;
false : jamais ; null : le hasard). Côté Godot,
`Globals.force_encounters(1 / 0 / -1)` et `Globals.encounters()`.

**Les tests démarrent sans aucune rencontre** (`boot` de `tests/lib.gd`) : un
test qui traverse l'herbe ne doit pas buter sur une boîte. Celui qui en veut
une appelle `force_encounters(1)`. Test : `tests/run.sh wild_encounter`.
