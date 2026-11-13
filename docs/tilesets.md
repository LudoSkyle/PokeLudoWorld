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
| Arbre isolé 3×4 | le tronc, sur ses **deux** cases |
| Maisons | pleine, **sauf** les tuiles opaques à moins de 25 % |
| Bouche de grotte `5:33,23` | **aucune** — c'est l'entrée |
| Eau profonde (`5:5,34`, `5:6,34`, `5:6,35`) | pleine |
| Eau claire `5:9,31` | **aucune** — faible profondeur, on y marche |
| Trait de côte, sable, chemins, herbes hautes, décors | aucune |

Trois de ces règles viennent d'une partie de test, et valent d'être comprises
plutôt que recopiées :

- **La rangée haute d'un arbre 3×3 ne bloque pas.** Les arbres sont posés
  toutes les deux cases, donc leurs collisions se chevauchent : bloquer les
  trois rangées rendait infranchissable une rangée d'herbe visible à l'écran.
  On peut désormais marcher derrière la cime, ce qui est le rendu attendu.
- **Le tronc de l'arbre isolé déborde sur la case du dessous.** Son polygone
  va de `+8` à `+36` en local, au-delà des bornes de la tuile — c'est permis,
  et c'est nécessaire : sinon le joueur a les pieds dans le tronc.
- **Une tuile de maison quasi transparente est du sol.** Les trois tuiles de
  la façade du Centre Pokémon (`5:99`, `6:99`, `7:99`, opaques à 19 %, 19 % et
  4 %) ne montrent que de l'herbe : les bloquer interdisait trois cases qui
  n'ont rien d'un mur. **Mesurer l'opacité avant de déclarer une collision.**

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
