# Boîtes de dialogue et objets lisibles

## La boîte

`scenes/ui/message_box.tscn`, instanciée une seule fois dans `game_manager`,
**à l'intérieur du `SubViewport`** : elle est donc rendue à la résolution du jeu
et suit le même filtrage pixel que le décor. Hors du SubViewport, elle serait
lissée.

```
MessageBox (CanvasLayer)   MessageBox.kt
└── Control
    └── Box (NinePatchRect)
        └── Text (RichTextLabel)
```

Le texte s'affiche lettre par lettre (`secondsPerLetter`, 0,02 s). `MessageBox`
s'expose en singleton par `MessageBox.instance`, comme `Globals`.

## Une seule lecture de la touche

**`MessageBox` ne lit jamais l'entrée.** C'est `Player` qui lit `interact` et
appelle `advance()`.

Ce n'est pas un détail : si les deux la lisaient, la pression qui ouvre la boîte
la ferait avancer dans la même frame, et le premier message sauterait. Un seul
lecteur rend le problème impossible plutôt que de le rattraper avec un drapeau.

Conséquence côté joueur : une boîte ouverte court-circuite le déplacement. Pas
de machine à états tant qu'il n'y a que deux modes — voir
[docs/player.md](player.md).

## `advance()` fait deux choses

- texte en cours de défilement → l'affiche en entier d'un coup ;
- texte déjà entier → passe au message suivant, et ferme s'il n'y en a plus.

C'est le comportement des jeux d'origine : une pression pour « accélérer », une
autre pour « suivant ».

## Les panneaux

`scenes/levels/sign.tscn` — un `StaticBody2D` avec son sprite et sa collision.

**Un panneau est un objet, pas une tuile.** Une tuile porterait son texte dans
le TileSet, donc *tous* les panneaux du jeu diraient la même chose. Les deux
panneaux de `start_town` étaient des tuiles `5:81,7` du calque `Props` ; ils ont
été retirés des données de tuiles et remplacés par des instances.

Ils vivent dans `World` pour être triés en Y, à la position du **centre de leur
case** comme le joueur.

### Ajouter un panneau

Instancier `sign.tscn` sous `World`, le placer sur un centre de case, et
remplir `text`. Une **barre verticale `|` sépare deux boîtes successives** :

```
text = "Maison de Ludo.|La porte n est jamais fermee, entrez donc."
```

Un tableau exporté serait plus propre en théorie, mais plus pénible à éditer
pour ce que ça apporte.

## L'interaction

`Player.readFacingObject()` interroge la case regardée via
`CharacterMovement.colliderAt(direction)` — la même requête physique que le
déplacement, mais elle renvoie *quoi* bloque et non seulement *si* ça bloque.
Si c'est un `Sign`, il se lit.

Tout ce qui sera interactif plus tard (PNJ, objets au sol) passera par là :
ajouter une branche dans `readFacingObject`.

## La touche

Action `interact` dans `project.godot` : **Espace** ou **Entrée**.
