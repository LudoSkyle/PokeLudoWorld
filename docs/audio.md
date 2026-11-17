# Sons et musiques

`scripts/core/AudioManager.kt`, un nœud de `game_manager.tscn`. Trois sortes de
sons, rangées dans trois dossiers de `assets/audio/` :

| Sorte | Dossier | Comportement |
|---|---|---|
| **musique** | `music/` | celle du lieu, en boucle |
| **jingle** | `jingles/` | **met la musique en pause**, joue, puis la musique **reprend où elle en était** |
| **bruitage** | `sfx/` | passe **par-dessus** la musique, sans y toucher |

Un son se désigne par le **nom de son fichier sans l'extension** : `bell`,
`bump`, `new_bark_town`. Le format est libre : WAV, OGG ou MP3. En ajouter un, c'est déposer le fichier dans le bon
dossier, avec son `.import`, et le noter dans `assets/audio/CREDITS.md`.

```kotlin
AudioManager.instance?.playMusic("elm_lab")
AudioManager.instance?.jingle("key_item")
AudioManager.instance?.sfx("bump")
```

## La musique d'un lieu

Chaque carte déclare la sienne par une métadonnée de sa racine `Level`, à côté
de son nom de lieu :

```
[node name="Level" type="Node2D"]
metadata/location = "Bourg-Ludo"
metadata/music = "new_bark_town"
```

`music` est la musique du lieu ; sans elle, le silence. Elle ne dépend pas de
l'histoire : le village garde la sienne après la Veillée.

`SceneManager` la demande à chaque chargement de carte. **Deux cartes qui
déclarent la même musique la partagent** : en passant de l'une à l'autre elle
continue, sans repartir du début. C'est ainsi que la maison de Ludo garde la
musique de l'île.

| Carte | Musique |
|---|---|
| `start_island`, `ludo_house`, `ludo_bedroom`, `orange_house_north`, `orange_house_south` | `new_bark_town` |
| `library` | `sprout_tower` |
| `lab_house` | `elm_lab` |

L'**écran titre** a la sienne, `title`, demandée par `TitleScreen` et non par
une carte ([title.md](title.md)). Elle s'éteint dans le même fondu quand la
première carte arrive.

**Une musique arrive toujours en fondu**, sur une seconde (`fade_seconds`) :
celle de l'écran titre au lancement comme celle d'un lieu.

**Changer de musique** est un **fondu enchaîné** d'une seconde : l'ancienne
s'éteint pendant que la nouvelle monte, les deux en même temps (deux lecteurs,
`Music` et `MusicOut`, qui échangent leurs rôles). Si l'on revient sur ses pas
avant la fin du fondu, la musique qui s'éteignait remonte là où elle en était,
sans repartir du début. Un troisième changement pendant un fondu coupe celle
qui finissait de s'éteindre.

Les pistes de la bande-son jouent leur boucle deux fois puis s'éteignent :
rejouées en boucle telles quelles, on entend ce fondu avant la reprise. Des
points de boucle propres restent à poser.

## Les jingles

| Jingle | Quand |
|---|---|
| `key_item` | une boîte donne un **objet rare** (`@give:`) |
| `item` | une boîte donne un objet ordinaire |
| `healed` | la machine de soin (`@sound:healed`) |
| `bell` | on accroche la cloche (`@sound:bell`) |
| `save` | la partie est sauvegardée |

**Tant qu'un jingle joue, le dialogue ne passe pas à la suite** : une pression
finit d'écrire le texte, rien de plus. Un objet rare reste donc à l'écran le
temps de son jingle, et au moins une seconde.

Une boîte de dialogue joue un jingle par la consigne **`@sound:<nom>`**, comme
elle donne un objet par `@give:` ([dialogue.md](dialogue.md)).

Si l'on change de lieu pendant un jingle, c'est la musique du nouveau lieu qui
démarre quand il se termine. Un jingle coupe court à un fondu en cours : la
musique qui s'éteignait se tait, l'autre attend en pause.

## Les bruitages

| Bruitage | Quand | Où c'est déclenché |
|---|---|---|
| `cursor` | le curseur d'un menu bouge, un réglage change | `MenuKeys`, `BagMenu`, `OptionsMenu` |
| `confirm` | on valide dans un menu, on fait avancer un dialogue, on examine quelque chose | `Player` |
| `cancel` | on referme un menu, on répond Non par la touche du menu | `Player` |
| `menu` | on ouvre le menu de pause | `Player` |
| `bump` | on bute contre un obstacle, à la cadence des pas (0,3 s) | `Player` |
| `jump` | on saute un rebord, à l'instant où le saut part | `Player` |
| `door` | on entre quelque part : porte, bouche de tunnel | `SceneManager.changeLevel` |
| `door_exit` | on sort par un paillasson ou un tapis d'escalier | `SceneManager.changeLevel` |

C'est `Player` qui fait entendre la validation, parce que c'est lui qui lit la
touche d'interaction, une seule fois pour tout le jeu.

Bruitages et jingles d'objet viennent du pack *Gen 4 Sound Effects* de Deo
(`assets/audio/CREDITS.md`).

## Ce qui manque

- **Un réglage du volume** dans les options (musique, bruitages).
- **Des points de boucle** pour les musiques.
- **Le bruit des pas dans l'herbe**, un son propre à l'escalier et au tunnel :
  le pack fourni les contient (`se_step_grass`, `se_door_slide`…), ils ne sont
  pas encore branchés.

## Tests

Lancé par `tests/run.sh`, le jeu joue tous ses sons **en silence** (le bus
principal est coupé). `AudioManager` expose ce qu'il fait : `music_id()`,
`music_audible()`, `music_starts()`, `jingle_playing()`, `last_jingle_id()`,
`last_sfx_id()`, `sfx_played()`. Dans un test : `audio()` et `wait_jingle()`
(`tests/lib.gd`).

```bash
tests/run.sh audio
```
