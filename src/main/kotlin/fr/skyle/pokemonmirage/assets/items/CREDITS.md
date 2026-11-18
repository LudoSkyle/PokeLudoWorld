# Icônes d'objets

**Un fichier par icône**, en quatre dossiers sous `icons/` :

| Dossier | Icônes | Contenu |
|---|---|---|
| `icons/named/` | 938 | les objets officiels dont on connaît le nom (908 objets) : `potion.png`, `master_ball.png` |
| `icons/unnamed/` | 252 | les objets officiels dont on n'a pas le nom, sous le numéro de leur case : `07_F_2_fan.png` |
| `icons/invented/` | 34 | les objets inventés par Kryptonlion ; le jeu ne les lit pas |
| `icons/custom/` | 2 | **les icônes faites pour ce jeu**, et elles seules : les deux cloches |

Les icônes font 24 × 24 sur fond transparent ; celles dont le dessin est plus
grand font 32 × 32 (48 dans `named/` : les cannes, les Z-cristaux du sac, les
poches…). **Le sac attend du 24 × 24** : un objet du catalogue ne prend pas
une icône de 32.

**Le nom d'un fichier dit ce qu'est l'icône, jamais à quoi le jeu
l'emploie.** Le jeu se sert de trois icônes sans nom — le ruban de la Veillée
(`unnamed/07_F_2_fan.png`, un dessin de fan, crédité ici), la flèche
« Retour » du sac (`unnamed/00_F_F_special.png`) et le point d'interrogation
d'un objet sans icône (`unnamed/frlg_227.png`) : elles gardent le nom de leur
case, et le code les désigne par ce fichier.

## D'où elles viennent

**La planche de Kryptonlion est la source des images** : l'« Ultimate Pokémon
ItemDex » (DeviantArt), toutes générations, **exportée en entier**. Ses 1449
cases dessinées portent 1215 dessins différents — 234 cases répètent
exactement le dessin d'une autre (un objet qui reprend l'icône d'un autre),
et ne donnent qu'un fichier.

| Source | Ce qu'on en garde |
|---|---|
| `sources/itemdex_kryptonlion.png` | **tout** : 938 dessins nommés dans `named/`, 243 dans `unnamed/`, 34 dans `invented/` |
| pokesprite et PokeAPI (hors du dépôt) | **les noms** de 998 cases — voir plus bas |
| `sources/essentials/` — Pokémon Essentials v21.1 | les noms de 8 cases ; plus aucune image |
| `sources/frlg.png` — Rouge Feu / Vert Feuille | 9 cases sans nom, dont le point d'interrogation du sac, et le nom de 15 CT |
| `sources/custom.png` | les deux cloches faites pour le jeu, dans `custom/` |

Ce qu'on garde d'une icône qui **ne vient pas** de la planche de Kryptonlion :

- la planche a exactement ce dessin, sous ce nom ou un autre → on ne la garde
  pas ;
- elle porte un nom que la planche n'a pas → on la garde, sous ce nom ;
- la planche a ce nom, et les deux dessins se ressemblent (même objet, teinte
  ou contour à peine différents) → **on ne garde que celui de Kryptonlion** ;
- la planche a ce nom, mais c'est un autre dessin → on garde les deux, le
  second sous `<nom>-<origine>.png` ;
- elle n'a pas de nom (une case de FRLG) → on la garde dans `unnamed/` si la
  planche n'a pas ce dessin.

Sont ainsi écartées les 445 icônes du kit et 258 cases de FRLG : la planche a
le même objet. `python3 tools/item_icons.py -v` les liste.

## La planche de Kryptonlion

`sources/itemdex_kryptonlion.png` : seize blocs numérotés `00` à `0F`, chacun
de 16 × 16 cases de 32 × 32 étiquetées en hexadécimal. Une case se désigne
comme sur la planche : `00:5:B` est le bloc `00`, rangée `5_`, colonne `_B`.
Le dessin tient presque toujours dans les 24 × 24 du centre.

**Le fond de chaque case dit sa famille**, d'après la légende en bas de la
planche. C'est elle qui trie les cases sans nom :

| Fond | Légende | Où va la case sans nom | Sans nom |
|---|---|---|---|
| jaune | objet officiel, icône officielle, couleurs récentes | `unnamed/…_official.png` | 0 |
| orange | objet officiel, icône officielle, anciennes couleurs | `unnamed/00_5_B_old_colors.png` | 7 |
| bleu | objet officiel, icône officielle recolorée | `unnamed/…_recolored.png` | 0 |
| brun | objet officiel, **dessin d'un fan** — *« Please give credit »* | `unnamed/07_F_2_fan.png` | 212 |
| brun foncé, noir, blanc | icônes de poche du sac, flèche | `unnamed/…_special.png` | 24 |
| sarcelle | **objet inventé** par Kryptonlion — *« Please ask for permission »* | `invented/` | 34 en tout |
| lavande | objet inventé, aux couleurs officielles : une CT ou une CS pour chaque type | `invented/` | |

Les teintes claires (jaune clair, orange clair…) sont les « Repeated » : un
objet qui reprend l'icône d'un autre. Ne sont pas exportées les cases vides
(vertes) ni les 189 cases grises « Work in Progress », qui ne portent qu'une
étiquette en attente de dessin.

- **Utiliser un dessin de fan** (`_fan`) : créditer Kryptonlion.
- **Utiliser un objet inventé** (`invented/`) : lui demander la permission
  d'abord. Le script refuse de nommer une case sarcelle.
- Les cases lavande qui sont, pixel pour pixel, une CT ou une CS officielle
  (22 sur 25) portent un nom : `machine_fire.png`, `machine_hm_water.png`.
- Quelques dessins s'étalent sur plusieurs cases (bloc `02`, rangée `3`) :
  chaque case est exportée telle quelle, en morceaux.

### Les noms : `sources/itemdex.txt`

La planche ne porte aucun nom. `itemdex.txt` en donne à 1021 cases — une
ligne par case : la case, puis le nom de l'objet officiel qu'elle représente.
On n'y écrit jamais le nom qu'un objet porte dans notre jeu.

- **961 cases sont, pixel pour pixel, une icône nommée de pokesprite**
  ([github.com/msikma/pokesprite](https://github.com/msikma/pokesprite),
  dossier `items/`, version du 22/07/2022 : 1074 icônes officielles des
  générations 3 à 8, classées par catégorie). Le nom est celui de pokesprite,
  écrit à notre façon : `ball/master` devient `master_ball`, `berry/razz`
  `razz_berry`, `tm/fire` `machine_fire`. Une ancienne version d'une icône
  porte sa génération : `town_map_gen3`, `devon_scope_gen3`.
- **6 cases sont, pixel pour pixel, une icône nommée de PokeAPI**
  ([github.com/PokeAPI/sprites](https://github.com/PokeAPI/sprites), dossier
  `sprites/items/`) : les anciennes couleurs de `red_orb`, `blue_orb` et
  `machine_hm_fighting`, `data_card`, `sparkling_stone`, `retro_mail`.
- **15 cases sont, pixel pour pixel, une CT de notre planche de FRLG** : les
  `machine_<type>-old_colors`, au disque plus petit.
- **31 cases** ont exactement la silhouette d'une icône de pokesprite ou de
  PokeAPI, à quelques teintes près, et ont été vérifiées à l'œil une à une :
  les quatorze objets du Lanceur Miracle (`wonder_launcher_potion`…),
  `dire_hit_1`, les anciennes couleurs de `park_ball` et `lure_ball`,
  `key_stone_gen6`, `red_orb_gen3`, `blue_orb_gen3`, `lock_capsule_gen4`,
  `travel_trunk_silver`, `lost_item`, `xtransceiver_blue`,
  `dowsing_machine_xy`, `fab_mail`, `pinap_berry_alt` (un second dessin de la
  Baie Nanana), `dark_memory`, `lift_key`, `basement_key_goldenrod`,
  `tm_case-recolored`.
- **8 cases**, qu'aucun des deux n'a, gardent le nom de l'icône de Pokémon
  Essentials dont elles ont la silhouette et les couleurs : les anciennes
  versions de `amulet_coin`, `old_rod`, `good_rod`, `super_rod`, `poke_flute`,
  `moomoo_milk`, `odd_keystone`, `dowsing_machine`.

**pokesprite et PokeAPI ne sont pas dans le dépôt** : ils n'ont servi qu'à
retrouver les noms, et leurs images sont celles de la planche. Pour refaire
la comparaison, cloner leurs dossiers d'icônes et chercher, pour chaque case,
l'icône identique.

**Ce qui reste sans nom** :

- **7 icônes aux anciennes couleurs** : trois disques qui sont sans doute les
  CS Normal, Vol et Eau de la 3ᵉ génération (`00:5:9`, `00:6:9`, `00:7:9`),
  deux CT (`00:5:8`, et `00:3:7` qui porte un pixel parasite), une plume
  (`00:5:B`) et une lettre (`0B:5:7`). Aucune source ne les a à l'identique,
  et rien ne permet de trancher entre deux candidates ;
- **212 dessins de fans**, qui n'existent dans aucune source officielle ;
- **24 icônes de poche** du sac et de service, qui ne sont pas des objets.

**Nommer une case de plus** — quand on a identifié l'objet officiel : ajouter
sa ligne à `itemdex.txt`, relancer `python3 tools/item_icons.py`. L'icône
passe de `unnamed/` à `named/`. **Se servir d'une icône sans nom ne demande
rien de tout cela** : le catalogue la désigne par son fichier,
`icon = "unnamed/07_F_2_fan"`.

## Comment `icons/` est fabriqué

`icons/` est **fabriqué** par `tools/item_icons.py` à partir de `sources/`, que
Godot ignore (`.gdignore`) et que le jeu ne lit jamais. Relancer le script
redonne exactement les mêmes fichiers, et retire ceux qu'il ne produit plus.
On ne retouche pas `icons/` à la main : on change une source, une table ou le
script. Godot n'importe pas `invented/`, qui porte un `.gdignore`.

## Les icônes du kit

`sources/essentials/` garde les 449 images de Pokémon Essentials v21.1
(2023-07-30) **telles quelles**, de 48 × 48, nommées par l'identifiant du kit
(`ANTIDOTE.png`), et son `items.txt` (`PBS/items.txt`), qui décrit les 693
objets : nom, poche, prix, description. Essentials est un kit de création
communautaire (Flameguru, Poccil, Maruno et ses contributeurs) ; ses icônes
sont celles des jeux de Game Freak. Le kit a été téléchargé par Ludovic le
16/11/2026.

**Plus aucune de ses images n'est dans `icons/`** : la planche de Kryptonlion
a chacun de ses objets, en plus récent. Il reste la source de huit noms, et
`items.txt` reste utile pour ajouter un objet au catalogue.

## La planche de FRLG

`sources/frlg.png` : les 267 icônes de Rouge Feu / Vert Feuille, 16 par
rangée, tirée de `sources/frlg_items.png` (cases espacées d'un pixel, fond
orange). `frlg.txt` nomme 215 de ses cases par leur rang, à partir de 0.

Presque tout y est écarté : la planche de Kryptonlion a le même dessin. Il en
reste neuf cases sans nom dans `unnamed/` (`frlg_204.png`…), dont
`frlg_227.png`, le point d'interrogation d'un objet sans icône.

La case 219, dont le jeu a fait sa « carte du village », est en réalité le
**Tri-Passe** : c'est `named/tri_pass.png`. Les vraies cartes sont
`town_map_gen3.png`, `town_map_gen4.png` et `town_map.png`.

## Les cloches

| Fichier | Origine |
|---|---|
| `custom/clear_bell.png` | redessinée en 24 × 22 d'après `sources/bell_pixel_art.jpg` |
| `custom/tarnished_bell.png` | la même, palette de bronze noirci et de vert-de-gris |

`sources/bell_pixel_art.jpg` est une illustration de cloche en pixel art de
30 × 28 pixels d'origine (agrandie dans un JPEG de 980 × 980), fournie par
Ludovic le 14/11/2026 sous le nom
`34206630-pixel-art-illustration-cloche-…-vectoriel.jpg`. **Auteur et page
d'origine inconnus.** La cloche a été relevée pixel par pixel, puis réduite à
24 × 22 en gardant ses sept couleurs et son trait noir.

**Ajouter une icône faite pour le jeu** : la dessiner en 24 × 24 sur fond
transparent dans la première case libre de `sources/custom.png`, lui donner
une ligne dans `sources/custom.txt`, puis relancer le script : elle sort dans
`icons/custom/`, et le catalogue la désigne par `icon = "custom/<nom>"`.
