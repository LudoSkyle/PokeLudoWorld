# Sauvegarde

Une seule sauvegarde, écrite depuis le menu de pause (**Sauvegarder**) et
**reprise automatiquement au lancement** du jeu : il n'y a pas encore d'écran
titre.

## Ce qui est enregistré

`SaveGame.kt`, dans `user://save.cfg` :

| Clé | Contenu |
|---|---|
| `scene` | chemin de la scène de la carte |
| `x`, `y` | position du joueur, un centre de case |
| `facing_x`, `facing_y` | direction regardée |
| `location`, `banner` | nom du lieu (en français) et son bandeau |
| `seconds` | temps de jeu total |
| section `[items]` | le contenu du sac : une quantité par identifiant d'objet |

Rien d'autre n'a d'état pour l'instant : les PNJ repartent de leur case de
départ, comme à chaque changement de carte. Un nouvel état à garder (drapeaux
d'histoire) s'ajoute dans `SaveGame.State`, `read` et `write`, comme le sac.

Le **temps de jeu** tourne en permanence, menus compris, comme dans les jeux
d'origine (`SceneManager.playSeconds`). Il s'affiche en heures:minutes.

## L'écran de sauvegarde

`scenes/ui/save_menu.tscn`, script `SaveMenu.kt`. Le panneau du menu de pause
se cache et laisse la place à :

- un **résumé** en haut à gauche : le lieu, le temps de jeu ;
- la **question** dans la boîte de dialogue ;
- **Oui / Non** dans une petite boîte au-dessus d'elle, qui n'apparaît qu'une
  fois la question entièrement écrite (`ChoiceBox.kt`, réutilisable pour toute
  question).

Déroulé :

1. « Voulez-vous sauvegarder la partie ? »
2. s'il existe déjà une sauvegarde : « Une sauvegarde existe déjà. Voulez-vous
   l'écraser ? »
3. « La partie est sauvegardée. » reste **une seconde** à l'écran une fois
   écrite (`hold_seconds`), puis tout se ferme, menu compris.

**Non**, ou la touche du menu, ramène au menu de pause sans rien écrire. Le
curseur s'ouvre toujours sur Oui.

`MessageBox.say(texte)` écrit un texte et le laisse à l'écran sans attendre de
touche ; c'est l'écran qui enchaîne ou referme (`MessageBox.close()`).

## La reprise

`SceneManager._ready` lit la sauvegarde (`load_save`, vrai par défaut), charge
sa carte à la place de la carte de départ, puis pose le joueur à sa place avec
son regard. Si la carte n'existe plus, la sauvegarde est ignorée et le jeu
démarre normalement.

Pour **repartir de zéro**, supprimer `save.cfg` dans le dossier utilisateur du
jeu (`~/Library/Application Support/Godot/app_userdata/PokeLudoWorld/`).

## Tests

Lancé par `tests/run.sh`, le jeu écrit dans `user://test_save.cfg`
(`GameFiles.kt`) et ne reprend pas de sauvegarde au démarrage : la sauvegarde
du joueur n'est ni lue ni touchée. `relaunch()` (`tests/lib.gd`) quitte et
relance le jeu en la reprenant, pour vérifier la reprise.
