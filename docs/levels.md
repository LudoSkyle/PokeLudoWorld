# Cartes, portes et changements de scène

## Le joueur n'appartient à aucune carte

`SceneManager` (dans `game_manager`, sous le `SubViewport`) instancie le joueur
**une fois** et le reparente dans le `World/Entities` de la carte courante à
chaque changement.

C'est le point d'architecture à retenir : le joueur doit être *dans* le groupe
trié en Y de la carte pour passer derrière les décors, mais il doit *survivre*
au changement de carte pour garder son état. Le reparentage satisfait les deux.
Une carte ne contient donc jamais d'instance de joueur.

Conséquence : après un changement, `PlayerCamera.applyLimits()` doit être
rappelée à la main — le joueur ne repasse pas par `_ready`.

## Structure d'une carte

```
Level (Node2D)
├── Background/Ground       le calque que lit la caméra pour ses limites
├── World (y_sort) ├── Props
│                  └── Entities        le joueur arrive ici
├── Doors (Node2D)          une SceneTrigger par porte, nommée
└── SpawnPoint (Node2D)     seulement sur la carte de départ
```

## Les portes se nomment entre elles

Une `SceneTrigger` est une **`Area2D`**, donc elle ne bloque pas : la requête de
déplacement du joueur n'interroge que les corps.

| Propriété | Rôle |
|---|---|
| `target_scene` | chemin `res://` de la carte visée |
| `target_door` | **nom du nœud** porte dans cette carte, sous son `Doors` |
| `entry_direction` | décalage d'arrivée, en cases, depuis la porte visée |

**`entry_direction` ne doit jamais être nul.** On arriverait pile sur la porte
d'arrivée, qui se redéclencherait aussitôt : aller-retour infini entre les deux
cartes. Toujours arriver une case à côté.

Une porte de maison vue du village utilise `(0, 1)` — on ressort devant la
maison ; vue de l'intérieur, `(0, -1)` — on entre dans la pièce.

## Les tuiles de porte doivent être praticables

Une porte posée sur une tuile de maison solide est inatteignable. Les deux
portes du village (`atlas (14,99)` et `(9,99)`) ont donc perdu leur collision et
portent `y_sort_origin = -15`, comme tout décor franchissable — voir
[tilesets.md](tilesets.md).

## Les intérieurs

Trois cartes : `ludo_house`, `ludo_bedroom`, `lab_house`.

Chacune est une pièce posée au milieu d'une grille de **32 × 20 cases remplies
de noir**. Ce cadre noir n'est pas décoratif : les limites de caméra sont
déduites de l'étendue du calque `Ground`, et une pièce seule serait plus petite
que le champ de vision. Le tutoriel de référence fait pareil.

Les pièces sont générées, pas peintes à la main. Les tuiles d'intérieur de
l'atlas, repérées une fois :

| Élément | Atlas |
|---|---|
| Mur (gauche / milieu / droite) | colonnes 60 / 61 / 62, lignes 44-46 |
| Parquet | `60-63, 47` · Brique `64-65, 47` · Planches `70-71, 51` |
| Escalier | `61, 48` sur 4×2, la marche praticable est `63, 50` |
| Noir de remplissage | `65, 49` |
| Lit `84,51` · Canapé `84,49` · Table `86,51` · Comptoir `88,52` | |
| Étagères `78,51` et `82,51` · Armoire `88,48` · Fenêtre `74,49` | |
| Tapis `81,55` · Paillasson `80,49` | |

L'escalier est un bloc solide dont seule la marche du bas est praticable : c'est
elle qui porte la porte.
