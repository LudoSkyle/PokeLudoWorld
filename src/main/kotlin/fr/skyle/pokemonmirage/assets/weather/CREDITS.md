# Météo

Les 23 images de ce dossier viennent de **Pokémon Essentials v21.1**
(2023-07-30), dossier `Graphics/Weather` du kit. Essentials est un kit de
création communautaire (Flameguru, Poccil, Maruno et ses contributeurs) ; ses
graphismes de météo sont repris des jeux de Game Freak.

Le kit n'est pas dans le dépôt : il a été téléchargé par Ludovic le 16/11/2026
et seules ces images en ont été tirées.

- `sources/` garde les originaux **tels quels**. Godot ignore ce dossier
  (`.gdignore`) et le jeu ne les lit jamais.
- Les images d'à côté en sont la **réduction de moitié**, fabriquée par
  `tools/weather_sheets.py`. Les originaux sont dessinés pour des cases de
  32 px en pixels doublés — chaque bloc de 2 × 2 est d'une seule couleur — ; on
  en garde un pixel par bloc, sans aucune perte. Relancer le script redonne
  exactement les mêmes fichiers.

| Fichier | Taille en jeu | Ce que c'est |
|---|---|---|
| `rain_1-3.png` | 8×32 à 16×64 | les trois longueurs de goutte, penchées d'un quart du haut-droite vers le bas-gauche |
| `rain_4.png` | 8×8 | l'éclaboussure au sol d'une goutte |
| `storm_1-3.png` | 64×64 à 96×96 | les traînées de l'averse, à 45° |
| `storm_4.png` | 16×8 | son éclaboussure |
| `hail_1-3.png` | 8×8 | les flocons, de la croix au gros grêlon |
| `blizzard_1-4.png` | 8×8 | les flocons du blizzard |
| `blizzard_tile.png` | 128×128 | sa nappe, tuilable, qui glisse par-dessus |
| `sandstorm_1-4.png` | 8×8 | les grains de sable |
| `sandstorm_tile.png` | 128×128 | la nappe de sable, tuilable |
| `fog_tile.png` | 64×64 | la nappe de brouillard, tuilable |
| `fog_tile_2.png` | 64×64 | une seconde nappe de brouillard, que rien n'utilise encore |

Quel temps prend quelle image, à quelle vitesse : [docs/weather.md](../../../../../../../docs/weather.md).
