# Pokémon sauvages

Un pas dans les hautes herbes peut faire surgir un Pokémon sauvage. Le
principe vient du projet de référence (`TallGrass.cs` : un tirage quand le
joueur entre sur une case d'herbe, contre le `EncounterRate` de la carte).

**État actuel : la rencontre s'annonce, par le nom de l'espèce, et c'est
tout.** Il n'y a pas encore de combat, ni de Pokémon à soi. `WildEncounters.step`
est l'endroit où le combat se branchera.

## Comment ça marche

`scripts/gameplay/wild/WildEncounters.kt`.

- **Quand** : à l'instant où le **joueur se pose** sur une case, à la fin de
  son pas (`Player._process`). Jamais en cours de pas, jamais à l'arrivée sur
  une carte, jamais en se retournant sur place. Un PNJ qui marche dans l'herbe
  ne déclenche rien.
- **Où** : la case doit porter une tuile du calque `Background/Grass` — le même
  qui dessine l'herbe ([tilesets.md](tilesets.md)). Rien à poser de plus.
- **Combien** : la carte donne la chance par pas, en pour cent, sur son nœud
  `Level` : `metadata/encounter_rate = 3` pour un pas marché,
  `metadata/encounter_rate_run = 5` pour un pas couru — courir dans l'herbe
  dérange davantage. Sans le second réglage, courir ou marcher revient au
  même ; sans le premier, ou à 0, ses herbes sont vides au pas. Ces deux
  valeurs sont celles des cartes du jeu (Ludovic, 17/11/2026 : à 10, on
  croisait trop de monde).
- **Qui** : la table de rencontres de la carte, `metadata/wild` (ci-dessous).
  Une carte qui a une chance mais pas de table n'a personne à montrer : pas de
  rencontre.
- **Ce qui passe avant** : un passage gardé ou une porte déclenchés par le même
  pas. Boîte ouverte, joueur retenu ou carte qui change : pas de tirage.
- **Ce qui arrive** : le compteur `WildEncounters.count` monte,
  `WildEncounters.last` garde le Pokémon tiré (espèce et niveau), le journal
  l'écrit, et la boîte de dialogue dit « Un Mulotin sauvage apparaît ! ». Le
  joueur est arrêté le temps de la boîte, même touche tenue. Le niveau est
  tiré mais pas encore montré.

## La table de rencontres d'une carte

Une ligne sur le nœud `Level`, lue par `WildTable.kt` :

```
metadata/encounter_rate = 3
metadata/encounter_rate_run = 5
metadata/wild = "mulotin:2-4*50 | piafeuille:2-5*35 | chenibulle:3*15"
```

Chaque entrée est `espèce:niveaux*poids`, séparée des autres par `|`.

- **espèce** : son `id` dans le catalogue.
- **niveaux** : une fourchette `2-4` (bornes comprises, tirage égal) ou un
  seul niveau `3`. De 1 à 100.
- **poids** : la part de l'espèce dans le tirage, par rapport au total des
  poids. Ici 50, 35 et 15 sur 100 ; avec `*2 | *1`, deux tiers et un tiers.
  Sans `*poids`, il vaut 1.

Une entrée mal écrite (espèce inconnue, niveaux à l'envers, poids nul) est
**écartée et signalée au journal** ; la carte garde ses autres espèces.
`tests/run.sh wild_table` passe toutes les cartes en revue et refuse une
entrée fausse ou une chance sans table.

| Carte | `encounter_rate` / `_run` | `wild` |
|---|---|---|
| `start_island` | 3 / 5 | en attendant la liste des espèces de la région : Mulotin 2–4 (50), Piafeuille 2–5 (35), Chenibulle 3 (15) |
| `route_1` | 3 / 5 | les mêmes, un peu plus forts : Mulotin 3–5 (45), Piafeuille 3–6 (35), Chenibulle 4–5 (20) |

Le terrain d'essai (`tests/maps/field.tscn`) garde 10 au pas et n'a pas de réglage
pour la course : ses tests imposent le sort.

## Les espèces

`scripts/gameplay/pokemon/Species.kt` : le catalogue `Dex`, sur le modèle de
`Items`. Une espèce a un `id`, un nom français (traduit à l'affichage), un ou
deux types et six statistiques de base — les champs de la fiche du projet de
référence (`PokemonResource.cs`), moins les attaques et les sprites, qui
viendront avec le combat. Types et statistiques ne servent encore à rien.

Ajouter une espèce : une ligne dans `Dex.ALL`, et son nom dans `locale/en.po`.

**Les trois espèces actuelles sont provisoires**, inventées pour faire tourner
les rencontres (noms et chiffres compris) : à remplacer par les vraies.

## Mise au point et tests

Le hasard se court-circuite : `WildEncounters.forced` (true : toujours ;
false : jamais ; null : le hasard). Côté Godot,
`Globals.force_encounters(1 / 0 / -1)`, `Globals.encounters()` et
`Globals.last_encounter()` (`"mulotin:3"`).

Une table se vérifie sans marcher : `Globals.wild_draws(table, n, graine)` rend
n tirages, `Globals.wild_errors(table)` ses entrées fausses.
`Globals.seed_encounters(graine)` rend le hasard du jeu rejouable.

**Les tests démarrent sans aucune rencontre** (`boot` de `tests/lib.gd`) : un
test qui traverse l'herbe ne doit pas buter sur une boîte. Celui qui en veut
une appelle `force_encounters(1)`. Tests : `tests/run.sh wild_encounter` (le
pas dans l'herbe) et `tests/run.sh wild_table` (la table et ses tirages).
