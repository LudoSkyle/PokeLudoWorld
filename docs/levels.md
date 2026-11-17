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
└── SpawnPoint        où apparaît une nouvelle partie : la chambre de Ludo ; l'île garde le sien
```

## L'île de départ

`scenes/levels/start_island.tscn` — 55 × 50 cases. C'est la carte où mènent
les sorties des intérieurs. **Une nouvelle partie commence dans la chambre de
Ludo** (`ludo_bedroom.tscn`, `SceneManager.start_scene`), debout au milieu du
tapis bleu, case (15,11), tourné vers le bas : on descend l'escalier, on sort
de la maison, et l'on arrive sur l'île devant chez Ludo.

**Elle a la géographie d'une carte d'exemple fournie par Ludovic, dans le
style de la Route 1** (17/11/2026). Elle n'en est pas la copie : le terrain de
l'exemple vient de `sources/seasons_trees_ponds.png`, mais ses arbres, ses
huttes et ses pontons viennent de planches que le projet n'a pas, et l'île du
jeu a une place et une cloche que l'exemple n'a pas. On en garde donc **où
est la mer, où sont les plages, où sont les terres en hauteur, où passent les
chemins, où pousse la forêt**, et on le pose avec les tuiles de la Route 1
(`route.png`) et des maisons découpées dans la même planche (`village.png`).

```
 forêt │ NORD-OUEST, plateau : │ trouée du nord (gardée) │ NORD-EST, plateau : la montagne, │ forêt
       │ Ludo, Anselme         │  LA CRIQUE : plage      │ le laboratoire                   │
       └──escalier─────────────┘   parasol, serviette    └──escalier──────────┬─ponton──────┘
 ~~~~ ponton ~~~~~~~~~~~~~~~~~~~~~  la baie  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ │ ~~~~~~~~~~~~~~
      └─────── ponton ────────►  LA PLACE, sur son plateau  ◄──── ponton ─────┴──┐
 OUEST, plateau : │ ponton       dallage, socle de la cloche, statues            │ SUD-EST, plateau :
 la bibliothèque  │                 └──escalier──┘                               │ Solange
   └─escalier─┐   │                                                   ┌─escalier─┘
 plage de     │ JARDIN du sud-ouest       LA PLAGE DU SUD : parasol, jetée        la presqu'île
 l'ouest      │ (hautes herbes)                  ~~~~ jetée ~~~~
```

**Trois niveaux.** La **mer**, pleine ; profonde au large. Les **plages**, de
sable, au ras de l'eau : on y marche, et leur bord ondule dans la case d'eau
voisine (le liseré, plein). Les **plateaux** : toute l'herbe, cernée d'une
falaise d'une case. Ses flancs et son bas, où la roche se voit, sont pleins.
**Son bord du haut ne l'est pas** : c'est de l'herbe avec un liseré, rien n'y
dit « falaise », et derrière lui il y a la plage — on s'y tient et l'on passe
de l'un à l'autre (Ludovic, 17/11/2026). Il n'y a pas d'herbe au niveau de la
plage : une tuile de sable bordé d'herbe manque encore.

**On change de niveau par cinq escaliers de pierre**, tous face au sud (la
planche n'en a pas d'autres) : trois marches entre deux poteaux. Sous chacun,
une anse de plage ; au-dessus, un bord de plateau droit sur cinq cases.

**Les pontons vont du dessus d'un plateau à l'autre**, larges de trois cases :
du nord-ouest à la place et de là au jardin ; du nord-est à la place et de là
au sud-est. La jetée du sud part de la plage.

**La place** se rejoint par ses deux pontons, par son escalier depuis la plage
du sud, et par son bord du nord depuis la crique. Le jardin du sud-ouest se
rejoint par son ponton, ou par son bord du haut depuis la plage du sud.

**L'eau reflète, le sable garde les traces** : la mer porte la donnée `water`
et le sable des plages la donnée `sand` ([tilesets.md](tilesets.md)). Le bord
du sable est posé à part, par-dessus l'eau (calque `Shore`), pour qu'un reflet
passe dessous au lieu de s'étaler sur le sable. Au-dessus de l'eau, l'ombre
d'un Pokémon volant bleuit.

| Lieu | Case | |
|---|---|---|
| départ, devant chez Ludo | (6,9) | `SpawnPoint` |
| `MaisonLudo` | (6,8) | → `ludo_house` ; hutte de chaume, porte à gauche |
| `MaisonNord` | (13,9) | → `orange_house_north`, chez Anselme |
| `Bibliotheque` | (3,29) | → `library` |
| `Laboratoire` | (45,8) | → `lab_house` ; la grande maison de chaume, au pied de la montagne |
| `MaisonSud` | (43,33) | → `orange_house_south`, chez Solange |
| la place | dallage x 24–32, y 22–27, sur le plateau du centre | socle de la cloche en (28,23), deux statues en (25,23) et (31,23) ; le coureur en fait le tour (x 23–33, y 21–28) |
| la trouée du nord | x 23–27, y 0–8 | un couloir de plage entre deux falaises ; deux gardes en y 3, un contre chaque paroi ; en y 0, cinq portes `Nord0`…`Nord4` mènent à la **Route 1** (`route_1`) |
| la crique du nord | x 19–31, y 8–17 | plage, parasol, serviette ; on passe sous un parasol, derrière son mât |
| la cloche | (14,21), dans l'eau | n'y est qu'**après que Roland a dit où chercher** (`bell_spotted`) ; se repêche depuis le ponton de l'ouest, en (14,22), tourné vers le nord |
| la jetée du sud | x 32–34, y 43–48 | le pêcheur est au bout, en (33,48) |
| escaliers (colonne de gauche, rangée) | (14,13), (31,13), (26,31), (2,33), (36,37) | nord-ouest, nord-est, place, bibliothèque, sud-est |
| hautes herbes | le jardin du sud-ouest (x 10–21, y 38–43) ; derrière chez Anselme (14–18, 4–6) ; près du labo (49–52, 12–15) | |
| objets à ramasser | Potion en (47,46), au bout de la presqu'île ; Poké Ball en (3,43), au fond de la plage de l'ouest ; Eau Fraîche en (49,5), au fond du couloir à droite du laboratoire | une Poké Ball posée au sol ([quests.md](quests.md)) |

Calques de fond, dans l'ordre : `Ground`, `Shore` (le bord du sable, sur
l'eau), `Cliffs1` (la falaise des plateaux),
`Cliffs2` (la montagne), `Paths`, `Plaza`, `Decorations` (fleurs, serviettes),
`Grass`, `Bridges` (pontons et escaliers). Dans `World`, triés en Y : `Trees`,
`Props` (rochers, sapins, bancs, parasols), `Houses`.

**Les pistes** font trois cases de large et sont d'un seul tenant sur chaque
plateau (`layout.PATHS`, tracées à la main là où l'exemple a ses chemins) :
plus étroite, une piste n'est que deux bords collés. **Les plages ont leurs
palmiers**, là où l'exemple pose quelque chose sur le sable, espacés de cinq
cases, jamais dans un passage ni contre le mobilier ; des massifs de buissons
garnissent les coins de la place, et les fleurs sont plus serrées autour
d'elle et sur la presqu'île du sud-est. La cloche, au fond de l'eau,
**scintille** (`Twinkle.kt`).

**Dans le ciel**, quatre Goélise et deux Bekipan, chacun dans sa zone de dix
cases sur dix (nœud `Sky`, [npcs.md](npcs.md)).

### Elle est produite par un générateur

`tools/maps/start_island/`, sur le modèle de celui de la Route 1 :

| Fichier | Rôle |
|---|---|
| `reference.png` | la carte d'exemple |
| `geography.py` | `--read` range chaque case de l'exemple dans une classe (mer, plage, chemin, herbe, forêt, toit, roche) et note où un objet est posé sur le terrain → `classes.json`. Puis il en tire la mer, les plages et les plateaux, **porte les retouches** (`RETOUCH`, en clair), et arrange les formes pour que chaque case ait sa tuile de bord |
| `layout.py` | pose le sol, la falaise, les pistes, les pontons, les escaliers, la forêt, les maisons ; calcule ce qui bloque et ce qu'on atteint |
| `generate.py` | pose la place, les panneaux, les lampadaires, le mobilier, les personnages et la quête ; contrôle ; écrit la scène et la source 14 du TileSet |

```bash
python3 tools/maps/start_island/generate.py                  # contrôle seulement
python3 tools/maps/start_island/generate.py --write          # écrit la scène et la source des maisons
python3 tools/maps/start_island/generate.py --preview a.png  # la carte, sans passer par Godot
python3 tools/maps/start_island/generate.py --map --where    # ce qui bloque ; où est posé quoi
```

**Rien ne se pose à la main dans l'éditeur** : relancer le générateur écrase
la scène. Ce que l'exemple ne peut pas dire se déclare dans ces fichiers :

- `geography.RETOUCH` : la trouée du nord, les anses sous les escaliers, de
  quoi poser les maisons, la mer sous les pontons de l'exemple ;
- `layout` : `HOUSES`, `PLAZA`, `STAIRS`, `DOCKS`, `PATHS` (les pistes qui
  mènent aux portes, aux escaliers, aux pontons), `TALL` ;
- `generate` : chaque panneau, lampadaire, banc, personnage a une case
  **souhaitée** ; `settle` et `stand` prennent la plus proche qui ne gêne pas
  — ni devant une porte ou un escalier, ni sur un ponton, ni dans un passage
  étroit, ni derrière un arbre.

Le générateur contrôle, dans les trois temps de l'histoire (avant, pendant,
après la Veillée), que chaque lieu se rejoint à pied, que le tour du coureur
est libre et que le bord de la carte ne s'atteint qu'à la trouée du nord.

`tests/run.sh island` : circulation (les trois niveaux, escaliers, pontons,
maisons, place, tout se rejoint, le décor ferme la carte), portes, objets à
ramasser, la quête en trois temps, l'indice de Roland, et le vol des oiseaux.

## La Route 1

`scenes/levels/route_1.tscn` — 69 × 50 cases, au nord de l'île. On y entre
par la trouée de la falaise de l'île (ses six cases `Nord0`…`Nord5`), et l'on
arrive au bas de la carte, en (44–46, 48), par les portes `Sud0`…`Sud2`.

**Elle reproduit, tuile pour tuile, une carte d'exemple fournie par Ludovic**
(17/11/2026). L'exemple est fait des tuiles de `sources/town_compilation.png` :
elles ont été retrouvées une à une, au pixel près, et la carte est posée avec
**ces tuiles-là** (`route.png`, source 11 — [tilesets.md](tilesets.md)).
`generate.py --compare` le mesure : **3372 cases sur 3450 sont identiques à
l'exemple**, pixel pour pixel. Les 78 autres :

- **la trouée du sud**, que l'exemple n'a pas — il faut bien arriver de l'île :
  un couloir de piste de trois cases (44–46, 46–49) ouvert dans la forêt, et
  les arbres qui le bordent ;
- **les objets du jeu** à la place de ceux de l'exemple : nos panneaux, nos
  Poké Balls à ramasser ;
- **l'ombre des sapins et de l'arbuste, dessinée en entier** : sur la planche
  elle déborde d'une rangée de pixels sous leur pied, que l'exemple coupe
  21 fois sur 24. Le jeu la dessine partout ;
- **quatre arbres ramenés à ce qu'est un arbre** (12 cases) : l'exemple en
  fait trois de deux essences — la cime de l'une sur le pied de l'autre — et
  pose deux fois le pied d'un quatrième, dont l'ombre est double. Dans le jeu
  un arbre a une seule teinte, celle de sa cime, et une seule ombre : à deux
  teintes, il a l'air d'une erreur (Ludovic, 17/11/2026) ;
- une dizaine de cases de détail que la planche n'explique pas : un rocher
  coupé par le bord du bas, le panneau de l'exemple, quelques pixels sous un
  arbre.

Trois choses que l'exemple cache sous un arbre ou un rocher sont **complétées**,
et non devinées : le bout du bas des rebords tournés vers l'est (c'est leur
bout du haut retourné — ce qu'on en voit le confirme au pixel), le bord de
falaise sous le bloc brun de (55, 18), la piste sous l'ombre du sapin de
(52, 30).

```
 forêt ─ sortie du NORD (fermée) ─ forêt │ rivière │   bras du nord-est   │ falaises
 terre du NORD-OUEST : clairières,       │    ~    │ forêt                │ LA MONTAGNE :
 hautes herbes, piste, REBORD            │    ~    │                      │ gradins de roche
 ════════ le bras de l'ouest ═══ PONT ═══╡    ~    │ HAUTES TERRES : herbes, deux escaliers
 terre du SUD-OUEST : forêt,             │    ~    │ pelouse, piste ───── sortie de l'EST (fermée)
 hautes herbes, piste ─────── PONT ──────┼─────────┤ forêt, hautes herbes, le bosquet fermé
 forêt                                   │    ~    │ forêt ─ trouée du SUD (vers l'île) ─ forêt
```

**Les terres sont en hauteur, et l'on n'atteint jamais l'eau.** Chaque terre
est cernée d'une **falaise à deux étages**, deux anneaux l'un dans l'autre :
la roche d'abord (`Cliffs1`), qui tombe dans la rivière, puis l'herbe
(`Cliffs2`), une case en retrait. Les plateaux du dessus et les gradins de la
montagne sont d'autres anneaux, posés par-dessus (`Cliffs3`). Une case
d'anneau bloque, **sauf les deux coins rentrants du haut de l'anneau d'herbe**
(`grassk`, `grassl`) : ce sont de la pelouse du plateau, avec un bout de
lisière dans leurs quatre rangées du haut, et ils ne touchent le vide que par
leur pointe — on s'y tient, on n'en tombe pas (ainsi (36, 33), au bout du pont
de l'est). Un test le contrôle : aucune case foulée ne touche l'eau ni le
sable, hors des ponts.

**L'eau a deux teintes** : claire au pied des falaises, profonde au milieu du
lit, la seconde fondue dans la première par les bords de son bloc. **Un
liseré de sable court au pied de chaque falaise** : le sable est sous l'anneau
de roche, et son bord ondule dans la case d'eau voisine.

**Dans l'eau, 40 rochers gris cernés d'écume**, aux places exactes de ceux de
l'exemple : 11 gros, 8 pointus, 21 petits. Rien d'autre ne dépasse de la
rivière.

**Les deux ponts font trois cases de large** et passent par-dessus les
falaises : x 14–16, y 18–29, et x 24–35, y 35–37. Ce sont les planches de
l'exemple, sans rambarde : le tablier bloque de lui-même, l'eau et les
falaises de part et d'autre étant pleines. Dessous, l'eau prend sa **variante
sans collision**.

**La forêt** : 312 arbres en quinconce — un arbre toutes les **quatre**
colonnes, la rangée suivante décalée de deux, une rangée par case
([mapping.md](mapping.md)). Un arbre bloque **ses deux rangées du bas sur ses
trois cases** : le tronc, et la cime qui retombe de chaque côté. On passe
derrière le haut de la cime.

**Les rebords de roche se sautent, dans un seul sens** : du haut vers le bas
de leur marche, là où tombe leur ombre ([player.md](player.md)). On retombe
une case plus loin ; dans l'autre sens ils arrêtent.

| Rebord (`Ledges`) | Se saute vers | Ce que ça donne |
|---|---|---|
| (15–17, 8) | le sud | le raccourci du retour sur la piste du nord ; à l'aller, on fait le tour par les hautes herbes de l'ouest |
| (18, 31–33) | l'est | |
| (46, 35–38), (54, 35–38) | l'est | la route de l'est se descend d'un trait ; on la remonte par les escaliers et les hautes terres |
| (52, 44–45) | l'ouest | une sortie du bosquet de l'Antidote, pas une entrée |

**Une chose de l'exemple que le jeu ne sait pas encore faire**, et qui ferme
donc un passage :

- l'**arbuste** de (61, 41) est un arbre à couper. Le bosquet qu'il garde
  (x 53–62, y 42–46) ne s'atteint donc pas — et **la seconde Poké Ball de
  l'exemple y reste**, en (58, 45) : c'est l'Antidote, la récompense de qui
  reviendra couper l'arbuste (Ludovic, 17/11/2026). Le générateur le vérifie
  dans les deux sens : hors d'atteinte aujourd'hui, à portée l'arbuste ôté.
  Examiné, il dit ce que disent les jeux d'origine — « Cet arbre semble
  pouvoir être coupé ! » (`Readables/CutTree0`, que le générateur pose sur
  chaque arbuste).

| Lieu | Case | |
|---|---|---|
| arrivée de l'île | (45,48) | `SpawnPoint` ; portes `Sud0`…`Sud2` en (44–46,49) |
| sortie du nord | (14–16,0) | fermée : trois `Readables/RoadEndNorth…` ; un dallage en chevrons la marque |
| sortie de l'est | (68,35–37) | fermée : trois `Readables/RoadEndEast…` |
| les hautes terres | x 48–62, y 21–33 | deux escaliers de pierre : marches en (50–52,34) et (56–58,33), un poteau de chaque côté |
| la montagne | x 49–68, y 3–25 | des gradins de roche emboîtés, quatre blocs bruns ; pleine |
| objets à ramasser | Potion (20,11), Antidote (58,45, derrière l'arbuste), Poké Ball (6,8), Super Potion (61,25) | la Potion est à la place exacte d'une Poké Ball de l'exemple ; aucun n'est posé sur une case qu'un arbre recouvre, ni derrière une cime qui le cacherait |
| personnages | campeur (18,38), fillette (9,36), pique-niqueuse (49,29), gamin (18,11), chasseur d'insectes dans les herbes du sud-est — ni pêcheur ni montagnard dans une forêt | leurs cases sont choisies par le générateur : hors piste, hors herbes, sans gêner un passage |

Calques de fond, dans l'ordre : `Ground`, `Cliffs1`, `Cliffs2`, `Cliffs3`,
`Paths` (contour des pistes, dallage), `Decorations` (fleurs), `Grass`,
`Ledges`, `Bridges` (ponts et escaliers). Dans `World`, triés en Y : `Trees`,
`Props` (sapins, arbuste, rochers).

**Dans le ciel**, dix Pokémon que le vent porte d'ouest en est, par groupes de
deux ou trois : trois Granivol, deux Floravol, trois Cotovol, deux Granivol
(nœud `Sky`, [npcs.md](npcs.md)). Pas d'oiseaux de mer au-dessus d'une forêt.

**Dans les herbes**, une rencontre a 3 chances sur 100 par pas marché, 5 par
pas couru ([encounters.md](encounters.md)).

Elle n'a pas de musique à elle : elle garde celle de l'île, en attendant une
musique de route.

### Elle est produite par un générateur, à partir d'un relevé

Le générateur est dans le dépôt, `tools/maps/route_1/` :

| Fichier | Rôle |
|---|---|
| `reference.png` | la carte d'exemple |
| `survey.py` | le **relevé par tuiles** : retrouve dans l'exemple chaque tuile de `route.png`, couche par couche, et écrit `survey.json`. Dit combien de cases il reconstitue au pixel près (3418 sur 3450) |
| `survey.json` | le relevé : sol, anneaux de falaise, décors, rebords, escaliers, ponts de chaque case ; ce qui est debout (arbres, rochers), par son pied |
| `layout.py` | pose chaque tuile relevée dans son calque, ouvre la trouée du sud, devine le sol que l'exemple cache, calcule ce qui bloque |
| `generate.py` | pose objets, personnages et portes, **contrôle**, écrit la scène et les sources 11 à 13 du TileSet |

```bash
python3 tools/route_tiles.py                                # la planche route.png (puis réimporter)
python3 tools/maps/route_1/survey.py                    # le relevé -> survey.json
python3 tools/maps/route_1/survey.py --why=46,38        # ce qui est trouvé sur une case, et les pixels inexpliqués
python3 tools/maps/route_1/generate.py                  # contrôle seulement
python3 tools/maps/route_1/generate.py --write          # écrit la scène et le TileSet
python3 tools/maps/route_1/generate.py --compare        # les cases qui diffèrent de l'exemple
python3 tools/maps/route_1/generate.py --preview a.png  # la carte sans passer par Godot
```

Il contrôle avant d'écrire : toute tuile posée est déclarée ; chaque lieu,
chaque marche d'escalier est atteignable depuis la trouée du sud ; aucune case
du bord ne l'est hors des trouées ; aucun personnage immobile ne gêne un
passage. **Relancer le générateur écrase la scène** : une retouche faite dans
l'éditeur se refait dans le générateur. La grille de collisions du moteur a
été comparée à celle du plan, case par case : elles sont identiques. Le rendu
du moteur a été comparé à l'exemple de la même façon.

**Comment le relevé procède** — c'est la méthode à reprendre pour toute carte
d'exemple dont on a la planche ([mapping.md](mapping.md)) : il épluche la carte
du dessus vers le dessous. D'abord ce qui est debout, rangée par rangée, de
l'avant vers l'arrière (un arbre cache le pied de celui de derrière) ; puis
ponts, escaliers, rebords, décors au sol ; puis jusqu'à trois anneaux de
falaise ; enfin le sol. Une tuile n'est retenue que si **tous** ses pixels
encore visibles sont ceux de l'exemple — sous une ombre translucide, assombris
d'autant. La carte est ensuite recomposée et comparée à l'exemple : ce qui
diffère est ce que la planche n'a pas, et se découpe dans l'exemple lui-même.

`tests/run.sh route` : circulation, portes dans les deux sens, objets, un
dialogue.

L'ancienne version de la route, faite des tuiles de l'atlas, n'est plus dans
le dépôt.

## Les intérieurs

Six cartes : quatre pour la maison de Ludo (salon et chambre), la bibliothèque
et le laboratoire, deux pour les maisons orange. Leurs sorties mènent toutes à
**l'île** (`start_island`), sur des portes de même nom.

| Bâtiment | Carte |
|---|---|
| **Chez Ludo** | `ludo_house` (salon) + `ludo_bedroom` (étage) |
| **la bibliothèque** | `library`, de plain-pied — plan dans [quests.md](quests.md) |
| **le laboratoire**, à la Poké Ball | `lab_house` |

Le paillasson de chacune
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
