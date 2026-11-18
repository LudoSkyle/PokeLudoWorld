# Sons et musiques

Trois dossiers ; le nom du fichier, sans l'extension, est l'identifiant que le
jeu utilise (`AudioManager`, voir `docs/audio.md`).

## `music/` — les musiques des lieux

Bande-son de **Pokémon Or HeartGold / Argent SoulSilver** (Nintendo / GAME
FREAK), pistes fournies par Ludovic le 14/11/2026.

| Fichier | Piste d'origine | Où on l'entend |
|---|---|---|
| `new_bark_town.mp3` | 04. New Bark Town | l'île de Bourg-Ludo et ses maisons |
| `elm_lab.mp3` | 07. Elm Pokémon Lab | le laboratoire |
| `sprout_tower.mp3` | 23. Sprout Tower | la bibliothèque |
| `union_cave.mp3` | 28. Union Cave | nulle part pour l'instant : c'était la musique de la grotte, supprimée avec l'ancien village |

La musique de l'écran titre vient d'ailleurs : **« Pixel Fantasia »** de
**Lofiewme** (Pixabay, piste 355123), fournie par Ludovic le 16/11/2026.

| Fichier | Piste d'origine | Où on l'entend |
|---|---|---|
| `title.mp3` | Lofiewme — Pixel Fantasia | l'écran titre |

Les pistes de la bande-son jouent leur boucle deux fois puis s'éteignent en fondu : rejouées
en boucle telles quelles, on entend ce fondu avant la reprise.

## `jingles/` — ils mettent la musique en pause

| Fichier | Origine | Quand |
|---|---|---|
| `key_item.wav` | pack Gen 4, `ME/me_obtained_key_item.wav` | on reçoit un objet rare |
| `item.wav` | pack Gen 4, `ME/Item get.wav` | on reçoit un objet ordinaire |
| `healed.wav` | pack Gen 4, `ME/Pkmn healing.wav` | la machine de soin |
| `save.wav` | pack Gen 4, `ME/GUI save game.wav` | la partie est sauvegardée |
| `bell.mp3` | « Heal Bell », génération 4, de la *Pokemon SFX Attack Moves & Sound Effects Collection* compilée par BellBlitzKing | on accroche la cloche |

## `sfx/` — les bruitages, par-dessus la musique

| Fichier | Origine dans le pack Gen 4 | Quand |
|---|---|---|
| `cursor.wav` | `SE/GUI sel cursor.wav` | le curseur d'un menu bouge |
| `confirm.wav` | `SE/GUI sel decision.wav` | on valide, on fait avancer un dialogue |
| `cancel.wav` | `SE/GUI sel cancel.wav` | on referme, on répond Non |
| `menu.wav` | `SE/GUI menu open.wav` | on ouvre le menu de pause |
| `bump.wav` | `SE/Player bump.wav` | on bute contre un obstacle |
| `door.wav` | `SE/Door enter.wav` | on entre quelque part |
| `door_exit.wav` | `SE/Door exit.wav` | on sort par un paillasson ou un escalier |

Un bruitage ne vient pas de ce pack mais du kit **Pokémon Essentials v21.1**
(2023-07-30), copié tel quel :

| Fichier | Origine dans Essentials v21.1 | Quand |
|---|---|---|
| `jump.ogg` | `Audio/SE/Player jump.ogg` | on saute un rebord |

Les cris (`cries/`), un par espèce (`wingull.ogg`), sont **copiés tels quels**
du pack de données de Pokémon Studio —
[GameDataPacks](https://github.com/PokemonWorkshop/GameDataPacks) de Pokémon
Workshop, `Gen 9/scarlet-violet/audio/se/cries` — par `tools/gamedata.py`, sous
la [Licence d'utilisation de Pokémon Studio](https://github.com/PokemonWorkshop/PokemonStudio/blob/develop/LICENSE-FR.md).

## Le pack Gen 4

**Gen 4 Sound Effects (Essentials v17.2)**, v1.0, compilé et extrait par **Deo**
(<https://reliccastle.com/>), qui demande à être crédité ; son `Readme.txt` est
recopié dans `sfx/README_gen4_sound_effects.txt`. Les sons d'origine sont la
propriété de Nintendo / GAME FREAK.

Le pack contient d'autres sons qui serviront (pas dans l'herbe, portes
coulissantes, PC, combat) : il est dans les téléchargements de Ludovic,
dossier `PokemonMirage - sons/Bruitages`.
