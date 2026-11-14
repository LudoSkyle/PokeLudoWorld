# Icônes d'objets

Une icône de **24×24** par objet, nommée d'après son identifiant
(`potion.png`). `_back.png` est la flèche de retour, `_unknown.png` le point
d'interrogation affiché pour un objet sans icône.

Elles sont découpées des planches de `sources/` (dossier ignoré par Godot, il
ne sert que de réserve) :

| Planche | Contenu | Cases | Auteur |
|---|---|---|---|
| `frlg_items.png` | les objets officiels de Rouge Feu / Vert Feuille | 24×24, espacées de 1 px, fond orange | extraits du jeu |
| `itemdex_kryptonlion.png` | « Ultimate Pokémon ItemDex », toutes générations | 32×32 séparées par un trait, **dessin de 24×24 centré** | Kryptonlion (DeviantArt), crédit demandé |

Les deux planches sont à la **même échelle** : un dessin de la seconde se
découpe en prenant le carré central de 24×24 de sa case (4 px de marge de
chaque côté), en rendant transparente la couleur de fond de la case.
