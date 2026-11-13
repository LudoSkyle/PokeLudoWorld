# Cartes, portes et changements de scène

## Le joueur n'appartient à aucune carte

`SceneManager` (dans `game_manager`, sous le `SubViewport`) instancie le joueur
**une fois** et le reparente dans le `World/Entities` de la carte courante à
chaque changement.

Le joueur doit être *dans* le groupe trié en Y de la carte pour passer derrière
les décors, mais il doit *survivre* au changement de carte pour garder son état.
Le reparentage satisfait les deux. Une carte ne contient donc jamais d'instance
de joueur.

## Ce que fait une arrivée

Quatre choses, toutes nécessaires — chacune correspond à un bug rencontré :

1. **Annuler le pas en cours** (`CharacterMovement.stop()`). Le pas qui a
   franchi la porte vise une case de l'*ancienne* carte ; sans ça le personnage
   glisse vers elle à travers les murs de la nouvelle.
2. **Poser le joueur une case à côté de la porte d'arrivée**, jamais dessus —
   elle se redéclencherait aussitôt, en boucle entre les deux cartes.
3. **L'orienter dos à la porte** (`PlayerInput.face`).
4. **Exiger une nouvelle pression** (`PlayerInput.requireFreshPress`). On monte
   un escalier en maintenant Haut ; à l'arrivée Haut est toujours enfoncé, et
   sans ça on rentre aussitôt dans l'escalier d'en face.

Pendant le fondu, le pas engagé se termine mais plus aucune entrée n'est lue.
Après, `PlayerCamera.applyLimits()` est rappelée à la main : le joueur est
reparenté sans repasser par `_ready`.

## Structure d'une carte

```
Level (Node2D)
├── Background
│   ├── Ground        le calque que lit la caméra pour ses limites
│   ├── Walls         murs, escalier                    (intérieurs)
│   ├── WallDecor     fenêtres, tableaux                (intérieurs)
│   └── Decor         tapis, paillassons — franchissables
├── World (y_sort) ├── Props      meubles, solides
│                  └── Entities   le joueur arrive ici
├── Doors             une SceneTrigger par porte, nommée
└── SpawnPoint        seulement sur la carte de départ
```

## Les portes se nomment entre elles

Une `SceneTrigger` est une **`Area2D`**, donc elle ne bloque pas : la requête de
déplacement du joueur n'interroge que les corps.

| Propriété (dans le `.tscn`) | Rôle |
|---|---|
| `target_scene` | chemin `res://` de la carte visée |
| `target_door` | **nom du nœud** porte dans cette carte, sous son `Doors` |
| `entry_direction` | où l'on arrive par rapport à la porte visée, et vers où l'on regarde |

`entry_direction` ne doit **jamais être nul** (voir plus haut). Une porte de
maison vue du village utilise `(0, 1)` ; vue de l'intérieur, `(0, -1)`.

La tuile sous une porte doit être praticable. Les deux portes du village
(`atlas (14,99)` et `(9,99)`) ont perdu leur collision et portent
`y_sort_origin = -15`, comme tout décor franchissable.

## Les intérieurs

Trois cartes : `ludo_house` (salon), `ludo_bedroom` (chambre à l'étage),
`lab_house`.

**Composition, calquée sur les jeux d'origine :** les meubles hauts sont
adossés au mur et tiennent *dans* ses rangées, donc le sol reste dégagé ; un
tapis centré porte la table ; des plantes occupent les coins du bas ; le
paillasson rouge de sortie est centré sur la dernière rangée.

Chaque pièce est posée au milieu d'une grille de **32 × 20 cases de noir**. Ce
cadre n'est pas décoratif : les limites de caméra viennent de l'étendue du
calque `Ground`, et une pièce seule serait plus petite que le champ de vision.

Le mur fait 37 px de haut dans ses 3 rangées : sa rangée du haut est presque
vide. C'est pour ça que les murs sont sur un calque à part, **au-dessus** du
noir de `Ground` — sinon on voit le gris de fond du viewport à travers.

### L'atlas `interiors.png`

**Les meubles de `environments.png` ne sont pas alignés sur la grille de
16 px** : l'escalier commence 11 px après une frontière de tuile, le lit fait
19 px de large. Les découper en tuiles les tranche au hasard — c'est ce qui
donnait des pièces « en vrac ».

`assets/levels/interiors.png` (source `7` du TileSet) contient ces mêmes
meubles **recalés** : chacun est centré horizontalement et aligné en bas dans
un bloc multiple de 16. C'est avec cette source qu'on peint un intérieur ; les
sols et les murs viennent toujours de la source `5`.

Règle de collision appliquée : une rangée d'un meuble est solide si le meuble
en couvre au moins la moitié. La rangée du haut d'une table basse reste donc
franchissable — on passe derrière, et elle couvre les jambes.

L'escalier est un bloc de mur 4×3 dont la colonne 2 est l'escalier ; sa case
basse (l'alcôve) est la seule praticable et porte la porte. Sous elle, `Ground`
a du sol et non du noir, le noir étant solide.

## Tester une carte

Deux contrôles, tous deux automatisables par une sonde (voir
[verification.md](verification.md)) :

- **Accessibilité** : relever la grille de collisions, puis vérifier par
  parcours en largeur que chaque case d'arrivée est libre et que toutes les
  portes sont atteignables depuis chacune.
- **Parcours réel** : calculer un chemin sur ces collisions et le suivre
  **touche par touche**, en vérifiant à chaque arrivée la case, l'immobilité et
  l'orientation. Téléporter le joueur sur une porte ne teste rien de tout ça —
  c'est comme ça qu'une sortie bloquée par une table et une glissade à
  l'arrivée sont passées.
