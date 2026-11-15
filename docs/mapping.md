# Composer une carte

Document de conception des cartes d'extérieur. **À relire en entier avant de
composer, générer ou retoucher une carte** : ces règles viennent des défauts
que Ludovic a relevés sur les versions successives de l'île (sept relectures le
15/11/2026), des conseils de conception de la communauté Essentials qu'il a
transmis, et de la page
[Good practices in level design](https://pokemonworkshop.com/en/learn/good-practices-in-level-design/)
de Pokémon Workshop. Les mêmes erreurs y ont été refaites plusieurs fois faute
de les avoir écrites.

Deux sortes de règles : les **principes**, qui disent dans quel esprit
composer, et les **règles précises**, chiffrées, qui se vérifient.

---

## Principes

1. **Une carte a un but.** Avant de poser une tuile, dire ce que le joueur
   vient y faire et ce qu'il doit en retenir. L'île : arriver, rencontrer le
   village, retrouver la cloche, partir par le nord.
2. **Penser au trajet du joueur avant de penser au décor.** Où va-t-il, par où
   passe-t-il, d'où voit-il quoi ? Le décor vient border ce trajet, il ne le
   coupe jamais.
3. **Le décor guide.** Un chemin, un escalier, un ponton, une trouée dans la
   falaise disent où aller mieux qu'un panneau. Ce qui compte se voit de loin.
   Et l'on n'arrive pas partout tout droit : l'île du centre ne se rejoint pas
   par le nord, il faut faire le tour par un ponton — le détour fait voir la
   carte.
4. **Le décor ferme la carte, jamais un mur invisible.** Ce qui arrête le
   joueur doit se voir : une lisière, une falaise, des rochers. Et ce qui a
   l'air de sol se foule.
5. **Rien de droit, rien d'aligné.** Dans la nature il n'y a ni ligne droite ni
   rectangle. Côtes, falaises, étangs, lisières, rangées d'arbres, rochers :
   tout se casse par des creux et des bosses.
6. **Du relief partout.** Une carte plate est vide même pleine d'objets. Des
   plateaux, des buttes, des marches — y compris au centre, y compris sous la
   place.
7. **Plus petit qu'on ne croit.** L'erreur de débutant est la carte trop
   grande et trop vide. Une carte qui paraît petite peut encore rétrécir.
8. **De l'air, mais pas du vide.** Trop d'arbres, de relief et de maisons
   serrés étouffent ; une étendue où rien ne se passe ennuie. Un lieu a un
   centre dégagé et des bords pleins, et l'on alterne les endroits denses et
   les endroits calmes.
9. **Varier.** Pas de motif qui se répète : on mêle les essences, les tailles
   (gros rochers et petits), les hauteurs, les matières.
10. **Chaque objet a une raison d'être là.** S'il n'éclaire rien, ne signale
    rien, ne borde rien, il n'a rien à faire là.
11. **Un lieu habité se voit.** Des bancs, un parasol sur la plage, des caisses
    sur le quai, des pots devant une façade, et des habitants près de ce qui
    les occupe. L'image de référence en est pleine ; une carte sans cela a
    l'air d'un décor vide.
12. **Les éléments spéciaux ne servent pas de décor.** L'arbre à fruits et les
    rochers moussus annoncent une mécanique de jeu : on ne les pose pas pour
    faire joli.
13. **Récompenser la curiosité.** Un cul-de-sac, un détour, un recoin : il doit
    y avoir quelque chose au bout (un objet, un point de vue, un personnage).
14. **Une tuile entière, ou rien.** On ne pose jamais un morceau d'un dessin
    plus grand, et un dessin n'empiète pas sur son voisin.
15. **S'il manque une pièce, on la cherche, puis on la fabrique.** D'abord dans les planches de `assets/levels/sources/` — les escaliers à
    poteaux y étaient ; sinon une tuile dérivée proprement de l'atlas. Jamais
    un raccord bricolé avec ce qui existe (des planches de ponton en guise
    d'escalier).
16. **Vérifier, pas supposer.** Chaque règle précise ci-dessous a son contrôle.
    Une carte se juge dans le moteur, en zoomant, et en mouvement.

---

## Règles précises

### A. Bords et marge

- **Une marge inaccessible entoure la carte.** La règle transmise : 8 cases à
  gauche et à droite, 6 en haut et en bas, pour un écran de 20 × 15 cases.
  *Ne s'applique pas aux intérieurs : le noir autour d'une pièce est voulu.*
- **Sur l'île, la marge est plus étroite, par choix** : une lisière de 6 cases
  à gauche et à droite et de 5 en bas, dont les **4 cases du bord (3 en bas)
  ne se foulent jamais**. Deux raisons : Ludovic a demandé une carte plus
  petite, et la caméra s'arrête au bord de la carte (`PlayerCamera`), si bien
  que le noir ne se voit de toute façon pas. **Choix à lui faire valider.**
- **Aucune case de la marge interdite n'est atteignable à pied** depuis le
  départ, et aucune case du bord de la carte. Contrôle : parcours des cases
  libres relevées dans le moteur. La première île laissait 82 cases de bord
  atteignables.
- **La terre va jusqu'au bord ; la mer ne le touche qu'à des passes
  étroites** (4 à 7 cases), chacune barrée d'une chaîne de rochers. Une passe
  large demande une muraille de rochers : on resserre la passe plutôt que
  d'empiler les rochers.
- **Dans la marge, une plage ne fait que ses deux cases** : la lisière descend
  jusqu'à elle, et un seul rocher suffit à la fermer.
- **Aucun endroit d'où l'on ne ressort pas.** Tout ce qu'on atteint à pied, on
  doit pouvoir le quitter à pied, sans compter sur un objet ou une capacité que
  le joueur pourrait ne pas avoir. À revérifier dès qu'il y aura rochers à
  pousser, glace ou rebords à sens unique.

### B. Taille et agencement

- **65 cases au plus dans chaque sens**, marge comprise ; **40 × 40 suffit**
  pour une carte simple. L'île fait **62 × 49** (elle en a fait 72 × 52).
- **Aucun bâtiment au centre exact de la carte, aucune rangée de bâtiments
  alignés.** Chaque maison à sa hauteur, décalée d'au moins une case.
- **Devant chaque porte, une rangée libre sur toute la façade, deux quand la
  place le permet.** La sortie ne bute sur rien : ni objet ni personnage sur
  la case devant la porte ni sur la suivante.

### C. Lignes droites

- **Jamais plus de 6 cases en ligne droite** pour une côte, un bord de plateau
  ou une lisière, hors bord de carte. Après l'outil rectangle, repasser à la
  main : retirer un coin, ajouter une bosse.
- **Exception voulue : autour d'un ponton et le long d'une passe**, la côte
  garde son tracé droit sur quelques cases — pour qu'un ponton arrive d'équerre
  et qu'un seul rocher ferme chaque berge.

### D. Relief

- **Des plateaux partout** : sous chaque maison, sous la place, et quelques
  buttes boisées dans les lisières. L'île en a huit.
- **Un plateau n'est pas un rectangle** : ses angles sont cassés, et son bord
  suit la côte quand elle s'approche.
- **Un plateau reste à deux cases de l'eau au moins** : jamais sur une case de
  rive.
- **Le toit d'une maison peut dépasser de son plateau** : ce n'est pas une
  contrainte (Ludovic, 15/11/2026). Ce qui compte, c'est que sa façade et sa
  porte soient sur le dessus, avec la place de sortir.
- **Un plateau peut s'adosser à la falaise** — il n'a alors pas de bord du
  haut, le mur monte derrière lui — et **en porter un autre** : le laboratoire
  est un étage plus haut que sa terrasse, deux escaliers l'un au-dessus de
  l'autre.
- **Le bord du haut d'un plateau est de l'herbe : on s'y tient.** Ce qu'on ne
  franchit pas, c'est le rebord, entre cette case et celle du dessus — une
  bande fine sur la couche des rebords ([tilesets.md](tilesets.md)). Une rangée
  d'herbe qui bloque sans raison visible est un mur invisible.
- **On y monte par des escaliers à poteaux de deux cases** (planche de l'île),
  en bas ou sur les côtés (`STAIRS` du plan). **Jamais sur le bord du haut** :
  un escalier vu à l'envers ne ressemble à rien. Devant et derrière un
  escalier, rien.
- **Rien à cheval sur un bord de plateau** : un arbre, un dallage, une fleur
  haute sont tout entiers dessus ou tout entiers en bas.

### E. Arbres

- **En quinconce** : d'une rangée à la suivante, les arbres sont décalés d'une
  case. Une rangée parfaitement alignée n'est admise que sur le bord même de
  la carte, jamais sur toute une rangée visible.
- **Une lisière est serrée** : un arbre toutes les deux cases, cimes qui se
  recouvrent. Des arbres espacés laissent passer.
- **Les arbres bordent** : ceinture de la marge, pied de falaise, flanc d'une
  maison, dessus d'une butte. Jamais semés au hasard sur une pelouse.
- **À trois cases de l'eau au moins**, pied compris : la touffe d'herbe au pied
  d'un arbre ou d'un palmier ne déborde ni sur le rivage ni sur l'eau.
- **Jamais devant un bâtiment** : la cime d'un arbre ne recouvre ni un toit ni
  une façade.
- **Le joueur ne passe jamais derrière le pied d'un arbre.** Debout à côté du
  tronc, il est dessiné devant. Les arbres 3×3 trient à `y_sort_origin = 14`
  (et non plus 22), le palmier à `22`.
- **Aucun arbre sur un passage, ni devant une porte.**
- **Pas d'arbre à fruits** (`6:24,0`) : c'est un arbre spécial.
- **Un arbre planté hors de la carte déborde dessus** : on n'en met que là où
  le bord est de la forêt, jamais au-dessous d'une plage ou de l'eau.
- **Les palmiers** vont sur le sable sec, à cinq cases les uns des autres, et
  pas au pied de la falaise du nord.

### F. Rochers

- **Seulement là où ils sont nécessaires** : en travers d'une passe, et un
  seul au bout de chaque plage qui sort de la carte. Une lisière se ferme
  d'abord avec des arbres ; le rocher ne vient que là où un arbre ne peut pas
  pousser (le sable).
- **Une barrière de rochers est une chaîne qui serpente** d'une rive à l'autre :
  chaque rocher touche le précédent (par un côté ou par un coin), aucun n'est
  aligné sur lui. Jamais une grille, jamais un semis au hasard.
- **Gros et petits mêlés** : surtout de gros rochers (2×2), un petit (1×1) de
  temps en temps pour casser la monotonie, jamais deux petits de suite. Les
  cailloux épars ne font qu'accompagner la chaîne, ils n'en font pas partie.
- **Jamais les rochers moussus** (`5:26-31,30-31`) : ce sont des obstacles
  spéciaux.
- **Elle ne fuit pas** : depuis le bord de la carte, la mer libre ne rejoint
  aucune eau de l'île. Contrôle automatique (générateur et test).
- **Ni à pied, ni à la nage.** Le jour où le joueur saura nager, il passera de
  la plage à l'eau où il veut : une chaîne ne vaut que si elle rejoint le
  rocher de plage, sans laisser une case d'eau du large au contact d'une plage
  où l'on marche. Le contrôle refait le parcours en amphibie ; ce qui fuit se
  bouche à l'endroit où le nageur se mettrait à l'eau, pas par une rangée de
  cailloux au bord de la carte.
- **Un rocher dans l'eau n'occupe que de l'eau** : il ne déborde pas sur la
  rive.
- **Rochers, arbres et relief se combinent** : la chaîne se prolonge sur la
  plage par un rocher de plage, puis par la lisière.

### G. Raccords de terrain

- **Une matière ne se raccorde qu'avec le jeu de tuiles fait pour elle** :
  sable à vagues `5:10-14,13-15`, son rivage `5:15-19,31-33`, l'eau claire.
  Mélanger deux sables ou deux eaux donne une couture droite.
- **Un seul sable par carte** : sentiers et plages dans la même matière.
- **Le rivage est dessiné sur la case de sable, jamais dans la case d'eau.**
  Sinon la mer, solide, a l'air de sable et le joueur bute dessus.
- **Une plage fait au moins deux cases de large** entre l'herbe et l'eau.
- **Aucune matière d'une seule case de large** : les raccords ne savent pas la
  dessiner.
- **Un dallage repose sur l'herbe** : lui et la case qui l'entoure sont en
  herbe (sa bordure est une frange d'herbe), jamais sur du sable ni sur un
  bord de plateau.

### H. Emprise des dessins

- **Mesurer un dessin dans l'atlas avant de le déclarer.** L'atlas n'est pas
  calé partout sur la grille : le palmier fait 53 px de large (4 cases, pas 3),
  les fougères débordent leur case. Contrôle : la composante de pixels opaques
  du dessin tient tout entière dans les tuiles qu'on lui donne, et rien
  d'étranger n'y entre.

### I. Pontons

- **Large de deux cases d'un bout à l'autre.** Là où la côte n'en laisserait
  qu'une à l'eau, c'est la côte qu'on corrige.
- **Une rambarde sur chaque côté qui donne sur l'eau**, dans les deux sens et
  dans les coins. L'atlas n'a que les rambardes d'un ponton nord-sud : les
  autres sont fabriquées (`island.png`, voir [tilesets.md](tilesets.md)).
- **Il ne touche la terre que par ses bouts**, jamais par le flanc, et chaque
  bout arrive sur la rive par une **planche de bout** : posée sur la case de
  sable, de la largeur du ponton, fermée d'un trait.
- **Rien sur un ponton ni devant** : ni lampadaire ni panneau sur les
  planches ; ils se posent sur le sable, à côté de l'arrivée.

### J. Collisions

- **La grille de collisions du moteur est celle du plan**, case pour case.
  Contrôle après chaque génération. La sonde interroge deux points par case :
  un point pile sur une arête interne d'un polygone fusionné passe au travers.
- **Ce qui se traverse n'a pas de collision** : fleurs, herbes. Tri à `-15`
  (et `1` pour la tuile du dessus) pour passer sous le joueur.
- **On passe derrière une maison** (demandé deux fois par Ludovic) : la rangée
  du haut de son toit se franchit tout entière, et dans la deuxième les coins
  où le sol se voit ; le toit, trié devant, recouvre le joueur. Vrai pour
  toutes les maisons, y compris celles de la première carte.
- **Avant de toucher une tuile partagée**, lister les cartes qui s'en servent
  et comparer leurs grilles dans le moteur, avant et après.
- **Un même dessin, une même collision partout** : les cailloux sont solides
  sur la première carte, ils le sont donc aussi sur les plages de l'île.

### K. Objets et personnages

- **Un lampadaire éclaire quelque chose** : une porte, un escalier, un
  débarcadère, un coin de place, un carrefour, un virage. Jamais deux côte à
  côte, jamais au milieu d'une pelouse. Chaque lampadaire porte sa raison dans
  le générateur.
- **Un panneau se lit depuis un chemin et ne le coupe pas.**
- **Aucun objet solide ne ferme ni n'étrangle un passage.** Contrôle : ses
  cases voisines libres se rejoignent encore entre elles sans passer par lui.
- **Rien sur un débarcadère, un escalier, ni la case devant.**
- **Un personnage immobile suit les mêmes règles qu'un objet** : jamais sur
  le trajet d'un personnage qui marche (le tour de la place), ni devant un
  escalier, ni dans un passage de deux cases.
- **Un passage gardé l'est à son endroit le plus étroit** : les gardes tiennent
  la trouée de la falaise, un contre chaque paroi, pas le milieu d'une plage.
- **Le mobilier a sa place, et c'est ce qu'il a l'air d'être** : un banc est un
  banc (`5:74-75,25`, pas une dalle de pierre), au bord d'un chemin ou face à
  quelque chose ; un parasol et sa serviette vont sur le sable sec ; des
  caisses sur le quai à côté du lampadaire ; **un pot de fleurs de chaque côté
  d'une porte, jamais devant** — et l'on mesure dans le dessin où est la porte.
  Aucun ne coupe quoi que ce soit du reste de la carte.
- **Un objet à ramasser est une Poké Ball posée au sol**, au bout d'un recoin
  ou d'un détour : c'est la récompense du curieux.
- **Chaque coin de la carte a quelqu'un**, près de ce qui l'occupe : un banc,
  un parasol, un ponton, des herbes. Et **pas de foule** : une dizaine de
  personnes au plus au même endroit, les autres répartis ailleurs.
- **Personne derrière un palmier ou un arbre** : un personnage qu'on ne voit
  pas n'existe pas.
- **Un rassemblement est un moment, pas un état** : la Veillée réunit le
  village, puis chacun retourne à ce qu'il faisait dès qu'on quitte la carte.
  Chaque personnage a donc trois temps — avant, pendant, après — et sa
  réplique d'après garde une trace de ce qui s'est passé ([npcs.md](npcs.md)).
- **Une boîte de dialogue, deux lignes.** Une réplique plus longue se coupe en
  plusieurs boîtes (`|`).

### L. Animations

- Un shader qui **décale** des pixels (le vent) ne lit jamais hors de la
  tuile et ne laisse aucun pixel vide : un pixel qui sortirait reste en place.
- **Pas de vent sur un dessin aussi large que sa case** (petits sapins) : il
  se déchirerait entre ses deux tuiles. Réservé aux plantes fines et aux
  grandes tuiles qui ont de la marge.
- Une animation se juge **en mouvement**, sur plusieurs images.

---

## Avant de rendre une carte

1. Le générateur ne signale rien : raccords, pontons, objets, barrières, marge.
2. Grille de collisions du moteur = grille du plan, dans chaque état de
   l'histoire (avant et après la Veillée).
3. Depuis le départ : chaque lieu est atteignable, aucune case de la marge
   interdite ni du bord ne l'est.
4. **Repasse globale** : faire rendre la carte entière par le moteur, la
   découper en zones d'une vingtaine de cases et les relire une à une,
   agrandies. Regarder chaque jonction : rivage, bord de plage, arrivée de
   ponton, bord et escalier de plateau, toit contre plateau, chaîne de rochers,
   pied d'arbre, bas de carte.
5. `tests/run.sh island` (ou le dossier de la carte), et les tests de toute
   carte qui partage des tuiles modifiées.
6. Dire à Ludovic ce qui n'a été jugé que sur image fixe.
