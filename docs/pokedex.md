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

Tout vient du **pack de données** `vendor/GameDataPacks/Gen 9/scarlet-violet`
— la base de Pokémon Studio et de PSDK (voir [CLAUDE.md](../CLAUDE.md)).
`tools/gamedata.py` en sort, pour les 1025 espèces :

```
python3 tools/gamedata.py
```

| Ce qu'il écrit | D'où, dans le pack |
|---|---|
| `resources/pokedex/national.tsv` — une espèce par ligne : numéro, `id`, génération, noms, catégories, taille (m), poids (kg), `icon`, `overworld` (1 si le fichier est là), descriptions, en français et en anglais | `Data/Studio/pokemon/*.json`, `Data/Text/Dialogs/100000` (noms), `100001` (catégories), `100002` (descriptions) |
| `assets/pokemon/overworld/<id>.png` — le sprite sur la carte | `graphics/characters/NNNN.png` |
| `assets/pokemon/icons/<id>.png` — l'icône, 64 × 32 : deux images de 32 × 32 | `graphics/pokedex/pokeicon/NNNN.png` |
| `assets/audio/cries/<id>.ogg` — le cri | `audio/se/cries/NNNN.ogg` |

L'`id` d'une espèce est son `dbSymbol` du pack (`wingull`, `ho_oh`). Les
fichiers sont **copiés tels quels**, un par espèce, jamais regroupés en
planche. Seule la forme de base est prise : ni chromatique, ni femelle, ni
forme régionale — elles sont dans le pack le jour où il les faudra. Un fichier
que l'outil n'écrit plus est retiré.

### Le sprite sur la carte

128 × 128 (160, 140 ou 256 pour un gros Pokémon) : quatre rangées — bas,
gauche, droite, haut — de quatre images carrées. Colonnes 0 et 2 : les deux
dessins de la direction ; colonnes 1 et 3 : **les mêmes, un pixel plus bas**.
Lues dans l'ordre, à six images par seconde, elles donnent le petit saut des
jeux d'origine à chaque changement de dessin (mesuré sur HeartGold /
SoulSilver : un dessin dure un tiers de seconde, haut puis bas). Le code
n'ajoute donc ni saut ni hauteur de vol : tout est dans l'image.
`PokemonFrames.kt` en fait les animations ([npcs.md](npcs.md)).

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
(quatre pixels d'écran par pixel : un gros Pokémon est plus grand),
sur **un damier dont chaque carreau fait un pixel du sprite**, avec les deux
axes de sa case : on voit s'il est centré. `tests/run.sh ui/debug_pokedex`.
