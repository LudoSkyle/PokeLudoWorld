# Pokémon

## En jeu (`overworld/`)

Un fichier par Pokémon qu'on voit sur une carte : un bloc de 64 × 128 sur fond
transparent, deux colonnes de quatre images de 32 × 32 — à gauche deux images
de dos puis deux de face, à droite deux vers la gauche puis deux vers la
droite.

| Fichier | Pokémon | Origine |
|---|---|---|
| `wingull.png` | Goélise | sorti de `sources/hgss_overworld_gen3.png` par `tools/pokemon_overworld.py` |
| `pelipper.png` | Bekipan | idem |
| `hoppip.png` | Granivol | sorti de `sources/hgss_overworld_gen2.png` par le même script |
| `skiploom.png` | Floravol | idem |
| `jumpluff.png` | Cotovol | idem |

Pour en sortir un autre : ajouter sa ligne à `WANTED` dans le script (planche,
colonne et rangée de son bloc) et le relancer.

## Les planches sources (`sources/`)

Dossier ignoré par Godot (`.gdignore`) : les planches **telles qu'elles ont
été téléchargées** par Ludo le 15/11/2026. Le jeu n'en lit aucune.

| Fichier | Contenu | Auteur | Nom d'origine |
|---|---|---|---|
| `hgss_overworld_gen1.png` … `gen4.png` | les Pokémon qui suivent le joueur dans Or HeartGold / Argent SoulSilver, générations 1 à 4, normaux et chromatiques | Game Freak ; extraits publiés sur The Spriters Resource | `DS _ DSi - Pokemon HeartGold _ SoulSilver - Overworld - Pokemon (… Generation, Overworld).png` |
| `hgss_overworld_misc.png` | formes et cas particuliers (même jeu) | idem | `… - Pokemon (Miscellaneous, Overworld).png` |
| `unova_overworld.png` | génération 5, dans le même style | **myumorph**, DeviantArt | `unova_overworlds_by_myumorph_d3cbfbw.png` |
| `unova_overworld_shiny.png` | génération 5, chromatiques | **2and2makes5**, DeviantArt | `unova_overworlds_shiny__by_2and2makes5_d51nqik.png` |
| `kalos_overworld.png`, `kalos_overworld_shiny.png` | génération 6 | **princess-phoenix**, DeviantArt ; motifs de Prismillon et version chromatique retouchés par **LunarDusk6** | `ow_gen_6_by_princess_phoenix_d8p510p.png`, `ow_gen_6_shiny_by_princess_phoenix_d929j1d.png` |
| `alola_overworld.png`, `alola_overworld_shiny.png` | génération 7 | **Princess-Phoenix, Larryturbo, Kidkatt, Zender1752, SageDeoxys** ; publiées par larryturbo, DeviantArt | `ow_gen_7_by_larryturbo_ddbjpi0.png`, `ow_gen_7_shiny_by_larryturbo_dddtd76.png` |
| `galar_overworld.png`, `galar_overworld_shiny.png` | génération 8 | **lasse00**, DeviantArt | `hgss_galar_pokemon_overworls_sprites…_by_lasse00_….png` |
| `gmax_overworld.png`, `gmax_overworld_shiny.png` | formes Gigamax | lasse00 | `hgss_gmax_pokemon_overworld_sprites…_by_lasse00_….png` |
| `hisui_overworld_shiny.png` | formes de Hisui, chromatiques | lasse00 | `hgss_hisuian_pokemon_overworld_sprites_shiny_by_lasse00_df33tfc.png` |
| `paldea_overworld.png`, `paldea_overworld_shiny.png` | génération 9 | **Darkus_Shadow, Princess-Phoenix, shaderr31, Wolfang62, CarmaNekko, EduarPokeN** ; publiées par darkusshadow, DeviantArt | `ow_gen_9_by_darkusshadow_dg06t9u.png`, `ow_gen_9_by_darkusshadow_dg06vh7.png` |
| `alcremie_overworld.png` | toutes les formes de Charmilly | lasse00 | `hgss_all_alcremie_forms_overworld_sprites_by_lasse00_df33s4p.png` |

### Les sprites de combat

Rangés avec elles, téléchargés par Ludo le 15/11/2026 : des **sprites de combat**
(face, dos, chromatiques) dans le style des jeux DS. Rien ne s'en sert encore.

| Fichier | Contenu | Auteur | Nom d'origine |
|---|---|---|---|
| `ds_style_battle/` | des Pokémon des générations 7 et 8 (n° 753 à 895, et le 577), un fichier par numéro de Pokédex : 144 images de 256 × 64 (quatre poses de 64 × 64), et 139 icônes de 32 × 64 dans `icons/` | non indiqué dans le dossier | dossier `Gen VI DS-Style 64x64 Pokemon Sprite Resource` (sous-dossier `Icon Sprites` renommé `icons`) |
| `alola_battle.png` | génération 7 | **leparagon**, DeviantArt | `genvii_ds_style_gba_sprites_by_leparagon_davylpt.png` |
| `galar_battle.png` | génération 8 | **leparagon**, DeviantArt | `genviii_ds_style_gba_sprites_by_leparagon_de3s18e.png` |
| `paldea_battle.png` | génération 9 | **imperio456**, DeviantArt | `pokemon_gen_9_by_imperio456_dgbgqty.png` |

**Ce qui manque** au 15/11/2026 : les formes de Hisui non chromatiques — seule
la planche chromatique était dans les téléchargements.
