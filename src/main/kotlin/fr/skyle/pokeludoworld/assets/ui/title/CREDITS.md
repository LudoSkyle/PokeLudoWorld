# Écran titre

Les images de ce dossier sont fabriquées par les scripts de `tools/` :

- `background.png`, `clouds_far.png`, `tower.png`, `clouds_near.png` :
  `tools/title_background.py`, qui dessine tout lui-même ;
- `prompt.png` : `tools/title_prompt.py`, de même ;
- `logo.png` : `tools/title_logo.py`. Le mot MIRAGE (Gill Sans UltraBold,
  police livrée avec macOS) est dessiné par le script. Le logo Pokémon vient
  de `sources/pokemon_logo.png` et l'emblème de `sources/emblem_reference.png`
  (l'insigne de Pokémon Donjon Mystère), tous deux fournis par Ludovic et
  recolorés sans que leur dessin change ; seul le centre de l'emblème est
  refait. Pokémon, son logo et Donjon Mystère appartiennent à Nintendo,
  Creatures, GAME FREAK et Spike Chunsoft.

`parts/` garde à part les morceaux du logo et de la tour, écrits par les mêmes
scripts (voir `docs/title.md`).

Les Goélise qui traversent l'écran viennent de `assets/pokemon/overworld/`
(voir `assets/pokemon/CREDITS.md`).

Voir `docs/title.md`.
