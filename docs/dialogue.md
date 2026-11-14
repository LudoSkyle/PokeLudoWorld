# Boîtes de dialogue et objets lisibles

## La boîte

`scenes/ui/message_box.tscn`, instanciée une seule fois dans `game_manager`,
**à l'intérieur du `SubViewport`** : elle est donc rendue à la résolution du jeu
et suit le même filtrage pixel que le décor. Hors du SubViewport, elle serait
lissée.

```
MessageBox (CanvasLayer)   MessageBox.kt
└── Control
    ├── Speaker (Control)      l'encart du nom
    ├── Box (NinePatchRect)
    │   └── Text (RichTextLabel)
    └── Choices (ChoiceBox)    Oui / Non d'une question
```

Le texte s'affiche lettre par lettre (`secondsPerLetter`, 0,02 s). `MessageBox`
s'expose en singleton par `MessageBox.instance`, comme `Globals`.

## Le nom de celui qui parle

Un PNJ qui a un nom (`display_name`, voir [npcs.md](npcs.md)) le voit affiché
dans un **encart au-dessus de la boîte, à gauche** (`Control/Speaker`), le temps
de son dialogue. L'encart prend la largeur du nom.

- Un personnage sans nom, un panneau, un meuble : pas d'encart.
- Une boîte qui **donne un objet** (`@give:`) est dite par le jeu, pas par le
  personnage : l'encart s'efface le temps de cette boîte, puis revient.
- Le nom est écrit en français et traduit à l'affichage, comme un texte.
- **Sa couleur dit le genre**, comme dans les jeux d'origine : rouge pour une
  femme (`gender = "female"`), bleu pour un homme (`"male"`), l'encre du
  texte si le genre n'est pas donné.

C'est un encart et non un préfixe « Alix : » dans le texte : une boîte tient
deux lignes, et plusieurs répliques les remplissent déjà.

## Une seule lecture de la touche

**`MessageBox` ne lit jamais la touche d'interaction.** C'est `Player` qui lit
`interact` et la lui passe à chaque image par `handle(interact)`, qui appelle
`advance()`.

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
text = "Maison de Ludo.|La porte n'est jamais fermée, entrez donc."
```

Un tableau exporté serait plus propre en théorie, mais plus pénible à éditer
pour ce que ça apporte.

`required_flag` / `forbidden_flag` font dépendre sa présence de l'histoire
([quests.md](quests.md)).

## Les meubles examinables

`scenes/levels/readable.tscn` — un `StaticBody2D` **invisible**, script
`Readable.kt`. Le meuble reste une tuile ; le corps est posé sur sa case pour
que le joueur le trouve devant lui.

| `kind` | Ce qu'il dit |
|---|---|
| `text` (défaut) | le contenu de `text`, avec `|` entre deux boîtes |
| `clock` | **l'heure réelle** de la machine, lue à chaque examen |
| `tv` | une émission **tirée au hasard** parmi dix |
| `item` | une **trouvaille** : donne un objet une fois, pose son drapeau — voir [quests.md](quests.md) |

Avec `kind = text`, l'export `states` fait dépendre le texte de l'histoire,
`ask` pose une question avant de le dire, et `required_flag` /
`forbidden_flag` décident de la présence du meuble : voir
[quests.md](quests.md).

Les émissions sont dans `Readable.TV_PROGRAMS`, dans l'esprit des jeux
d'origine : la télé décrit en une phrase ce qui passe (« Il y a un film à la
télé… »), ou donne la météo. Tant que le monde n'a pas de Pokémon, aucune n'en
parle.

Dans les intérieurs, ils sont générés avec la pièce, sous un nœud `Readables` :

| Meuble | Texte |
|---|---|
| bibliothèques, étagères à livres | pleine de livres qui ont l'air très intéressants |
| poubelle | vide — elle pourra contenir quelque chose plus tard |
| serveurs | ont l'air de contenir des données très importantes |
| télé, horloge | voir `kind` |

Un corps est posé sur **chaque case solide** du meuble, pour qu'on puisse
l'examiner de n'importe quel côté. Une horloge est au mur : son corps est sur
la case **en dessous**, celle qu'on regarde depuis le sol.

La police est **Pokémon DP Pro** (`assets/fonts/pokemon-dp-pro.ttf`,
crystalwalrein, CC BY-SA 3.0), la même que dans les menus, en **64 px** sans
lissage : un pixel de la police vaut quatre pixels écran, comme le décor. Elle
a les accents et l'apostrophe. Encre `#585850`, ombre `#a8b8b8` à droite, en dessous et en diagonale
(`PixelShadow`, voir [menu.md](menu.md)).

La boîte fait 960×168 px, centrée en bas de l'écran. Elle tient **deux lignes**
d'environ 43 caractères ; au-delà, couper avec `|`. Le bandeau de lieu, lui,
garde Pokémon Emerald Pro en 48 px.

## L'interaction

`Player.readFacingObject()` interroge la case regardée via
`CharacterMovement.colliderAt(direction)` — la même requête physique que le
déplacement, mais elle renvoie *quoi* bloque et non seulement *si* ça bloque.
Si c'est un `Sign` ou un `Readable`, il se lit.

La case d'un meuble examinable contient deux corps : le calque de tuiles, qui
dessine et bloque, et le `Readable`. `colliderAt` renvoie en priorité le
`StaticBody2D`, sinon le calque.

Tout ce qui sera interactif plus tard (PNJ, objets au sol) passera par là :
ajouter une branche dans `readFacingObject`.

## La touche

Action `interact` dans `project.godot` : **Espace** ou **Entrée**.

## Les consignes en tête de boîte

Une boîte peut commencer par des consignes, exécutées **au moment où elle
s'affiche** et jamais affichées. Chacune est suivie d'une espace ; elles se
combinent dans n'importe quel ordre.

| Consigne | Effet |
|---|---|
| `@give:<id>`, `@give:<id>*3` | met l'objet dans le sac ; un objet rare est montré au centre de l'écran — voir [bag.md](bag.md) |
| `@take:<id>`, `@take:<id>*3` | retire l'objet du sac |
| `@flag:<drapeau>` | pose un drapeau d'histoire — voir [quests.md](quests.md) |
| `@sound:<jingle>` | joue un jingle, musique en pause ; le dialogue attend qu'il finisse — voir [audio.md](audio.md) |
| `@reload` | recharge la carte dans un fondu **une fois le dialogue refermé** — voir [quests.md](quests.md) |

## Une question dans un dialogue

`MessageBox.ask(question, suite)` écrit la question, puis montre **Oui / Non**
au-dessus de la boîte (`Control/Choices`, une `ChoiceBox`). Oui enchaîne sur la
suite ; Non, ou la touche du menu, referme. Pendant la question, une pression
ne fait que finir de l'écrire.

C'est ce que fait l'export `ask` d'un PNJ ou d'un meuble
([quests.md](quests.md)). L'écran de sauvegarde et le sac posent leurs propres
questions avec `say()`, parce qu'ils enchaînent autre chose qu'un dialogue.
