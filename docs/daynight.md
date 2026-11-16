# Jour et nuit

Le dehors change de couleur avec l'heure, et l'heure est **celle de la
machine** : il fait nuit dans le jeu quand il fait nuit chez le joueur.

`scripts/core/DayNight.kt` répond à deux questions — quelle heure est-il, de
quelle couleur cette heure teinte-t-elle le dehors. `SceneManager` applique la
teinte.

## Les quatre moments

| Moment | Teinte | Plein effet |
|---|---|---|
| **nuit** | bleu sombre | de 20 h 30 à 5 h 30 |
| **aube** | claire, rosée | à 6 h 30 |
| **jour** | aucune — le décor tel qu'il est dessiné | de 7 h 30 à 17 h 30 |
| **crépuscule** | orangé | à 19 h |

Entre deux moments la teinte **glisse** de l'une à l'autre, sans saut : la
nuit pâlit de 5 h 30 à 6 h 30, le jour tombe de 17 h 30 à 19 h, et ainsi de
suite. C'est la liste `KEYS` de `DayNight.kt` : une suite de repères « à telle
heure, telle teinte », deux repères de même teinte faisant un palier. Changer
une heure ou une couleur se fait là, et nulle part ailleurs.

Les heures sont fixes toute l'année.

## Ce qui est teinté

Une carte **d'extérieur** le déclare sur sa racine `Level` :

```
metadata/daylight = true
```

`SceneManager` lui ajoute alors un nœud `Daylight` (un `CanvasModulate`) à son
chargement, et règle sa couleur à chaque image. Tout ce que la carte dessine en
prend la teinte : décor, joueur, PNJ.

La météo, elle, ne touche pas à cette couleur : elle a sa propre teinte
d'écran, appliquée **sous** celle de l'heure pour que les deux ne s'empilent
pas ([weather.md](weather.md)). Et le zénith, qui est le soleil, s'éteint avec
la nuit.

- **Un intérieur n'a pas cette métadonnée** : il reste éclairé de nuit comme
  de jour.
- **L'interface n'est jamais teintée** : dialogues, menus et bandeau de lieu
  sont sur leurs propres calques.

Aujourd'hui seule `start_island` est dehors (et le terrain d'essai des tests).

## Les lampadaires

`scenes/levels/street_lamp.tscn`, script `StreetLamp.kt` : un objet posé sur
une case, solide comme un panneau, avec sa lumière (un `PointLight2D`).

- **La lumière ne s'allume que la nuit** : éteinte le jour, à l'aube et au
  crépuscule. Sa force vient de `DayNight.light()` : 1 la nuit, 0 aux trois
  autres moments. Elle monte donc pendant que la nuit tombe (de 19 h à
  20 h 30) et baisse quand elle s'en va (de 5 h 30 à 6 h 30), sans saut.
- **Elle perce la teinte** : autour du lampadaire le décor et les personnages
  retrouvent leurs couleurs, dans un halo chaud de 4 cases de rayon.
- Le halo est un dégradé fabriqué dans la scène, sans asset. Le dessin du
  lampadaire est découpé dans `environments.png`, qui en a une vingtaine de
  modèles côte à côte (rangées 17-19, à partir de la colonne 71).

**En poser un** : instancier `street_lamp.tscn` sous `World`, sur un centre de
case. Rien d'autre à régler. `brightness` change sa force.

Ceux de l'île sont listés dans [levels.md](levels.md) ; le terrain d'essai des
tests en a deux, `LampWest` et `LampEast`.

## Les fenêtres éclairées

La nuit, les vitres des maisons virent au jaune et répandent une lueur sur la
façade. Deux pièces :

**La vitre** — un shader, `resources/shaders/window.gdshader`, attaché dans
`level.tres` aux tuiles de maison qui ont une vitre :

```
15:99/0/material = SubResource("ShaderMaterial_window")
```

- Il ne touche que les **pixels bleu vitre** de la tuile ; le mur, le toit et
  les jardinières ne changent pas. Le dessin des tuiles n'est pas modifié.
- La vitre s'allume avec `DayNight.light()`, comme les lampadaires : la nuit
  seulement, en montant pendant qu'elle tombe. À l'aube et au crépuscule
  elle reste une vitre bleue.
- **Elle n'est pas assombrie par la nuit.** La teinte multiplie tout le
  dehors ; le shader divise donc la couleur de la vitre par la teinte du
  moment, que le moteur remultiplie ensuite.
- Il lit deux valeurs globales, déclarées dans `project.godot`
  (`[shader_globals]`) et réglées à chaque image par `SceneManager` :
  `night_light`, la force des lumières, et `day_tint`, la teinte du dehors.
  Dans un intérieur elles valent 0 et blanc.

Les 23 tuiles concernées ont été trouvées en cherchant les pixels bleu clair
dans les tuiles du calque `Houses`. **Une nouvelle maison à fenêtres a besoin
de cette ligne sur ses tuiles vitrées**, comme pour une collision.

**La lueur** — `scenes/levels/window_glow.tscn`, script `NightLight.kt` : une
petite lumière chaude qui suit l'heure, comme celle d'un lampadaire en plus
faible. On en pose une par groupe de fenêtres, sous `World`, au centre des
vitres.

## Le voile du dehors

Par-dessus toute carte d'extérieur, un **voile clair et nuageux** : une brume
pâle, à peine bleutée, et des bancs de nuages plus clairs qui dérivent
lentement. C'est ce qui donne au dehors son air lumineux, un peu céleste.

- `resources/shaders/sky.gdshader`, sur un `ColorRect` nommé `Haze` que
  `SceneManager` ajoute à la carte en même temps que `Daylight`
  (`metadata/daylight`). Il couvre toute la carte, au-dessus du décor
  (`z_index = 50`) et sous l'interface, qui vit sur ses propres calques.
- Les nuages sont **ancrés au monde** : on marche dessous, ils ne suivent pas
  la caméra. Un bruit en trois octaves, découpé en paliers nets et en grains de
  2 px pour rester du pixel art.
- Le voile est teinté par `Daylight` comme le reste, et **se retire presque la
  nuit** (il lit l'uniforme global `night_light`) : la nuit, c'est la nuit qui
  teinte.
- Réglages (uniformes du shader) : `haze` (0,12, l'opacité partout), `clouds`
  (0,19, ce qu'un nuage ajoute), `size` (170 px), `drift` (5 px/s vers l'est),
  `grain`, `levels`, `tint`.

## Mise au point

Comme l'heure est réelle, on ne verrait la nuit que la nuit. Deux moyens de
l'imposer :

- **En jeu** : Debug → la ligne **Heure**. Chaque validation passe au moment
  suivant — réelle, aube, jour, crépuscule, nuit, puis de nouveau réelle. Le
  libellé dit où l'on en est, et la boîte reste ouverte ([menu.md](menu.md)).
- **Dans un script** : `Globals.set_hour(23.0)` impose une heure de 0 à 24 ;
  une valeur négative rend la main à l'horloge. `Globals.hour()` la lit.

L'heure imposée n'est pas sauvegardée : au lancement suivant on est de
nouveau à l'heure réelle.

## Tests

Les tests se jouent **en plein jour** : `tests/lib.gd` impose midi avant de
lancer le jeu, pour qu'un test ne change pas de résultat selon l'heure où on
le lance. Ceux qui veulent une autre heure la demandent avec `set_hour()`, et
lisent la teinte avec `daylight()`.

```bash
tests/run.sh daynight
```
