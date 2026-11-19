# Le joueur

`scenes/characters/player.tscn`, instancié dans `World/Entities` de chaque map.

```
Player (CharacterBody2D)     Player.kt — assemble les composants
├── Sprite (AnimatedSprite2D)  CharacterAnimation.kt
├── Collider (CollisionShape2D)
├── Camera (Camera2D)          PlayerCamera.kt
├── Input (Node)               PlayerInput.kt
└── Movement (Node)            CharacterMovement.kt
```

Trois composants indépendants, assemblés par `Player.kt` : l'entrée ne connaît
pas le déplacement, le déplacement ne connaît pas l'animation.

Pas de machine à états : une boîte de dialogue ouverte se contente de
court-circuiter le déplacement dans `Player._process`. Elle s'imposera le jour
où un troisième mode apparaîtra (combat, menu).

`Player` lit aussi la touche `interact` — et il est le **seul** à la lire, y
compris pour faire avancer un dialogue. La raison est dans
[dialogue.md](dialogue.md).

## Repère et échelle

L'origine du joueur est le **centre de sa case**, soit `(col*16+8, row*16+8)`.
C'est différent du tutoriel, qui ancre au coin haut-gauche — la raison tient au
tri Y et est expliquée dans [architecture.md](architecture.md).

Le sprite source fait 32×48, mais il est rendu à **`scale = 0.5`**, donc 16×24 :
une case de large, une case et demie de haut. Sans cette mise à l'échelle le
personnage est deux fois trop gros pour le décor. Son décalage `(0, -4)` place
ses pieds au bas de la case.

Caméra en `zoom = 4` — l'écran est en **4:3**, 1280×960 (`[display]` dans
`project.godot`, et le `SubViewport` de `game_manager.tscn`) : on voit
**20 cases de large et 15 de haut**, soit 320×240 pixels de jeu. Rester sur un
zoom **entier** : un zoom fractionnaire donne des pixels de largeurs inégales
qui scintillent en marchant.

Elle est bornée à **l'étendue de la carte** (`PlayerCamera.contentRect`) : le
sol de `Background/Ground` sans son noir de remplissage, plus les autres
calques du fond (les murs dépassent du sol). Rien à régler quand la map change
de taille.

- Carte plus grande que l'écran : la caméra suit le joueur et s'arrête aux bords.
- Carte **plus petite que l'écran** sur un axe (une pièce d'intérieur) : elle
  est **centrée** sur cet axe et la caméra n'y bouge plus
  (`tests/run.sh room_centered`). Le noir de remplissage — la tuile `5:65,49`
  de `Ground` — sert alors de bordure autour de la pièce ; il doit couvrir tout
  l'écran, sinon on voit le gris de fond.

L'interface est dessinée ×4 dans ces 1280×960. Boîte de dialogue, nom, Oui/Non,
menu de pause et objet reçu sont **ancrés** : la boîte de dialogue en bas, d'un
bord à l'autre, le nom et Oui/Non sur ses bords gauche et droit (voir
[dialogue.md](dialogue.md)), le menu de pause au bord droit, l'objet reçu en
bas au centre ; le sac et le Pokédex tiennent tout l'écran ; les options et la
vue de debug du Pokédex gardent leur planche de 1152×648, centrée sur un fond
uni.

## Déplacement

Case par case, et **un pas engagé va toujours jusqu'au bout** : l'entrée n'est
lue qu'entre deux pas, sinon le personnage s'arrête entre deux cases.

Le ressenti Pokémon vient du seuil de maintien (`holdThreshold`, 0,12 s) :

- pression brève → le personnage **pivote** sans avancer ;
- pression maintenue → il **marche**, et enchaîne tant que la touche est tenue.

**Deux directions tenues : la dernière pressée commande.** On tient Haut, on
presse Gauche : on va à gauche ; on relâche Gauche, Haut reprend la main.
Aucune direction n'a priorité sur une autre (`PlayerInput.heldDirection`). Un
ordre fixe — Haut, Bas, Gauche, Droite — a existé : Haut et Bas l'emportaient
toujours, et Gauche / Droite étaient ignorées tant qu'on tenait l'une d'elles.

Vitesse : `walk_pace`, 4 cases par seconde.

### Courir

**Maj maintenue** (action `run` de `project.godot`) : le personnage va à
`run_pace`, 8 cases par seconde, deux fois l'allure de la marche.

- L'allure se décide **au départ de chaque pas** : un pas engagé va au bout à
  l'allure où il a commencé, et relâcher Maj fait marcher dès le pas suivant.
- La touche seule ne fait rien : il faut une direction. Le pivot sur place
  (pression brève) ne change pas.
- **Le joueur a une pose de course** : `run_sheet` (`playable/renko_run.png`),
  une planche au découpage de la marche, chargée au démarrage en animations
  `run_<direction>`. Elle remplace la marche tant qu'il court, et tourne deux
  fois plus vite (`speed_scale = 2`). `run_sheet` vide, ou un PNJ sans planche
  de course : c'est la marche qui s'accélère.
- Une scène qui déplace le joueur le fait au pas : repoussé par un garde alors
  qu'il arrivait en courant, il recule en marchant.

On court partout, intérieurs compris.

## Sauter un rebord

Un rebord de roche est une **case pleine** : on ne s'y tient jamais. Mais
quand le joueur avance vers lui dans le sens de sa marche — du haut vers le
bas, là où tombe son ombre — il le **saute** et retombe une case plus loin.

- `CharacterMovement.tryJump(direction)`, appelé par `Player` quand
  `tryWalk` a refusé le pas. Il réussit si la case voisine porte, dans un
  calque de `Background`, une tuile dont la donnée `jump` du TileSet vaut
  cette direction ([tilesets.md](tilesets.md)), et si la case d'après est
  libre. Elle est réservée comme pour un pas.
- Le saut est **un pas de deux cases**, qu'on n'interrompt pas, à son allure
  à lui : 5 cases par seconde, soit 0,4 s, qu'on arrive au pas ou en courant.
- **C'est l'image qui monte**, en cloche, jusqu'à 8 px (`lift`) ; le nœud du
  joueur reste au sol, où sont son tri en Y et sa caméra.
- **Son ombre reste au sol** le temps du saut (`JumpShadow` dans
  `player.tscn`, la même tache que sous un Pokémon volant) : c'est elle qui
  dit qu'il est en l'air. Hors saut on ne la voit pas.
- **Le saut s'entend** à l'instant où il part (`sfx/jump`), à la place du choc
  qu'on aurait eu contre un mur.
- Dans l'autre sens, par le bout ou sans place pour retomber : pas de saut,
  on bute comme sur un mur.
- **Seul le joueur saute.** Un PNJ s'arrête devant un rebord.
- En retombant on s'est posé sur une case : une rencontre peut s'y tirer,
  une porte s'y déclencher, comme après un pas.

Pour qu'une tuile se saute : lui donner la donnée `jump` et une collision
pleine. Sur la Route 1 c'est le générateur qui l'écrit.
`tests/run.sh route_ledges`.

## Glisser sur le verglas

Sur une case de verglas on ne s'arrête pas : on **glisse tout droit**, sans que
les touches comptent, jusqu'à **buter** — une paroi, un caillou, un personnage
— ou jusqu'à **la première case qui n'est plus du verglas**. Contre un obstacle
on est arrêté *sur* le verglas, et l'on repart de là dans le sens qu'on veut.

**C'est porté de Pokémon SDK** (`Game_Character`, dans
`scripts/4 Systems/003 Map Engine/2 Logic/50 RMXP/` de
gitlab.com/pokemonsdk/pokemonsdk, version 26.62), en gardant ses méthodes et
leurs noms, dans `CharacterMovement.kt` :

| PSDK | Chez nous | Ce que ça fait |
|---|---|---|
| `@sliding` | `isSliding` | vrai tant qu'on glisse |
| `movement_process_end` | `movementProcessEnd()` | au **départ** d'un pas : si la case où il mène est du verglas, on glisse — dès ce pas-ci |
| `update_sliding` | `updateSliding()` | un pas fini, on en refait un devant soi |
| `can_slide?` | `canSlide()` | tant qu'on se tient sur du verglas |
| `move_down`… qui échoue : `@sliding = false` | `tryWalk` refusé | la case de devant ne se passe pas : la glissade est finie |
| `stop_slide` | `stopSlide()` | on n'est plus sur du verglas : finie aussi |
| `@no_slide` | `no_slide` (export) | ce personnage marche sur le verglas comme ailleurs |
| `:begin_slide`, `:end_slide` | — | deux événements que PSDK émet et que rien n'écoute chez lui : pas de son, pas de particules. Rien chez nous non plus |

- **Les jambes ne bougent pas**, du pas qui entre sur le verglas au pas qui en
  sort (PSDK fige `@pattern`) : `Player` et `Npc` passent `false` à
  `CharacterAnimation.refresh` tant que `isSliding`.
- **Pas d'allure à part** : on garde celle du pas qui a fait entrer, marche ou
  course.
- **Tant qu'on glisse, rien n'est lu ni déclenché** : ni direction, ni menu,
  ni interaction, ni passage gardé, ni rencontre. Tout reprend à l'arrêt, sur
  la case où l'on s'est posé.
- **Tout le monde glisse** : le joueur, un PNJ (`Npc` ne décide de rien tant
  qu'il glisse), et le Pokémon qui suit, puisqu'il refait les pas du joueur.
  Un PNJ marqué `no_slide` marche sur le verglas (le `[noslide=on]` de PSDK).
- **Ce qui est du verglas se déclare dans le TileSet** : la donnée perso `ice`
  ([tilesets.md](tilesets.md)). Rien n'est codé en dur.

Trois écarts voulus :

- PSDK fait glisser « en avant », dans le sens où le personnage **regarde** ;
  nous dans le sens de son **dernier pas** (`heading`). C'est pareil en
  marchant, et juste pour un personnage qu'une scène fait reculer.
- **Quel calque dit que c'est du verglas.** Chez PSDK (`Game_Map#system_tag`)
  c'est le premier calque, en partant du haut, qui porte **un tag** : une
  tuile sans tag posée sur la glace ne change rien, et il faut la tuile
  `StopSlide` pour arrêter. Chez nous c'est **le calque de sol le plus haut**,
  tagué ou non — la règle qu'ont déjà le sable et l'eau : une tuile à plat
  posée sur le verglas (une crevasse, une passerelle) arrête, sans tuile à
  part.
- **Le Pokémon qui suit** n'a pas de déplacement à lui : il refait les pas du
  joueur, et fige son image tant que **le joueur** glisse, pas quand lui-même
  est sur la glace (une case d'écart).

Conséquence pour les cartes : sur le verglas, **atteindre n'est plus
réciproque** — on peut traverser une plaque dans un sens et pas dans l'autre,
ou s'y retrouver coincé. Le constructeur et le contrôleur en tiennent compte
([mapping.md](mapping.md), « Grotte »).

`tests/run.sh moves/ice_slide`, sur la glacière (`tests/maps/ice.tscn`) : le
joueur, le suiveur et un PNJ. Les chemins des tests sont faits des cases où
l'on s'arrête (`tests/lib.gd`, `glide`).

## Les traces de pas

Sur le sable, un personnage — le joueur comme un PNJ — laisse derrière lui une
**paire d'empreintes par case quittée** : un pied de chaque côté de sa
trajectoire, l'un devançant l'autre. Le pied qui mène change à chaque pas,
d'où le zigzag. En courant, les paires se suivent deux fois plus vite.

- C'est le nœud `Steps` (`Footprints.kt`), enfant du personnage comme `Grass`.
- Une empreinte n'a pas de couleur à elle : elle **assombrit le sable de 26 %**,
  ce qui va sur la plage sèche comme sur le rivage mouillé. Elle garde cette
  force la moitié de sa vie, puis s'efface — **1 s en tout** (`darkness` et
  `life_seconds` sur le nœud) : à l'allure de la marche on voit quatre paires
  derrière soi, pas davantage. Un fondu dès le premier instant rendait pâles
  les traces juste derrière le personnage, celles qu'on regarde.
- Chaque empreinte vit sa vie seule (`Footprint.kt`) : on peut repartir, courir
  ou changer de carte, elles s'effacent quand même.
- Elles sont rangées dans un `Background/Footprints` créé au besoin par le
  premier personnage qui marche sur la carte, **juste au-dessus du calque du
  sol** : tout le reste du décor se dessine par-dessus.
- **Ce qui est du sable se déclare dans le TileSet**, une fois par tuile — la
  donnée perso `sand`, voir [tilesets.md](tilesets.md). Rien n'est codé en dur
  ici, et une serviette posée sur le sable ne garde pas de traces.
- La planche est `assets/levels/footprints.png`, fabriquée par
  `tools/footprint_tiles.py` : huit cases de 8 px, une par direction et par
  pied, dérivées d'une seule forme tournée et retournée.

`tests/run.sh moves/footprints` : le sable garde, l'herbe non, tout s'efface.

## Le reflet dans l'eau

Au bord de l'eau, un personnage s'y reflète **en temps réel** : le reflet
reprend à chaque frame l'image du moment — même pose, même direction, même
instant —, retournée, pâlie et tirée vers le bleu. Marcher, courir ou pivoter
se voit aussitôt dans l'eau.

- C'est le nœud `Mirror` (`Reflection.kt`), posé comme `Grass` et `Steps` ;
  le joueur et les PNJ en ont un. **Les Pokémon qui volent, non** : trop haut,
  et de l'un d'eux on ne voit déjà qu'une ombre — sur l'eau elle bleuit, c'est
  tout ([npcs.md](npcs.md)).
- Le reflet est le **miroir de la ligne où le personnage touche le sol**
  (`ground_offset` : ses pieds, soit 8 px sous son origine). `lift` le remonte
  de 5 px pour le coller aux pieds — le bas d'une image de personnage est
  transparent sur deux ou trois pixels, et le miroir double cet écart.
- Il n'apparaît que si **la case qui commence sous cette ligne est de l'eau**,
  ce que déclare la donnée perso `water` de la tuile
  ([tilesets.md](tilesets.md)) : au-dessus du sable ou d'un ponton, rien.
- Les reflets vivent dans un `Background/Reflections` créé au besoin, **juste
  au-dessus du calque d'eau**. Le sable, les pontons et le reste du décor se
  dessinant par-dessus, un reflet qui déborde sur le côté est recouvert sans
  qu'on ait à s'en occuper.
- **On ne montre du reflet que ce qui tombe dans l'eau** : on cherche la nappe
  d'eau sous la ligne de sol, et l'image est coupée à ses deux bords. C'est ce
  qui le fait **émerger au fil du pas** — en approchant du bord, le sommet de
  la tête sort le premier, puis le reflet remonte jusqu'aux pieds à mesure
  qu'on avance ; il n'apparaît jamais d'un bloc. À l'autre bout, au bord d'une
  eau basse (le sud de l'étang du terrain d'essai, une seule case sous les
  pieds), il s'arrête à la berge au lieu d'y baver.
- **En largeur aussi** : pendant un pas de côté le personnage est à cheval sur
  deux colonnes, dont l'une peut être du sable. Le reflet ne garde que les
  colonnes où il y a de l'eau, et la hauteur qu'elles ont en commun
  (`waterPool`).
- Il **balance d'un pixel** au rythme des rides de l'eau (quatre crans par
  seconde, comme `water.gdshader`), de quoi ne pas avoir l'air collé.

`tests/run.sh visuals/reflection` : au bord de l'eau oui, sur le sable non.

## Collisions

Le joueur interroge la case visée avec `intersect_point` sur le **masque 1**,
celui des tuiles. Il est lui-même sur le **calque 2**, pour ne jamais se
détecter lui-même — c'est plus simple que d'exclure son propre corps de la
requête.

Rien n'est codé en dur : si une tuile bloque, c'est qu'elle a un polygone de
collision dans `level.tres`. Voir [tilesets.md](tilesets.md).

## Animations

`resources/spriteframes/player.tres`, nommées `<etat>_<direction>`.

Les rangées du sprite sheet sont, dans l'ordre : **bas, gauche, droite, haut**.
C'est contre-intuitif à l'œil — vérifier au rendu avant de corriger quoi que ce
soit, l'ordre a déjà été remis à l'endroit une fois.

Un demi-tour sur place joue `turn_<direction>` : deux images, une image de pas
puis l'image fixe, en 0,2 s. C'est le petit à-coup des jeux d'origine quand on
pivote sans avancer. L'animation ne boucle pas, et `refresh()` la laisse aller
au bout avant de retomber sur l'`idle_*` — sans ça elle serait écrasée dès la
frame suivante.


## Le Pokémon qui suit

`scenes/characters/follower.tscn` (`Follower.kt`) : un Pokémon marche **une
case derrière le joueur**, sur la case qu'il vient de quitter, à son allure —
après un saut de rebord il rattrape les deux cases dans le temps du saut.
Arrêté, il regarde le joueur, et **continue de s'animer sur place**, comme
dans les jeux d'origine. Il n'a pas de corps : il n'arrête personne, et
le joueur qui rebrousse chemin passe à travers lui.

`SceneManager` le pose avec le joueur dans `World/Entities` à chaque carte,
sur la case du joueur et caché : il apparaît au premier pas. Si le joueur est
posé ailleurs sans marcher (une scène), il se range de nouveau.

Son espèce est `follower_species` du `SceneManager` (`wingull` pour l'instant ;
vide : personne ne suit) — ce sera le premier Pokémon de l'équipe. Son image
est le fichier de l'espèce, lu par `PokemonFrames` ([npcs.md](npcs.md)) :
n'importe quelle espèce découpée peut suivre, sans fichier de plus.

Pour savoir quand bouger, il lit dans le `CharacterMovement` du joueur le
nombre de pas engagés (`steps`), la place d'où part le dernier (`origin`) et
son allure (`paceNow`). `tests/run.sh follower`.

## Changement de carte

Le joueur n'appartient à aucune carte : `SceneManager` le reparente. À
l'arrivée son pas est annulé, il est orienté dos à la porte et une nouvelle
pression est exigée avant de bouger — le détail et les raisons sont dans
[levels.md](levels.md).
