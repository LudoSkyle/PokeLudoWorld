# Pokédex

Deux Pokédex sont prévus (Ludovic, 17/11/2026) :

- **le national** — toutes les espèces qui existent, sans exception. Pour
  l'instant c'est **une vue de debug**, hors du jeu : elle montre tout, vu ou
  non, pour vérifier que chaque espèce est bien renseignée ;
- **le régional** — le seul qu'on ouvre en jeu : une espèce s'y découvre une
  fois rencontrée, ses détails une fois capturée. Pour l'instant ce sont **les
  151 espèces de la première génération**, dans leur ordre (Ludovic,
  19/11/2026 : « on verra plus tard pour les changer »). Voir plus bas.

## Les données du national

Tout vient du **pack de données** `vendor/GameDataPacks/Gen 9/scarlet-violet`
— la base de Pokémon Studio et de PSDK (voir [CLAUDE.md](../CLAUDE.md)).
`tools/gamedata.py` en sort, pour les 1025 espèces :

```
python3 tools/gamedata.py
```

| Ce qu'il écrit | D'où, dans le pack |
|---|---|
| `resources/pokedex/national.tsv` — une espèce par ligne : numéro, `id`, génération, noms, catégories, taille (m), poids (kg), `icon`, `overworld` (1 si le fichier est là), descriptions, en français et en anglais, `front` (1 si le portrait est là) | `Data/Studio/pokemon/*.json`, `Data/Text/Dialogs/100000` (noms), `100001` (catégories), `100002` (descriptions) |
| `assets/pokemon/overworld/<id>.png` — le sprite sur la carte | `graphics/characters/NNNN.png` |
| `assets/pokemon/icons/<id>.png` — l'icône, 64 × 32 : deux images de 32 × 32 | `graphics/pokedex/pokeicon/NNNN.png` |
| `assets/pokemon/front/<id>.png` — le portrait de face, 96 × 96 : celui de la fiche du Pokédex | `graphics/pokedex/pokefront/NNNN.png` |
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

## Le Pokédex régional

### Ses espèces

`resources/pokedex/regional.json`, **au format des Pokédex de Pokémon Studio**
(les fichiers de `Data/Studio/dex/` du pack) : un tableau `creatures` de
`{ "dbSymbol": "bulbasaur", "form": 0 }`. **Le numéro régional d'une espèce
est sa place dans ce tableau** ; tout le reste — noms, textes, images — vient
du national. Le fichier se modifie à la main ou dans Pokémon Studio : changer
la région, c'est changer cette liste, rien d'autre. `RegionalDex.kt` la lit ;
une espèce inconnue du national est signalée au journal et sautée.

### Ce qu'on a vu, ce qu'on a pris

`Pokedex.kt` retient deux listes d'identifiants : les espèces **vues**
(`see`) et les espèces **prises** (`catch` — une espèce prise est vue). Elles
font partie de la sauvegarde ([save.md](save.md)). Une rencontre dans l'herbe
inscrit l'espèce comme vue (`WildEncounters`). **Rien n'inscrit encore une
prise** : il n'y a pas de capture. Les trois espèces provisoires des tables de
rencontre (`mulotin`…) ne sont pas de la région : elles s'inscrivent, mais ne
se voient ni ne se comptent dans l'écran.

### L'écran

Menu de pause → **Pokédex** (`PokedexMenu.kt`, `scenes/ui/pokedex_menu.tscn`).
320 × 240 pixels de jeu, tout l'écran en 4:3.

- **La liste**, à droite : douze espèces à la fois, numéro et nom ; une espèce
  jamais vue n'a que des tirets, une espèce prise a sa marque au bout de la
  ligne. À gauche, le portrait et la carte de celle que montre le curseur :
  numéro, nom, catégorie (si prise), et « Inconnu », « Vu » ou « Attrapé ».
  En haut, le compte des espèces vues et prises.
- **La fiche**, qu'on ouvre en validant une espèce déjà vue, à la place de la
  liste : taille, poids, description — des points d'interrogation tant qu'on
  ne l'a pas prise.
- Haut/Bas : une espèce (en boucle) ; Gauche/Droite : dix d'un coup ; valider
  ouvre ou referme la fiche ; la touche du menu referme la fiche, puis l'écran.

**Son habillage est provisoire** : des cadres du jeu sur un fond uni. Ludovic
a une interface à lui pour cet écran (avec les onglets des zones et des
formes, qu'on n'a pas encore) ; ses fichiers ne sont pas dans le dépôt le
19/11/2026. Seule la scène est à refaire : la liste, les états et les touches
sont dans le script.

Pour l'essayer : Debug → **Remplir le Pokédex** inscrit une espèce sur trois
comme prise, une sur trois comme vue. `tests/run.sh ui/pokedex` (l'écran),
`ui/pokedex_saved` (l'outil de Debug, et la sauvegarde après une relance) ;
`./gradlew test` (`PokedexTest`).

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
