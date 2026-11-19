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
0 — et s'ajoute à `FRONTS` dans `TallGrass.kt`. La Route 1 a les
siennes (`12` et `13`, voir « Les terrains de la Route 1 »).

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

**L'île de départ ne se sert plus de ces terrains** : depuis le 17/11/2026 elle
est posée avec ceux de la Route 1 (plus bas), et ses maisons viennent de
`village.png` (source 14). Les terrains de l'atlas décrits ici restent ceux du
terrain d'essai des tests (`tests/maps/field.tscn`). Chaque famille est un bloc 3×3 (coins, bords, centre) plus quatre
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

## Les terrains de la Route 1

**L'île de départ s'en sert aussi** (17/11/2026), avec trois ajouts :

- **la plage** : `sand5` dans sa **variante sans collision** (`/1`). Sur la
  Route 1 le sable est le liseré du pied des falaises, plein ; sur l'île c'est
  aussi le sol des plages, où l'on marche. Le bord du sable reste dans la case
  d'eau voisine, plein. Le sol posé **sous une falaise** prend aussi cette
  variante : c'est la falaise qui arrête, et ses deux coins rentrants du haut
  doivent rester libres ;
- **les maisons** : `village.png`, source 14, fabriquée par
  `tools/village_tiles.py` à partir de la même planche. Chaque maison est une
  seule tuile de plusieurs cases, calée pour que sa porte tombe au milieu d'une
  case, avec trois rangées de plus en bas pour son ombre. Elle bloque ses
  quatre rangées du bas sauf la case de la porte ; on passe derrière le haut du
  toit. Ses trois rectangles de collision sont **rentrés d'un pixel** : bord à
  bord, le moteur les soude et y laisse un trou. Elle se trie à −1 : qui se
  tient sur la case de la porte passe devant ;
- **la falaise à deux étages, comme sur la route** : l'anneau d'herbe sur du
  `rock5`, cerné de l'anneau de roche sur du `sand5`. Le bord du haut
  (`grass8`) bloque de nouveau : derrière lui il y a le gradin de roche ;
- **le rivage en deux calques** : l'eau (`water`) dans `Ground`, et par-dessus,
  dans `Shore`, le bord du sable **sans son eau** (`shore7`…`shorel`,
  `11:0-5,7-8`, dérivés des bords `sand…` par `route_tiles.py` : tout ce qui
  est bleu et pas clair s'en va, l'écume reste). Les reflets se rangent juste
  au-dessus de `Ground` : le sable du bord les recouvre. D'une seule pièce, le
  reflet s'étalait sur le sable ;
- **les données `water` et `sand`** : l'eau, l'eau profonde, les bords `sand…`
  et `shore…` portent `water` (reflet, ombre bleue des volants) ; `sand5` porte
  `sand` (traces de pas). Sur la Route 1 cela ne change rien à pied — on n'y
  touche jamais l'eau — sauf l'ombre des volants au-dessus de la rivière ;
- **les coins rentrants du sable ne sont pas rangés comme ceux des falaises** :
  l'eau de `sandi` est en bas à gauche, celle de `sandk` en haut à gauche
  (`layout.SAND_CORNER`). Posés comme ceux d'une falaise, ils sont à l'envers ;
- **le pied d'un parasol ne bloque plus** (`10:11-14,5`), et **ses trois
  rangées se trient ensemble**, juste derrière la rangée du pied
  (`y_sort_origin` −1, 15 et 31) : sur cette rangée on passe devant tout le
  parasol, toile comprise ; une rangée plus haut, on est dessous. Triées à
  part, le bas de la toile était coupé net sur le joueur ;
- **les plantes de l'île** : `village.png` porte aussi un petit palmier, un
  grand et un massif de buissons (`village_tiles.PLANTS`), découpés dans la
  même planche avec leur ombre. Une seule case pleine chacun : le tronc ;
- le mobilier (bancs, parasols, serviettes), les lampadaires et les statues
  restent ceux de l'atlas : la planche de la Route 1 n'en a pas encore été
  fouillée.

`route_1` ne lit **que** `route.png` (source 11) et ses hautes herbes
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
| `pond` : l'étang, une eau au niveau de l'herbe, sa berge brune en haut et sur les côtés | `11:8-10,16-18` | `11:11-12,16-17` | `Paths`, sur `lawn` | pleine (variante 1 sans collision, sous un pont) |
| `earth` : la terre nue bordée d'herbe, la plaque d'une clairière | `11:0-2,19-21` | `11:3-4,19-20` | `Paths`, sur `lawn` | aucune |
| `wheat` : le blé, un bloc qui se pose sur la terre d'un champ (pas de coin rentrant : la case pleine en tient lieu) | `11:5-7,19-21` | — | `Crops`, sur `earth` | pleine |
| `lily1` `lily2` `lily3` : nénuphars, détourés de l'eau de la planche | `11:13-15,16` | — | `Decorations` | aucune |
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
  `tools/maps/route_1/generate.py --write`.** Une collision de la route ne
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
| volée double : la rangée de marches en deux variantes faites pour se suivre, `stairU4/5/6` (haut, sans pied de poteau) et `stairL4/5/6` (bas, l'ombre d'une contremarche à la place du vide) | `11:4-5,16` `11:7,14` `11:4-6,17` | 1×1 | rien : les marches se foulent |
| escalier de côté : le bloc de la volée double tourné d'un quart, `stairW<colonne><rangée>` (son pied est à l'ouest) et `stairE…` (son pied est à l'est) | `11:9-12,13-15` `11:0-3,16-18` | 4 colonnes × 3 rangées, entre deux poutres | ses poutres du haut et du bas ; les marches se foulent |
| jetée : planches en travers entre deux longerons à pieux, `pier4/5/6`, et son dernier rang `pier1/2/3` | `11:12-14,12` `11:15,12-14` | 1×1 | rien |
| les deux premiers rangs de la jetée, que le sable recouvre : `pierT4/5/6`, `pierU4/5/6` — le masque d'herbe du bout du pont de `environments.png`, reporté au pixel près | `11:13-14,13` `11:13,14` `11:14,14` `11:13-14,15` | 1×1 | rien |
| coins rentrants du dallage : `pavedl/k/j/i`, le pavé plein et un bout de liseré dans le coin | `11:14-15,7-8` | 1×1 | rien |
| clôture de bois : un poteau par case, deux lisses ; coins et côtés d'un enclos, `fence7/8/9/4/6/1/2/3` — dessinée par `route_tiles.py` | `11:8-10,7-9` | 1×1 | toute la case |
| coquillages : Saint-Jacques, bigorneau, étoile de mer, deux petits (`shell1…4`) — dessinés par `route_tiles.py`, rien n'en avait dans ce style | `11:13-15,5` `11:14,6` | 1×1 | rien : du décor, sur `Decorations` |

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

## La planche de la grotte (`cavern.png`, source 15)

`assets/levels/cavern.png` — 240 × 96, cases de 16 px sans marge : la roche
d'une grotte. **Rien n'y est dessiné à la main** : `tools/cavern_tiles.py` la
découpe dans `sources/cliffs_caves.png` (le kit de grotte brune), et
`--write` réécrit sa source dans `level.tres`. Relancé, il redonne le même
fichier ; lui et `tools/maps/route_1/generate.py` laissent chacun le TileSet
tel que l'autre l'a écrit (la source de la grotte est rangée avant celles de
la route).

Mêmes conventions que `route.png` : un bloc 3 × 3 nommé comme un pavé
numérique, puis ses quatre coins rentrants `i j / k l`.

| Nom | Cases | Calque | Collision |
|---|---|---|---|
| `rock` : la paroi, un gradin de roche — sa face est en bas | `15:0-2,0-2`, coins `15:3-4,0-1` | les falaises, par-dessus le sol | pleine, sauf `rock5` (le dessus plat, que rien n'atteint) |
| `void` : le noir autour de la grotte. Ses huit bords sont des cases de vide **qui touchent la roche**, avec un liseré du côté de la roche, et **du sol derrière lui jusqu'au bord de la case** (voir ci-dessous) ; son centre est le noir plein. Coins rangés à l'inverse (`l k / j i`) | `15:5-7,0-2`, coins `15:8-9,0-1` | `Ground` | pleine |
| `pond` : un bassin dans sa berge de roche (l'eau bouge : même matériau que la mer) | `15:0-2,3-5`, coins `15:3-4,3-4` | `Paths` | pleine |
| `earth` : une plaque de sol sombre | `15:5-7,3-5`, coins `15:8-9,3-4` | `Paths` | aucune : on y marche |
| `lawn` : le sol de la grotte | `15:10,0` | `Ground` | aucune |
| `rock_s`, `pebbleA`, `pebbleB` : petits rochers | `15:11,0`, `15:12,0`, `15:13,0` | `Props` | sa case |
| `spire` : une stalagmite, 1 × 2 | `15:14,0` | `Props` | sa case du pied |
| `boulder` : un gros bloc, 2 × 2 | `15:10,2` | `Props` | ses quatre cases |
| `ladder` : une échelle de bois, 1 × 2, adossée au haut d'une paroi | `15:12,2` | `Bridges` | **aucune** — on monte dessus |

**L'échelle est la seule tuile qui ne vienne pas de `cliffs_caves.png`** : aucun
des huit kits de falaises n'en a. Elle est découpée dans
`sources/ice_cave.png`, la planche de la grotte de glace — même auteur, même
famille de dessin. C'est du **bois** : la règle F de
[mapping.md](mapping.md) (« un rocher a la matière de ce qui le porte ») ne la
concerne pas, et c'est la même échelle dans les deux teintes. Elle est sur le
calque `Bridges`, avec les ponts et les escaliers, et non `Decorations` : le
contrôleur compte tout ce qui est sur `Decorations` comme une fleur, et une
grotte n'a rien de vivant.

Le décor `tools/mapgen/themes/cave.toml` ne lit que cette planche. Les noms
sont ceux que le constructeur attend d'un décor : c'est pourquoi le sol de la
grotte s'appelle `lawn` et son bassin `pond`.

### Le liseré du vide : du sol derrière lui, pas du noir

La planche de falaises dessine le vide comme un **trou rond** : son liseré est
un anneau arrondi d'environ 30 px, là où trois cases en demandent 32. Découpé
tel quel, il tombait au milieu de la case et il restait **1 à 3 px de noir
entre lui et la roche** — un filet clair qui avait l'air de flotter dans le
noir, tout autour de la grotte (Ludovic, 18/11/2026 : « le contour ondulé est
mis à l'envers »).

La carte de référence qu'il a fournie ce jour-là ne s'y prend pas autrement, et
c'est elle qui donne la règle : mesurée colonne par colonne, **sa case de bord
contient du noir, le liseré, puis de la roche jusqu'au bas de la case**, qui se
prolonge dans la case suivante. Son bord n'est pas une tuile à part : c'est une
tuile moitié vide, moitié roche.

`cavern_tiles.backfill` fait pareil pour la **grotte brune** (la grotte de glace,
elle, pose son liseré en surcouche, voir plus bas) : on part du bord qui touche la grotte, on remonte dans le noir
jusqu'au liseré, qui arrête, et **tout ce qu'on atteint devient la case de sol,
au même endroit dans la case** — la trame se suit donc d'une case à l'autre.
Aucun pixel n'est inventé. Mesuré sur une carte entière : le filet noir passe
de 1 915 px à 145, le reste étant un pixel isolé à certaines jointures de
tuiles, là où l'anneau se referme sur lui-même.

## La planche de la grotte de glace (`ice_cavern.png`, source 16)

`assets/levels/ice_cavern.png` — 240 × 256. **Ses onze premières colonnes sont
la planche source telle quelle** (`sources/ice_cave.png`, « Evolina ice cave »
de Phyromatical), case pour case : rien n'est déplacé, une tuile s'appelle donc
comme dans le relevé de la carte d'exemple. Quatre colonnes de plus portent ce
qui a dû être recalé — l'échelle et le trou à échelle.
`tools/ice_cave_tiles.py` la fabrique, `--write` réécrit sa source ; elle est
rangée juste avant celle de la grotte brune, elle-même avant celles de la
route, et chacun des trois outils laisse le fichier tel que les autres l'ont
écrit.

**Ce kit se superpose. Ce n'est pas la grotte brune repeinte**, et le lire
ainsi a donné deux décors faux de suite (18/11/2026 : « y'a rien qui va, ni
contour, ni sol »). Ce qui a tranché : la carte d'exemple de l'auteur
(`tools/maps/ice_cave/reference.png`), **relevée tuile par tuile et par
couches** (`tools/maps/ice_cave/survey.py`), puis rebâtie par notre
constructeur à partir de quatre classes de cases seulement
(`tools/maps/ice_cave/compare.py`). Elle est faite de cinq familles, de bas en
haut :

| Famille | Cases | Calque | Ce que c'est |
|---|---|---|---|
| `floor…` | `16:0-2,11-13`, coins `16:3-4,11-12` | `Ground` | le **sol**, bleu-gris foncé : une matière à bords **pleine** — ses bords portent la glace pâle en dur. `lawn` est sa case du centre |
| `earth…` | `16:5-7,13-15`, coins `16:8-9,13-14` | `Ground` | la **glace lisse**, striée (le `,` du plan) : une autre matière à bords pleine, posée à la place du sol. On y marche ; on y glissera |
| `tall…` | `16:0-2,3-6`, plis `16:3-4,3-5` | `Cliffs1` | le **grand plateau**, sur **toute** la paroi : bord du haut (`talla`), côtés (`tallb`), puis **deux rangées de face** au sud (`tallc`, `talld`). Les plis (`…3`, `…4`) sont pour les marches que fait la face : une case dont la voisine est une rangée de face plus bas. **C'est lui qui arrête** |
| `short…` | `16:0-2,0-2`, coins `16:3-4,0-1` | `Cliffs2` | le **petit plateau**, posé sur le grand : le dessus du grand, **en retrait d'une case à l'est et à l'ouest**. Sa lèvre (`short1`-`3`) tombe ainsi juste au-dessus de la face du grand |
| `ring…` | `16:0-2,7-9`, coins `16:3-4,7-8` | `Ledges` | le **liseré du vide** : du noir dehors, un filet, du transparent dedans. Il se pose **sur** la dernière case de paroi, pas sur une case de vide. `void5` (`16:1,8`) est le noir plein |

Ce que ça donne, et que l'ancien décor n'avait pas :

- **la glace pâle est le dessus des parois** — là où l'on ne va pas — et le
  sol est le bleu-gris. Entre les deux il y a **toujours une face de falaise**
  quand la paroi est au nord du sol : liseré, lèvre du petit plateau, deux
  rangées de face ;
- **la bordure de la grotte ne fait qu'une case de glace pâle**, parce que le
  liseré est une surcouche de la paroi : la moitié de sa case est noire ;
- **le sol a son contour** partout où il touche la paroi, et il passe **sous**
  le bord du haut du grand plateau là où le petit ne le couvre pas — c'est ce
  qu'on voit dans l'arrondi de ses coins ;
- **toute la paroi arrête**, dessus compris : chacune de ses cases porte une
  tuile du grand plateau ;
- **sous la paroi, de la glace claire** (`short5`), pas du sol : c'est elle
  qu'on voit dans les jours des tuiles du grand plateau — le pied arrondi
  d'une face, le coin d'un dessus —, et elle rejoint le liseré clair que le
  sol porte sur son bord. Avec du sol foncé dessous, ce liseré restait seul et
  dessinait un cadre carré autour de chaque massif (Ludovic, 18/11/2026).

**Ce que le kit demande à la forme de la carte**, et que le générateur tient
(`worldgen.generate_cave`, « kit ») :

- **une paroi au-dessus d'un sol fait trois cases de haut** — son dessus, puis
  ses deux rangées de face — **et deux de large**. Plus basse, sa face commence
  sans dessus, coupée net ; d'une seule case de large, il lui manque un flanc.
  Les massifs sont donc faits de blocs de 2 × 3, et une paroi plus mince
  redevient du sol ;
- **une matière à bords fait deux cases dans chaque sens**. Le sol n'a pas de
  tuile pour deux angles rentrants à la fois : entre deux roches, ou entre une
  roche et le verglas, il lui faut **deux cases**, coins compris — ou aucune
  (le verglas touche la paroi). Une encoche de sol d'une case redevient de la
  roche.

Le constructeur **prévient** quand un plan ne les tient pas (« paroi : N cases
coupées net », « sol : N cases trop étroites pour leurs bords ») ; le
contrôleur en fait une règle manquée (« la carte s'assemble sans
avertissement du constructeur »), que le balayage compte.

Le petit plateau ne se pose que s'il a **trois cases de large** : à deux, ses
deux rebords se touchent et font des rails sur le dessus d'un éperon. Plus
mince, on voit le dessus uni du grand.

Le constructeur applique cette grammaire dès que le décor déclare des `tall…`
(`tools/mapgen/build.py`, « un décor à plateaux »). Pas de bassin : la planche
n'a pas d'eau.

Ce qui se pose :

| Nom | Cases | Calque | Collision |
|---|---|---|---|
| `pebbleA` | `16:7,0` | `Props` | sa case. Le **caillou foncé** : au sol |
| `spire` | `16:5,1`, 1 × 2 | `Props` | la case de son pied. Le **pic foncé** : au sol, sa pointe sur la case du dessus |
| `roundA`, `roundB` | `16:6,1`, `16:6,2` | `Props` | leur case. Les **cailloux ronds et pâles** : jamais au sol — voir plus bas |
| `boulder` | `16:7,1`, 2 × 2 | `Props` | ses quatre cases. Déclaré, mais le générateur ne le pose plus : sur l'exemple il est adossé au pied d'une paroi, à cheval sur elle |
| `ladder` | `16:11,0`, 1 × 2 | `Bridges` | aucune. L'échelle qui **monte** : son pied sur la première case de sol, son haut sur la dernière rangée de face — c'est ainsi qu'elles sont sur la carte d'exemple |
| `hole` | `16:12,0`, 3 × 2, `anchor = 1` | `Bridges` | aucune. L'échelle qui **descend** : un trou vu de dessus, son dessin posé centré dans un bloc de largeur **impaire** — à largeur paire il n'y a pas de case du milieu, et le joueur arrivait décalé |
| `crack` | `16:6,8`, 2 × 2 | `Bridges` | aucune. Des **fissures** dans le sol, à plat : du décor, pour que le sol ne soit pas partout le même carreau. La carte d'exemple en sème seize sur ses 255 cases de sol ; le générateur en met une pour dix-huit cases de sol nu, jamais deux qui se touchent, jamais sur la glace lisse ni devant la sortie |

**Chaque caillou a sa place** (Ludovic, 18/11/2026 : « sur le sol, il n'y a que
ces deux cailloux-là » ; le relevé de la carte d'exemple le confirme case par
case) :

- **au sol, seulement les deux foncés** : le caillou (`pebbleA`, 28 fois sur
  l'exemple) et le pic (`spire`, 23 fois). Jamais retournés, jamais sur le
  verglas ;
- **les ronds et pâles** (`roundA`, `roundB`) à deux endroits seulement :
  **sur le dessus du grand plateau, là où le petit ne le couvre pas** — le
  dessus uni d'un éperon, d'un massif épais, d'un redan (les quatorze de
  l'exemple y sont tous) —, ou **sur le verglas**, où ils serviront d'obstacles
  aux casse-têtes. Le générateur les pose sur les parois, et un ou deux sur
  chaque grande plaque de verglas — seulement là où l'on traverse toujours,
  dans les deux sens.

**Le verglas se déclare dans le TileSet** : la donnée perso **`ice`**
(`custom_data_layer_3`, booléen), posée par `ice_cave_tiles.py` sur toute la
matière `earth…`, bords compris. C'est elle que lit le déplacement
(`CharacterMovement.isIce`, [player.md](player.md)) ; le décor, lui, dit au
constructeur que cette matière glisse (`slick = "earth"` dans
`cave_ice.toml`).

**Le petit plateau s'écarte sous un caillou.** Là où le petit plateau couvre
le grand — toute la paroi du tour, jusqu'à son flanc —, le constructeur retire
du petit la case qui porte un caillou : une **encoche d'une case**, avec sa
lèvre au-dessus et ses coins. C'est le dessin des quatorze cailloux de
l'exemple (liseré, bord du petit plateau, caillou, flanc du grand). Le
générateur en pose ainsi deux ou trois **sur le tour de la grotte** (Ludovic,
19/11/2026 : « là il n'y en a aucun sur le tour »), dans la colonne du bord du
petit plateau, là où la paroi est assez épaisse pour garder le liseré et un
bord entre le caillou et le vide.

Les deux premières versions du décor avaient pris le rond pour un caillou de
sol, et l'avaient retourné pour en faire un second : on ne sème pas une tuile
avant d'avoir relevé **où** l'exemple la pose.

**La mesure.** `python3 tools/maps/ice_cave/compare.py` rebâtit la carte
d'exemple et compte les cases refaites au pixel près, au bruit du JPEG près :
**80,5 %** aujourd'hui (78 % avant la glace claire sous la paroi). Ce qui reste en écart n'est pas la grammaire : ce sont les
objets que le plan ne dit pas (rochers, échelles, crevasses), et les raccords
que l'auteur a faits à la main là où deux lobes de sa grotte se rejoignent —
un contour pincé d'une demi-case, une lèvre suivie d'un bord du haut. Avant ce
relevé, le même calcul donnait une carte où **aucune** case de paroi n'était
la bonne.

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
