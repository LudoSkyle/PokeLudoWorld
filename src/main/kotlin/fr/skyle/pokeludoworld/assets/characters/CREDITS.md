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
