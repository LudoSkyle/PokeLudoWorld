# Inventer une carte

Un **monde** est un fichier `<monde>.toml` : une graine et des réglages. Le générateur (`tools/mapgen/worldgen.py`)
en tire un plan — relief, plages, forêts, hautes herbes, chemins, décor — que le constructeur assemble.

```
python3 tools/mapgen/worldgen.py tools/mapgen/worlds/prairie.toml --preview /tmp/prairie.png
```

Il écrit `plans/<carte>.toml` et dit ce qui ne se rejoint pas. On change un réglage, on relance, on regarde ; quand
la carte plaît, on retouche son plan à la main s'il le faut, puis `build.py --write` en fait la scène.

```
  monde (graine, réglages)  --worldgen.py-->  plan (tout est écrit)  --build.py + décor-->  scène
        on invente                              on lit, on retouche                          on assemble
```

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
| `sand` | 0.40 | le seuil sous lequel c'est le sable ; au-dessus, l'herbe |
| `terrace` | 2.0 | le seuil au-dessus duquel l'herbe est en terrasse (2 : jamais) |
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

## Ce qu'on place

| Table | Champs |
|---|---|
| `[map]` | `name`, `size = [largeur, hauteur]`, `theme`, `location`, `banner`, `music`, `wild` |
| `[[exit]]` | `side` (`north`, `south`, `west`, `east`), `at` (de 0 à 1, le long du bord), `name`, `scene`, `door` |
| `[[house]]` | `name`, `kind`, `near = [x, y]` (de 0 à 1 dans la carte), `scene`, `door` |

Le générateur cherche la place la plus proche de ce qu'on demande où la chose tient : une sortie en plein plateau,
une maison sur l'herbe, loin de la falaise. Il relie le tout par des chemins.

## Ce qu'il ne fait pas encore

Les ponts et les escaliers quand un chemin doit franchir l'eau ou descendre à la plage (il prévient : « pas de
chemin à pied sec »), les rebords, les personnages et les objets — tout cela s'ajoute au plan à la main. Et il ferme
les bords d'une rangée de sapins, pas d'une vraie lisière.
