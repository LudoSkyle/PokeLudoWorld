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
`y_sort_origin = -15`, comme tout décor franchissable. Celles des deux maisons
orange de l'île (`(19,99)` et `(23,99)`) aussi : triée depuis le bas de sa
case, une porte se dessine **par-dessus le joueur qui entre**. Le test
`island_doors` le contrôle sur les cinq portes.

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

## L'île de départ

`scenes/levels/start_island.tscn` — 62 × 49 cases. C'est **la carte où le jeu
commence** (`SceneManager.start_scene`) et où mènent les sorties des
intérieurs. L'ancien village, `start_town.tscn`, est gardé tel quel : plus rien
n'y mène, mais la plupart des tests de mécanique s'en servent encore.

Elle est composée selon [mapping.md](mapping.md) : une baie intérieure
entourée de terres, pas une île au milieu de l'eau. Du relief partout : chaque
maison est sur un **plateau**, la place aussi ; le laboratoire est même **un
étage plus haut**, sur une terrasse adossée à la falaise.

```
 falaise du nord ═════════╗ trouée (gardée) ╔═════════ falaise du nord
 lisière │ NORD-OUEST, plateau │  LA CRIQUE DU NORD : plage, banc,   │ NORD-EST : terrasse,   │ lisière
         │ Ludo, maison orange │  parasol, hautes herbes             │ puis le labo au-dessus │
 ≈passe≈      │ ponton (en T)   ~~~~~~~~~ la baie ~~~~~~~~~            ponton (en L) │
         └────┴──────────────►  LA PLACE, sur son plateau  ◄─────────────────────────┘ ≈passe≈
 lisière │ OUEST, plateau : bibliothèque ─ponton─►  (socle de la cloche)
 ≈passe≈    (la cloche est sous ce ponton)        │
 lisière │ SUD-OUEST : hautes herbes, butte   plage du sud, palmiers, jetée   SUD-EST, plateau │ lisière
         └────── lisière ──────┘          ≈passe≈          └──── lisière ────┘  maison orange
```

**On n'arrive pas sur la place par le nord.** La crique où débouche la trouée
ne touche pas l'île du centre : il faut passer par le nord-est (ou le
nord-ouest), descendre son ponton et arriver par le côté. La place se monte par
l'ouest, l'est et le sud.

| Lieu | Case | |
|---|---|---|
| départ, devant chez Ludo | (8,9) | `SpawnPoint` |
| `MaisonLudo` | (8,8) | → `ludo_house` |
| `Bibliotheque` | (8,27) | → `library` |
| `Laboratoire` | (48,9) | → `lab_house` ; deux escaliers en dessous, en (48–49,11) et (48–49,14) |
| `MaisonNord` | (15,7) | → `orange_house_north`, chez Anselme |
| `MaisonSud` | (48,37) | → `orange_house_south`, chez Solange |
| la place | dallage x 26–34, y 22–26, sur le plateau du centre | socle de la cloche au milieu, deux statues ; le coureur en fait le tour (x 25–35, y 21–27) |
| la trouée de la falaise | x 28–33, y 0–3 | deux gardes en y 3, un contre chaque paroi ; le bout de la route en y 0 |
| la crique du nord | x 20–40, y 4–10 | plage, parasol, banc, une touffe de hautes herbes (26–28,6–7) |
| la cloche | (19,25), dans l'eau | se repêche depuis le ponton de l'ouest, en (19,26), tourné vers le nord |
| la jetée du sud | x 30–31, y 42–43 | le pêcheur est au bout ; des caisses sur le quai |
| hautes herbes | x 6–12, y 39–42 ; (12–15,15–16) ; (26–28,6–7) | |
| objets à ramasser | Potion en (55,32), Poké Ball en (5,40) | une Poké Ball posée au sol ([quests.md](quests.md)) |

**Les escaliers.** On monte sur un plateau par un escalier à poteaux de deux
cases, posé sur son bord du bas ou d'un côté — jamais sur celui du haut.

**Les rebords.** Le bord du haut d'un plateau est de l'herbe : on s'y tient,
mais on ne le franchit pas ([tilesets.md](tilesets.md), « Les rebords »).

**Le mur du nord est une montagne en gradins.** Il tient dans les rangées 0 à
3 — la carte ne grandit pas — et sa hauteur vient de **blocs de roche posés
les uns sur les autres** : un socle (`World/Cliffs`), des buttes de largeurs
inégales dessus (`CliffsMid`), et une butte de plus sur les plus larges
(`CliffsTop`). C'est le même bloc `5:26-28,22-23` à chaque étage ; ses coins
arrondis laissent voir le gradin du dessous. La rangée 0 n'a pas de bord : la
montagne continue au nord, hors de la carte.

**Les maisons sont serrées contre ce qui les borde.** Chez Ludo et la maison
orange du nord **touchent le mur** : la rangée du haut de leur toit recouvre
le pied de la falaise, rien ne passe derrière. Leur plateau s'allonge vers
l'est et porte les arbres du pied du mur. Le laboratoire remplit toute la
largeur de son étage ; on passe derrière lui, derrière la bibliothèque et
derrière la maison du sud, sous la rangée du haut de leur toit.

**Pas de sentier de sable sur l'herbe** : au pied d'un escalier, c'est de
l'herbe. Le sable, c'est la plage.

**Le mobilier.** Cinq bancs de bois (au fond de la place, dans la crique, au pied du
plateau de Ludo, sur la terrasse du labo, au pied du plateau du sud-est), un
parasol et sa serviette dans la crique et sur la plage du sud, des caisses sur
le quai, un pot de fleurs de chaque côté de la porte des maisons orange.

**Dans le ciel**, quatre Goélise et deux Bekipan volent au-dessus de la baie,
des bras de mer et de la plage du sud, chacun dans sa zone de dix cases sur
dix (nœud `Sky`, [npcs.md](npcs.md)).

**Les pontons** font deux cases de large, portent une rambarde sur chaque côté
qui donne sur l'eau et arrivent sur la rive par une planche de bout. Celui du
nord-ouest est en T (il relie aussi la terre de l'ouest), celui du nord-est en
L. La terre de l'ouest ne tient au reste que par ses deux pontons.

**Les bords sont fermés par le décor, à pied comme à la nage.** Une ceinture
d'arbres court le long des bords ouest, est et sud ; une falaise ferme le
nord. La mer ne touche le bord qu'à **quatre passes étroites**, chacune barrée
par une chaîne de rochers qui va d'un rocher de plage à l'autre. Aucune case
des 4 colonnes du bord (3 rangées en bas) n'est atteignable à pied, et un
nageur n'atteint ni le bord ni la terre de la marge.

**La Veillée prend fin quand on quitte l'île** : `metadata/on_leave =
"bell_hung > vigil_over"` (une règle « drapeau posé > drapeau à poser », lue
par `SceneManager` au changement de carte — un rechargement n'est pas un
départ). Qui est où avant, pendant et après : [npcs.md](npcs.md).

Trois calques de fond de plus que les autres cartes, entre `Paths` et
`Decorations` : **`Relief`** (les plateaux), **`Plaza`** (le dallage, posé sur
le plateau) et **`Bridges`** (les pontons et les escaliers). Leurs tuiles sont
décrites dans [tilesets.md](tilesets.md).

### Elle est produite par un générateur

La carte n'a pas été peinte à la main : un script la calcule à partir d'un
plan (terres, plateaux, pontons, bâtiments), pose les raccords de terrain,
plante le décor en laissant des couloirs dégagés vers chaque lieu, puis
**contrôle** avant d'écrire le `.tscn` : chaque lieu est accessible à pied,
aucune case de la marge ne l'est, aucune barrière de rochers ne fuit, aucun
ponton ne touche la terre par le flanc, aucun objet ni personnage n'étrangle
un passage. Il n'est pas dans le dépôt : il est rangé avec les notes de
session (`island_generator/` : `plan.py`, `gen.py`, `build.py`, et la sonde
qui relève la grille du moteur). Retoucher la carte dans l'éditeur reste
possible ; relancer le générateur écraserait ces retouches.

Les tuiles que l'atlas n'avait pas (rambardes, planches de bout, petits
rochers) sont fabriquées par `tools/island_tiles.py`, qui, lui, est dans le
dépôt.

`tests/run.sh island` : circulation (ce qui bloque, ce qui porte, les rebords,
tout se rejoint, la marge à pied et à la nage, les pontons), portes, objets à
ramasser, la quête en trois temps, et le vol des oiseaux.

## Les intérieurs

Six cartes : quatre pour les trois bâtiments du village, deux pour les maisons
orange de l'île.

Les sorties des trois bâtiments mènent maintenant à **l'île**
(`start_island`), sur des portes de même nom ; le tableau donne leurs cases
sur l'ancien village.

| Bâtiment sur `start_town` | Porte (case) | Carte |
|---|---|---|
| maison en bas à gauche — **Ludo** | `MaisonLudo` (8,15) | `ludo_house` (salon) + `ludo_bedroom` (étage) |
| maison du centre — **la bibliothèque** | `Bibliotheque` (21,13) | `library`, de plain-pied — plan dans [quests.md](quests.md) |
| grand bâtiment en haut à droite, à la Poké Ball — **le laboratoire** | `Laboratoire` (28,7) | `lab_house` |

Les deux maisons orange n'existent que sur l'île. Le paillasson de chacune
(`Doors/Entree`) ramène sur `start_island`, à la porte dont le nom suit :

| Maison sur `start_island` | Porte visée | Carte | Pièce | Habitant |
|---|---|---|---|---|
| petite maison orange du nord-ouest | `MaisonNord` | `orange_house_north` | 12 × 6, parquet à chevrons | Anselme |
| grande maison orange du sud-est | `MaisonSud` | `orange_house_south` | 16 × 8, tomettes | Solange |

Leurs plans sont plus bas, sous « Les maisons orange ».

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

### Les maisons orange

Deux pièces de plain-pied, une par maison orange de l'île, chacune avec son
habitant ([npcs.md](npcs.md)). Elles prennent dans l'atlas des pièces déjà
déclarées qu'aucune carte ne posait encore — la table carrée, la vitrine, la
grande table à nappe, le tapis vert, le tableau au cadre rouge, le tabouret
vert — et un sol à elles : chevrons `5:63,47` au nord, tomettes `5:70,47` au
sud. Le mur reste le papier peint des maisons, le seul qui porte une
collision.

Dans les deux, **le tapis n'est pas centré et ne porte pas la table** : il
marque un coin de la pièce (lecture au nord, télé au sud) et la table est de
l'autre côté. Les deux colonnes de la porte (`x 15-16`) restent nues du
paillasson jusqu'à la fenêtre : on entre Haut tenu sans rien heurter.

Dans les plans, sur le sol, une case en **majuscules bloque** ; en minuscules,
on marche dessus ou on passe derrière. Les rangées du mur, elles, bloquent
toutes.

**`orange_house_north` — chez Anselme.** Un couple de retraités, peu de
choses : de la vaisselle, des livres, une horloge. 12 colonnes (`x 10-21`),
mur en `y 5-7`, 6 rangées de sol (`y 8-13`).

```
      x 10 11 12 13 14 15 16 17 18 19 20 21
y 6      .  . ta ta ho FF FF  .  .  .  .  .   au mur : tableau, horloge, fenêtre
y 7     vi vi co co  . FF FF bv bv et et  .   hauts des meubles adossés
y 8     VI VI CO CO  .  . An BV BV ET ET  .   vitrine, commode, Anselme, bibliothèque, étagère
y 9      .  .  .  .  .  .  .  .  .  .  .  .   allée du fond
y 10     .  .  t  t  .  .  .  . tp tp tp  .   (haut de table : on passe derrière)
y 11     . sv TT TT sr  .  .  . tp tp tp  .   tabourets, table carrée, tapis vert
y 12    pl  . TT TT  .  .  .  . tp tp tp pl   feuillages
y 13    PL  .  .  .  . MM MM  .  .  .  . PL   pots, paillasson
```

Anselme est en `(16, 8)`, **à la fenêtre**, dos à la porte, entre l'horloge et
ses livres : c'est son poste. On lui parle depuis `(15, 8)` ou `(16, 9)`.
L'horloge se lit depuis `(14, 8)` (un `Readable` sur la case de mur sous
elle, comme au laboratoire), les livres depuis `(17-20, 9)`. Le tableau est
au-dessus de la commode, qui est basse : son haut ne mord que de 7 px sur le
mur et ne touche pas le cadre.

**`orange_house_south` — chez Solange.** Deux sœurs, une grande pièce à
vivre bien remplie et pas très rangée. 16 colonnes (`x 8-23`), mur en
`y 4-6`, 8 rangées de sol (`y 7-14`).

```
      x  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23
y 5      .  .  .  .  . li  . FF FF  .  .  .  .  .  .  .   au mur : liste épinglée, fenêtre
y 6     bo bo cu cu fr  . ar FF FF ar tv tv bb bb bu bu   hauts des meubles adossés
y 7     BO BO CU CU FR  . AR  .  . AR TV TV BB BB BU BU   bocaux, cuisinière et évier, frigo, arbustes, télé, livres, buffet
y 8      .  .  . So  .  .  .  .  .  .  .  .  .  .  .  .   Solange, devant l'évier
y 9      .  .  .  .  .  .  .  .  .  . tp tp tp  .  .  .   tapis bleu, devant la télé
y 10     .  .  t  t  t  .  .  .  . cj tp tp tp  . co co   (hauts de table et de commode : on passe derrière)
y 11     . sr TT TT TT sv  .  .  .  . tp tp tp  . CO CO   tabourets, grande table, commode
y 12     .  .  . sb  .  .  .  .  .  .  .  . cb  f  f  .   tabouret, coussin, feuilles par terre
y 13    pl  .  .  .  .  f  .  .  .  .  .  .  .  f  f pl   feuillages
y 14    PL  .  .  .  .  .  . MM MM  .  .  .  .  .  . PL   pots, paillasson
```

À gauche la cuisine et la table, à droite le coin télé. Solange est en
`(11, 8)`, **devant l'évier**, tournée vers la porte ; on lui parle depuis
`(10, 8)`, `(12, 8)` ou `(11, 9)`. Le désordre dont elle s'excuse se voit :
trois tabourets dépareillés, un coussin à gauche du tapis (`cj`) et un autre
en dessous (`cb`), des feuilles par terre. Les deux arbustes qui encadrent la fenêtre et les
plantes des coins sont ceux de sa sœur, qui jardine dehors. La télé se
regarde depuis `(18-19, 8)`, les livres se lisent depuis `(20-21, 8)`.

Deux choses apprises en les composant :

- **Un coussin ne se pose pas sur un tapis** : tous deux sont dans `Decor`,
  qui ne porte qu'une tuile par case. Il va à côté.
- **Une table de deux cases ne se centre pas sur un tapis de trois.** La
  table carrée (`7:21-22,0-2`) se pose donc sur le sol nu.

Tests : `tests/run.sh doors/orange` (la case d'arrivée sur l'île reste à
renseigner dans les deux fichiers) et `tests/run.sh audit`.

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
- `music` : la musique du lieu — voir [audio.md](audio.md).
- `daylight` : vrai pour une carte d'extérieur, qui prend la teinte de
  l'heure — voir [daynight.md](daynight.md).
- `banner` : un fichier de `assets/ui/banners` — `wood` (défaut), `metal`,
  `stone`, `cave`, `forest`, `beach`, `water`, `sea`. Le texte passe en blanc
  sur les bandeaux sombres (`cave`, `forest`, `water`).

Le bandeau est dessiné à 4 pixels écran par pixel, comme le décor ; sa largeur
est fixe (131 px source), donc un nom tient en une vingtaine de caractères.
`SceneManager` l'annonce à chaque changement de carte, après le fondu.
