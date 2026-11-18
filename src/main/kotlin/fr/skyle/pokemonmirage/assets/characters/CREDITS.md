# Planches de personnages

Toutes les planches viennent du Megapack décrit ci-dessous. Les 125 planches
d'**aveontrainer** des débuts du projet (du même style, dont `player`,
`worker`, `gardener` et `bug_catcher` venues du projet de référence) ont été
retirées le 15/11/2026 au profit du pack ; elles restent dans l'historique git.

Format commun : 4 colonnes × 4 rangées, rangées bas, gauche, droite, haut,
cases de 48 de haut, pieds sur la ligne 45 de chaque rangée. La planche type
fait 128×192 (cases de 32×48).

Le joueur est **Renko** : `playable/renko.png`, lue par
`resources/spriteframes/player.tres`.

## FRLG Accurate NPC Megapack

Les planches préfixées `frlg_`, `rse_`, `hgss_`, `dppt_`, `anime_` et
`custom_`, et tout le dossier `playable/`, viennent du **« FRLG Accurate NPC
Megapack (Relic Castle Edition) »**, version 1.0 du 3 octobre 2021, compilé par
SoulfulLex : des personnages de toutes les générations redessinés dans le style
de Rouge Feu / Vert Feuille. Téléchargé par Ludo le 15/11/2026.

**Les auteurs sont listés sprite par sprite dans
[MEGAPACK_README.txt](MEGAPACK_README.txt)**, le lisez-moi du pack, copié tel
quel. Le compilateur demande de créditer les auteurs d'origine plutôt que lui.

| Préfixe | Dossier du pack | Planches |
|---|---|---|
| `frlg_` | FRLG NPCs | 31 |
| `rse_` | RSE NPCs | 81 |
| `hgss_` | HGSS NPCs | 42 |
| `dppt_` | DPPt NPCs | 10 |
| `custom_` | Other or Custom NPCs | 6 |
| `anime_` | Anime NPCs | 69 |
| `playable/` | Playable Characters/Characters | 47 |

Ce qui a été fait à l'import (`trainer_ACETRAINER_M.png` devient
`frlg_acetrainer_m.png`) :

- noms passés en minuscules avec des `_`, préfixe `trainer_` retiré, préfixe du
  dossier ajouté — deux dossiers ont souvent une planche du même nom ;
- six planches avaient les pieds à 2 px de la ligne 45 et ont été réalignées :
  `frlg_roughneck2v1`, `rse_cyclist_f`, `rse_cyclist_m`, `rse_tuber2_m`,
  `hgss_biker`, `hgss_swimmer2_m` ;
- quinze planches sont plus larges (160×192 ou 192×192, cases de 40 ou 48 de
  large) : motards, cyclistes, jumelles, quelques champions. Elles marchent
  telles quelles, le découpage se fait au quart de la largeur.

`playable/` garde les planches des personnages jouables sans retouche : la
marche (`renko.png`), la course (`_run`), le vélo (`_bike`, cases de 48×48), le
surf (`_surf`) et la pêche (`_fish`, cases de 96×80). Leurs pieds ne sont pas
tous sur la ligne 45 : c'est voulu, la pose de course est plus ramassée.

Non repris : les sprites de combat (`Trainers/`) et les icônes de carte
(`Pictures/`) du pack.

## Les planches sources (`sources/`)

Dossier ignoré par Godot (`.gdignore`) : des planches **telles qu'elles ont été
téléchargées**, gardées dans le projet pour ne pas avoir à les rechercher. Le
jeu n'en lit aucune ; ce qu'on en prend est sorti à part.

| Fichier | Contenu | Auteur | Nom d'origine |
|---|---|---|---|
| `hgss_trainers_overworld.png` | les dresseurs et personnages d'Or HeartGold / Argent SoulSilver sur la carte, dans leur dessin d'origine (une planche de 957 × 1101, pas le format redessiné du Megapack) | Game Freak ; extrait publié sur The Spriters Resource | `DS _ DSi - Pokemon HeartGold _ SoulSilver - Overworld - Trainers (Overworld).png` |

Téléchargée par Ludo le 15/11/2026.

### `sources/teraleak/` — « Teraleak OWs & Assets »

Un pack de **PurpleZaffre** : 264 images tirées de versions bêta des jeux,
mises en planche par lui. Téléchargé par Ludo le 15/11/2026.

| Dossier | Dossier du pack | Images | Contenu |
|---|---|---|---|
| `rs_pt_hgss/` | `RS, PT & HGSS` | 92 | personnages et dresseurs sur la carte (`HGSS_Beta…`, `Pt_Beta…`, `…BetaTrainer…`), quelques Pokémon (Lugia, Ho-Oh, les formes de Motisma), et des écrans de sac, de menu et d'options, des icônes, deux cartes, un arbre, un rocher, un panneau |
| `bw_b2w2/` | `BW & B2W2` | 172 | personnages sur la carte (`BW_Beta…`, `B2W2_Beta…`), des Pokémon d'Unys (Reshiram, Zekrom, Kyurem, Victini, Meloetta, Cobaltium, Terrakium, Viridium, et deux planches mêlées), des icônes, deux portraits, des objets, effets et animations |

Les planches de personnages font 256 × 256 : quatre colonnes de marche, quatre
rangées — bas, gauche, droite, haut — soit des cases de 64 × 64, le double de
la taille du jeu. Les noms de fichiers sont ceux du pack ; seuls les deux
dossiers ont été renommés.

**Licence** : [`sources/teraleak/Credits.txt`](sources/teraleak/Credits.txt),
copié tel quel, demande de **créditer PurpleZaffre** et de **ne pas
redistribuer** le pack. Il est versionné ici sur décision de Ludo (projet
personnel, non commercial).
