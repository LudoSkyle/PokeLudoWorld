# Polices locales

Ce dossier n'est pas versionné (sauf ce fichier). Il accueille les polices dont
la licence interdit la redistribution : elles servent sur la machine de celui
qui les a téléchargées, mais ne peuvent pas être publiées avec le dépôt.

| Fichier attendu | Rôle | Sans lui |
|---|---|---|
| `menu.ttf` | police des menus (pause, options), rendue en 40 px | les menus utilisent Pokémon Emerald Pro en 48 px |

Police utilisée par Ludo pour `menu.ttf` : « Pokémon FireRed & LeafGreen Font
Recreation » de SHR16 (FontStruct, licence non commerciale sans
redistribution), https://fontstruct.com/fontstructions/show/1723353.

Après avoir posé le fichier, lancer un import Godot puis mettre
`antialiasing=0` et `subpixel_positioning=0` dans `menu.ttf.import` : c'est une
police en pixels, dont un pixel vaut 4 pixels écran à 40 px.
