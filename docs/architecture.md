# Architecture des scènes

## Structure d'une map

Chaque map vit dans `scenes/levels/<nom>.tscn` et suit ce squelette :

```
Level (Node2D)
├── Background (Node2D)          sous le joueur, jamais trié
│   ├── Ground                   terrain de base
│   ├── Paths                    chemins (peints au pinceau terrain)
│   ├── Decorations              fleurs, cailloux — purement décoratif
│   └── Grass                    herbes hautes
├── World (Node2D)               y_sort_enabled
│   ├── Cliffs                   falaises, entrées de grotte
│   ├── Props                    clôtures, panneaux, souches, rochers
│   ├── Houses                   bâtiments
│   ├── Trees                    arbres
│   └── Entities (Node2D)        joueur, PNJ
└── Overhead (TileMapLayer)      ce qui passe AU-DESSUS du joueur
```

Trois groupes, trois rôles :

- **`Background`** se dessine en premier, dans l'ordre des enfants. Rien n'y est
  trié : l'ordre des calques fait tout.
- **`World`** est trié en Y. Chaque `TileMapLayer` qu'on y met doit porter
  `y_sort_enabled = true`, sinon il ne participe pas au tri du parent et se
  dessine d'un bloc.
- **`Overhead`** se dessine après tout le monde : toits en surplomb, cimes,
  ponts sous lesquels on passe.

**Un décor qui doit masquer le joueur va dans `World`, pas dans `Background`.**
`World` se dessine intégralement après `Background` : un élément de fond ne peut
jamais repasser devant, quel que soit son `y_sort_origin`. C'est ce qui est
arrivé aux falaises, d'abord rangées dans `Background`, où les arbres leur
passaient dessus.

## Tri en Y

Godot trie un élément sur `map_to_local(case d'ancrage).y + y_sort_origin`.
Pour une tuile 1×1 le centre de case est à +8 du haut, donc **`y_sort_origin = 8`
place le point de tri au pied de la tuile** — c'est la valeur par défaut à
utiliser pour tout décor normal.

Les valeurs en place, et pourquoi :

| Tuiles | `y_sort_origin` | Raison |
|---|---|---|
| Décors 1×1 (Props, Houses, Cliffs) | `8` | pied de la tuile |
| Arbres de bordure 3×3 | `22` | voir ci-dessous |
| Arbre isolé 3×4 | `28` | base du tronc |

L'arbre 3×3 est à `22` et pas `24` à cause d'une **égalité de tri**. Son pied
tombe au bas de la rangée `ancre+1` — exactement là où commence le toit du
Centre Pokémon. Les deux triaient à 48, l'ordre devenait arbitraire et le tronc
passait sur le toit. À 22 l'arbre trie à 46 : tout décor 1×1 de la même rangée
passe devant, et l'arbre garde la main sur ce qui est strictement au-dessus.

**Règle générale : quand un décor large et un décor 1×1 se disputent la même
rangée, baisse le `y_sort_origin` du large de 2 px plutôt que de réordonner les
calques.**

## Écarts assumés par rapport au tutoriel

Le tutoriel garde une liste plate de calques sous un nœud `Tiles`, sans tri Y
global, et donne au joueur `z_index = 5` en l'ajoutant directement au viewport :
**chez lui le joueur passe toujours devant tout, on ne marche jamais derrière un
arbre.**

On a choisi l'inverse. Conséquence à ne pas oublier :

> Quand le joueur sera créé, il va dans `World/Entities` avec `z_index = 0`.
> Ne pas recopier le `z_index = 5` du tutoriel, sinon le tri Y ne sert à rien.

Aucun script du tutoriel ne référence de chemin de nœud du genre `Tiles/Ground`
(vérifié sur `part14_2`), donc ce changement de structure ne casse pas son code.

## Ce qui n'existe pas encore

- Le joueur et les PNJ (`World/Entities` est vide).
- Les déclencheurs de transition entre maps. Le tutoriel utilise une scène
  `scene_trigger.tscn` instanciée sous un nœud `SceneTriggers`.
- Les limites de map : le tutoriel pose des `StaticBody2D` à la main sous un
  nœud `Boundaries`. Ici la forêt et l'eau sont solides via le TileSet, ce qui
  suffit tant que la bordure est fermée — **sauf la sortie ouest de start_town,
  laissée ouverte exprès** pour y brancher une transition.
