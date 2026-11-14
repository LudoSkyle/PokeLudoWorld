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
3. **Bloquer le chemin du retour, et lui seul**
   (`PlayerInput.blockUntilReleased`). La direction qui ferait repartir par où
   l'on arrive — celle qui déclenche une sortie, ou le demi-tour vers une porte
   à contact — est ignorée tant que sa touche reste enfoncée : on prend un escalier en maintenant Gauche, on arrive Gauche
   toujours enfoncé, et sans ça on le reprend aussitôt, en boucle.

   Les autres directions ne sont pas touchées : **une touche tenue continue de
   faire marcher après la porte**. Entrer dans une maison en maintenant Haut
   fait avancer dans la pièce sans relâcher, comme dans les jeux d'origine.

Pendant le fondu, le pas engagé se termine mais plus aucune entrée n'est lue.
Après, `PlayerCamera.applyLimits()` est rappelée à la main : le joueur est
reparenté sans repasser par `_ready`.

## Recharger la carte sur place

`SceneManager.reload()` recharge la carte courante dans le même fondu qu'une
porte, le joueur gardant sa place et son regard. Si la carte rechargée a posé
quelque chose sur sa case, il recule d'une case. Le bandeau de lieu ne se
réannonce pas. C'est ce que déclenche la consigne de dialogue `@reload`
([quests.md](quests.md)).

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

Quatre cartes pour les trois bâtiments du village :

| Bâtiment sur `start_town` | Porte (case) | Carte |
|---|---|---|
| maison en bas à gauche — **Ludo** | `MaisonLudo` (8,15) | `ludo_house` (salon) + `ludo_bedroom` (étage) |
| maison du centre — **la bibliothèque** | `Bibliotheque` (21,13) | `library`, de plain-pied — plan dans [quests.md](quests.md) |
| grand bâtiment en haut à droite, à la Poké Ball — **le laboratoire** | `Laboratoire` (28,7) | `lab_house` |

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
  calque `WallDecor`) — et seulement au-dessus d'une colonne **sans meuble
  haut** : un meuble adossé monte dans la rangée 2 et masquerait le cadre.
- **Un meuble posé au milieu de la pièce ne ferme aucune case** : vérifier
  qu'il ne reste pas une poche de sol inaccessible entre lui et le mur.
- Un tapis centré porte la table ; des plantes occupent les coins du bas ; le
  paillasson rouge de sortie est centré sur la dernière rangée.
- **Tabourets et coussins sont franchissables** (calque `Decor`) : on marche
  dessus, comme dans les jeux d'origine.
- **Seul le pot d'une plante bloque** : on passe derrière son feuillage.

Le mur fait 37 px de haut dans ses 3 rangées : sa rangée du haut est presque
vide. C'est pour ça que les murs sont sur un calque à part, **au-dessus** du
noir de `Ground` — sinon on voit le gris de fond du viewport à travers.

### Le laboratoire

Composé d'après celui du Prof. Chen (Rouge Feu / Vert Feuille), avec le
mobilier du labo du Prof. Orme (HeartGold) :

- contre le mur du fond, les appareils : serveurs, bureau et son PC, étagère à
  fioles, machine de soin, une bibliothèque ;
- au mur, une note, une horloge, une carte ;
- **au milieu, la machine aux trois Poké Balls**, face à l'entrée ;
- une rangée de bibliothèques à mi-pièce, coupée par la machine et deux allées ;
- des feuilles au sol, deux plantes à l'entrée, sol carrelé gris.

Le mur est encore le papier peint des maisons, faute d'un mur de labo dans
l'atlas.

En cas de doute sur une pièce, aller chercher une référence du jeu d'origine
(Bulbapedia, Poképédia) avant de composer.

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

**On passe aussi derrière le haut d'un meuble haut.** La rangée du haut d'une
bibliothèque (les quatre modèles) et le dôme de la machine aux trois Poké Balls
ne bloquent pas : seul leur pied bloque. Le joueur s'y glisse et le meuble le
recouvre, sa tête dépassant au-dessus. Contre un mur ça ne change rien — la
rangée du mur bloque déjà ; ça compte pour un meuble posé au milieu d'une
pièce, dont on peut ainsi faire le tour par derrière.

Un `Readable` ne se pose donc que sur les cases **du pied** d'un tel meuble :
c'est un corps solide, posé sur la rangée du haut il la refermerait.

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

Les deux sont des blocs 2×3 dans le coin haut-gauche de la pièce, à partir de
la rangée 2. **On n'y entre pas** : leurs deux rangées hautes sont solides.

Leur rangée du bas, elle, est **praticable** : l'escalier n'y déborde que de
8 px de socle, rien n'y gêne, et on doit pouvoir se tenir devant. La règle
générale « solide si couvert à moitié » la bloquait à tort — pour un escalier
le seuil est de 12 px.

Deux contraintes fixent leur position, et elles se vérifient à l'œil, joueur
posé sur le tapis :

- **Un escalier colle le mur**, comme dans le jeu d'origine : son haut mord
  sur le bas du mur, jamais de bande de plancher entre les deux.
- **Le personnage entre par le milieu**, pas par la rampe : ses pieds arrivent
  au ras de la rampe du bas de la volée, son corps dans l'ouverture de la
  cage. C'est ce qui place la case d'accès en **rangée 3**, la première de
  sol, et non une case plus bas.

Le tapis part du haut de cette case et dépasse de 5 px en dessous. Ces
décalages sont imposés dans `interiors.png` (`OFFSET` du script d'empilement) ;
l'écart escalier / tapis de la planche d'origine ne convient pas, il décolle
la cage du mur.

**L'accès tient en une seule case** : le tapis, à la même case aux deux étages.
C'est une *sortie* (`Escalier`, `exit_direction = (-1, 0)`) : on se tient sur le
tapis et on avance vers l'escalier. On arrive sur le tapis de l'autre étage,
tourné vers la pièce. Comme pour le paillasson, traverser le tapis ou s'y
arrêter ne déclenche rien. Depuis la case du dessous, avancer vers la gauche
ne prend pas l'escalier : on passe simplement devant.

## La grotte

Trois cartes, sur le modèle du Mont Sélénite (Rouge Feu) :

| Carte | Forme |
|---|---|
| `cave_1f` | une grande salle ouverte coupée de crêtes rocheuses ; la sortie en bas |
| `cave_b1f` | deux boyaux **isolés dans le noir**, sans lien entre eux |
| `cave_b2f` | une salle autour d'un lac souterrain |

```
village ── Sortie ── 1F ── TunnelA ── B1F ouest ── TunnelC ──┐
                      └─── TunnelB ── B1F est ──── TunnelD ── B2F
```

On descend par un tunnel et on remonte par l'autre : les deux boyaux du
sous-sol ne communiquent que par le niveau du dessus ou celui du dessous.

**Les niveaux se relient par des bouches de tunnel**, percées dans une paroi
nord, et non par des échelles : l'atlas n'a pas de tuile d'échelle. Une bouche
est une porte à contact ; on en ressort une case en dessous, dos à elle.

La sortie du 1F est un couloir qui file jusqu'au bas de la carte : ses deux
dernières cases sont des *sorties* (`exit_direction` vers le bas).

### Les tuiles

`assets/levels/cave.png` (source `8`) : la roche grise de `environments.png`
recopiée, plus une tuile.

- **Pourquoi une copie.** Dans l'atlas d'origine ce bloc est décalé d'un pixel :
  la première rangée et la première colonne de pixels appartiennent aux dessins
  voisins, ce qui trace des liserés bleus et noirs en jeu.
- **La tuile en plus est le sol.** C'est le dessus du massif, qui se répète sans
  raccord — mais en tuile à part, car celle du massif est solide et tout le sol
  le devenait.

Une salle est une cuvette : sol au centre, parois autour, noir au-delà. Les
parois se déduisent du voisinage de chaque case de roche ; une paroi doit faire
au moins deux cases d'épaisseur entre deux salles.

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

## Bandeau de lieu

`scenes/ui/location_banner.tscn`, script `LocationBanner.kt`, instancié dans
`game_manager.tscn`. Il descend en haut à gauche quand on arrive dans un lieu,
reste deux secondes, puis remonte.

Chaque carte déclare son lieu par deux **métadonnées de sa racine** `Level` :

```
[node name="Level" type="Node2D"]
metadata/location = "Maison de Ludo"
metadata/banner = "wood"
```

- `location` : le nom affiché. Le bandeau ne s'annonce que si ce nom **change** :
  deux cartes du même lieu (rez-de-chaussée et étage) portent le même nom, et
  l'escalier ne le fait pas réapparaître. Sans nom, pas de bandeau.
- `banner` : un fichier de `assets/ui/banners` — `wood` (défaut), `metal`,
  `stone`, `cave`, `forest`, `beach`, `water`, `sea`. Le texte passe en blanc
  sur les bandeaux sombres (`cave`, `forest`, `water`).

Le bandeau est dessiné à 4 pixels écran par pixel, comme le décor ; sa largeur
est fixe (131 px source), donc un nom tient en une vingtaine de caractères.
`SceneManager` l'annonce à chaque changement de carte, après le fondu.
