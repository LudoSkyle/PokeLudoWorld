# Sauvegarde

**Trois emplacements** de sauvegarde. Une partie s'écrit depuis le menu de
pause (**Sauvegarder**), dans l'emplacement qu'elle occupe, et se reprend
depuis l'écran titre, en choisissant sa carte ([title.md](title.md)).

## Les emplacements

Un fichier par emplacement : `user://save_1.cfg`, `save_2.cfg`, `save_3.cfg`
(`GameFiles.save(slot)`, `SaveGame.SLOTS`). **La partie en cours occupe
`SaveGame.slot`**, choisi à l'écran titre : « Continuer » prend celui de la
carte, « Nouvelle partie » le premier libre. Le menu de pause n'écrit que dans
celui-là, et « Une sauvegarde existe déjà » ne parle que de lui.

Une nouvelle partie **réserve** son emplacement sans rien y écrire : tant
qu'elle n'a pas été sauvegardée, l'emplacement reste libre aux yeux de l'écran
titre.

**L'ancienne sauvegarde unique** (`user://save.cfg`, d'avant les emplacements)
n'est pas perdue : au lancement, si elle existe et que le premier emplacement
est libre, elle est renommée en `save_1.cfg` (`SaveGame.adoptOldSave`).

## Ce qui est enregistré

`SaveGame.kt`, dans le fichier de l'emplacement :

| Clé | Contenu |
|---|---|
| `scene` | chemin de la scène de la carte |
| `x`, `y` | position du joueur, un centre de case |
| `facing_x`, `facing_y` | direction regardée |
| `location`, `banner` | nom du lieu (en français) et son bandeau |
| `seconds` | temps de jeu total |
| `badges`, `pokedex`, `team` | badges gagnés, espèces vues, équipe (espèces séparées par des virgules) — **toujours 0, 0 et vide** : rien ne les compte encore, mais la carte de la partie les lit déjà |
| section `[items]` | le contenu du sac : une quantité par identifiant d'objet |
| section `[flags]` | les drapeaux d'histoire posés ([quests.md](quests.md)) : `nom=true` |

Rien d'autre n'a d'état pour l'instant : les PNJ repartent de leur case de
départ, comme à chaque changement de carte. Un nouvel état à garder s'ajoute
dans `SaveGame.State`, `read` et `write`, comme le sac et les drapeaux.

Une **nouvelle partie** part d'un sac vide et sans aucun drapeau
(`SceneManager.prepare`). Elle n'efface pas la sauvegarde : celle-ci reste en
place tant qu'on ne sauvegarde pas par-dessus.

Le **temps de jeu** tourne en permanence, menus compris, comme dans les jeux
d'origine (`SceneManager.playSeconds`). Il s'affiche en heures:minutes.

## L'écran de sauvegarde

`scenes/ui/save_menu.tscn`, script `SaveMenu.kt`. Le panneau du menu de pause
se cache et laisse la place à :

- un **résumé** en haut à gauche : le lieu, le temps de jeu ;
- la **question** dans la boîte de dialogue ;
- **Oui / Non** dans une petite boîte au-dessus d'elle, qui n'apparaît qu'une
  fois la question entièrement écrite (`ChoiceBox.kt`, la même boîte que pour
  les actions du sac ; `scenes/ui/choice_box.tscn` en est la version à
  réponses libres).

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

« Continuer », sur la carte d'une partie, appelle
`SceneManager.start(slot, resume = true)` : il lit la sauvegarde de cet
emplacement, charge sa carte à la place de la carte de départ, puis pose le
joueur à sa place avec son regard. Si la carte n'existe plus, la sauvegarde est
ignorée et le jeu démarre normalement.

Sans écran titre (`show_title = false`, le cas des tests), on joue sur le
premier emplacement, et c'est `load_save` qui décide de le reprendre au
lancement.

Pour **effacer une partie**, la choisir à l'écran titre, puis Effacer.

## Tests

Lancé par `tests/run.sh`, le jeu écrit dans `user://test_save_1.cfg` à
`test_save_3.cfg` (`GameFiles.kt`), saute l'écran titre et ne reprend pas de sauvegarde au
démarrage : la sauvegarde du joueur n'est ni lue ni touchée. `relaunch()` (`tests/lib.gd`) quitte et
relance le jeu en la reprenant, pour vérifier la reprise.
