# Inventer une carte

Un **monde** est un fichier `<monde>.toml` : une graine et des réglages. Le générateur (`tools/mapgen/worldgen.py`)
en tire un plan — relief, plages, forêts, hautes herbes, chemins, décor — que le constructeur assemble.

```
python3 tools/mapgen/worldgen.py tools/mapgen/worlds/prairie.toml --preview /tmp/prairie.png
```

Il écrit `plans/<carte>.toml`, le passe au contrôleur (`check.py`) et dit son **taux de composition**, les règles
de `docs/mapping.md` qu'il enfreint encore, et — à part — s'il est **injouable**. On change un réglage, on relance,
on regarde ; quand la carte plaît, on retouche son plan à la main s'il le faut, puis `build.py --write` en fait la
scène.

```
  monde (graine, réglages)  --worldgen.py-->  plan (tout est écrit)  --build.py + décor-->  scène
        on invente                              on lit, on retouche                          on assemble
```

## Orienter la carte en quelques mots — `[style]`

Avant les nombres, on dit ce qu'on veut. Chaque mot règle plusieurs nombres d'un coup ; ce qu'on écrit ensuite dans
`[relief]`, `[climate]` ou `[vegetation]` passe toujours devant. `styles_apercu.png` montre six exemples, dans
l'ordre : `style_ile`, `style_anneau`, `style_couloir`, `style_plaine`, `style_cote`, `style_baie`.

```toml
[style]
kind = "route"                   # le style de la carte : route (le défaut), mountain, seaside ou beach
size = "medium"                  # small (40 × 30), medium (64 × 44), large (90 × 64), ou [largeur, hauteur]
shape = "coast"                  # la forme générale
character = ["rocky", "jagged"]  # un ou plusieurs caractères, qui se cumulent
sea = "west"                     # pour coast et bay : le côté de la mer
```

| `kind` | Ce que c'est (les règles de chaque style sont dans [`docs/mapping.md`](../../../docs/mapping.md), « Les styles de carte ») |
|---|---|
| `route` | une route : la terre va jusqu'au bord, toute eau est un lac ou un bras dans les terres |
| `mountain` | une route de montagne : **la roche ferme la carte, en gradins**, et **la vallée monte en terrasses** d'un mur à l'autre, de plus en plus hautes vers le nord — on passe de l'une à l'autre par un escalier de pierre sur le trajet. Il lui faut une sortie au nord et une au sud, et de la hauteur : `size = [46, 66]` donne trois terrasses, une carte moyenne deux, une petite aucune. `montagne_apercu.png` en montre une (`style_montagne`). Pas encore : la rivière et ses cascades, l'entrée de grotte |
| `seaside` | une route côtière : **la mer longe le flanc `sea` jusqu'au bord**, une chaîne de rochers la suit au large ; peu de sable |
| `beach` | une plage : **la mer va jusqu'au bord** du côté `sea`, le sable est le sol — palmiers serrés, rochers par grappes, buttes boisées posées sur le sable. Sa forme est `coast`. On y descend par un escalier ; quand la plage est au nord ou sur le côté du plateau, par un escalier de côté. `plage_apercu.png` en montre une (`style_plage`). À faire en `medium` : en `small` la plage n'a pas la place, en `large` elle ne s'atteint pas toujours |

Les autres styles que le contrôleur connaît — `forest`, `fields`, `village`, `city` — ne s'inventent pas encore : le
générateur le dit et s'arrête.

**`galerie/` montre dix mondes finis**, un par fichier, de styles et de caractères différents, chacun avec son
aperçu : six routes (plaine, forêt, étangs, anneau, île, couloir du nord au sud), une route de montagne en terrasses,
une route côtière, deux plages.

| `shape` | Ce que ça donne |
|---|---|
| `free` | le bruit décide de tout (le défaut) |
| `island` | la terre au milieu, la mer tout autour |
| `ring` | un anneau de terre autour d'un lac — ou d'un massif, avec `core = "mountain"` |
| `plain` | de la terre presque partout, fermée par une lisière |
| `coast` | la mer d'un côté (`sea = "north"`, `"south"`, `"west"`, `"east"`), la terre de l'autre |
| `bay` | la mer entre par un côté (`sea`) et creuse la carte |
| `corridor` | une route comme celles de Johto : un couloir entre deux murs de forêt (`axis = "vertical"` ou `"horizontal"`), qui serpente par un ou deux détours et ne s'élargit qu'en poches — avec une mare dans l'une d'elles |
| `archipelago` | des îlots |

| `character` | Ce que ça change |
|---|---|
| `rocky` | de la montagne sur les hauteurs, des blocs, plus de rochers en mer |
| `sandy` | de larges plages, plus de palmiers et de coquillages |
| `wooded` | beaucoup de forêt, et une lisière qui ferme la carte |
| `open` | peu de forêt, de grandes pelouses |
| `grassy` | de grandes taches de hautes herbes |
| `flowery` | plus de fleurs |
| `wet` | plus d'eau |
| `jagged` | des rives déchiquetées |
| `smooth` | de grandes courbes calmes |

D'où ils viennent : des cartes d'exemple (une plaine de champs et de bosquets, une côte avec sa baie et sa grande
plage, une route en couloir fermée par la forêt) et de ce que les planches du décor savent dessiner. Ce qu'on y voit
et que le générateur ne fait pas encore : les champs clôturés, les mares, les grottes, les herbes de plage.

## Le hasard — `[seed]`

| Réglage | |
|---|---|
| `world` | la graine du monde : la même redonne la même carte, au pixel |
| `relief`, `climate`, `grass`, `paths`, `trees`, `decor`, `shore` | une graine par couche. Sans elle, la couche tire la sienne de `world`. En donner une change cette couche seule : `decor = 5` déplace les fleurs sans toucher au relief |

## Le relief — `[relief]`

| Réglage | Défaut | |
|---|---|---|
| `scale` | 16 | la taille des grandes formes, en cases. Petite : des confettis ; grande : de vastes plaines et de grands lacs |
| `octaves` | 4 | le nombre de couches de détail sur les contours |
| `persistence` | 0.5 | le poids de chaque couche de détail par rapport à la précédente : plus haut, des rives plus déchiquetées |
| `lacunarity` | 2.0 | la finesse de chaque couche par rapport à la précédente |
| `water` | 0.34 | le seuil sous lequel c'est la mer (le relief va de 0 à 1) |
| `sand` | 0.42 | le seuil sous lequel c'est le sable ; au-dessus, l'herbe |
| `beach` | 3 | la largeur d'une plage, en cases depuis l'eau : au-delà, le sable redevient de l'herbe (`sandy` : 6) |
| `terrace` | 0.80 | au-dessus de 1, aucune butte : la carte reste plate |
| `pond_max` | 150 | la taille, en cases, jusqu'où une eau dans les terres est un **étang à plat** (au niveau de l'herbe, avec sa berge et ses nénuphars). Jusqu'à près du double elle l'est encore, en perdant sa case de rive ; au-delà c'est un grand lac, avec ses falaises et sa plage. 0 : jamais d'étang à plat |
| `mountain` | 2.0 | le seuil au-dessus duquel c'est la montagne (2 : jamais) |
| `island` | false | le relief retombe vers la mer en approchant du bord : une île |
| `smooth` | 2 | passes de lissage : une case isolée prend le terrain de ses voisines |

## Le climat — `[climate]`

Un second bruit, l'humidité, croisé avec le relief : sur l'herbe, là où elle dépasse `forest` pousse la forêt.

| Réglage | Défaut | |
|---|---|---|
| `scale` | 12 | la taille des massifs |
| `forest` | 0.56 | le seuil d'humidité de la forêt : plus bas, plus de forêt |

## La végétation — `[vegetation]`

| Réglage | Défaut | |
|---|---|---|
| `tall_grass` | 0.10 | la part de l'herbe couverte de hautes herbes |
| `tall_grass_scale` | 6 | la taille de leurs taches |
| `decorations` | 0.06 | la chance d'une petite fleur sur une case de pelouse |
| `blooms` | 5 | le nombre de massifs de grandes fleurs |
| `tree_spacing` | 4 | l'écart entre deux troncs. 4 : une forêt fermée ; plus : on passe entre les arbres |
| `tree_dark` | 0.15 | la part d'arbres foncés |
| `palms` | 2 | palmiers par plage |
| `sea_rocks` | 0.02 | la chance d'un rocher sur une case de pleine mer |
| `shells` | 16 | un coquillage pour tant de cases de sable sec |

## La jouabilité — `[gameplay]`

| Réglage | Défaut | |
|---|---|---|
| `path_width` | 3 | la largeur des chemins tracés entre les sorties et les maisons |
| `poi_radius` | 2 | le rayon laissé libre autour de chaque point d'intérêt : ni arbre, ni hautes herbes |
| `close_edges` | true | fermer le bord de la carte partout où ce n'est pas une sortie |
| `frame` | 7 | l'épaisseur de la ceinture de terre et de forêt qui fait le tour de la carte : la mer ne touche pas le bord |
| `items` | 4 | le nombre d'objets à ramasser, cachés dans les recoins |
| `bridge_max` | 18 | la longueur d'un pont, en cases, au plus : au-delà, une langue de terre vaut mieux qu'un tablier de trente cases |
| `path` | `"dotted"` | le chemin n'est dessiné qu'aux sorties, devant ce qui compte (porte, pont, escalier) et par tronçons : entre eux on marche dans l'herbe. `"full"` : une piste continue d'un bout à l'autre |
| `grass_bars` | 4 | le nombre de plaques de hautes herbes posées **en travers du trajet**, d'un mur à l'autre (une de plus par 3000 cases de carte) ; 0 : aucune |
| `ledges` | 8 | le nombre de rebords au plus (un pour 90 cases où l'on marche) |

Et dans `[vegetation]` : `border_forest` (une lisière d'arbres le long des bords), `boulders` (la chance d'un bloc sur la montagne).

## Ce qu'on place

| Table | Champs |
|---|---|
| `[map]` | `name`, `theme`, `location`, `banner`, `music`, `wild` (la taille se dit dans `[style]`, ou ici : `size = [largeur, hauteur]`) |
| `[[exit]]` | `side` (`north`, `south`, `west`, `east`), `at` (de 0 à 1, le long du bord) **ou `cell`** (la colonne ou la rangée exacte de son milieu : la terre s'y fait, la sortie ne se déplace pas), `name`, `scene`, `door` |
| `[seam]` | la couture avec la carte du sud : `high` (les colonnes où sa terre est un cran plus haut que sa sortie — ses falaises d'herbe continuent ici sur huit ou neuf rangées, puis se referment), `phases` (la trame de ses arbres, zone par zone : la forêt d'ici la continue), `trees` (ses arbres que le bord coupe : leur autre moitié est dessinée ici). Aucun autre arbre n'est coupé par ce bord |
| `[[shore]]` | l'eau de la carte voisine arrive à ce bord : `side`, `from` et `to` (les colonnes ou rangées qu'elle prend), `depth` (jusqu'où elle entre, 12 par défaut). Elle continue ici, puis le relief reprend la main |
| `[[house]]` | `name`, `kind`, `near = [x, y]` (de 0 à 1 dans la carte), `scene`, `door` |

**Prolonger une carte.** `neighbor.py` lit le bord d'une carte et écrit ce qu'il faut coller dans le monde de sa
voisine — la sortie à la case près, l'eau, la couture :

```
python3 tools/mapgen/neighbor.py tools/mapgen/plans/route_1_bis.toml north
```

`route_nord.toml` est la route au nord de la Route 1, faite ainsi : même largeur (69 cases), sa sortie du sud sous
la sortie du nord de la Route 1, la mer qui continue des colonnes 28 à 68, les deux talus de part et d'autre du chemin
qui se prolongent, et la forêt sur la même trame. `route_nord_et_route_1.png` colle les deux cartes : **c'est sur
cette image, agrandie à la couture, qu'on juge le raccord**. Ce qui ne se suit pas encore : le contour de l'eau
profonde, décalé d'une colonne. Et seul le cas « la voisine est au sud » est fait.

Le générateur cherche la place la plus proche de ce qu'on demande où la chose tient : une sortie en plein plateau,
une maison sur l'herbe, loin de la falaise et des buttes. Sans `[[exit]]`, il en ouvre deux tout seul.

## Les règles qu'il applique

Il ne tire pas une carte au hasard pour la juger ensuite : chaque étape applique les règles de
[`docs/mapping.md`](../../../docs/mapping.md), et sonde le constructeur pour raisonner sur la carte telle qu'elle
sera dessinée.

| Étape | Ce qu'elle garantit (la lettre est la section de `mapping.md`) |
|---|---|
| Le cadre | la terre va jusqu'au bord, la mer ne le touche pas ; une ceinture de forêt de trois arbres d'épaisseur (A) |
| Le relief | aucun bras d'eau trop étroit pour ses deux falaises, **les eaux dans les terres à plat, en étangs** (O), aucune mare de moins de douze cases, aucun sable sec, des plages de deux cases (G), jamais plus de six cases de bord en ligne droite (C), deux ou trois buttes trapues et boisées (D) |
| Les chemins | trois cases de large, aux bords qui ondulent, dessinés par tronçons — aux sorties, devant ce qui compte, et de loin en loin (N) ; chaque sortie et chaque porte reliée au départ — par un pont au point le plus étroit (O), d'île en île s'il le faut, un escalier vers la plage, de face ou de côté, taillé s'il n'y a pas de bord droit (D), deux plages réunies en rognant le cap qui les sépare (J), un étang comblé s'il barre le passage, un détour par la lisière, et en tout dernier recours une langue de terre jetée au plus court — le générateur le dit |
| La végétation | des bosquets de quatre arbres au moins, des arbres de butte qui tiennent tout entiers sur leur butte, quelques petits sapins en décor au bord des bois — jamais pour boucher une lisière (D, E), des hautes herbes par plaques de 10 à 40 adossées à un obstacle, jamais en rectangle, jamais devant une porte, **quelques-unes en travers du trajet, d'un mur à l'autre**, pour un sixième au moins de ce qu'on foule (M), des fleurs par touffes de deux ou trois, une pour 15 à 60 cases (Q), aucune pelouse nue de plus de 4 × 4 (B), un bois sur toute terre où l'on n'ira pas |
| Les rebords | des **allées de côté** : deux arbres font un îlot, derrière lui une allée de trois cases contre un mur d'arbres, barrée d'un rebord (vers le sud ou vers l'est) — on y saute dans un sens, on fait le tour dans l'autre. Plus ceux que le terrain offre : de trois à huit cases, les deux bouts contre un arbre, une butte ou une berge, jamais sur le seul passage (P) |
| Les objets | un panneau à chaque entrée, trois objets au moins dans les recoins, jamais derrière une cime ni dans un goulet (K) |

## Ce que ça vaut, mesuré

`sweep.py` invente des mondes sur des graines qu'on lui donne — huit formes de route et la plage, trois tailles, six
caractères — et relève le taux de chacun :

```
python3 tools/mapgen/sweep.py 29,404,6000,90
```

Au 18/11/2026, dernier balayage (après les étangs à plat, les routes façon Johto et la montagne en gradins), sur 33
mondes de graines jamais regardées — 24 routes, 3 plages, 3 routes côtières, 3 routes de montagne : **33 jouables, 33 à
85 % ou plus, taux moyen 96 %**, le plus bas à 86 %. Ce n'est pas une garantie : dans la même journée, deux balayages
ont encore sorti un monde injouable chacun, pour deux raisons nouvelles — un arbre planté sur le trajet en fermant la
lisière, des terrasses sur une carte trop petite pour elles. Les deux sont corrigées. **Après toute retouche de `worldgen.py`, balayer des graines neuves** : celles sur lesquelles on vient
de corriger ne prouvent rien — chaque balayage de ce jour-là a sorti un défaut que le précédent n'avait pas vu.

Un taux élevé ne dit pas que la carte est belle : il dit qu'aucune faute mesurable n'y est. Le reste se juge sur
l'aperçu, jonction par jonction.

## Ce qu'il ne fait pas encore

- **Les styles autres que la route et la plage** : forêt profonde, champs, village, ville côtière.
- **Sur une plage** : les herbes de plage et le tablier d'herbe au pied de la forêt (le décor et le constructeur ne
  les ont pas), les chaînes de rochers en arc autour d'un îlot, une maison sur le sable.
- **Sur une route**, la mer ne touche jamais le bord : les passes barrées de rochers (A) sont à faire.
- Un plateau sous chaque maison, la montagne à gradins, les rebords, les clôtures, les personnages.
- Quand ni pont ni escalier ne relie une sortie, le chemin fait le tour par la lisière : la ceinture de forêt y est
  plus mince, et le générateur le dit.
