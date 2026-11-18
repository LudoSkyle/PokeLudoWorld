# Décors

| Fichier | Contenu | Origine |
|---|---|---|
| `bell_stand.png` | le socle de la cloche, 96×48 : **vide** à gauche, **avec sa cloche** à droite (48×48 chacun) | découpé dans le tileset ci-dessous |
| `footprints.png` | les traces de pas laissées dans le sable, 64×8 : huit cases de 8 px, une par direction et par pied | fabriqué par `tools/footprint_tiles.py`, **dessiné de toutes pièces** : une marque de 3×6 pixels tournée et retournée, en noir plein — c'est le jeu qui règle son opacité |
| `island.png` | les tuiles de l'île que l'atlas n'a pas, 256×112 : pontons à rambardes, planches de bout, petits rochers dans l'eau ; escaliers à poteaux, parasols, serviettes, caisses, pot de fleurs, Poké Ball posée au sol, bancs de bois | fabriqué par `tools/island_tiles.py`, aucun pixel dessiné à la main : trois rangées **dérivées de `environments.png`**, le reste **découpé dans `sources/town_compilation.png`** (auteur à retrouver), sauf la Poké Ball (`sources/public_indoor.png`) et les bancs de bois (recalés depuis `environments.png`) |
| `route.png` | les tuiles de la route du nord, 256×256 : sable, eau à deux teintes, falaises à dessus de roche et d'herbe, pistes, dallage, fleurs, hautes herbes, escalier de pierre, arbres, sapin, arbuste, rochers, ponts de planches, rebords de roche | fabriqué par `tools/route_tiles.py`, aucun pixel dessiné à la main : **découpé dans `sources/town_compilation.png`** (auteur à retrouver), ombres translucides comprises ; ce que cette planche n'a pas — centre des pistes, ponts, rebords, rochers de la rivière — est **découpé dans la carte d'exemple** `tools/maps/route_1/reference.png`, fournie par Ludovic le 17/11/2026 (auteur de la carte inconnu) ; les deux états écartés des hautes herbes sont dérivés de la touffe |
| `village.png` | les maisons de l'île de départ, 288×144 : deux huttes de chaume (porte à gauche, porte à droite) et la grande maison de chaume, chacune avec son ombre | fabriqué par `tools/village_tiles.py`, aucun pixel dessiné à la main : **découpé dans `sources/town_compilation.png`** (auteur à retrouver), ombres translucides comprises |
| `ice_cavern.png` | la glace d'une grotte, 240×256 : **la planche source telle quelle** sur ses onze premières colonnes — le sol bleu-gris et la glace lisse (deux matières à bords), le grand plateau et sa face de deux rangées, le petit plateau, le liseré du vide, les rochers —, puis l'échelle, le trou à échelle et deux cailloux retournés dans quatre colonnes de plus | fabriqué par `tools/ice_cave_tiles.py`, aucun pixel dessiné à la main : **repris de `sources/ice_cave.png`** (le kit de grotte de glace de Phyromatical) sans rien déplacer ; l'ombre portée de l'échelle — une ombre de planche de présentation — n'est pas reprise. La façon de l'employer est lue sur une carte du même auteur, `tools/maps/ice_cave/reference.png` (« Old n random mountain entrance », Phyromatical, DeviantArt), fournie par Ludovic le 18/11/2026 |
| `cavern.png` | la roche d'une grotte, 240×96 : la paroi en gradins et ses coins, le vide et son liseré, un bassin dans sa berge, une plaque de sol sombre, le sol, stalagmite, rochers, gros bloc, et **une échelle de bois** | fabriqué par `tools/cavern_tiles.py`, aucun pixel dessiné à la main : **découpé dans `sources/cliffs_caves.png`** (le kit de grotte brune), sur la grille de 16 — **sauf l'échelle**, découpée dans `sources/ice_cave.png` : aucun des huit kits de falaises n'en a, et comme c'est du bois et non de la roche, c'est la même dans les deux teintes de grotte |

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
| `cliffs_caves.png` | 800×1248 | « Evolina mountains, full set » : falaises, parois et entrées de grotte en huit teintes (terre, neige, sable, roche rouge, glace…), chacune avec son vide, son bassin, ses rochers et ses stalagmites. **`cavern.png` en vient** | **Phyromatical**, DeviantArt (identifiant `dasvc37` — le même auteur que la planche de la Route 1) | `dasvc37-f67540e8-…png` ; retéléchargée le 18/11/2026 sous son nom complet, `dot_day24_evolina_mountains_full_set_by_phyromatical_dasvc37.png` : le même fichier, à l'octet près |
| `stone_ruins.png` | 464×352 | murs, arches et escaliers de ruines en pierre claire | inconnu (DeviantArt) | `das05e7-f87191b8-…png` |
| `autumn_village.png` | 384×400 | arbres d'automne, deux maisons, une boutique, falaises | **Phyromatical**, DeviantArt | `dot_day5_gen_4_halloween_by_phyromatical_daqrvl5.png` ; retéléchargée le 18/11/2026 sous le même nom : le même fichier, à l'octet près |
| `campground.png` | 960×912 | camping : tentes, caravanes, voitures, canoës, feux de camp, totems, concours de capture d'insectes | **TerribleJared**, [DeviantArt](https://www.deviantart.com/terriblejared/art/Campground-And-Bug-Catching-Contest-Tiles-1355310886) | `dmex0km-a1fcf3c0-…png` |
| `town_compilation.png` | 2240×2400 | grande compilation de style DS : arbres de toutes saisons, sols, eaux, falaises, **escaliers à poteaux**, ponts, clôtures, mobilier de rue (bancs, lampadaires, parasols, étals), bateaux, et plus d'une centaine de bâtiments | inconnu (DeviantArt, identifiant `d5xdb0y`) | `d5xdb0y-7cca5199-…png` |
| `seasons_trees_ponds.png` | 960×800 | arbres en huit teintes (été, automne, neige), mares et falaises par saison, quatre maisons à toit rouge | inconnu (DeviantArt, identifiant `ddi8611`) | `ddi8611-3d98db15-…png` |
| `public_indoor.png` | 960×960 | intérieurs : sols, murs, escaliers, meubles, électroménager, tapis | **ChaoticCherryCake**, DeviantArt (« Public Indoor Tileset from Public Tiles ») | `public_indoor_tileset_from_public_tiles_by_chaoticcherrycake_d801ty3.png` |
| `ice_cave.png` | 336×336 | **grotte de glace**, relevée case par case pour `ice_cavern.png` : paroi de glace 3×3 et ses coins rentrants, le vide et ses coins, un bassin d'eau sombre, une plaque de glace mate, une plaque de **glace lisse striée**, deux petits rochers, un gros bloc, une colonne de glace de 22 px, de grandes stalagmites, une bouche de grotte, des liserés de rebord en U, **une échelle de bois** (1 × 2), **un trou à échelle** vu de dessus, **deux passerelles de planches**, un coffre. **Pas une seule marche d'escalier** | **Phyromatical**, DeviantArt (« DOT Day 17 — Evolina ice cave ») | `dot_day17_evolina_ice_cave_by_phyromatical_das20xd.png` |
| `snow_trees.png` | 240×240 | **neige** : quatre sapins enneigés en deux tailles, buissons sous la neige, sols de neige et de glace, rochers coiffés de blanc, cadres de bois | **Phyromatical**, DeviantArt (« Tons of tileset 5/10 — cool Gaia tiles ») | `tons_of_tileset_5_10_cool_gaia_tiles_by_phyromatical_d81nzad.png` |
| `hgss_mountains.png` | 336×256 | montagnes et rochers du style HGSS : parois en plusieurs teintes, entrées de grotte, gros rochers, cailloux, cristaux bleus, ce qui ressemble à des échelles | **thunderdove**, DeviantArt (la casse du nom est celle du fichier) | `hgss_tileset_mountains_rocks_by_thunderdove_d3bpz02.png` |
| `shining_grove.png` | 224×384 | bosquet d'automne : arbres dorés et roux de trois tailles, falaises à dessus doré, herbe, mare, sable | **Phyromatical**, DeviantArt (« Shining grove tileset mix ») | `shining_grove_tileset_mix_by_phyromatical_d96hjkz.png` |
| `volcano.png` | 368×320 | volcan : roche brune en gradins, coulées de lave, bassins de lave, entrées de grotte, rochers calcinés, arbres morts | **Phyromatical**, DeviantArt (« DOT Day 23 — alternate volcano tiles ») | `dot_day23_alternate_volcano_tiles_by_phyromatical_dasqpje.png` |
| `dark_ruins.png` | 384×400 | ruines sombres : arbres noirs, rochers gris-violet, murs et dallages de pierre violette, fenêtres, arches, un tonneau, et ce qui ressemble à une échelle et à des marches | **Phyromatical**, DeviantArt (« DOT Day 18 — dark ruins tileset ») | `dot_day18_dark_ruins_tileset_by_phyromatical_das9141.png` |
| `water_dungeon.png` | 400×368 | donjon d'eau : murs et dallages turquoise, bassins et canaux, piliers, ponts, arche, et ce qui ressemble à une volée de marches | **Phyromatical**, DeviantArt (« DOT Day 4 — water dungeon tileset ») | `dot_day4_water_dungeon_tileset_by_phyromatical_daqn9je.png` |
| `bridgeton.png` | 496×432 | maisons à toit d'ardoise (dont une à colombages et un porche à deux corps), **ponts de pierre**, dallages, arbres et buissons verts | **Phyromatical**, DeviantArt (« DOT Day 6 — Bridgeton tileset ») | `dot_day6_bridgeton_tileset_by_phyromatical_daqsf4z.png` |

Les huit dernières ont été téléchargées par Ludo le 18/11/2026. Deux autres
planches du même lot n'ont **pas** été rangées : elles étaient déjà là sous un
autre nom, à l'octet près — `dot_day24_evolina_mountains_full_set` est
`cliffs_caves.png`, et `dot_day5_gen_4_halloween` est `autumn_village.png`.

**Droits d'usage à connaître.** `dawn_desert.png` porte la mention « Please
Do only use for Pokemon Dawn » : son auteur la réserve à son propre jeu, et les
deux grandes planches portent le logo du même projet. Ludovic a choisi de bâtir
les cartes sur les planches de The-Red-eX (15/11/2026) ; créditer l'auteur est
le minimum. Les pages d'origine de `cliffs_caves.png`, `stone_ruins.png`,
`town_compilation.png` et `seasons_trees_ponds.png` sont à retrouver pour
pouvoir créditer leurs auteurs. **Piste pour `stone_ruins.png`** : son
identifiant `das05e7` est du même lot d'envoi que `das20xd`, `das9141` et
`dasqpje`, tous trois de la série « DOT Day » de **Phyromatical** — à
confirmer sur sa galerie avant de l'écrire comme un crédit.

**Le jeu ne lit jamais une planche de `sources/`.** Ce sont des planches de
présentation : fond blanc opaque, éléments posés hors grille. Ce qu'on en
prend est sorti à part — la règle est dans
[docs/tilesets.md](../../../../../../../../docs/tilesets.md), « Prendre un
élément dans une planche source ».
