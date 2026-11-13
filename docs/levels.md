# Cartes, portes et changements de scène

## Le joueur n'appartient à aucune carte

`SceneManager` (dans `game_manager`, sous le `SubViewport`) instancie le joueur
**une fois** et le reparente dans le `World/Entities` de la carte courante à
chaque changement.

Le joueur doit être *dans* le groupe trié en Y de la carte pour passer derrière
les décors, mais il doit *survivre* au changement de carte pour garder son état.
Le reparentage satisfait les deux. Une carte ne contient donc jamais d'instance
de joueur.

## Deux sortes de portes

Une porte est une `SceneTrigger` — une **`Area2D`**, donc elle ne bloque pas.

| | Porte à contact | Sortie |
|---|---|---|
| Exemples | porte de maison vue du village | paillasson rouge d'un intérieur, tapis d'escalier |
| Se déclenche | dès qu'on marche dessus | quand on **avance dans `exit_direction`** en étant dessus |
| On arrive | une case à côté, décalé de `entry_direction` | **sur** la porte |
| On regarde | dans `entry_direction` | à l'opposé de `exit_direction` |

Une sortie ne réagit pas au contact : on peut traverser un paillasson de côté
ou y arriver par le haut sans quitter la pièce. C'est `Player` qui l'active,
quand le joueur immobile dessus demande à marcher vers la sortie — il retrouve
la porte sous ses pieds par `CharacterMovement.areaUnderfoot()` (les portes
sont sur le calque de collision 3 pour ça).

Propriétés, **en snake_case dans le `.tscn`** :

| Propriété | Rôle |
|---|---|
| `target_scene` | chemin `res://` de la carte visée |
| `target_door` | **nom du nœud** porte dans cette carte, sous son `Doors` |
| `entry_direction` | porte à contact : décalage et orientation d'arrivée |
| `exit_direction` | non nul = sortie ; la direction à prendre pour sortir |

Pour une porte à contact, `entry_direction` ne doit **jamais être nul** : on
arriverait dessus et elle se redéclencherait, en boucle entre les deux cartes.

La tuile sous une porte doit être praticable. Les deux portes du village
(`atlas (14,99)` et `(9,99)`) ont perdu leur collision et portent
`y_sort_origin = -15`, comme tout décor franchissable.

## Ce que fait une arrivée

1. **Annuler le pas en cours** (`CharacterMovement.stop()`). Le pas qui a
   franchi la porte vise une case de l'*ancienne* carte ; sans ça le personnage
   glisse vers elle à travers les murs de la nouvelle.
2. **Poser et orienter le joueur** selon la sorte de porte (tableau ci-dessus).
3. **Exiger une nouvelle pression** (`PlayerInput.requireFreshPress`). On prend
   un escalier en maintenant Gauche ; à l'arrivée Gauche est toujours enfoncé,
   et sans ça on reprend aussitôt l'escalier dans l'autre sens.

Pendant le fondu, le pas engagé se termine mais plus aucune entrée n'est lue.
Après, `PlayerCamera.applyLimits()` est rappelée à la main : le joueur est
reparenté sans repasser par `_ready`.

## Structure d'une carte

```
Level (Node2D)
├── Background
│   ├── Ground        le calque que lit la caméra pour ses limites
│   ├── Walls         murs                              (intérieurs)
│   ├── WallDecor     fenêtres, tableaux                (intérieurs)
│   └── Decor         tapis, paillassons, tabourets — on marche dessus ;
│                     les escaliers aussi, mais eux sont solides
├── World (y_sort) ├── Props      meubles, solides
│                  └── Entities   le joueur arrive ici
├── Doors             une SceneTrigger par porte, nommée
└── SpawnPoint        seulement sur la carte de départ
```

## Les intérieurs

Trois cartes : `ludo_house` (salon), `ludo_bedroom` (chambre à l'étage),
`lab_house`.

Chaque pièce est posée au milieu d'une grille de **32 × 20 cases de noir**. Ce
cadre n'est pas décoratif : les limites de caméra viennent de l'étendue du
calque `Ground`, et une pièce seule serait plus petite que le champ de vision.

### Règles de composition

Le mur occupe les rangées 0 à 2 de la pièce, le sol commence à la rangée 3.

- **Un meuble adossé au mur est posé au sol.** Son bloc 2×2 commence à la
  rangée 2 : le haut contre le bas du mur, le pied sur la première rangée de
  sol. S'il tenait entièrement dans les rangées du mur, il aurait l'air
  accroché dessus.
- **Seuls fenêtres, tableaux et tableau noir sont dans le mur** (rangées 1-2,
  calque `WallDecor`).
- Un tapis centré porte la table ; des plantes occupent les coins du bas ; le
  paillasson rouge de sortie est centré sur la dernière rangée.
- **Tabourets et coussins sont franchissables** (calque `Decor`) : on marche
  dessus, comme dans les jeux d'origine.
- **Seul le pot d'une plante bloque** : on passe derrière son feuillage.

Le mur fait 37 px de haut dans ses 3 rangées : sa rangée du haut est presque
vide. C'est pour ça que les murs sont sur un calque à part, **au-dessus** du
noir de `Ground` — sinon on voit le gris de fond du viewport à travers.

### L'atlas `interiors.png`

**Les meubles de `environments.png` ne sont pas alignés sur la grille de
16 px** : le lit fait 19 px de large, les tables tombent à cheval sur les
frontières de tuiles. Les découper en tuiles les tranche au hasard.

`assets/levels/interiors.png` (source `7` du TileSet) contient ces mêmes
meubles **recalés** : chacun est centré horizontalement et aligné en bas dans
un bloc multiple de 16. C'est avec cette source qu'on peint un intérieur ; les
sols et les murs viennent toujours de la source `5`.

Règle de collision : une rangée d'un meuble est solide si le meuble en couvre
au moins la moitié. La rangée du haut d'une table basse reste donc
franchissable — on passe derrière, et elle couvre les jambes.

### L'escalier

`environments.png` n'a pas d'escalier de maison. Ceux de `interiors.png`
viennent d'une **seconde planche d'intérieur**, série verte. Ce sont des
découpes telles quelles, comme le reste de l'atlas ; la planche elle-même
n'est pas dans le dépôt.

**Monter et descendre ne sont pas le même dessin.** Deux pièces distinctes, à
ne pas intervertir :

| Tuile | Ce que c'est | Où |
|---|---|---|
| `stairs_up` | une **volée** à rampe qui s'élève vers la gauche | en bas : on monte |
| `stairwell_down` | une **cage**, trou dans le plancher, ouverte à droite | en haut : on descend |
| `stair_mat_up`, `stair_mat` | le petit tapis de chacune, 1×2, franchissable | à leur droite |

Les deux sont des blocs 2×3 dans le coin haut-gauche de la pièce, tous deux
**entièrement solides** : on n'y entre pas.

- La volée commence à la rangée 2 : son sommet monte le long du mur et sa
  coupe franche tombe sur le bord gauche de la pièce.
- La cage commence à la rangée 3 : elle est posée sur le plancher, pas adossée
  au mur.

Leur position dans le bloc reproduit **au pixel près** l'écart escalier / tapis
de la planche : le tapis tombe pile devant l'ouverture de la cage, et au pied
de la volée. Ne pas les recaler « en bas du bloc » comme un meuble.

**L'accès tient en une seule case** : le tapis, à la même case aux deux étages.
C'est une *sortie* (`Escalier`, `exit_direction = (-1, 0)`) : on se tient sur le
tapis et on avance vers l'escalier. On arrive sur le tapis de l'autre étage,
tourné vers la pièce. Comme pour le paillasson, traverser le tapis ou s'y
arrêter ne déclenche rien, et pousser vers l'escalier depuis la case du dessus
ou du dessous non plus.

## Tester une carte

Deux contrôles, tous deux automatisables par une sonde (voir
[verification.md](verification.md)) :

- **Accessibilité** : relever la grille de collisions, puis vérifier par
  parcours en largeur que chaque case d'arrivée est libre, que toutes les
  portes sont atteignables depuis chacune, et qu'une sortie bute bien sur du
  solide dans sa direction.
- **Parcours réel** : calculer un chemin sur ces collisions et le suivre
  **touche par touche**, en vérifiant à chaque arrivée la case, l'immobilité et
  l'orientation. Y inclure les cas négatifs : traverser un paillasson de côté
  ne doit rien déclencher. Téléporter le joueur sur une porte ne teste rien de
  tout ça.
