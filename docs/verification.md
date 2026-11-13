# Vérifier sans ouvrir l'éditeur

Godot n'est pas dans `/Applications` sur la machine de dev. Pose-le une fois :

```bash
GODOT=/Users/godart/Downloads/Godot.app/Contents/MacOS/Godot
```

> Lancé depuis `~/Downloads`, macOS l'exécute via AppTranslocation, depuis un
> chemin temporaire en lecture seule : les réglages d'éditeur ne persistent pas.
> Le déplacer dans `/Applications` règle le problème.

## Le projet compile-t-il, la scène charge-t-elle ?

```bash
"$GODOT" --headless --path "$PWD" --import && "$GODOT" --headless --path "$PWD" --quit-after 30
```

Aucune sortie en dehors des logs de `Globals` = aucune erreur.

## Rendre une image

Le mode headless ne rend rien. Il faut une fenêtre, et un script GDScript
temporaire — qui cohabite sans problème avec le Kotlin :

```gdscript
extends SceneTree
func _initialize() -> void: _run.call_deferred()
func _run() -> void:
    root.size = Vector2i(768, 448)
    var level := load("res://.../start_town.tscn").instantiate()
    root.add_child(level)
    await process_frame
    root.get_texture().get_image().save_png("user://shot.png")
    quit()
```

```bash
"$GODOT" --path "$PWD" --script res://.probe_tmp/shot.gd
```

L'image sort dans `~/Library/Application Support/Godot/app_userdata/PokeLudoWorld/`.
**Supprimer le dossier de sonde après usage.**

## Tester les collisions

Headless suffit : instancier la map, attendre trois `physics_frame`, puis
`intersect_point` sur le centre de chaque case et imprimer une carte ASCII.
C'est ce qui a permis de voir que la bouche de grotte était le seul trou de la
falaise, et que la sortie ouest était ouverte.

## Tester le tri Y

Ajouter des `Polygon2D` magenta dans `World/Entities`, origine aux pieds :

```gdscript
p.polygon = PackedVector2Array([Vector2(-6,-22), Vector2(6,-22), Vector2(6,0), Vector2(-6,0)])
p.position = Vector2(case.x * 16 + 8, case.y * 16 + 16)
```

Au-dessus d'un arbre on doit passer derrière, en dessous devant.

## Une capture qui ne montre pas le joueur n'est pas un résultat

La caméra est bornée à l'étendue de la map : près d'un bord, le joueur n'est
plus au centre de l'image, et un recadrage fixe sur le centre peut ne pas le
montrer du tout. Ça s'est produit sur la zone d'eau, la capture est passée pour
bonne, et le défaut est remonté par le joueur.

Dans une sonde, lever les limites avant de capturer :

```gdscript
cam.limit_left = -10000 ; cam.limit_top = -10000
cam.limit_right = 10000 ; cam.limit_bottom = 10000
```

Le joueur est alors exactement au centre, et `cam.get_screen_center_position()`
doit valoir sa position — à imprimer, c'est l'assertion qui empêche de valider
une image vide.

## Tester en jouant, pas en téléportant

Poser le joueur sur une case par `position = ...` court-circuite tout ce qui
peut mal tourner : le chemin pour y arriver, le pas en cours, la touche encore
enfoncée. Trois défauts sont passés ainsi sur les changements de carte.

Une sonde peut jouer pour de vrai : `Input.action_press("ui_up")`, attendre que
la case change, relâcher. Avec un parcours en largeur sur les collisions du
jeu, elle suit n'importe quel trajet. Les contrôles à faire à chaque arrivée
sont listés dans [levels.md](levels.md).

## Les quatre questions, avant toute sonde

Un test automatique vérifie ce qu'on a décidé, pas si ça a du sens. Avant de
rendre la main, se poser ces questions **case par case**, le personnage posé à
chaque endroit clé :

1. **Est-ce visuellement logique, possible ?** Un pot de fleurs ici a-t-il un
   sens ? Une fenêtre peut-elle être là ?
2. **Le comportement est-il logique ?** On entre par la porte, par le milieu de
   l'escalier ; on ne traverse pas une barrière. Comme dans la vraie vie.
3. **L'ensemble est-il cohérent ?** Pas de caillou dans une maison, pas
   d'algues sur l'herbe.
4. **Les collisions sont-elles logiques ?** Pour chaque case bloquée : qu'est-ce
   qui gêne physiquement ? Pour chaque case libre : pourrait-on s'y tenir ?

Quand une référence du jeu d'origine est fournie, c'est à elle qu'on compare,
avant la planche de tuiles.

## La règle qui coûte cher quand on l'oublie

**Ne jamais valider un rendu sur une vue d'ensemble.** Deux bugs sont passés
comme ça : un tronc d'arbre sur un toit, une entrée de grotte recouverte par le
chemin. Les deux tenaient sur quelques dizaines de pixels.

La méthode qui marche :

1. Calculer par programme **toutes** les cases où deux calques se recouvrent.
   Sur `start_town` il n'y en a que 11.
2. Zoomer sur chacune, une par une.
3. Comparer au rendu d'avant la modification par un **diff case par case** sur
   toute la map, et annoncer le chiffre.

Et quand on demande une relecture visuelle dans l'éditeur : **le redémarrer
soi-même**. Un éditeur déjà ouvert garde les anciens fichiers en mémoire, et on
se fait renvoyer la même capture.
