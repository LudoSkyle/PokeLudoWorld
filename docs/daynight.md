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

## Ce qui manque

La teinte seule assombrit tout uniformément. Restent à faire : **des
lampadaires et leurs halos**, **des fenêtres éclairées**, qui percent la nuit
là où il y a de la lumière.

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
