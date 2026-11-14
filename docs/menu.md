# Menu de pause

`scenes/ui/pause_menu.tscn`, script `PauseMenu.kt`, instancié dans
`game_manager.tscn`. Une colonne d'entrées en haut à droite, un curseur en
début de ligne.

| Touche | Effet |
|---|---|
| **X** ou **Échap** (action `menu`) | ouvre le menu ; le referme s'il est ouvert |
| Haut / Bas | déplace le curseur, qui **boucle** aux deux bouts |
| interaction | valide l'entrée sous le curseur |

Entrées actuelles : **Sac** (voir [bag.md](bag.md)), **Sauvegarder** (voir
[save.md](save.md)), **Options** (ouvre l'écran des options), **Debug** (outils
de mise au point : remplit le sac d'objets de test), **Quitter** (ferme le
menu). Le menu est collé au coin haut droit
de l'écran, comme dans les jeux d'origine. À chaque ouverture, le curseur repart de la **première entrée** ; il ne garde
sa place que le temps d'un aller-retour dans un écran ouvert depuis le menu.

## Haut et Bas maintenus

Dans tous les menus (pause, options, sac, boîtes de choix, quantité à jeter),
Haut et Bas passent par `MenuKeys` : une pression avance d'un cran ; touche
maintenue, le curseur repart après 0,35 s puis avance toutes les 0,11 s. Une
touche déjà enfoncée à l'ouverture du menu ne fait rien défiler.

Gauche et Droite ne se répètent pas : ils changent une poche ou un réglage, pas
une position dans une liste.

## Qui lit les touches

Comme pour la boîte de dialogue, **c'est le joueur** (`Player.kt`) : il ouvre le
menu, puis lui passe la main à chaque image avec `handle(interact)`. La touche
d'interaction n'est donc lue qu'à un seul endroit du jeu, et la pression qui
valide « Quitter » ne peut pas déclencher autre chose dans la foulée.

Le menu ne s'ouvre qu'**entre deux pas**, jamais pendant un dialogue, un fondu
ou une scène qui verrouille le joueur.

## Le monde est figé

Menu ouvert, le joueur ne marche ni ne se tourne, et les PNJ ne bougent plus
d'eux-mêmes (`Npc.isHeld`) : un coureur termine son pas, s'arrête, et repart à
la fermeture.

## Ajouter une entrée

1. Un `Label` de plus sous `Control/Menu/Entries`, à sa place dans l'ordre
   (un menu Debug irait avant `Quit`) ; agrandir `Menu`, `Frame` et `Entries`
   de 64 px écran (16 px de jeu pour `Frame`, qui est à l'échelle 4).
2. Un cas dans `PauseMenu.confirm()`, sur le **nom du nœud**.

## Le cadre

`frame` (export de `PauseMenu`) : un fichier de `assets/ui/frames`, `rse_01` à
`rse_20` ou `frlg_01` à `frlg_10`. Ce sont des 9-patch de 24×24 à marges de 8,
dessinés à l'échelle 4 comme le décor. Le texte, lui, n'est pas mis à
l'échelle : il est rendu en 48 px (voir [dialogue.md](dialogue.md)).

## Écran des options

`scenes/ui/options_menu.tscn`, script `OptionsMenu.kt`. Il couvre l'écran,
par-dessus le menu resté ouvert : un cadre de titre, un cadre de lignes.

| Touche | Effet |
|---|---|
| Haut / Bas | change de ligne |
| Gauche / Droite | change la valeur de la ligne ; pas de boucle, les bouts sont des butées |
| interaction sur **Retour**, **X** ou **Échap** | ramène au menu de pause |

Le choix en cours est en **rouge**. Une valeur s'applique et s'enregistre dès
qu'on la change, sans validation.

| Ligne | Valeurs | Effet |
|---|---|---|
| Vitesse du texte | x0.5, x1 (défaut), x2, x4 | multiplie la vitesse de la boîte de dialogue ; x1 = 0,02 s par lettre |
| Langue | Français (défaut), English | langue de tout le jeu, voir [i18n.md](i18n.md) |

Les réglages vivent dans `Settings.kt` et sont gardés dans
`user://settings.cfg`. `MessageBox` les relit au démarrage. Le menu de pause
passe la main à l'écran des options tant qu'il est ouvert (`PauseMenu.handle`).

**Ajouter un réglage** : une ligne sous `Control/Screen/Rows` (avant `Back`),
sa valeur dans `Settings`, un cas dans `OptionsMenu.handle`, et 16 px de jeu de
plus à `ListFrame`.

Lancé par `tests/run.sh`, le jeu écrit ses réglages dans un fichier de test
(`GameFiles.kt`), effacé au début de chaque test : les tests ne lisent ni ne
modifient les réglages du joueur.

## La police et le curseur

Les menus utilisent **Pokémon DP Pro** (`assets/fonts/pokemon-dp-pro.ttf`) en
64 px : la police fait 16 px de haut, un de ses pixels vaut donc 4 pixels
écran, comme les cadres et le décor. Elle a tous les accents français.

Sa ligne fait 18 px, deux de trop pour des entrées espacées de 16 : les scènes
passent par une `FontVariation` qui retire 4 px écran en haut et en bas
(`spacing_top`, `spacing_bottom`), sans rogner les lettres.

**L'ombre n'est pas dans la police.** Dans les jeux d'origine, chaque pixel de
lettre porte une ombre à droite, en dessous **et** en diagonale. Godot ne
décale l'ombre d'un texte que dans une direction : le `Label` garde la
diagonale (4 px écran, soit un pixel de police), et `PixelShadow.attachAll`
glisse derrière lui deux copies du texte, couleur d'ombre, décalées à droite et
vers le bas. Encre `#585850`, ombre `#a8b8b8`, relevées sur la capture de
référence. La boîte de dialogue fait de même ; son texte change à chaque
lettre, elle passe donc par `PixelShadow.setText`.

Le curseur (`assets/ui/cursor.png`, 6×10 avec son ombre) est extrait de la même
capture, et dessiné à l'échelle 4.
