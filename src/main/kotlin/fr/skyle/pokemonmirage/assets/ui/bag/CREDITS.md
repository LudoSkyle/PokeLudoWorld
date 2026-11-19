# Écran du sac

Éléments tirés de la planche « Interface & Bag Screens » de Rouge Feu / Vert
Feuille (`source_frlg_bag_screens.png`, gardée telle quelle à côté).

- `background.png` : le fond d'origine fait 240×160. Il est porté à **288×162**,
  la taille de l'écran du jeu : 48 colonnes du panneau de liste sont recopiées
  (un multiple de la période des pointillés, qui restent donc réguliers) et
  deux rangées de bleu sont ajoutées au-dessus de la case d'icône.
  Puis à **320×240**, l'écran en 4:3 (19/11/2026), par `tools/bag_background.py` :
  32 colonnes du panneau de plus (quatre périodes de pointillés), trois lignes
  de liste, 30 rangées de bleu autour de la case de l'icône.
- `bag_*.png` : le sac, fermé ou ouvert sur une poche, 64×64.
- `arrow_*.png` : les flèches rouges, 16×16.
- La **case de l'icône**, dessinée dans `background.png`, est agrandie de
  28 × 28 à 36 × 36 (18/11/2026), dans son dessin d'origine : les icônes
  d'objets du pack de données font 32 × 32.
