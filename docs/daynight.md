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

- **Un intérieur n'a pas cette métadonnée** : il reste éclairé de nuit comme
  de jour. La grotte non plus : elle a son ambiance à elle.
- **L'interface n'est jamais teintée** : dialogues, menus et bandeau de lieu
  sont sur leurs propres calques.

Aujourd'hui seule `start_town` est dehors.

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

Dans `start_town`, sept lampadaires, tous sur l'herbe au bord d'un chemin :

| Nœud | Case | Où |
|---|---|---|
| `LampWestRoad` | (12,6) | au nord de la route de l'ouest |
| `LampLudo` | (5,17) | à gauche du chemin de la maison de Ludo |
| `LampLibrary` | (16,17) | dans le tournant, entre le chemin de Ludo et celui de la bibliothèque |
| `LampLab` | (25,7) | à gauche du laboratoire, contre sa façade |
| `LampSquareWest`, `LampSquareEast` | (28,16), (34,16) | au sud de la place, de part et d'autre |
| `LampCave` | (40,6) | à droite du chemin de la grotte |

Aucun n'est sur une ronde de PNJ ni sur une case où quelqu'un se tient après
la Veillée.

## Ce qui manque

**Des fenêtres éclairées** la nuit, sur les maisons.

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
