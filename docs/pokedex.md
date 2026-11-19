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
| `resources/pokedex/national.tsv` — une espèce par ligne : numéro, `id`, génération, noms, catégories, taille (m), poids (kg), `icon`, `overworld` (1 si le fichier est là), descriptions, en français et en anglais, `front` (1 si le portrait est là), `type1` et `type2` (les types, par leur nom dans le pack ; le second vide s'il n'y en a qu'un) | `Data/Studio/pokemon/*.json`, `Data/Text/Dialogs/100000` (noms), `100001` (catégories), `100002` (descriptions) |
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

**C'est le Pokédex de Pokémon Essentials v21.1, porté**, dans l'habillage que
Ludovic a choisi pour lui : le « Custom Legends-inspired Pokedex UI » de
delusionsofgrandr, « conçu autour de la mise en page d'origine d'Essentials »
(`assets/ui/pokedex/`, voir son `CREDITS.md`). Tout est posé aux places des
deux scripts d'Essentials (`Data/Scripts/016_UI/003_UI_Pokedex_Main.rb` et
`004_UI_Pokedex_Entry.rb`, github.com/Maruno17/pokemon-essentials, branche
`master`), dont les méthodes gardent leur nom dans le nôtre : `pbPokedex`,
`pbRefreshDexList`, `pbRefresh`, `pbDexEntry`, `pbScene`, `drawPageInfo`,
`pbGoToPrevious`, `pbGoToNext`.

**L'écran est dessiné dans les pixels de l'habillage**, 512 × 384, puis grossi
**deux fois et demie** (`Control/Screen`, `scale = 2.5`) : il tient les
1280 × 960 de l'écran, en 4:3. Les places de la scène sont donc celles
d'Essentials, telles quelles. Ses traits font deux pixels d'épaisseur : ils en
font cinq à l'écran, nets. La police y est à la taille 32 — deux pixels de
l'habillage par pixel de police —, et ses ombres le savent
(`PixelShadow.attachAll(écran, 2.0)`).

- **La liste** (`bg_list.png`) : dix espèces à la fois, numéro et nom ; la
  marque d'une espèce vue ou prise devant sa ligne ; le cadre rouge sur la
  ligne choisie ; l'ascenseur à droite. À gauche, le nom et le portrait de
  l'espèce choisie, et les comptes des espèces vues et prises.
  **La liste s'arrête à la dernière espèce vue** : les inconnues de la fin ne
  se montrent pas, celles du milieu ont une ligne de tirets. Rien de vu : la
  liste est vide.
- **La fiche** (`bg_info.png`), qu'on ouvre en validant une espèce déjà vue :
  son portrait, son numéro et son nom, et — **si on l'a prise** — sa marque,
  sa catégorie, ses types (`icon_types.png`), sa taille, son poids et sa
  description ; sinon des points d'interrogation. L'espèce **crie** quand sa
  fiche s'ouvre.
- Dans la liste : Haut/Bas, une espèce (en boucle) ; Gauche/Droite, dix d'un
  coup ; valider ouvre la fiche ; la touche du menu referme l'écran. Dans la
  fiche : Haut/Bas passent à l'espèce **vue** d'avant ou d'après ; la touche
  du menu ramène à la liste.

Ce qui n'est pas porté, ou pas pareil :

- **un seul onglet**, « INFO » : ni les zones ni les formes, qu'on n'a pas
  (leurs images sont dans `assets/ui/pokedex/source/`) ;
- ni la recherche de la liste, ni la trace de pas de la fiche, ni son compte
  de combats ;
- le portrait est posé **huit à douze pixels plus haut** que chez Essentials :
  ceux du pack de données ont les pieds au bas de leur image, sans marge, et
  dépassaient du cadre ;
- nos textes sont **sept pixels plus haut** que les ordonnées d'Essentials
  (huit pour la description) : notre police n'a pas la marge du haut de la
  sienne ;
- les étiquettes des types sont des images, en anglais ;
- la marque d'une espèce seulement vue, le cadre de la ligne et l'ascenseur
  sont ceux du kit d'Essentials : l'habillage ne les redessine pas.

Les types viennent de deux colonnes de plus de `national.tsv` (`type1`,
`type2`), sous leur nom dans le pack (`grass`).

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
