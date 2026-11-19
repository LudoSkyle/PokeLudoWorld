# Sac et objets

## Les objets

`scripts/gameplay/items/Items.kt` est le **catalogue** : une ligne par objet.

| Champ | Rôle |
|---|---|
| `id` | identifiant ; c'est aussi sa ligne dans la sauvegarde |
| `name`, `description` | en français, traduits à l'affichage ([i18n.md](i18n.md)) |
| `pocket` | la poche : `ITEMS`, `KEY_ITEMS`, `BALLS` |
| `icon` | son icône sous `assets/items/icons/` — **par défaut, `<identifiant>.png`** : `potion` se dessine avec `potion.png` (`ItemIcons.kt`). Se donne quand l'icône ne porte pas le nom de l'objet : voir « La réserve d'icônes » |

Un objet de la poche `KEY_ITEMS` est un **objet rare** (`isKey`) : unique, sans
quantité affichée, impossible à jeter, et montré à l'écran quand on le reçoit.

`Inventory.kt` est **le contenu du sac** : `add(id, n)`, `remove(id, n)`,
`count(id)`, `has(id)`. Les objets y restent dans l'ordre où on les a reçus. Il
fait partie de la sauvegarde ([save.md](save.md)).

### Ajouter un objet

1. Une ligne dans `Items.ALL`, avec ses textes entre `N("...")`.
2. Son icône : par défaut, **le fichier `assets/items/icons/<identifiant>.png`**,
   en 32 × 32. Le pack de données en fournit près de 1 700, nommées d'après
   l'identifiant de l'objet dans Pokémon Studio (`super_repel.png`,
   `great_ball.png`) : donner à l'objet cet identifiant suffit. Si l'icône
   manque, voir « La réserve d'icônes » ci-dessous. Un objet sans fichier
   affiche un point d'interrogation.
3. Ses deux textes dans `locale/en.po`, puis `tests/run.sh i18n`.

### La réserve d'icônes

`assets/items/icons/` (le `CREDITS.md` du dossier dit d'où vient chaque icône) :

| Où | Contenu |
|---|---|
| à la racine | les 1689 icônes du pack de données, copiées par `tools/gamedata.py` : `potion.png` |
| `custom/` | **les icônes faites pour ce jeu**, et elles seules : les deux cloches |
| `other/` | trois icônes venues d'ailleurs, que le pack n'a pas : le ruban, la flèche « Retour », le point d'interrogation |

**Le nom d'un fichier dit ce qu'est l'icône, jamais à quoi le jeu
l'emploie.** C'est le champ `icon` du catalogue qui va chercher l'icône où
elle est.

| L'objet prend… | `icon` | Exemple |
|---|---|---|
| l'icône du pack qui porte son nom | rien à écrire | `potion` → `potion.png` |
| l'icône d'un autre objet du pack | le nom du fichier | `"rule_book"` pour le registre poussiéreux |
| une icône faite pour le jeu | `custom/<fichier>` | `"custom/clear_bell"` — `clear_bell.png` est le Glas Transparent officiel |
| une icône venue d'ailleurs | `other/<fichier>` | `"other/07_F_2_fan"` pour le ruban de la Veillée |

- **Toutes les icônes font 32 × 32**, et le sac les affiche quatre fois plus
  grandes, dans une case de 36 × 36 dessinée dans son fond. Une icône faite
  pour le jeu se dessine à cette taille ; les cinq anciennes de 24 × 24 ont
  été posées au centre d'un fichier de 32.
- La flèche « Retour » du sac et le point d'interrogation d'un objet sans
  icône : `ItemIcons.BACK` et `ItemIcons.UNKNOWN`.

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

Pour la mise au point, l'outil **Remplir le sac** de l'entrée **Debug** du
menu de pause remplit le sac (`PauseMenu.fillBag`, voir [menu.md](menu.md)) : huit objets, des Poké Balls,
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

Au-delà de neuf lignes la liste défile avec le curseur, et une flèche en haut ou
en bas du panneau signale ce qui reste (`tests/ui/bag_scroll.gd`).

## Le fond

Le fond d'origine fait 240×160. Il a d'abord été élargi à 288×162, l'ancien
format de l'écran, puis porté à **320×240**, l'écran en 4:3, par
`tools/bag_background.py` (`assets/ui/bag/CREDITS.md`) : rien n'est redessiné,
des bandes du fond sont recopiées — 32 colonnes du panneau, trois lignes de
liste, 30 rangées du bandeau bleu. **Le sac tient tout l'écran**, et sa liste
montre **neuf lignes** au lieu de six. Repères, en pixels de jeu : titre de
poche centré sur `x 6-82, y 3-19` ; sac en `(8, 79)` ; lignes de la liste tous
les 16 px à partir de `y 8`, texte à `x 100`, quantité calée à droite sur
`x 308` ; icône en `(5, 184)` ; description à partir de `(40, 166)`, quatre
lignes au plus.
