# Menu de pause

`scenes/ui/pause_menu.tscn`, script `PauseMenu.kt`, instancié dans
`game_manager.tscn`. Une colonne d'entrées en haut à droite, un curseur en
début de ligne.

| Touche | Effet |
|---|---|
| **X** (action `menu`) | ouvre le menu ; le referme s'il est ouvert |
| Haut / Bas | déplace le curseur, qui **boucle** aux deux bouts |
| interaction | valide l'entrée sous le curseur |

Entrées actuelles : **Sac** et **Options** (ne font encore rien), **Quitter**
(ferme le menu). Le curseur garde sa place d'une ouverture à l'autre.

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
