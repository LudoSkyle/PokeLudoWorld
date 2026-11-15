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

Caméra en `zoom = 4` — l'écran est en **4:3**, 1280×960 (`[display]` dans
`project.godot`, et le `SubViewport` de `game_manager.tscn`) : on voit
**20 cases de large et 15 de haut**, soit 320×240 pixels de jeu. Rester sur un
zoom **entier** : un zoom fractionnaire donne des pixels de largeurs inégales
qui scintillent en marchant.

Elle est bornée à **l'étendue de la carte** (`PlayerCamera.contentRect`) : le
sol de `Background/Ground` sans son noir de remplissage, plus les autres
calques du fond (les murs dépassent du sol). Rien à régler quand la map change
de taille.

- Carte plus grande que l'écran : la caméra suit le joueur et s'arrête aux bords.
- Carte **plus petite que l'écran** sur un axe (une pièce d'intérieur) : elle
  est **centrée** sur cet axe et la caméra n'y bouge plus
  (`tests/run.sh room_centered`). Le noir de remplissage — la tuile `5:65,49`
  de `Ground` — sert alors de bordure autour de la pièce ; il doit couvrir tout
  l'écran, sinon on voit le gris de fond.

L'interface est dessinée ×4 dans ces 1280×960. Boîte de dialogue, nom, Oui/Non,
menu de pause et objet reçu sont **ancrés** (bas-centre ou bord droit) ; le sac
et les options gardent leur planche de 1152×648, centrée sur un fond uni.

## Déplacement

Case par case, et **un pas engagé va toujours jusqu'au bout** : l'entrée n'est
lue qu'entre deux pas, sinon le personnage s'arrête entre deux cases.

Le ressenti Pokémon vient du seuil de maintien (`holdThreshold`, 0,12 s) :

- pression brève → le personnage **pivote** sans avancer ;
- pression maintenue → il **marche**, et enchaîne tant que la touche est tenue.

**Deux directions tenues : la dernière pressée commande.** On tient Haut, on
presse Gauche : on va à gauche ; on relâche Gauche, Haut reprend la main.
Aucune direction n'a priorité sur une autre (`PlayerInput.heldDirection`). Un
ordre fixe — Haut, Bas, Gauche, Droite — a existé : Haut et Bas l'emportaient
toujours, et Gauche / Droite étaient ignorées tant qu'on tenait l'une d'elles.

Vitesse : `walk_pace`, 4 cases par seconde.

### Courir

**Maj maintenue** (action `run` de `project.godot`) : le personnage va à
`run_pace`, 8 cases par seconde, deux fois l'allure de la marche.

- L'allure se décide **au départ de chaque pas** : un pas engagé va au bout à
  l'allure où il a commencé, et relâcher Maj fait marcher dès le pas suivant.
- La touche seule ne fait rien : il faut une direction. Le pivot sur place
  (pression brève) ne change pas.
- La planche du joueur n'a **pas d'images de course** : c'est l'animation de
  marche qui s'accélère (`speed_scale = 2`). Une vraie course demande une
  planche en plus.
- Une scène qui déplace le joueur le fait au pas : repoussé par un garde alors
  qu'il arrivait en courant, il recule en marchant.

On court partout, intérieurs compris.

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
