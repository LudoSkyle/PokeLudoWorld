# Le générateur de l'île — une archive

Ces fichiers ont produit `scenes/levels/start_island.tscn` (voir
[docs/levels.md](../../../docs/levels.md), « L'île de départ »). Ils étaient
rangés hors du dépôt, avec des notes de session ; ils sont copiés ici le
17/11/2026 **tels quels**, pour ne pas les perdre.

**Ce n'est pas un outil prêt à tourner.** Ils gardent les chemins de la
session où ils ont été écrits :

- `gen.py` et `build.py` cherchent leurs modules dans `/tmp/plw` et
  `/tmp/plw/island` (`plan`, `crop`, `tmx` — tous trois sont dans ce dossier) ;
- `gen.py` lit `/tmp/plw/level_clean.tres`, une copie du TileSet d'avant l'île,
  pour reprendre les collisions des maisons de la première carte. Cette copie
  n'est pas ici ; le `level.tres` du dépôt la remplace.

| Fichier | Rôle |
|---|---|
| `plan.py` | le plan : terres, plateaux, pontons, mobilier, objets |
| `gen.py` | du plan aux calques de tuiles, avec ses contrôles (marge, barrières de rochers, pontons) |
| `build.py` | écrit la scène, déclare les tuiles au TileSet, pose les personnages |
| `crop.py`, `tmx.py` | lecture et écriture de PNG, lecture et écriture de `tile_map_data` |

**La scène a été retouchée depuis** — les six cases de la trouée du nord
mènent maintenant à la route du nord (`Doors/Nord0`…`Nord5`). Relancer ce
générateur écraserait ces retouches : pour le remettre en service, y reporter
d'abord ce changement, et prendre modèle sur `tools/maps/north_route/`, qui,
lui, tourne depuis le dépôt.
