# Personnages non joueurs

Repris du projet de référence, qui fait d'un PNJ un `CharacterBody2D` avec une
apparence au choix, une liste de messages et un mode de déplacement. Écarts :
pas de machine à états, pas de recherche de chemin (une ronde va en ligne
droite d'un point au suivant), et le tri se fait par le groupe trié en Y plutôt
que par un `ZIndex` recalculé.

## Un PNJ

`scenes/characters/npc.tscn`, script `Npc.kt`. Il réutilise les composants du
joueur : `CharacterMovement` pour les pas, `CharacterAnimation` pour le sprite.

| Propriété (`.tscn`) | Rôle |
|---|---|
| `appearance` | nom d'une planche de `assets/characters`, sans l'extension |
| `display_name` | son nom, s'il en a un : affiché au-dessus de la boîte quand il parle ([dialogue.md](dialogue.md)) |
| `gender` | `female` ou `male` : le nom s'écrit en rouge ou en bleu ; vide, à l'encre du texte |
| `facing` | direction regardée au repos |
| `text` | ce qu'il dit, avec `|` entre deux boîtes |
| `states` | ce qu'il dit selon l'histoire : `drapeau > texte`, voir [quests.md](quests.md) |
| `ask` | question Oui / Non posée avant de parler : `Question ?` ou `drapeau > Question ?` |
| `required_flag`, `forbidden_flag` | drapeau sans lequel, ou avec lequel, il n'est pas sur la carte |
| `movement` | `static` (défaut), `wander` ou `patrol` |
| `pace` | cases par seconde ; 4 = le joueur, 2 = les PNJ du projet de référence |
| `wander_layer` | errance : calque de tuiles dont il ne sort pas |
| `wander_pause` | errance : pause entre deux gestes, tirée entre x et y secondes |
| `route` | ronde : cases à rejoindre l'une après l'autre, en boucle |

- Il se pose sous **`World/Entities`**, comme le joueur, sur un **centre de
  case** : c'est ce qui le trie correctement devant ou derrière le décor.
- Il est sur le calque de collision 1 : il **bloque** comme un mur.
- Quand on lui parle, il **se tourne vers nous**, puis dit son texte. Le
  dialogue fini, un PNJ `static` **reprend sa direction de repos**. S'il est
  en train de marcher, il **termine son pas** puis répond.
- Personne ne bouge de soi-même pendant un dialogue ou un fondu.

### Errance (`wander`)

Après chaque pause, il se tourne dans une direction au hasard ; trois fois sur
dix il s'en tient là, sinon il avance d'une case **si elle est dessinée par
`wander_layer`**. `"Background/Grass"` le garde donc dans les hautes herbes,
quelle que soit la forme de la zone : rien à mesurer à la main. Sans calque, il
erre partout où il peut marcher.

### Ronde (`patrol`)

`route = PackedVector2Array(13, 16, 26, 16, ...)` : des **cases**, pas des
pixels. Il rejoint chaque point en ligne droite (d'abord en x, puis en y) et
recommence au premier. Deux points consécutifs doivent donc être reliés par un
trajet libre. Si quelqu'un est sur sa route, il **attend** sur place.

### Qui arrête qui

`CharacterMovement.obstacle_mask` : le joueur (calque 2) ne s'arrête que sur le
calque 1, un PNJ s'arrête sur 1 **et** 2 — sans ça il marcherait sur le joueur,
qui n'est pas un mur. Un pas ordonné par une scène (`Npc.walk`, voir le passage
gardé) ignore le joueur : c'est la scène qui règle leurs places.

Un corps n'occupe sa case d'arrivée qu'à la fin du pas. Le déplacement
**réserve** donc la case visée pendant le pas, pour tous les personnages : deux
marcheurs partis en même temps vers la même case ne s'y retrouvent pas.

### Ajouter une apparence

Déposer une planche de 128×192 dans `assets/characters/` (4 colonnes × 4
rangées de 32×48, rangées bas, gauche, droite, haut, pieds sur la ligne 45) et
la laisser importer. Son nom de fichier est la valeur d'`appearance` :
`CharacterFrames` découpe les animations à la volée, il n'y a pas de `.tres` à
écrire. Le catalogue et son origine sont dans `assets/characters/CREDITS.md`.

## Un passage gardé

`scenes/levels/roadblock.tscn`, script `Roadblock.kt` : une zone posée sur la
**case laissée libre à côté d'un garde**.

| Propriété | Rôle |
|---|---|
| `guard` | nom du garde sous `World/Entities` ; il doit être sur une case voisine |
| `push_direction` | direction dans laquelle le joueur est repoussé |
| `required_flag`, `forbidden_flag` | drapeau sans lequel, ou avec lequel, le passage n'est pas gardé ([quests.md](quests.md)) |

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
| `GrassWatcher` | départ (8,4) | chasseur d'insectes : erre dans les hautes herbes, à 2 cases/s, un geste toutes les 2 à 5 s |
| `Runner` | départ (13,9) | coureur : boucle sur le chemin entre les maisons, à 3 cases/s |
| `Roland` | (39,3) | ancien de la grotte, à droite de son entrée ; ses répliques suivent la quête ([quests.md](quests.md)) |
| `Fisher` | (40,17) | pêcheur les pieds dans l'eau claire, au bord de l'eau profonde, tourné vers le large |

Après la Veillée (`bell_hung`), les gardes, le passage, le coureur, le pêcheur
et Roland cèdent la place à leurs doubles « After » et aux visiteurs, sur la
place : voir [quests.md](quests.md).

Les gardes ne sont pas au bord de la carte : plus à l'ouest, la cime des arbres
recouvre la rangée du bas et cachait l'un d'eux.

La boucle du coureur fait le tour du tronçon de chemin large de trois cases qui
relie les deux maisons : aller par le bord, retour par l'allée du milieu, 52
cases. Elle évite les cases d'arrivée des portes. Une carte est réinstanciée à
chaque entrée : les PNJ repartent de leur case de départ quand on sort d'une
maison.
