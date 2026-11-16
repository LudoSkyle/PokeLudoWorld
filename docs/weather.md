# La météo

Huit temps, comme dans Rubis / Saphir / Émeraude : le ciel clair, la pluie,
l'averse, la neige, le blizzard, la tempête de sable, le zénith et le
brouillard. Ils ne changent pas tout seuls — on les choisit (voir « Mise au
point » plus bas).

**C'est le portage de la météo de Pokémon Essentials**, pas une imitation :
mêmes images, mêmes valeurs, même algorithme, méthode pour méthode. Deux
fichiers, comme chez eux :

| Chez nous | Chez eux | Rôle |
|---|---|---|
| `scripts/core/Weather.kt` | `012_Weather.rb` (`GameData::Weather`) | **décrit** chaque temps : ses images, ses vitesses, sa teinte |
| `scripts/core/WeatherLayer.kt` | `001_Overworld_Weather.rb` (`RPG::Weather`) | **anime** : fait naître, tomber et mourir les particules, glisser les nappes, teinter l'écran |

Les fonctions de `WeatherLayer` portent les noms des leurs
(`reset_sprite_position`, `update_sprite_position`,
`recalculate_tile_positions`…) pour qu'on puisse relire les deux côte à côte.
**Avant de « corriger » quoi que ce soit ici, relire leur fichier** : trois
versions maison ont été écrites puis jetées, chacune fausse d'une façon qui se
voyait.

## Les huit temps

| Temps | Chez eux | Ce qui tombe | Vitesse (px de jeu/s) | Nappe | Teinte ajoutée |
|---|---|---|---|---|---|
| **normale** | `:None` | — | — | — | — |
| **pluie** | `:Rain` | `rain_1-3`, éclaboussure `rain_4` | (-300, 1200) × 0,3 | — | -30 partout, gris 10 |
| **averse** | `:HeavyRain` | `storm_1-3`, éclaboussure `storm_4` | (-1800, 1800) × 0,3 | — | -45 partout, gris 10 |
| **neige** | `:Snow` | `hail_1-3` | (-120, 120) | — | +30 partout |
| **blizzard** | `:Blizzard` | `blizzard_1-4` | (-360, 120) | `blizzard_tile` à (-600, 300) | +45 partout |
| **tempête de sable** | `:Sandstorm` | `sandstorm_1-4` | (-600, 320) | `sandstorm_tile` à (-400, 200) | +30 rouge, -30 bleu |
| **zénith** | `:Sun` | — | — | — | (64, 64, 32), et elle bat |
| **brouillard** | `:Fog` | — | — | `fog_tile` à (-16, 0) | — |

**Une seule conversion** : leurs cases font 32 px et les nôtres 16, donc toutes
les distances et toutes les vitesses sont les leurs divisées par deux.

**Un seul écart voulu** : la pluie et l'averse tombent à trois dixièmes de leur
allure (`Weather.RAIN_PACE`). À la leur, une goutte traverse l'écran en un
sixième de seconde ; la GBA, elle, laisse suivre chaque goutte des yeux. Mettre
`1.0` rend l'allure d'Essentials.

## Comment une goutte vit

C'est le point qui a tout changé, et celui qu'il ne faut pas réinventer.

- **Rien ne défile.** Chaque goutte est un sprite à part. Elle naît à un endroit
  tiré au sort, avance **le long de sa propre pente**, puis **meurt** quand elle
  a parcouru une distance tirée au sort elle aussi — et renaît ailleurs. Il n'y
  a ni grille, ni champ de gouttes qui glisse d'un bloc.
- **60 sprites**, pas davantage : c'est ce qu'une carte demande
  (`(9 + 1) * 60 / 10` dans `Game_Screen#weather`). Sous la pluie, **un sur deux
  est une éclaboussure** : il reste trente gouttes à l'écran.
- **Trois longueurs de goutte**, distribuées par le rang du sprite.
- **Une éclaboussure ne suit aucune goutte.** Elle est posée au hasard, vit de
  0,3 à 0,5 s, et ne se montre que ses deux derniers dixièmes de seconde.
- **La pente du mouvement est celle du dessin.** Les traînées de `rain_*` sont
  penchées d'un quart, celles de `storm_*` de 45° — mesuré sur les images — et
  ce sont exactement les rapports de leurs vitesses. Une goutte avance donc dans
  son axe ; changer d'image sans changer la vitesse la fait déraper de côté.
- **La neige flotte** : sa chute reçoit trois petits écarts à chaque image (plus
  vite en bas de l'écran, un pas de côté au hasard, une variété selon le rang).

Les trois versions jetées, pour mémoire : un motif dessiné par un shader ; une
planche de pluie répétée comme une tuile, qui donnait un rideau de centaines de
traînées ; une goutte par cellule d'une grille qui glissait d'un bloc — vingt
gouttes, mais qu'on voyait **défiler de côté**, parce que toutes bougeaient
ensemble et qu'aucune ne mourait.

## Tout est ancré à la carte

Les particules et les nappes ont des positions **dans le monde**, pas à l'écran
(`@weather.ox = $game_map.display_x` chez eux). On ne regarde l'écran que pour
faire naître une particule ou la faire reboucler d'un bord à l'autre. Quand on
marche, la pluie reste où elle tombe ; elle ne suit pas la caméra.

Chez nous l'écran est la vue de la caméra : 320 × 240 pixels de jeu.

## Les nappes

Le blizzard, le sable et le brouillard posent par-dessus une image **tuilée**
qui glisse : assez de tuiles pour couvrir l'écran plus une rangée et une
colonne, recalées sur elles-mêmes dès qu'elles sortent. C'est
`recalculate_tile_positions` et `update_tile_position`, tels quels.

## La teinte d'écran

Une teinte de RPG Maker **ajoute** une couleur à l'image — elle ne la multiplie
pas — après lui avoir retiré un peu de la sienne (le « gris »). La pluie retire
30 à chaque canal, la neige en ajoute 30 ; le zénith ajoute (64, 64, 32) et
**bat** : sa force monte de 60 en 0,8 s puis redescend.

- `resources/shaders/weather.gdshader`, sur le rectangle `Tone` de la scène. Il
  **relit l'écran** déjà dessiné (`hint_screen_texture`) et lui applique la
  formule de mkxp, le moteur d'Essentials.
- `Tone` est le dernier enfant de la scène : il teinte la carte, les
  personnages **et** ce qui tombe, comme leur `Viewport`.
- Par beau temps et dans le brouillard, qui n'ont pas de teinte, le rectangle
  est caché.

### La météo passe sous l'heure

RPG Maker teinte l'image finale. Chez nous l'image finale porte déjà la teinte
de l'heure ([daynight.md](daynight.md)) : de nuit, retirer 30 à une image que
la nuit a déjà assombrie la noyait — **les deux teintes s'empilaient**.

Le shader **défait d'abord la teinte de l'heure** (il lit `day_tint`, le même
uniforme global que les vitres), teinte le monde tel qu'il est en plein jour,
puis la remet. La pluie assombrit donc la nuit **en proportion**, comme elle
assombrit le jour :

| Heure | Teinte de l'heure | Ce que la pluie retire à l'écran |
|---|---|---|
| midi | (1 ; 1 ; 1) | (0,113 ; 0,118 ; 0,113) |
| 19 h | (1 ; 0,76 ; 0,58) | (0,113 ; 0,089 ; 0,065) |
| 23 h | (0,38 ; 0,44 ; 0,78) | (0,044 ; 0,052 ; 0,089) |

Mesuré, et c'est au centième le produit des deux. Même chose pour la neige, qui
n'illumine pas la nuit comme le jour. La lumière des lampadaires n'est bornée
qu'à la fin : elle dépasse la teinte de la nuit, et le doit.

La météo ne touche pas au `CanvasModulate` : l'heure reste réglée par
`SceneManager`, seule.

### Pas de zénith sans soleil

Le zénith est la lumière du soleil : **sa teinte se retire à mesure que la nuit
tombe**, au rythme où les lampes s'allument (`1 - DayNight.light()`), et
revient avec le jour. À 23 h il ne teinte rien ; au crépuscule il brille encore.
Le temps reste « zénith » dans le menu — c'est son effet qui suit le soleil.

## Les images

`assets/weather/` — 23 planches tirées du kit (voir le `CREDITS.md` du dossier).

Les originaux, dans `assets/weather/sources/` que Godot ignore, sont dessinés
pour des cases de 32 px en **pixels doublés** : chaque bloc de 2 × 2 est d'une
seule couleur. `tools/weather_sheets.py` en garde un pixel par bloc — une
réduction de moitié **sans aucune perte**, qui pose chaque goutte sur notre
grille de pixels. Le script s'arrête si un bloc n'est pas uniforme.

## Comment c'est posé

Sur toute carte d'extérieur (`metadata/daylight`, comme le voile du dehors),
`SceneManager` ajoute `scenes/levels/weather.tscn` **juste au-dessus du voile**
(`z_index = 51`), sous l'interface :

```
Weather (Node2D)      WeatherLayer.kt
├── Particles         ce qui tombe : 60 sprites au plus
├── Tiles             la nappe tuilée
└── Tone              la teinte d'écran, dessinée en dernier
```

Un intérieur n'en a pas : il n'y pleut pas.

## Ce qui s'écarte d'Essentials

Trois choses, toutes voulues :

- **l'allure de la pluie et de l'averse**, à trois dixièmes de la leur
  (`Weather.RAIN_PACE`) ;
- **la teinte passe sous celle de l'heure** au lieu de teinter l'image finale ;
- **le zénith s'éteint la nuit**.

## Ce qui n'est pas porté

- **Les fondus d'un temps à l'autre.** On change d'un coup, comme Essentials
  quand la durée vaut zéro — ce qui est son cas à l'entrée d'une carte.
- **Les éclairs de l'orage** (`:Storm`). L'averse est leur `:HeavyRain`, qui a
  les mêmes images et la même allure, sans les éclairs.
- L'image que leur éclaboussure laisse voir à sa naissance avant d'être cachée :
  un accroc de leur côté, qu'on ne reproduit pas.

## Ajouter un temps

1. Une entrée de plus dans `Weather.Sky`, écrite comme les autres : sa famille,
   ses images, ses vitesses, sa teinte.
2. Sa traduction dans `locale/en.po` ([i18n.md](i18n.md)).
3. Ses images dans `assets/weather/sources/`, puis `python3
   tools/weather_sheets.py`.

Rien d'autre : `WeatherLayer`, le menu de mise au point et les tests
parcourent l'énumération.

## Mise au point

- **En jeu** : Debug → la ligne **Météo**. Chaque validation passe au temps
  suivant, et revient au beau après le brouillard. La boîte reste ouverte
  ([menu.md](menu.md)).
- **Dans un script** : `Globals.set_weather(5)` impose un temps par son rang
  dans la liste (0 normale … 7 brouillard), `Globals.weather()` le lit et
  `Globals.weather_label()` en donne le nom.

Le temps choisi n'est pas sauvegardé : au lancement suivant, il fait beau.

## Tests

```bash
tests/run.sh visuals/weather     # 60 sprites, 30 gouttes, leur pente, leur mort, l'ancrage à la carte, les teintes
tests/run.sh ui/debug_weather    # la ligne du menu de mise au point
```

`visuals/weather` mesure la vitesse des gouttes **sur leurs sprites**, par la
médiane de leurs déplacements, y compris pendant que le joueur marche : c'est
ce qui dit qu'elles tombent le long de leur pente et qu'elles ne suivent pas la
caméra.
