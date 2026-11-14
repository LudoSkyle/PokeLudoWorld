# Icônes d'objets

Deux **atlas** d'icônes de 24×24, sur fond transparent. Un objet désigne la
sienne par une référence (`Item.icon`, voir `ItemIcons.kt`).

| Atlas | Contenu | Référence | Auteur |
|---|---|---|---|
| `frlg.png` | les 267 icônes officielles de Rouge Feu / Vert Feuille, 16 par rangée | `frlg:<numéro>`, de 0 à 266, dans l'ordre de la planche d'origine | extraites du jeu |
| `itemdex.png` | « Ultimate Pokémon ItemDex », toutes générations, 1382 icônes | `dex:<bloc>:<rangée>:<colonne>`, en hexadécimal, **comme sur la planche d'origine** : `dex:01:0:3` est le bloc `01`, rangée `0_`, colonne `_3` | Kryptonlion (DeviantArt), crédit demandé |

Icônes de service : `frlg:226` est la flèche de retour, `frlg:227` le point
d'interrogation affiché quand une référence ne mène à rien.

## Trouver une icône

Les planches d'origine sont dans `sources/` (dossier ignoré par Godot) :

- `frlg_items.png` : cases de 24×24 espacées d'un pixel, sur fond orange. Le
  numéro d'une icône est son rang en lisant la planche de gauche à droite et de
  haut en bas, à partir de 0.
- `itemdex_kryptonlion.png` : seize blocs numérotés `00` à `0F`, chacun de
  16×16 cases de 32×32 étiquetées en hexadécimal. Le dessin occupe les 24×24
  du centre de sa case ; les deux planches sont donc à la **même échelle**.

L'atlas `itemdex.png` laisse vides les cases dont le dessin déborde du carré
central (les étiquettes de texte, quelques cases spéciales du bloc `00`).
