# Le joueur

`scenes/characters/player.tscn`, instancié dans `World/Entities` de chaque map.

```
Player (CharacterBody2D)     Player.kt — assemble les composants
├── Sprite (AnimatedSprite2D)  CharacterAnimation.kt
├── Collider (CollisionShape2D)
├── Camera (Camera2D)          PlayerCamera.kt
├── Input (Node)               PlayerInput.kt
└── Movement (Node)            CharacterMovement.kt
```

Trois composants indépendants, assemblés par `Player.kt` : l'entrée ne connaît
pas le déplacement, le déplacement ne connaît pas l'animation.

Pas de machine à états : une boîte de dialogue ouverte se contente de
court-circuiter le déplacement dans `Player._process`. Elle s'imposera le jour
où un troisième mode apparaîtra (combat, menu).

`Player` lit aussi la touche `interact` — et il est le **seul** à la lire, y
compris pour faire avancer un dialogue. La raison est dans
[dialogue.md](dialogue.md).

## Repère et échelle

L'origine du joueur est le **centre de sa case**, soit `(col*16+8, row*16+8)`.
C'est différent du tutoriel, qui ancre au coin haut-gauche — la raison tient au
tri Y et est expliquée dans [architecture.md](architecture.md).

Le sprite source fait 32×48, mais il est rendu à **`scale = 0.5`**, donc 16×24 :
une case de large, une case et demie de haut. Sans cette mise à l'échelle le
personnage est deux fois trop gros pour le décor. Son décalage `(0, -4)` place
ses pieds au bas de la case.

Caméra en `zoom = 4` — le viewport fait 1152×648, on voit donc 18 cases de
large et 10 de haut, plus un liseré de la onzième. Rester sur un zoom
**entier** : un zoom fractionnaire donne des pixels de largeurs inégales qui
scintillent en marchant. Elle est bornée à l'étendue du calque `Background/Ground` lue par
`getUsedRect()` : rien à régler quand la map change de taille.

## Déplacement

Case par case, et **un pas engagé va toujours jusqu'au bout** : l'entrée n'est
lue qu'entre deux pas, sinon le personnage s'arrête entre deux cases.

Le ressenti Pokémon vient du seuil de maintien (`holdThreshold`, 0,12 s) :

- pression brève → le personnage **pivote** sans avancer ;
- pression maintenue → il **marche**, et enchaîne tant que la touche est tenue.

Vitesse : `tilesPerSecond = 4`.

## Collisions

Le joueur interroge la case visée avec `intersect_point` sur le **masque 1**,
celui des tuiles. Il est lui-même sur le **calque 2**, pour ne jamais se
détecter lui-même — c'est plus simple que d'exclure son propre corps de la
requête.

Rien n'est codé en dur : si une tuile bloque, c'est qu'elle a un polygone de
collision dans `level.tres`. Voir [tilesets.md](tilesets.md).

## Animations

`resources/spriteframes/player.tres`, nommées `<etat>_<direction>`.

Les rangées du sprite sheet sont, dans l'ordre : **bas, gauche, droite, haut**.
C'est contre-intuitif à l'œil — vérifier au rendu avant de corriger quoi que ce
soit, l'ordre a déjà été remis à l'endroit une fois.

Un demi-tour sur place joue `turn_<direction>` : deux images, une image de pas
puis l'image fixe, en 0,2 s. C'est le petit à-coup des jeux d'origine quand on
pivote sans avancer. L'animation ne boucle pas, et `refresh()` la laisse aller
au bout avant de retomber sur l'`idle_*` — sans ça elle serait écrasée dès la
frame suivante.


## Changement de carte

Le joueur n'appartient à aucune carte : `SceneManager` le reparente. À
l'arrivée son pas est annulé, il est orienté dos à la porte et une nouvelle
pression est exigée avant de bouger — le détail et les raisons sont dans
[levels.md](levels.md).
