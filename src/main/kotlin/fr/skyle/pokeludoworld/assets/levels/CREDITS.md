# Décors

| Fichier | Contenu | Origine |
|---|---|---|
| `bell_stand.png` | le socle de la cloche, 96×48 : **vide** à gauche, **avec sa cloche** à droite (48×48 chacun) | découpé dans le tileset ci-dessous |
| `footprints.png` | les traces de pas laissées dans le sable, 64×8 : huit cases de 8 px, une par direction et par pied | fabriqué par `tools/footprint_tiles.py`, **dessiné de toutes pièces** : une marque de 3×6 pixels tournée et retournée, en noir plein — c'est le jeu qui règle son opacité |
| `island.png` | les tuiles de l'île que l'atlas n'a pas, 256×112 : pontons à rambardes, planches de bout, petits rochers dans l'eau ; escaliers à poteaux, parasols, serviettes, caisses, pot de fleurs, Poké Ball posée au sol, bancs de bois | fabriqué par `tools/island_tiles.py`, aucun pixel dessiné à la main : trois rangées **dérivées de `environments.png`**, le reste **découpé dans `sources/town_compilation.png`** (auteur à retrouver), sauf la Poké Ball (`sources/public_indoor.png`) et les bancs de bois (recalés depuis `environments.png`) |

## Le socle de la cloche

La planche d'origine est `sources/bell_stand_tileset.png` (896×2048, dossier
ignoré par Godot), fournie par Ludovic le 14/11/2026 sous le nom
`dewbuse-4e75cedf-d775-4bb4-b3b7-26445f9eebf6.png`. **Auteur et page d'origine
inconnus.** La cloche sur son socle y occupe le carré de 48×48 dont le coin
haut-gauche est en `(512, 0)`.

Cette planche ne contient que la version avec cloche. La version **vide** en
est dérivée : la cloche et son attache au-dessus du linteau sont retirées, le
linteau retrouve son trait du dessous, et l'ombre portée de la cloche sur le
sable est remplacée par du sable.

## Les planches en jeu

Ce que lit le TileSet `resources/tilesets/level.tres` ([docs/tilesets.md](../../../../../../../../docs/tilesets.md)) :

| Fichier | Taille | Contenu | Origine |
|---|---|---|---|
| `environments.png` | 1504×2273, tuiles de 16 | tout l'extérieur : sols, chemins, eau, arbres, maisons, Centres, immeubles | arrivée avec le projet de référence. C'est une sélection **recalée et détourée** des planches « Pokémon Dawn » de **The-Red-eX** rangées dans `sources/` : mêmes pixels (vérifié sur quelques tuiles), mais sur une grille de 16 et sur fond transparent |
| `interiors.png` | 384×144 | meubles d'intérieur, recalés sur la grille | découpés dans `environments.png` |
| `cave.png` | 336×48 | roche de grotte nettoyée | découpée dans `environments.png` |
| `bell_stand.png` | 96×48 | socle de la cloche, vide et avec cloche | voir plus haut |

## Les planches sources (`sources/`)

Dossier ignoré par Godot (`.gdignore`) : des planches gardées **telles
qu'elles ont été téléchargées**, pour y découper les tuiles des prochaines
cartes. Aucune n'est encore lue par le jeu. Toutes sont en tuiles de 16×16
natives et à l'échelle de `environments.png` (porte d'une case).

Téléchargées par Ludo le 15/11/2026, sauf la première. **Toute planche
compatible qu'il télécharge vient ici**, pour ne pas avoir à la rechercher sur
son ordinateur : même grille de 16, même échelle (porte d'une case).

| Fichier | Taille | Contenu | Auteur | Nom d'origine |
|---|---|---|---|---|
| `bell_stand_tileset.png` | 896×2048 | village médiéval, tours, sols, sapins | inconnu | `dewbuse-4e75cedf-…png` |
| `dawn_tileset_2_5.png` | 6000×4800 | la grande planche « Pokémon Dawn » : arbres, sols, eau, falaises, grottes, ruines, mobilier urbain, et plusieurs centaines de bâtiments | **The-Red-eX** (Lukasz L.), DeviantArt | `pokemon_dawn_tileset_2_5_by_the_red_ex_d5qoi5v.png` |
| `dawn_tileset_omega_v2.png` | 4000×4000 | version antérieure de la même planche | The-Red-eX, avec Omega | `pokemon_dawn_tileset_red_ex_omega_lukasz_l_v_2_by_the_red_ex_d5n2zzz.png` |
| `dawn_desert.png` | 859×525 | désert : cactus, murs à glyphes, rochers, falaises, oasis | The-Red-eX | `desert_1_by_the_red_ex_d5qa283.png` |
| `dawn_forest_ruins.png` | 562×392 | arbres sombres, blés, pont de bois, sols, arches et colonnes en ruine | The-Red-eX | `nu_nu_nu_3_by_the_red_ex_d5qalcq.png` |
| `cliffs_caves.png` | 800×1248 | falaises et entrées de grotte en huit teintes (terre, neige, sable, roche rouge, glace…) | inconnu (DeviantArt) | `dasvc37-f67540e8-…png` |
| `stone_ruins.png` | 464×352 | murs, arches et escaliers de ruines en pierre claire | inconnu (DeviantArt) | `das05e7-f87191b8-…png` |
| `autumn_village.png` | 384×400 | arbres d'automne, deux maisons, une boutique, falaises | **Phyromatical**, DeviantArt | `dot_day5_gen_4_halloween_by_phyromatical_daqrvl5.png` |
| `campground.png` | 960×912 | camping : tentes, caravanes, voitures, canoës, feux de camp, totems, concours de capture d'insectes | **TerribleJared**, [DeviantArt](https://www.deviantart.com/terriblejared/art/Campground-And-Bug-Catching-Contest-Tiles-1355310886) | `dmex0km-a1fcf3c0-…png` |
| `town_compilation.png` | 2240×2400 | grande compilation de style DS : arbres de toutes saisons, sols, eaux, falaises, **escaliers à poteaux**, ponts, clôtures, mobilier de rue (bancs, lampadaires, parasols, étals), bateaux, et plus d'une centaine de bâtiments | inconnu (DeviantArt, identifiant `d5xdb0y`) | `d5xdb0y-7cca5199-…png` |
| `seasons_trees_ponds.png` | 960×800 | arbres en huit teintes (été, automne, neige), mares et falaises par saison, quatre maisons à toit rouge | inconnu (DeviantArt, identifiant `ddi8611`) | `ddi8611-3d98db15-…png` |
| `public_indoor.png` | 960×960 | intérieurs : sols, murs, escaliers, meubles, électroménager, tapis | **ChaoticCherryCake**, DeviantArt (« Public Indoor Tileset from Public Tiles ») | `public_indoor_tileset_from_public_tiles_by_chaoticcherrycake_d801ty3.png` |

**Droits d'usage à connaître.** `dawn_desert.png` porte la mention « Please
Do only use for Pokemon Dawn » : son auteur la réserve à son propre jeu, et les
deux grandes planches portent le logo du même projet. Ludovic a choisi de bâtir
les cartes sur les planches de The-Red-eX (15/11/2026) ; créditer l'auteur est
le minimum. Les pages d'origine de `cliffs_caves.png`, `stone_ruins.png`,
`town_compilation.png` et `seasons_trees_ponds.png` sont à retrouver pour
pouvoir créditer leurs auteurs.

**Le jeu ne lit jamais une planche de `sources/`.** Ce sont des planches de
présentation : fond blanc opaque, éléments posés hors grille. Ce qu'on en
prend est sorti à part — la règle est dans
[docs/tilesets.md](../../../../../../../../docs/tilesets.md), « Prendre un
élément dans une planche source ».
