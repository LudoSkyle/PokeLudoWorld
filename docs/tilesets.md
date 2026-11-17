# Tuiles, collisions et terrains

## Le principe

`resources/tilesets/level.tres` est **le** TileSet du jeu. Tout y est déclaré
par coordonnée d'atlas, jamais par position sur une map :

```
49:27/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
49:27/0/y_sort_origin = 8
```

`49:27` désigne la tuile dans l'atlas. Elle arrive avec sa collision partout où
on la pose, dans cette map comme dans les suivantes.

**Corollaire : ne pose jamais un `StaticBody2D` à la main sur une map pour
bloquer un décor.** Si une tuile ne bloque pas, c'est sa déclaration qu'il faut
corriger, une fois, pour tout le projet.

## L'atlas

`assets/levels/environments.png` — 1504 × 2273, tuiles de 16 × 16, `margins (1,1)`,
pas de séparation. Deux sources :

| Source | Nom | Contenu |
|---|---|---|
| `5` | `environments` | tuiles 1×1 (sol, chemins, maisons, décors, falaises) |
| `6` | `border_environments` | grosses tuiles 3×3 et 3×4 (arbres) |
| `7` | `interiors` | meubles d'intérieur recalés sur la grille — voir [levels.md](levels.md) |
| `8` | `cave` | la roche de grotte nettoyée — voir [levels.md](levels.md) |
| `9` | `grass_front` | le bas des touffes de hautes herbes, par bandes de 16×4 — voir plus bas |

**Les grosses tuiles sont centrées sur leur case d'ancrage**, pas ancrées en
haut à gauche. Une tuile 3×3 posée en `(x, y)` couvre `x-1..x+1` et `y-1..y+1`.
C'est vrai pour le dessin, pour le polygone de collision et pour le point de
tri — tous partagent le même repère local, centré sur la case d'ancrage.
Vérifié par rendu comparé ; se tromper là-dessus décale tout de 16 px.

Deux autres sources complètent l'atlas principal : `7`, les meubles recalés
(`interiors.png`), et `8`, la roche de grotte nettoyée (`cave.png`) — voir
[levels.md](levels.md).

## Prendre un élément dans une planche source

`assets/levels/sources/` garde les planches téléchargées **telles quelles**
(inventaire et auteurs : `assets/levels/CREDITS.md`). Godot ignore ce dossier,
et **le TileSet ne s'y branche jamais**. Ce sont des planches de présentation :
fond opaque, éléments posés librement sur la page, hors de toute grille.
`environments.png` est justement une sélection de ces planches déjà recalée.

Quand une carte a besoin d'un élément qui n'est pas dans les planches du jeu :

1. **Le sortir à part.** On ne retouche pas `environments.png` à la main : les
   éléments extraits vont dans une planche recomposée, une par thème, dans
   `assets/levels/`, produite par un script à partir d'une liste « source,
   rectangle → case de destination » — de quoi la régénérer.
2. **Le détourer.** Le fond des planches « Dawn » est un blanc pur, uniforme,
   sans pixels intermédiaires au bord des dessins : on l'enlève en partant de
   l'extérieur de l'élément, pas en supprimant tout le blanc. Il reste
   quelques pixels blancs enfermés dans le dessin (0,3 à 0,7 % du blanc) : ou
   bien du vrai blanc (neige, reflet), ou bien un trou à vider (entre deux
   barreaux). **Zoomer et trancher**, pièce par pièce.
3. **Le recaler** sur la grille de 16, pieds en bas de case.
4. **Le créditer** dans `CREDITS.md`.

**Les collisions se posent au fil du besoin** : seulement pour les tuiles
qu'une carte utilise vraiment, au moment où on les pose. On ne cartographie pas
une planche entière d'avance.

## Couche physique

Une seule : `physics_layer_0/collision_layer = 1`. Le polygone standard pour une
tuile 1×1 pleine :

```
PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
```

Les cas particuliers en place :

| Tuiles | Collision |
|---|---|
| Arbres de bordure 3×3 | les **deux rangées basses** (48×32) |
| Arbre isolé 3×4 | la **rangée du pied**, sur les 3 cases de large |
| Maisons | pleine, **sauf** les tuiles opaques à moins de 25 % |
| Bouche de grotte `5:33,23` | **aucune** — c'est l'entrée |
| Eau profonde (`5:5,34`, `5:6,34`, `5:6,35`) | pleine |
| Eau claire `5:9,31` et plantes `5:13,32` | **aucune** — faible profondeur |
| Bancs blancs `5:74,25`, `5:75,25` (plus posés sur l'île : elle a ses bancs de bois, source 10) | pleine |
| Dallage de la place `5:5-7,47-49` | aucune |
| Trait de côte, sable, chemins, herbes hautes, décors | aucune |

Trois de ces règles viennent d'une partie de test, et valent d'être comprises
plutôt que recopiées :

- **La rangée haute d'un arbre 3×3 ne bloque pas.** Les arbres sont posés
  toutes les deux cases, donc leurs collisions se chevauchent : bloquer les
  trois rangées rendait infranchissable une rangée d'herbe visible à l'écran.
  On peut désormais marcher derrière la cime, ce qui est le rendu attendu.
- **L'arbre isolé bloque sa rangée de pied, pas la case du dessous.** On doit
  pouvoir se tenir sous l'arbre, devant le tronc ; ce qu'il faut interdire,
  c'est de remonter d'une case, des deux côtés comme au milieu. Le polygone
  couvre donc toute la largeur de la cime sur la seule rangée du pied.
- **Une tuile de maison quasi transparente est du sol.** Les trois tuiles de
  la façade du Centre Pokémon (`5:99`, `6:99`, `7:99`, opaques à 19 %, 19 % et
  4 %) ne montrent que de l'herbe : les bloquer interdisait trois cases qui
  n'ont rien d'un mur. **Mesurer l'opacité avant de déclarer une collision.**
  Ces trois-là portent en plus `y_sort_origin = -8` : ce sliver appartient
  visuellement à la rangée du dessus, et sans ça il coupait la tête du joueur
  qui se tient devant.

## Décor franchissable : trier depuis le haut de la case

**Toute tuile 1×1 d'un calque de `World` posée sur une case franchissable doit
porter `y_sort_origin = -15`.** Sinon elle se dessine par-dessus le joueur qui
s'y tient.

La valeur n'est pas arbitraire : elle place le point de tri de la tuile **1 px
sous celui du joueur de la rangée du dessus**. Les trois comportements attendus
sont alors satisfaits — joueur au-dessus : tuile devant ; joueur sur la case ou
en dessous : joueur devant.

Pourquoi pas `-8`, le bord haut de la case ? Parce que le tri utilise la
position **interpolée** pendant un pas. À `-8` la bascule tombe au milieu du
pas : en entrant dans la case par le haut, la tuile recouvrait brièvement les
jambes du joueur. À `-15` elle tombe après 1 px sur 16, soit une frame.

Les six cases concernées aujourd'hui, à recalculer après toute modification de
collision :

| Tuile | Cases |
|---|---|
| `5:13,32` plantes aquatiques | (39,16) (40,18) |
| `5:5,99` `5:6,99` `5:7,99` façade | (31,7) (32,7) (33,7) |
| `5:33,23` bouche de grotte | (38,2) |

La liste se recalcule : croiser les cases non solides mesurées en jeu avec les
cases couvertes par `Cliffs`, `Props` et `Houses`. Les grosses tuiles d'arbres
sont exclues — là on veut justement passer derrière.

## Les hautes herbes

Comme dans les jeux d'origine, une case de hautes herbes est faite de **deux
tuiles superposées** :

| Calque | Tuile | Rôle |
|---|---|---|
| `Background/Grass` | `5:6,0`, la touffe entière | dessinée **sous** les personnages |
| `World/GrassFront` | `9:6,0`, ses 4 pixels du bas | dessinée **par-dessus** celui qui se tient sur la case |

Le personnage a ainsi l'air d'être dans l'herbe jusqu'à la taille. **Les deux
tuiles sont fixées à la case** : rien n'est attaché au personnage, donc rien ne
le suit quand il marche.

- **On ne peint que `Background/Grass`**, avec la touffe `5:6,0`. Le calque de
  devant est créé au chargement, sur les mêmes cases (`TallGrass.kt`).
- La source `9` (`grass_front`) lit le même atlas par bandes de 16×4 : sa tuile
  `x,0` est le bas de la tuile `5:x,0`. Elle est décalée au bas de la case
  (`texture_origin`) et **triée en Y à 2 px sous le centre** (`y_sort_origin`) :
  devant le personnage de sa case, derrière la tête de celui de la case du
  dessous.
- **Pourquoi 2 et pas plus.** Le tri se fait sur la position pendant le pas.
  Un personnage qui monte vers une case d'herbe passe derrière sa bande dès
  qu'il est à moins de `y_sort_origin` pixels de l'arrivée. À 7, la bande lui
  barrait la taille à mi-pas puis descendait le long des jambes ; à 2, elle
  n'apparaît que sur les pieds, à la toute fin du pas.
- 4 pixels, parce que les personnages en font une quinzaine de haut : avec 8,
  on ne voyait plus que leur tête.

La touffe a trois états, côte à côte dans l'atlas : `6` dressée, `7` qui
s'écarte, `8` écartée. Quand un personnage entre sur une case, elle **bruisse
sur place** : ses deux tuiles passent par `7, 8, 8, 7` puis reviennent à `6`
(0,07 s par état). À l'arrêt l'herbe est normale. Touche tenue, les cases
qu'on vient de quitter bruissent encore derrière soi.

C'est le composant `TallGrass.kt`, un nœud `Grass` du joueur comme de chaque
PNJ : rien à régler par carte, il suffit que le calque s'appelle
`Background/Grass`.

**Une planche qui a ses propres hautes herbes** apporte sa paire de sources,
rangées de la même façon — les trois états aux colonnes 6, 7, 8 de la rangée
0 — et s'ajoute à `FRONTS` dans `TallGrass.kt`. La route du nord a les
siennes (`12` et `13`, voir « Les terrains de la route du nord »).

Deux essais écartés, pour mémoire : un cache d'herbe attaché au personnage (il
glisse sur l'herbe pendant le pas), et la touffe qui reste couchée tant qu'on
est dessus, comme dans le projet de référence (le personnage n'a plus l'air
d'être dans l'herbe). Ce projet tire aussi, au même endroit, la chance d'une
rencontre quand le joueur entre : chez nous c'est `WildEncounters`, voir
[encounters.md](encounters.md).

Le même calque sert de zone d'errance à un PNJ ([npcs.md](npcs.md)).

## Le sable qui garde les pas

Une tuile de sable porte la donnée perso **`sand`** — la première des deux
couches de données du TileSet (`custom_data_layer_0`, type booléen) :

```
11:14/0/custom_data_0 = true
```

Les 26 tuiles qui la portent sont celles de la plage (`5:10-12,13-15` et ses
coins rentrants `5:13-14,13-14`) et du rivage (`5:15-17,31-33`, coins
`5:18-19,31-32`) : les deux blocs de « Les terrains de l'île ». **Les chemins de
`sand_path` ne l'ont pas**, même s'ils sont de la même couleur : ils traversent
l'herbe et le village, et une piste d'empreintes y serait là en permanence.

Un personnage qui quitte une de ces cases y laisse une paire d'empreintes, qui
s'efface en une seconde — voir [player.md](player.md). Donner ce
comportement à une autre matière (la neige, la cendre) ne demande qu'une ligne
par tuile.

**C'est le calque le plus haut qui décide.** On lit le premier calque de
`Background` qui couvre la case, en partant du dessus : une serviette de plage
ou une planche de ponton posée sur du sable n'est pas du sable, et ne garde
donc aucune trace.

## L'eau qui bouge

Aucun des atlas n'a d'images d'animation pour l'eau. Elle bouge par un
**shader**, `resources/shaders/water.gdshader`, attaché aux tuiles d'eau
elles-mêmes dans `level.tres` :

```
9:31/0/material = SubResource("ShaderMaterial_water")
```

Des rides claires glissent en biais, par crans (4 par seconde), comptées en
pixels du décor. Elles ne touchent que les **pixels bleus** : sur une tuile de
rivage, le sable ne bouge pas ; sur le lac de la grotte, la vase non plus.

| Tuiles qui portent le shader | |
|---|---|
| `5:9,31` | eau claire |
| `5:5,34` `5:6,34` `5:6,35` | eau profonde |
| `5:16,33` `5:17,32` `5:17,33` `5:19,32` | rivage |
| `5:13,32` `5:13,33` `5:14,33` | plantes aquatiques, rochers dans l'eau |
| `8:12-14,0-2` | le lac de la grotte |

**Une nouvelle tuile d'eau ne bouge pas tant qu'on ne lui a pas donné ce
matériau** — une ligne, comme pour une collision. `steps_per_second` et
`strength` se règlent sur le matériau.

### L'eau où l'on se mire

Une seconde donnée perso, **`water`** (`custom_data_layer_1`, booléen), dit
qu'une tuile est de l'eau **pleine** : on s'y reflète. Cinq tuiles la portent —
la mer `5:6,32`, l'eau claire `5:9,31`, l'eau profonde `5:5,34` `5:6,34`
`5:6,35`.

**Ni le rivage ni les tuiles mixtes** : `5:15-17,31-33` sont à moitié du sable,
et portent déjà `sand`. Une tuile est l'un ou l'autre — ce qui se foule, ou ce
dans quoi on se mire.

Un personnage posé au bord d'une de ces cases y voit son reflet, en temps réel
([player.md](player.md)) ; là encore c'est **le calque le plus haut** qui
décide, donc une planche de ponton posée sur l'eau ne reflète rien.

## Les terrains de l'île

`start_island` reprend la plage de l'ancien village et y ajoute le relief et les
pontons. Chaque famille est un bloc 3×3 (coins, bords, centre) plus quatre
coins rentrants ; aucune ne sait dessiner une matière **d'une seule case de
large**. Les règles d'emploi sont dans [mapping.md](mapping.md).

| Matière | Bloc 3×3 | Coins rentrants | Posée sur | Collision |
|---|---|---|---|---|
| la mer | `5:6,32` | — | toute case d'eau | pleine, et le shader de l'eau |
| eau sous un ponton | `5:9,31` (même dessin) | — | sous chaque case de ponton | **aucune** : c'est ce qui laisse marcher dessus |
| plage, bord côté herbe | `5:10-12,13-15` | `5:13-14,13-14` | la case de sable qui touche l'herbe | aucune |
| plage, centre | `5:11,14` | — | le sable qui ne touche ni herbe ni eau | aucune |
| rivage | `5:15-17,31-33` | `5:18-19,31-32` | **la case de sable** qui touche l'eau | aucune : on marche jusqu'au bord |
| plateau d'herbe | `5:38-40,24-26` | `5:41,24` `5:43,24` `5:41,26` `5:43,26` | calque `Relief` ; la rangée du bas est la falaise | les flancs, le bas et les coins où la falaise se voit ; le dessus `5:39,25`, **le bord du haut `5:39,24`** et les deux coins rentrants du haut sont libres |
| ponton de bois | source `10` (`island.png`, voir plus bas) ; pilotis `5:48,24` | — | calque `Bridges`, par-dessus l'eau | aucune |
| dallage de la place | `5:5-7,47-49` | — | calque `Plaza`, sur le dessus d'un plateau | aucune |

- **Le rivage est sur la case de sable, pas dans l'eau.** L'eau reste de
  l'eau, entièrement ; ce qui a l'air de sable se foule.
- **Une plage fait au moins deux cases de large** entre l'herbe et l'eau : une
  même case ne peut pas porter le rivage et le bord d'herbe.
- `5:6,32` et `5:9,31` sont le même dessin : l'une est solide (la mer), l'autre
  non (l'eau claire du rivage, et l'eau sous les pontons).
- **Un escalier est un bloc de la planche de l'île**, posé par-dessus une
  case de bord de plateau qui prend sa variante sans collision (voir plus bas).
- Un plateau se dessine entièrement dans le fond : son pourtour étant solide,
  le joueur ne chevauche jamais un bord, il n'y a pas de tri à régler.

Les rochers :

| | Tuiles | Où |
|---|---|---|
| gros rochers dans l'eau, 2×2 | `5:26-39,32-33` | en chaîne dans les passes ; pas de collision à eux, la mer dessous est solide |
| petits rochers dans l'eau, 1×1 | `10:8-11,2` | dans la chaîne (`10:11,2`) ou épars autour (`10:8-10,2`) ; pleins |
| rochers de plage, 2×2 | `5:32-33,30-31`, `5:26-27,27-28`, `5:34-35,27-28` | un seul au bout d'une plage qui sort de la carte ; pleins |
| cailloux, 1×1 | `5:39-42,29` | épars sur le sable sec, à l'écart des passages ; pleins, comme sur la première carte |
| buissons, souche | `5:40,0` `5:41,0` `5:40,1`, `5:20,9` | au bord d'un bois ; pleins |

**Jamais les rochers moussus** (`5:26-31,30-31`) ni l'arbre à fruits
(`6:24,0`) : ce sont des éléments spéciaux, pas du décor
([mapping.md](mapping.md)).

## Les terrains de la route du nord

`north_route` ne lit **que** `route.png` (source 11) et ses hautes herbes
(sources 12 et 13) : la carte d'exemple qu'elle reproduit est faite des tuiles
de `sources/town_compilation.png`, et ce sont elles qu'on a découpées. Rien de
l'atlas `environments.png` n'y est posé — deux styles ne se mélangent pas sur
une même carte.

`assets/levels/route.png` — cases de 16 px sans marge, fabriquée par
`tools/route_tiles.py`, qui en est aussi **le catalogue** : le relevé y lit
quelles tuiles chercher dans l'exemple, le TileSet où elles sont. Une matière à
bords est un bloc 3 × 3 nommé comme un pavé numérique (`rock7` en haut à
gauche, `rock5` au centre, `rock3` en bas à droite), suivi de ses quatre coins
rentrants `i j / k l`.

| Matière | Bloc 3×3 | Coins rentrants | Calque | Collision |
|---|---|---|---|---|
| `sand` : sable bordé d'eau claire | `11:0-2,0-2` | `11:3-4,0-1` | `Ground` | pleine |
| `water` : eau claire | `11:3,2` | — | `Ground` | pleine |
| `deep` : eau profonde, bords fondus dans la claire | `11:5-7,0-2` | — | `Ground` | pleine |
| `lawn` : pelouse | `11:4,2` (`11:8,0` : pelouse fleurie) | — | `Ground` | aucune |
| `trailC` : le centre d'une piste | `11:8,1` | — | `Ground` | aucune |
| `trail` : le contour d'herbe d'une piste, centre vide | `11:9-11,0-2` | `11:12-13,0-1` | `Paths`, sur `trailC` | aucune |
| `paved` : dallage en chevrons | `11:11-13,6-8` | — | `Paths` | aucune |
| `rock` : falaise à dessus de roche | `11:0-2,3-5` | `11:3-4,3-4` | `Cliffs1`…`Cliffs3` | pleine, sauf le centre `rock5` |
| `grass` : falaise à dessus d'herbe | `11:5-7,3-5` | `11:8-9,3-4` | `Cliffs1`…`Cliffs3` | pleine ; son centre est la pelouse |
| `hollow` : la même, dessus vide | `11:10-12,3-5` | `11:13-14,3-4` | `Cliffs1`…`Cliffs3`, sur n'importe quel sol | pleine |
| rebords de roche | `11:12-14,2` (vers le sud), `11:15,0-2` (vers l'est), `11:15,3-4` (vers l'ouest) | — | `Ledges` | pleine — voir plus bas |
| fleurs | `11:0-4,6` | — | `Decorations` | aucune |
| escalier de pierre | `11:6-8,13-15` : la rangée du milieu est celle des marches ; celle du bas ne porte que le pied des poteaux et le bord de la dernière marche, deux rangées de pixels qui débordent sur la case du dessous — **à poser**, sinon l'escalier est coupé net | — | `Bridges` | aucune |
| ponts de planches | `11:0-4,12` (vertical), `11:5-8,12` (horizontal), `11:9-11,12` (son dessous, qui déborde d'une rangée) | — | `Bridges` | aucune |

- **Toute tuile qui bloque a une variante 1 : le même dessin, sans
  collision.** Elle se pose sous le tablier d'un pont et sous les marches d'un
  escalier. C'est le générateur qui choisit la variante ; les collisions,
  elles, sont déclarées par `route_tiles.blocks`.
- **Les sources 11 à 13 sont réécrites en entier par
  `tools/maps/north_route/generate.py --write`.** Une collision de la route ne
  se retouche pas dans l'éditeur.
- **La falaise est un anneau d'une case**, sur le pourtour d'un niveau. Deux
  anneaux l'un dans l'autre, roche puis herbe, font la falaise à deux étages
  qui borde chaque terre ; sous l'anneau de roche, le sol est du sable.
- **L'eau porte le shader**, sable bordé d'eau compris : il ne touche que le
  bleu. Elle ne porte **pas** la donnée `water` : la rivière est au fond d'un
  ravin, on ne s'y mire pas depuis un pont.
- **Les ombres sont translucides** dans la planche (arbres, falaises,
  rochers) et le restent dans `route.png` : le moteur les fond sur ce qu'il y
  a dessous, comme l'exemple.
- **Un rebord de roche est plein, et se saute dans un sens.** Sa tuile porte
  ce sens dans la donnée perso **`jump`** (`custom_data_layer_2`, un
  `Vector2i`) : `(0, 1)` pour `ledgeL/M/R`, `(1, 0)` pour `ledgeV…`, `(-1, 0)`
  pour `ledgeW…` — du côté où tombe son ombre (`route_tiles.jump`). Une tuile
  sans cette donnée ne se saute pas. `CharacterMovement.tryJump` la lit
  ([player.md](player.md)).

Ce qui est debout est **une seule tuile de plusieurs cases**, posée sur la
case en bas à gauche de son pied (`size_in_atlas`, `texture_origin`), dans un
calque trié en Y de `World` :

| | Tuile | Taille | Bloque |
|---|---|---|---|
| arbres : deux essences. Les arbres que l'exemple fait des deux à la fois ne sont pas dans `route.png` : `route_tiles.py` ne les recompose que pour le relevé | `11:0,9` `11:3,9` | 3×3 | ses **deux rangées du bas, sur ses trois cases** ; pas le haut : on passe derrière |
| sapin, arbuste | `11:6,7` `11:7,7` | 1×3 : deux cases, et une rangée d'ombre **sous** le pied | sa case |
| caillou, bloc brun | `11:8,11`, `11:9,10` | 1×1, 2×2 | ses cases |
| rochers de la rivière : gros, pointu, deux petits | `11:11,9` `11:13,10` `11:14,11` `11:15,11` | 2×3, 1×2, 1×1 | rien : l'eau qui les porte bloque |

- **Pourquoi deux rangées entières.** La cime retombe de chaque côté du
  tronc : une case qu'elle recouvre n'est pas une case où l'on se tient, et
  ce qu'on y poserait serait dessiné par-dessus l'arbre. Et les arbres sont
  plantés toutes les quatre colonnes, une rangée sur deux décalée : ne bloquer
  que le tronc laisserait une colonne libre sur deux, cachée sous les cimes.
- **Un arbre se trie 2 px au-dessus du centre de la case de son tronc**
  (`y_sort_origin = -2`) : qui passe derrière la cime passe derrière. Les
  autres se trient à −1 : devant l'arbre planté sur la même rangée.
- **L'ombre du sapin et de l'arbuste déborde d'une rangée de pixels sous leur
  pied** (`route_tiles.SHADOW_ROW`). Leur tuile fait donc trois cases de haut,
  centrée sur la case du pied (`texture_origin = (0, 0)`) : deux cases
  au-dessus du sol, une rangée d'ombre en dessous.
- **Deux coins rentrants ne bloquent pas** : `grassk` et `grassl`
  (`route_tiles.blocks`), de la pelouse avec un bout de lisière en haut — voir
  [levels.md](levels.md).
- **Ce que la planche n'a pas est découpé dans l'exemple lui-même**
  (`REFERENCE_PIECES`) : le centre de la piste, les ponts, les rebords, les
  rochers de la rivière. Le fond connu en est retiré — toutes les teintes de
  la pelouse, ou l'eau pixel à pixel. Le bout du bas du rebord tourné vers
  l'est, que l'exemple ne montre jamais en entier, est son bout du haut
  retourné (`ledge_bottom`).

Les hautes herbes de la route ont leurs sources à elles, rangées comme celles
de l'atlas pour que `TallGrass.kt` les traite pareil : `12:6-8,0` (la touffe
et ses deux états foulés, la rangée 6 de `route.png`) et `13:6-8,0` (ses
4 pixels du bas). Les deux états foulés sont dérivés de la touffe
(`route_tiles.pressed`) : elle **se tasse** de deux, puis de trois pixels, le
pied restant en place, et au plus tassé elle **s'éclaircit** d'un cran dans
ses cinq verts. Elle ne se fend pas en deux : c'était le premier essai,
refusé par Ludovic (17/11/2026). `TallGrass.kt` lit la source de la
touffe sur la case et prend la moitié basse dans la source appariée
(`5 → 9`, `12 → 13`).

## Les rebords

Le bord du haut d'un plateau (`5:39,24`) est de l'herbe, avec un liseré tout en
haut : on doit pouvoir s'y tenir, mais pas passer de là à la case du dessus —
ni dans l'autre sens. C'est une passabilité **par direction**, que les
collisions pleines ne savent pas dire.

- Le TileSet a une seconde couche physique, `physics_layer_1` (couche de
  collision **8**), où aucun corps ne vit. `5:39,24` y porte une bande de 3 px
  le long de son bord du haut, et n'a plus rien sur la couche 0.
- `CharacterMovement.tryWalk` teste la case visée comme avant (un point en son
  centre, couche des obstacles), puis cherche un rebord **de part et d'autre de
  la frontière** entre les deux cases (deux points à 2 px de la frontière,
  couche 8). Joueur et PNJ passent par là.
- Les tests ont `ledge_between(a, b)` et `can_step(a, b)` dans `tests/lib.gd` ;
  `find_path` s'en sert. `is_free` seul ne suffit plus à dire qu'on passe.

Un plateau adossé à la falaise n'a pas de bord du haut : il continue sous
elle, et ses flancs montent jusqu'au mur.

## La planche de l'île (`island.png`, source 10)

`assets/levels/island.png` — 256 × 48, cases de 16 px sans marge. Ce sont les
tuiles que `environments.png` n'a pas ; **rien n'y est dessiné à la main**,
tout est dérivé de l'atlas par `tools/island_tiles.py`, qu'on relance pour la
refaire à l'identique.

| Cases | Contenu |
|---|---|
| rangée 0, colonnes 0–15 | planche de ponton, selon ses côtés à rambarde : gauche = 1, droite = 2, haut = 4, bas = 8, additionnés |
| rangée 1, colonnes 0–3 puis 4–7 | planche de bout posée sur la rive, bout en haut puis en bas (rambarde gauche = 1, droite = 2) |
| rangée 2, colonnes 0–3 puis 4–7 | bout à gauche puis à droite (rambarde haut = 1, bas = 2) |
| rangée 2, colonnes 8–11 | petits rochers dans l'eau : les cailloux `5:39-42,29`, cernés d'écume |
| rangée 2, colonne 12 | planches tournées d'un quart (ancien escalier de côté, plus posé) |
| rangées 3–4, colonnes 0–7 | **escaliers à poteaux**, un bloc de 2×2 par côté de plateau : bas, haut, gauche, droite |
| rangées 3–5, colonnes 11–14 | parasols bleu et orange, avec leur ombre (la rangée 5 est le pied) |
| colonne 15, rangées 3–4 et 5–6 | serviettes de plage |
| rangées 5–6, colonnes 0–2 | caisses empilées, une caisse, pot de fleurs |
| rangée 6, colonne 3 | Poké Ball posée au sol : l'image d'un objet à ramasser (une région de texture, pas une tuile) |
| rangées 5–6, colonnes 4–5 | **banc de bois vu de face** : la rangée 6 est l'assise (pleine), la rangée 5 le haut du dossier |
| rangées 3–5, colonnes 8 et 9 | **banc de bois de profil**, dossier à gauche puis à droite : deux cases pleines (rangées 4 et 5), deux pixels qui dépassent en rangée 3 |

Pourquoi les fabriquer : dans l'atlas, le ponton n'a de rambarde que sur ses
flancs gauche et droit (`5:47,22` et `5:49,22`). Un ponton est-ouest perdait
donc son rebord gris, un angle n'avait pas de pièce, et rien ne le faisait
arriver proprement sur le sable. Les rambardes du haut et du bas sont celles
des flancs tournées d'un quart ; une planche de bout est une planche fermée
d'un trait sombre, celui du contour du ponton.

Les rangées 3 à 6 ne viennent pas de l'atlas : elles sont **découpées dans
les planches de `sources/`** et recalées sur la grille (voir « Prendre un
élément dans une planche source »). Les escaliers, les parasols, les
serviettes, les caisses et le pot viennent de `town_compilation.png`, la Poké
Ball de `public_indoor.png`. Les bancs de bois viennent de l'atlas lui-même
(`environments.png`, autour du pixel 1089,609), où ils sont posés **hors
grille** : le script les recale. La liste `PIECES` dit d'où vient chaque bloc.

**Un escalier** est un bloc de 2×2 posé sur le calque `Bridges`, par-dessus le
bord du plateau : deux cases sur le bord, deux qui débordent de 6 px sur le
dessus (le haut des poteaux). Celui de côté est celui du bas tourné d'un quart. La
planche a aussi celui du haut, retourné, mais on ne le pose pas : un escalier
vu à l'envers ne ressemble à rien. Dessous, la case de bord garde son dessin mais
prend sa **variante 1, sans collision** (`39:26/1`, `39:24/1`, `38:25/1`,
`40:25/1`) : c'est ce qui laisse passer.

Collisions : les petits rochers, le pied des parasols, les caisses et le pot.
Parasols, caisses et pot sont dans `Props` et se trient par leur pied ;
pontons, escaliers et serviettes sont dans le fond.

## Le vent dans les plantes

Comme pour l'eau, aucune image d'animation : un shader,
`resources/shaders/sway.gdshader`, décale la cime des plantes d'un pixel ou
deux, par crans, le pied restant planté. Un pixel qui irait lire hors de sa
tuile reste à sa place : sans ça la plante se troue.

| Matériau | Sur | |
|---|---|---|
| `ShaderMaterial_sway_bottom` | le pied des grandes fleurs | `base = 0` |
| `ShaderMaterial_sway_top` | leur cime, la tuile du dessus | `base = 1` : elle prolonge le mouvement du pied |
| `ShaderMaterial_sway_palm` | le palmier `6:30,11` | une tuile de 64×64 (4×4 cases : son dessin fait 53 px de large), dont il faut donner le coin dans l'atlas (`origin`) |

Deux sortes de plantes d'**une case de large sur deux de haut** :

| | Tuiles | Collision | Tri |
|---|---|---|---|
| grandes fleurs | `5:0-7,3-4` | **aucune** : on marche dessus | pied `-15`, cime `1` — elles passent sous le joueur |
| petits sapins | `5:33-38,0-1` | pied solide | pied `8`, cime `24` ; **pas de vent** : aussi larges que leur case, ils se déchireraient |

## Ce qui reste à déclarer

Les collisions ont d'abord couvert les ~150 tuiles que l'ancien village utilisait.
**Une tuile jamais posée jusqu'ici n'a pas de collision tant qu'on ne l'a pas
déclarée** — une fois, et c'est acquis.

Trou connu : le terrain `mountain` (colonnes 20-25, lignes 21-23) est déclaré
comme terrain mais aucune de ses tuiles n'a de collision. Peindre une montagne
avec ce pinceau donne un décor traversable.

## Terrains (autotuilage)

| Set | Nom | Tuiles |
|---|---|---|
| `terrain_set_0` | `sand_path` | colonnes 0-4, lignes 16-18 |
| `terrain_set_1` | `mountain` | colonnes 20-25, lignes 21-23 |

Les chemins existants ont été peints avec `sand_path`. **Peins toujours un
chemin au pinceau terrain**, jamais tuile par tuile : les raccords de bord et de
coin se placent seuls.

## Manque par rapport au tutoriel

Une couche de données perso **`LEDGE`** (type String, valeurs `"DOWN"`,
`"LEFT"`, `"RIGHT"`). Le tutoriel l'interroge dans `CharacterMovement.cs` quand
le joueur touche une tuile : si la direction correspond, il saute le talus au
lieu d'être bloqué. Nos rebords passent par une seconde couche physique (voir
« Les rebords ») ; les couches de données, elles, existent maintenant — `sand`
et `water` — donc ajouter `LEDGE` ne demande plus qu'une ligne dans
`[resource]`.
