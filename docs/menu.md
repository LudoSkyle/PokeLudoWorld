# Menu de pause

`scenes/ui/pause_menu.tscn`, script `PauseMenu.kt`, instancié dans
`game_manager.tscn`. Une colonne d'entrées en haut à droite, un curseur en
début de ligne.

| Touche | Effet |
|---|---|
| **X** (action `menu`) | ouvre le menu ; le referme s'il est ouvert |
| Haut / Bas | déplace le curseur, qui **boucle** aux deux bouts |
| interaction | valide l'entrée sous le curseur |

Entrées actuelles : **Sac** (ne fait encore rien), **Options** (ouvre l'écran
des options), **Quitter** (ferme le menu). Le menu est collé au coin haut droit
de l'écran, comme dans les jeux d'origine. Le curseur garde sa place d'une ouverture à l'autre.

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
| interaction sur **Retour**, ou **X** | ramène au menu de pause |

Le choix en cours est en **rouge**. Une valeur s'applique et s'enregistre dès
qu'on la change, sans validation.

| Ligne | Valeurs | Effet |
|---|---|---|
| Vitesse du texte | Lente, Normale, Rapide (défaut), Instant | secondes par lettre de la boîte de dialogue : 0,08 / 0,04 / 0,02 / 0 |

Les réglages vivent dans `Settings.kt` et sont gardés dans
`user://settings.cfg`. `MessageBox` les relit au démarrage. Le menu de pause
passe la main à l'écran des options tant qu'il est ouvert (`PauseMenu.handle`).

**Ajouter un réglage** : une ligne sous `Control/Screen/Rows` (avant `Back`),
sa valeur dans `Settings`, un cas dans `OptionsMenu.handle`, et 16 px de jeu de
plus à `ListFrame`.

Les tests forcent la vitesse Rapide au démarrage (`tests/lib.gd`) : ils ne
dépendent pas du réglage enregistré par le joueur.
