# Tuiles, collisions et terrains

## Le principe

`resources/tilesets/level.tres` est **le** TileSet du jeu. Tout y est déclaré
par coordonnée d'atlas, jamais par position sur une map :

```
49:27/0/physics_layer_0/polygon_0/points = PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
49:27/0/y_sort_origin = 8
```

`49:27` désigne la tuile dans l'atlas. Elle arrive avec sa collision partout où
on la pose, dans cette map comme dans les suivantes.

**Corollaire : ne pose jamais un `StaticBody2D` à la main sur une map pour
bloquer un décor.** Si une tuile ne bloque pas, c'est sa déclaration qu'il faut
corriger, une fois, pour tout le projet.

## L'atlas

`assets/levels/environments.png` — 1504 × 2273, tuiles de 16 × 16, `margins (1,1)`,
pas de séparation. Deux sources :

| Source | Nom | Contenu |
|---|---|---|
| `5` | `environments` | tuiles 1×1 (sol, chemins, maisons, décors, falaises) |
| `6` | `border_environments` | grosses tuiles 3×3 et 3×4 (arbres) |

**Les grosses tuiles sont centrées sur leur case d'ancrage**, pas ancrées en
haut à gauche. Une tuile 3×3 posée en `(x, y)` couvre `x-1..x+1` et `y-1..y+1`.
C'est vrai pour le dessin, pour le polygone de collision et pour le point de
tri — tous partagent le même repère local, centré sur la case d'ancrage.
Vérifié par rendu comparé ; se tromper là-dessus décale tout de 16 px.

## Couche physique

Une seule : `physics_layer_0/collision_layer = 1`. Le polygone standard pour une
tuile 1×1 pleine :

```
PackedVector2Array(-8, -8, 8, -8, 8, 8, -8, 8)
```

Les cas particuliers en place :

| Tuiles | Collision |
|---|---|
| Arbres de bordure 3×3 | les **deux rangées basses** (48×32) |
| Arbre isolé 3×4 | la **rangée du pied**, sur les 3 cases de large |
| Maisons | pleine, **sauf** les tuiles opaques à moins de 25 % |
| Bouche de grotte `5:33,23` | **aucune** — c'est l'entrée |
| Eau profonde (`5:5,34`, `5:6,34`, `5:6,35`) | pleine |
| Eau claire `5:9,31` et plantes `5:13,32` | **aucune** — faible profondeur |
| Trait de côte, sable, chemins, herbes hautes, décors | aucune |

Trois de ces règles viennent d'une partie de test, et valent d'être comprises
plutôt que recopiées :

- **La rangée haute d'un arbre 3×3 ne bloque pas.** Les arbres sont posés
  toutes les deux cases, donc leurs collisions se chevauchent : bloquer les
  trois rangées rendait infranchissable une rangée d'herbe visible à l'écran.
  On peut désormais marcher derrière la cime, ce qui est le rendu attendu.
- **L'arbre isolé bloque sa rangée de pied, pas la case du dessous.** On doit
  pouvoir se tenir sous l'arbre, devant le tronc ; ce qu'il faut interdire,
  c'est de remonter d'une case, des deux côtés comme au milieu. Le polygone
  couvre donc toute la largeur de la cime sur la seule rangée du pied.
- **Une tuile de maison quasi transparente est du sol.** Les trois tuiles de
  la façade du Centre Pokémon (`5:99`, `6:99`, `7:99`, opaques à 19 %, 19 % et
  4 %) ne montrent que de l'herbe : les bloquer interdisait trois cases qui
  n'ont rien d'un mur. **Mesurer l'opacité avant de déclarer une collision.**
  Ces trois-là portent en plus `y_sort_origin = -8` : ce sliver appartient
  visuellement à la rangée du dessus, et sans ça il coupait la tête du joueur
  qui se tient devant.

## Décor franchissable : trier depuis le haut de la case

**Toute tuile 1×1 d'un calque de `World` posée sur une case franchissable doit
porter `y_sort_origin = -15`.** Sinon elle se dessine par-dessus le joueur qui
s'y tient.

La valeur n'est pas arbitraire : elle place le point de tri de la tuile **1 px
sous celui du joueur de la rangée du dessus**. Les trois comportements attendus
sont alors satisfaits — joueur au-dessus : tuile devant ; joueur sur la case ou
en dessous : joueur devant.

Pourquoi pas `-8`, le bord haut de la case ? Parce que le tri utilise la
position **interpolée** pendant un pas. À `-8` la bascule tombe au milieu du
pas : en entrant dans la case par le haut, la tuile recouvrait brièvement les
jambes du joueur. À `-15` elle tombe après 1 px sur 16, soit une frame.

Les six cases concernées aujourd'hui, à recalculer après toute modification de
collision :

| Tuile | Cases |
|---|---|
| `5:13,32` plantes aquatiques | (39,16) (40,18) |
| `5:5,99` `5:6,99` `5:7,99` façade | (31,7) (32,7) (33,7) |
| `5:33,23` bouche de grotte | (38,2) |

La liste se recalcule : croiser les cases non solides mesurées en jeu avec les
cases couvertes par `Cliffs`, `Props` et `Houses`. Les grosses tuiles d'arbres
sont exclues — là on veut justement passer derrière.

## Ce qui reste à déclarer

Les collisions couvrent les ~150 tuiles que `start_town` utilise réellement.
**Une tuile jamais posée jusqu'ici n'a pas de collision tant qu'on ne l'a pas
déclarée** — une fois, et c'est acquis.

Trou connu : le terrain `mountain` (colonnes 20-25, lignes 21-23) est déclaré
comme terrain mais aucune de ses tuiles n'a de collision. Peindre une montagne
avec ce pinceau donne un décor traversable.

## Terrains (autotuilage)

| Set | Nom | Tuiles |
|---|---|---|
| `terrain_set_0` | `sand_path` | colonnes 0-4, lignes 16-18 |
| `terrain_set_1` | `mountain` | colonnes 20-25, lignes 21-23 |

Les chemins existants ont été peints avec `sand_path`. **Peins toujours un
chemin au pinceau terrain**, jamais tuile par tuile : les raccords de bord et de
coin se placent seuls.

## Manque par rapport au tutoriel

Une couche de données perso **`LEDGE`** (type String, valeurs `"DOWN"`,
`"LEFT"`, `"RIGHT"`). Le tutoriel l'interroge dans `CharacterMovement.cs` quand
le joueur touche une tuile : si la direction correspond, il saute le talus au
lieu d'être bloqué. On a zéro couche de données perso aujourd'hui — à ajouter
avant d'implémenter les talus.
