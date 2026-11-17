# Pokédex

Deux Pokédex sont prévus (Ludovic, 17/11/2026) :

- **le national** — toutes les espèces qui existent, sans exception. Pour
  l'instant c'est **une vue de debug**, hors du jeu : elle montre tout, vu ou
  non, pour vérifier que chaque espèce est bien renseignée ;
- **le régional** — le seul qu'on ouvrira en jeu : une espèce s'y découvre une
  fois rencontrée, ses détails une fois capturée. **Pas encore fait** ; ses
  espèces seront choisies avec Ludovic. L'écran, lui, attend qu'il ait trouvé
  une interface qui convienne.

## Les données du national

`resources/pokedex/national.tsv` : une espèce par ligne, ses champs séparés par
des tabulations, dans cet ordre —

| Champ | |
|---|---|
| `number`, `id`, `generation` | le numéro national, l'identifiant (`mr_mime`), la génération |
| `name_fr`, `name_en` | le nom |
| `genus_fr`, `genus_en` | la catégorie (« Pokémon Graine ») |
| `height`, `weight` | en mètres, en kilos ; 0 si la donnée manque |
| `icon`, `overworld` | 1 si on a son icône, son sprite de marche |
| `text_fr`, `text_en` | la description, sur une ligne ; vide si elle manque |

`tools/pokedex.py` le fabrique :

```bash
python3 -I tools/pokedex.py <dossier des CSV de PokéAPI> <dossier du kit Pokémon Essentials>
```

- **Noms, catégories, taille, poids, descriptions** : les CSV du dépôt
  [PokeAPI/pokeapi](https://github.com/PokeAPI/pokeapi) (`data/v2/csv/` :
  `pokemon_species`, `pokemon_species_names`, `pokemon_species_flavor_text`,
  `pokemon`), téléchargés le 17/11/2026 (commit `7764ee08de86`). Ils ne sont
  pas versionnés : le `.tsv` l'est. La description retenue est la plus récente
  de chaque langue.
- **Icônes** : `Graphics/Pokemon/Icons/` du kit Essentials, ramenées à 32 × 32
  et rangées dans **une seule planche**, `assets/pokemon/icons.png` — une case
  de 64 × 32 par espèce (ses deux images), 25 espèces par rangée, à la place
  que donne son numéro.
- **Sprites de marche** : `tools/pokemon_overworld.py` les découpe dans les
  planches HGSS de `assets/pokemon/sources/` et les range dans **une planche**,
  `assets/pokemon/overworld.png` — une case de 64 × 128 par espèce (deux
  colonnes de quatre images de 32 × 32 : dos, dos, face, face ; gauche,
  gauche, droite, droite), à la place de son numéro. **Un gros Pokémon** n'y
  tient pas : il a son fichier dans `assets/pokemon/overworld/`, même
  disposition en 128 × 256 (Steelix, Lugia, Ho-Oh, Wailord, Kyogre, Groudon,
  Rayquaza, Dialga, Palkia, Regigigas, Giratina, Arceus). Les Pokémon du décor
  y ont aussi le leur, que lisent les volants : un bloc brut de 64 × 128, que
  la vue de debug ne montre pas — elle ne prend un fichier que s'il est plus
  large qu'une case, donc celui d'un gros Pokémon. L'outil retire de ce
  dossier tout fichier qu'il n'écrit plus.

### Lire une planche HGSS

Les espèces y sont dans l'ordre du Pokédex, un bloc de 64 × 128 chacune, **avec
des blocs en plus** qu'il faut connaître — `SHEETS`, dans l'outil, les liste :

- la **femelle** d'une espèce (un point rose ; le mâle a un point bleu), ou une
  **autre forme** (les 27 autres Zarbi, les capes de Cheniti, Motisma…) : le
  bloc qui suit, à sauter ;
- un **gros Pokémon** : quatre blocs — dos, face, gauche, droite —, deux images
  de 64 × 64 par bloc ; sur la planche de la 3ᵉ génération, deux blocs côte à
  côte, quatre rangées de deux images de 64 × 32.

Les comptes tombent juste (153, 144, 142 et 141 blocs). Pour contrôler une
découpe : poser l'icône de chaque espèce au-dessus du sprite qu'on lui a
donné, et regarder — une erreur d'un bloc décale toute la suite.

**La grille n'est pas régulière** (Ludovic, 17/11/2026 : Draco coupé de
travers, « après le numéro 200 il y en a énormément de mal découpés »). Une
colonne de 63 pixels dans la planche de la 1ʳᵉ génération, et même de 61 sur
ses deux dernières rangées seulement ; des rangées de 129 à 131 dans celle de
la 2ᵉ ; la dernière de la 3ᵉ fait 160 de haut. L'outil lit donc les **filets
de séparation** (`grid`) : les rangées, puis les colonnes rangée par rangée,
puis le haut, la largeur et la hauteur de chaque bloc.

**À l'intérieur d'un bloc non plus, rien n'est au pas** : Caratroc est posé
deux pixels plus bas (ses pattes tombaient dans l'image d'en dessous), le
profil de Suicune déborde d'un pixel sur la colonne voisine, et les images
d'un gros Pokémon sont où elles veulent. On ne coupe donc **jamais au pas** :

- un bloc ordinaire est découpé **par son contenu** (`split`) : les morceaux
  d'un seul tenant, chaque gros morceau donné à la case dont il est le plus
  près, chaque petit morceau détaché au gros le plus proche ;
- puis chaque **paire d'images d'une direction est centrée** dans sa case, pieds
  à deux pixels du bas, les deux images gardant leur écart (c'est l'animation)
  (`settle`). Des deux, **la plus basse est rangée en premier** : c'est la
  première qu'un Pokémon immobile montre, et il flotterait sinon un pixel
  au-dessus de ses voisins (121 paires inversées, sur 51 espèces) ;
- un gros Pokémon est découpé de même, bloc par bloc ; ceux de la 3ᵉ
  génération, serrés jusqu'à se toucher, par les lignes les moins remplies
  (`lanes`). Chacune de ses images est centrée pour elle-même (`settle_big`).

**Les crabes marchent de côté** : Krabby et Krabboss ont leurs deux colonnes
échangées (`sideways`).

Le contrôle qui compte est **chiffré, image par image** : aucune image vide,
aucune collée au bord, chacune centrée à trois pixels près, pieds près du bas.
Sur les 493 espèces, une vingtaine restent signalées et sont normales : des
oiseaux dont une des deux images a les ailes levées (elle est donc plus haute,
ou moins large, que l'autre). Une planche de vignettes réduites ne suffit pas :
un décalage de deux pixels ne s'y voit pas.

## Ce qui manque (17/11/2026)

`tools/pokedex.py` le redit à chaque passage, et la vue de debug le montre
espèce par espèce.

| | Manque à | |
|---|---|---|
| description en français | 127 espèces, n° 899 à 1025 | PokéAPI n'a pas de texte français pour Hisui ni pour la génération 9 |
| icône | 376 espèces, n° 650 à 1025 | le kit n'a d'icônes que jusqu'à la génération 5 |
| sprite de marche | 532 espèces, n° 494 à 1025 | les générations 1 à 4 sont découpées. Les planches des générations 5 à 9 (`unova_`, `kalos_`, `alola_`, `galar_`, `paldea_overworld.png`) ont chacune un autre format — cartes arrondies sur fond en damier pour la 5ᵉ — et restent à lire une à une |

Noms (FR et EN), catégories, taille, poids et description anglaise : complets
pour les 1025.

## La vue de debug

Menu de pause → Debug → **Pokédex national** (`PokedexDebug.kt`,
`scenes/ui/pokedex_debug.tscn`). À gauche la liste, quatorze espèces à la fois ;
à droite la fiche : icône, sprite, les deux noms, la catégorie, la génération,
la taille, le poids, les deux descriptions, et en rouge ce qui manque. Une
étoile dans la liste marque une espèce incomplète ; le titre les compte.

Haut/Bas : une espèce (en boucle) ; Gauche/Droite : dix d'un coup ; la touche
du menu referme. Le sprite de marche se montre de face, puis **tourne sur
lui-même** d'un quart de tour par seconde — face, gauche, dos, droite — pour
qu'on vérifie ses quatre côtés. Il est dessiné **à la même échelle pour tous**
(quatre pixels d'écran par pixel : un gros Pokémon est deux fois plus grand),
sur **un damier dont chaque carreau fait un pixel du sprite**, avec les deux
axes de sa case : on voit s'il est centré. `tests/run.sh ui/debug_pokedex`.
