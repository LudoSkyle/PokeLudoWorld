# Écran du Pokédex

L'habillage est le **« Custom Legends-inspired Pokedex UI »** de
**delusionsofgrandr**, un jeu d'images pour Pokémon Essentials « conçu autour
de la mise en page d'origine d'Essentials ». L'archive est gardée telle quelle
dans `source/` (hors du jeu : `.gdignore`), avec son `credit.txt` ; on en sort
ce dont l'écran se sert :

| Fichier | Ce que c'est |
|---|---|
| `bg_list.png` | le fond de la liste, 512 × 384 |
| `bg_info.png` | le fond de la fiche, 512 × 384 |
| `page_info.png` | l'onglet « INFO », 86 × 28 : éteint en haut, allumé en bas |
| `icon_own.png` | la marque d'une espèce prise, 28 × 28 |
| `icon_types.png` | les étiquettes des types, 96 × 32 chacune, dans l'ordre d'Essentials |

Trois images que l'archive ne redessine pas viennent du kit de **Pokémon
Essentials v21.1** (Maruno et l'équipe d'Essentials), `Graphics/UI/Pokedex/` :

| Fichier | Ce que c'est |
|---|---|
| `cursor_list.png` | le cadre rouge de la ligne choisie, 244 × 44 |
| `icon_seen.png` | la marque d'une espèce seulement vue, 28 × 28 |
| `icon_slider.png` | l'ascenseur de la liste : ses deux flèches et sa boîte |

Restent dans `source/` pour le jour où ils serviront : les onglets et les
fonds des zones et des formes (`page_area`, `page_forms`, `bg_area`,
`bg_forms`, `overlay_area`…), les flèches d'onglet (`page_arrows`), le menu
des Pokédex (`bg_menu`).
