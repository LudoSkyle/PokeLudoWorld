# Personnages non joueurs

Repris du projet de référence, qui fait d'un PNJ un `CharacterBody2D` avec une
apparence au choix et une liste de messages. Deux écarts : pas de machine à
états ni de déplacement autonome pour l'instant (ronde, errance), et le tri se
fait par le groupe trié en Y plutôt que par un `ZIndex` recalculé.

## Un PNJ

`scenes/characters/npc.tscn`, script `Npc.kt`. Il réutilise les composants du
joueur : `CharacterMovement` pour les pas, `CharacterAnimation` pour le sprite.

| Propriété (`.tscn`) | Rôle |
|---|---|
| `appearance` | nom d'une planche de `resources/spriteframes` : `worker`, `gardener`, `bug_catcher` |
| `facing` | direction regardée au repos |
| `text` | ce qu'il dit, avec `|` entre deux boîtes |

- Il se pose sous **`World/Entities`**, comme le joueur, sur un **centre de
  case** : c'est ce qui le trie correctement devant ou derrière le décor.
- Il est sur le calque de collision 1 : il **bloque** comme un mur.
- Quand on lui parle, il **se tourne vers nous**, puis dit son texte.

### Ajouter une apparence

Une planche de 128×192 (4 colonnes × 4 rangées de 32×48, rangées bas, gauche,
droite, haut) dans `assets/characters/`, et une copie de
`resources/spriteframes/player.tres` qui pointe dessus. Le nom du `.tres` est la
valeur d'`appearance`.

## Un passage gardé

`scenes/levels/roadblock.tscn`, script `Roadblock.kt` : une zone posée sur la
**case laissée libre à côté d'un garde**.

| Propriété | Rôle |
|---|---|
| `guard` | nom du garde sous `World/Entities` ; il doit être sur une case voisine |
| `push_direction` | direction dans laquelle le joueur est repoussé |

Si le joueur s'engage sur la case :

1. il est verrouillé et **recule d'une case sans se retourner** ;
2. le garde vient **à sa place**, face à lui, et dit son texte — le même que
   quand on lui parle ;
3. la boîte fermée, le garde **retourne à son poste** et le joueur reprend la
   main.

Ce n'est pas une collision : le joueur entre vraiment sur la case.

**C'est le joueur qui prévient le passage**, à l'instant où il termine son pas.
Un script qui observerait le joueur de l'extérieur ne le verrait jamais posé :
avec la touche tenue, il enchaîne le pas suivant dans la même image. D'où une
zone sur le calque des portes, retrouvée par `areaUnderfoot()`.

À la fin, la direction qui mène au passage est ignorée tant que sa touche reste
enfoncée, sinon la scène repartirait en boucle.

## Dans `start_town`

| Nœud | Case | Rôle |
|---|---|---|
| `GuardNorth`, `GuardSouth` | (5,7) et (5,9) | ouvriers qui ferment la sortie ouest |
| `Triggers/WestRoadblock` | (5,8) | la case du milieu ; garde : `GuardNorth` |
| `GrassWatcher` | (8,4) | chasseur d'insectes dans les hautes herbes |

Les gardes ne sont pas au bord de la carte : plus à l'ouest, la cime des arbres
recouvre la rangée du bas et cachait l'un d'eux.
