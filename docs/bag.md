# Sac et objets

## Les objets

`scripts/gameplay/items/Items.kt` est le **catalogue** : une ligne par objet.

| Champ | Rôle |
|---|---|
| `id` | identifiant ; c'est aussi sa ligne dans la sauvegarde |
| `name`, `description` | en français, traduits à l'affichage ([i18n.md](i18n.md)) |
| `pocket` | la poche : `ITEMS`, `KEY_ITEMS`, `BALLS` |
| `icon` | référence dans un atlas : `frlg:12`, `dex:01:0:3` ou `custom:0` (`ItemIcons.kt`) |

Un objet de la poche `KEY_ITEMS` est un **objet rare** (`isKey`) : unique, sans
quantité affichée, impossible à jeter, et montré à l'écran quand on le reçoit.

`Inventory.kt` est **le contenu du sac** : `add(id, n)`, `remove(id, n)`,
`count(id)`, `has(id)`. Les objets y restent dans l'ordre où on les a reçus. Il
fait partie de la sauvegarde ([save.md](save.md)).

### Ajouter un objet

1. Une ligne dans `Items.ALL`, avec ses textes entre `N("...")`.
2. Son icône : une référence vers l'un des atlas de `assets/items/`. Deux
   contiennent **toutes** les icônes de leur planche (267 officielles, 1382 de
   l'ItemDex) ; le troisième, `custom.png`, reçoit celles qu'on dessine pour
   le jeu. Le `CREDITS.md` du dossier explique comment lire le numéro
   d'une icône sur la planche d'origine. Une référence fausse affiche un point
   d'interrogation.
3. Ses deux textes dans `locale/en.po`, puis `tests/run.sh i18n`.

### Donner un objet

Dans un dialogue, une boîte qui commence par **`@give:<id>`** met l'objet dans
le sac au moment où elle s'affiche (`@give:<id>*3` pour trois exemplaires) :

```
text = "Tiens, prends ça.|@give:old_rod Vous recevez la Vieille canne !|Fais-en bon usage."
```

Si c'est un **objet rare**, son icône apparaît en fondu au centre de l'écran,
dans un cadre de menu (`ItemReveal.kt`). Elle reste **une seconde** une fois le
texte écrit, puis le dialogue passe seul à la boîte suivante, ou se ferme : les
touches ne pressent pas ce passage, elles ne font que finir d'écrire le texte.

Une boîte qui commence par **`@take:<id>`** le **retire** du sac de la même
façon (`@take:<id>*3`).

Un objet **à ramasser** sur une carte est un `Readable` de `kind = "item"` :
il donne son objet par ce même `@give:`, une seule fois
([quests.md](quests.md)).

Rien dans le jeu ne donne encore d'objet. En attendant, l'entrée **Debug** du
menu de pause remplit le sac (`PauseMenu.debug`) : huit objets, des Poké Balls,
et deux objets rares donnés par `@give:` pour voir leur présentation.

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

Le sac s'ouvre toujours sur la première poche, en haut de la liste, et changer
de poche remet le curseur en haut.

### Les actions sur un objet

Valider un objet ouvre une petite boîte en bas à droite (`ChoiceBox`), et le
bas de l'écran rappelle l'objet choisi :

| Objet | Actions |
|---|---|
| rare | **Annuler** |
| les autres | **Jeter**, **Annuler** |

**Jeter** se fait en trois temps :

1. **combien** : 1 par défaut ; Haut augmente, Bas diminue, et la valeur
   **boucle** — Bas à 1 saute au maximum possédé, Haut au maximum revient à 1 ;
2. **confirmation** : « Jeter Potion x2 ? », Oui / Non ;
3. le message « Vous jetez Potion x2. », qui attend une touche. La liste montre
   déjà ce qu'il reste ; un objet dont on jette le dernier exemplaire en sort.

À chaque étape, Non, Annuler ou la touche du menu ramènent à la liste sans rien
jeter. Les poches et le curseur ne bougent pas tant qu'une boîte est ouverte.

Au-delà de six lignes la liste défile avec le curseur, et une flèche en haut ou
en bas du panneau signale ce qui reste (`tests/ui/bag_scroll.gd`).

## Le fond

Le fond d'origine fait 240×160 ; il est élargi à 288×162, la taille de l'écran
du jeu (`assets/ui/bag/CREDITS.md`). Repères, en pixels de jeu : titre de poche
centré sur `x 6-82, y 3-19` ; sac en `(8, 31)` ; lignes de la liste tous les
16 px à partir de `y 8`, texte à `x 100`, quantité calée à droite sur `x 276` ;
icône en `(9, 126)` ; description à partir de `(40, 114)`, trois lignes au plus.
