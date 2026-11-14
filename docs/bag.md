# Sac et objets

## Les objets

`scripts/gameplay/items/Items.kt` est le **catalogue** : une ligne par objet.

| Champ | Rôle |
|---|---|
| `id` | identifiant ; nomme aussi l'icône (`assets/items/<id>.png`) et la ligne de la sauvegarde |
| `name`, `description` | en français, traduits à l'affichage ([i18n.md](i18n.md)) |
| `pocket` | la poche : `ITEMS`, `KEY_ITEMS`, `BALLS` |
| `counted` | faux pour un objet unique : le sac n'affiche pas de quantité |

`Inventory.kt` est **le contenu du sac** : `add(id, n)`, `remove(id, n)`,
`count(id)`, `has(id)`. Les objets y restent dans l'ordre où on les a reçus. Il
fait partie de la sauvegarde ([save.md](save.md)).

### Ajouter un objet

1. Une ligne dans `Items.ALL`, avec ses textes entre `N("...")`.
2. Son icône de **24×24** dans `assets/items/`, découpée d'une planche de
   `assets/items/sources/` (voir le `CREDITS.md` du dossier : les deux planches
   sont à la même échelle). Sans icône, le sac montre un point d'interrogation.
3. Ses deux textes dans `locale/en.po`, puis `tests/run.sh i18n`.

Rien dans le jeu ne donne encore d'objet. En attendant, l'entrée **Debug** du
menu de pause met dans le sac un exemplaire de chaque (`PauseMenu.debug`).

## L'écran du sac

`scenes/ui/bag_menu.tscn`, script `BagMenu.kt`, ouvert par l'entrée **Sac** du
menu de pause. Une poche à la fois :

- à gauche, le **nom de la poche** et le **sac**, ouvert sur cette poche ;
- à droite, la **liste**, six lignes visibles, qui se termine toujours par
  **Retour** — une poche vide ne contient que lui ;
- en bas, l'**icône** et la **description** de la ligne sous le curseur.

| Touche | Effet |
|---|---|
| Haut / Bas | parcourir la liste ; elle ne boucle pas, Retour en est le bout |
| Gauche / Droite | changer de poche ; les flèches rouges disent où l'on peut aller, les poches ne bouclent pas |
| interaction sur **Retour**, **X** ou **Échap** | refermer le sac, retour au menu de pause |

Valider un objet ne fait encore rien. Le sac s'ouvre toujours sur la première
poche, en haut de la liste, et changer de poche remet le curseur en haut.

Au-delà de six lignes la liste défile avec le curseur, et une flèche en haut ou
en bas du panneau signale ce qui reste. **Ce défilement n'est pas testé** : le
catalogue ne permet pas encore de remplir une poche à ce point.

## Le fond

Le fond d'origine fait 240×160 ; il est élargi à 288×162, la taille de l'écran
du jeu (`assets/ui/bag/CREDITS.md`). Repères, en pixels de jeu : titre de poche
centré sur `x 6-82, y 3-19` ; sac en `(8, 31)` ; lignes de la liste tous les
16 px à partir de `y 8`, texte à `x 100`, quantité calée à droite sur `x 276` ;
icône en `(9, 126)` ; description à partir de `(40, 114)`, trois lignes au plus.
