# Composer une carte

Document de conception des cartes d'extérieur. **À relire en entier avant de
composer, générer ou retoucher une carte** : ces règles viennent des défauts
que Ludovic a relevés sur les versions successives de l'île (huit relectures le
15/11/2026), des conseils de conception de la communauté Essentials qu'il a
transmis, et de la page
[Good practices in level design](https://pokemonworkshop.com/en/learn/good-practices-in-level-design/)
de Pokémon Workshop. Les mêmes erreurs y ont été refaites plusieurs fois faute
de les avoir écrites.

Le 17/11/2026, Ludovic a fourni vingt cartes de référence bien composées. Six
règles d'ici les contredisaient : **il a tranché pour les références**, et ces
six règles sont réécrites ci-dessous (marquées « références, 17/11/2026 »).
Les autres règles tirées de ces cartes — marquées « références » — complètent
les sections existantes et font les sections M à R. Leurs chiffres ont été lus
sur les images ; seuls la taille des cartes et le plus grand carré d'herbe nue
ont été mesurés case par case, sur sept d'entre elles.

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
17. **Un thème, un repère, deux ou trois motifs** (références). Chaque carte a
    un thème, un repère qu'elle seule possède — un phare, une pagode, une
    estrade, des éoliennes, un arbre pas comme les autres — et deux ou trois
    motifs qui reviennent : tournesols, blé, palmiers.
18. **Le construit est symétrique, la nature ne l'est pas** (références).
    Statues, lampadaires, massifs et pots vont par paires de part et d'autre
    d'un axe ; arbres, étangs et herbes jamais. La symétrie est stricte pour
    ce qui est cérémoniel ou monumental (une estrade, une arène) ; dans un
    village rustique une paire peut être légèrement cassée — un élément
    décalé d'une case, un pot d'un côté et un banc de l'autre.

---

## Règles précises

**Les fourchettes sont des repères, pas des quotas.** Une carte peut s'écarter
d'une règle chiffrée quand son thème le demande — un grand champ de blé, une
place de cérémonie dégagée. C'est permis **une ou deux fois par carte, et
l'écart se nomme à Ludovic** en lui rendant la carte. Un écart qu'on ne sait
pas justifier est une erreur.

### A. Bords et marge

- **Une marge inaccessible entoure la carte.** La règle transmise : 8 cases à
  gauche et à droite, 6 en haut et en bas, pour un écran de 20 × 15 cases.
  *Ne s'applique pas aux intérieurs : le noir autour d'une pièce est voulu.*
- **Sur l'île, la marge est plus étroite, par choix** : une lisière de 6 cases
  à gauche et à droite et de 5 en bas, dont les **4 cases du bord (3 en bas)
  ne se foulent jamais**. Deux raisons : Ludovic a demandé une carte plus
  petite, et la caméra s'arrête au bord de la carte (`PlayerCamera`), si bien
  que le noir ne se voit de toute façon pas. **Validé par Ludovic le
  15/11/2026** : c'est « moins grave » chez nous puisque la caméra s'arrête au
  bord, alors que dans les jeux d'origine elle montre plus sur les côtés.
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
- **La ceinture de forêt fait au moins trois arbres d'épaisseur** sur tout
  bord qui n'est pas la mer ; deux suffisent là où une falaise ou de l'eau la
  double (références).
- **Une sortie est une trouée de 2 à 4 cases** dans cette ceinture, et le
  chemin la traverse (références).
- **Aucun endroit d'où l'on ne ressort pas.** Tout ce qu'on atteint à pied, on
  doit pouvoir le quitter à pied, sans compter sur un objet ou une capacité que
  le joueur pourrait ne pas avoir. À revérifier dès qu'il y aura rochers à
  pousser, glace ou rebords à sens unique.

### B. Taille et agencement

- **Un village fait 35 à 55 cases de côté ; une route s'allonge dans le sens
  du trajet**, jusqu'à une centaine de cases, sur une bande praticable de 20 à
  30 cases de large (références, 17/11/2026 — l'ancienne limite de 65 cases
  dans chaque sens ne vaut plus). Le principe 7 demeure : la taille suit le
  contenu, et une carte qui paraît petite peut encore rétrécir. L'île fait
  **55 × 50**, la taille de sa carte d'exemple (elle en a fait 72 × 52, puis
  62 × 49).
- **Aucun bâtiment au centre exact de la carte.**
- **Dans un village, les maisons ne s'alignent pas** : chacune à sa hauteur,
  décalée d'au moins une case. **Dans une ville, la grille est admise** : des
  rangées de bâtiments alignés le long des rues (références, 17/11/2026).
- **Une maison se serre contre ce qui la borde** : pas d'espace perdu derrière
  elle (contre la falaise quand il y en a une), et son plateau ajusté autour
  d'elle plutôt qu'une grande pelouse vide (Ludovic, 15/11/2026).
- **Devant chaque porte, une rangée libre sur toute la façade, deux quand la
  place le permet.** La sortie ne bute sur rien : ni objet ni personnage sur
  la case devant la porte ni sur la suivante.
- **Une porte est au sud et donne sur un chemin ou une placette**
  (références).
- **Centre Pokémon et Boutique côte à côte, près de l'entrée de la ville**
  (références).
- **Le bâtiment repère est au bout d'un axe** : on le voit en arrivant
  (références).
- **Aucune pelouse nue de plus de 4 × 4** (références ; mesuré : de 2 × 2 à
  5 × 5 selon la carte). Tout carré plus grand reçoit des hautes herbes, un
  bosquet, un étang, un chemin ou des fleurs. Une carte peut avoir **une
  respiration voulue**, jusqu'à 6 × 6 environ, si elle a une fonction — une
  placette, une clairière, le parvis d'un repère — et qu'elle est bordée de
  tous côtés.
- **Une route offre un trajet évident, une ou deux boucles, et des culs-de-sac
  récompensés** (références ; principe 13).

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
- **Une falaise basse est une ligne fine d'une case qui serpente et relie deux
  bosquets** (références). La ligne et les arbres forment ensemble la
  barrière ; l'escalier est le seul passage.
- **Une ville côtière est en terrasses concentriques** (références) : des
  paliers de 2 à 4 cases, aux contours parallèles et en escalier, avec
  plusieurs escaliers d'un niveau à l'autre.
- **Une butte rocheuse isolée, entourée d'arbres** (de 6 × 5 à 10 × 8), fait
  un obstacle au milieu d'une route (références).
- **Un plateau n'est pas un rectangle** : ses angles sont cassés, et son bord
  suit la côte quand elle s'approche.
- **Une falaise peut tomber dans la mer ou dans une rivière, avec un liseré de
  sable à son pied** (références, 17/11/2026 — l'ancienne règle des deux
  cases entre un plateau et l'eau ne vaut plus). Le sable est **sous la
  paroi** — on le voit dans ses coins arrondis — et son bord ondule **dans la
  case d'eau** qui touche la terre. La terre garde sa case entière pour sa
  paroi.
- **Une rivière encaissée ne s'atteint jamais** : ses deux rives sont des
  falaises, d'un bout à l'autre. Avant de dessiner une eau, dire comment on
  la borde — plage (on y marche), falaise (on ne l'atteint pas), berge
  d'étang — et s'y tenir sur toute sa longueur.
- **La falaise d'une rivière a deux étages : deux anneaux d'une case, l'un
  dans l'autre** (mesuré tuile par tuile sur la Route 1). L'anneau de
  roche fait le tour de la terre et tombe dans l'eau ; l'anneau d'herbe est
  collé derrière lui, une case en retrait, coins compris. On marche à partir
  de la troisième case de terre. Un plateau de plus, une montagne : d'autres
  anneaux, posés par-dessus, chacun fermé sur lui-même.
- **Une case de falaise se juge à ce qu'on y voit et à ce qu'elle touche.**
  Un flanc, un bas de plateau montrent la roche : ils arrêtent, et l'on
  change de niveau par un escalier, posé sur un bord du bas tout droit. Un bord
  du haut n'est qu'un liseré sur de l'herbe : il arrête là où il donne sur le
  vide (la Route 1), pas là où ce qui est derrière se foule (les plages de
  l'île).
  Un coin rentrant du haut de l'anneau d'herbe, lui, est de la pelouse avec un
  bout de lisière dans un angle, et ne touche le vide que par sa pointe : **il
  se foule**. Une case qui a l'air d'être de l'herbe et où l'on ne peut pas
  aller est une collision injustifiée (Ludovic, 17/11/2026).
- **Un pont va du dessus d'un plateau à l'autre**, par-dessus les falaises et
  l'eau, sur des bords droits, large de trois cases. Ses planches sont celles
  de la planche de la carte : avec leurs rambardes si elle en a, nues sinon.
  Son tablier recouvre les anneaux qu'il enjambe.
- **Ce que l'exemple suppose que le jeu sait faire ferme un passage tant que
  le jeu ne le sait pas** : un arbuste à couper, une eau où l'on surfe (le
  rebord de roche, lui, se saute depuis le 17/11/2026). On les pose quand même — c'est la
  carte — mais on dit quel passage chacun ferme et par où l'on fait le tour.
  **Ce que l'exemple range derrière y reste** : un objet derrière un arbuste à
  couper est la récompense de qui reviendra le couper, on ne le sort pas
  devant (Ludovic, 17/11/2026). Le générateur vérifie qu'il est hors
  d'atteinte aujourd'hui et à portée une fois l'obstacle ôté.
- **Un exemple dont on n'a pas les planches donne sa géographie, pas ses
  tuiles** (l'île de départ, 17/11/2026). On cherche d'abord quelle planche
  explique son *terrain* ; ce qui est posé dessus et qu'aucune planche
  n'explique dit seulement « ici, il y a quelque chose » — presque toujours un
  arbre. On classe alors chaque case (mer, plage, plateau, chemin, forêt), on
  pose le résultat avec les tuiles d'une carte déjà faite, pour que le jeu
  garde un seul style, et l'on déclare à la main, en clair, ce que l'exemple ne
  peut pas dire : retouches, escaliers, pontons, maisons.
- **Un escalier impose sa géographie.** La planche de la Route 1 n'a que des
  escaliers face au sud : chaque plateau doit donc avoir un bord du bas droit
  sur cinq cases, avec de la plage dessous. Là où l'exemple monte par le côté,
  on creuse une anse.
- **Une route fait trois cases de large.** Plus large est très rare — cela
  arrive, ce n'est pas courant (Ludovic, 17/11/2026). Les pistes des
  générateurs font trois cases.
- **Deux cartes qui se suivent se raccordent** : à la sortie de l'une et à
  l'entrée de l'autre, le même sol (pas du sable d'un côté et de l'herbe de
  l'autre), la même hauteur (pas la plage d'un côté et un plateau de l'autre),
  la même largeur de route, et autant de cases de passage. On regarde la carte
  d'après avant de dessiner la sortie.
- **Rien ne se pose sur une piste** : ni banc, ni lampadaire, ni panneau, ni
  personnage immobile. Une piste est ce qui reste libre ; on garnit ses bords
  (Ludovic, 17/11/2026). Le générateur de l'île le refuse, et un test le
  contrôle.
- **Un lampadaire se met le plus souvent dans un angle** : au coin que font
  deux pistes, contre un coin de falaise, au bout d'un chemin — pas
  exclusivement, mais c'est là qu'on le cherche d'abord. Un banc de profil
  borde une piste qui monte ; celui qui s'y tient regarde la piste.
- **Un mur va d'un bout à l'autre** : pas de trou de deux cases dans une
  falaise ou une montagne qui longe le bord de la carte.
- **Ce qui vit sur une carte est du milieu de la carte.** Dans une forêt, ni
  pêcheur ni montagnard : des campeurs, des gamins, des chasseurs d'insectes.
  Au-dessus d'elle, pas d'oiseaux de mer : des Pokémon de prairie, portés par
  le vent. Les Goélise et les Bekipan sont pour la plage (Ludovic,
  17/11/2026).
- **Un arbre a une seule teinte.** Si l'exemple en fait un de deux essences
  — la cime de l'une, le pied de l'autre —, c'est un accident de calques : on
  plante l'essence de sa cime.
- **Une montagne a la taille que lui donne l'exemple**, et plusieurs gradins
  posés les uns sur les autres : on érode sa silhouette d'une case par
  gradin.
- **Le toit d'une maison peut dépasser de son plateau** : ce n'est pas une
  contrainte (Ludovic, 15/11/2026). Ce qui compte, c'est que sa façade et sa
  porte soient sur le dessus, avec la place de sortir.
- **Un plateau peut s'adosser à la falaise** — il n'a alors pas de bord du
  haut, le mur monte derrière lui — et **en porter un autre** : le laboratoire
  est un étage plus haut que sa terrasse, deux escaliers l'un au-dessus de
  l'autre.
- **Une montagne se fait en superposant ses tuiles** (demandé trois fois par
  Ludovic, avec trois références, le 15/11/2026) : pas une bande de roche
  plate, mais des blocs de roche **posés les uns sur les autres**, de largeurs
  inégales, sur des calques empilés — le contour est irrégulier, les parois
  se chevauchent. **Sans agrandir la carte** : la hauteur vient des étages, pas
  de rangées en plus.
  Elle porte un bloc rocheux pour une vingtaine de cases ; une entrée de
  grotte est en haut, dans l'axe d'un escalier, son panneau à côté
  (références).
- **Le bord du haut d'un plateau est de l'herbe : on s'y tient.** Ce qu'on ne
  franchit pas, c'est le rebord, entre cette case et celle du dessus — une
  bande fine sur la couche des rebords ([tilesets.md](tilesets.md)). Une rangée
  d'herbe qui bloque sans raison visible est un mur invisible.
- **On y monte par des escaliers à poteaux, dans l'axe d'un chemin**, en bas
  ou sur les côtés (`STAIRS` du plan). **Larges de trois à quatre cases sur
  l'axe principal** (références) — à fabriquer si la planche ne les a pas,
  principe 15 — ; **deux cases suffisent pour un accès secondaire** (ceux de
  la planche de l'île). **Jamais sur le bord du haut** : un escalier vu à
  l'envers ne ressemble à rien. Devant et derrière un escalier, rien.
- **Rien à cheval sur un bord de plateau** : un arbre, un dallage, une fleur
  haute sont tout entiers dessus ou tout entiers en bas.

### E. Arbres

- **En quinconce** : d'une rangée à la suivante, les arbres sont décalés d'une
  case. Une rangée parfaitement alignée n'est admise que sur le bord même de
  la carte, jamais sur toute une rangée visible.
- **Une lisière est serrée** : un arbre toutes les deux cases, cimes qui se
  recouvrent. Des arbres espacés laissent passer.
- **Une forêt est pleine** (Ludovic, 17/11/2026 : « tout le centre ouest de ta
  map est vide alors que sur l'exemple c'est rempli d'arbres »). Ce qui n'est
  ni chemin, ni clairière, ni herbes est de la forêt. Sa trame **se mesure
  sur l'exemple, avec l'arbre de l'exemple** : pour l'arbre de la route du
  nord (trois cases de large, une cime de deux cases et quart), 315 arbres
  disent tous la même chose — **un arbre toutes les quatre colonnes, la
  rangée suivante décalée de deux, une rangée par case**. Deux arbres d'une
  même colonne sont à deux cases l'un de l'autre. Les arbres de bordure de
  l'atlas, plus larges, se plantent toutes les deux cases : la trame dépend
  de l'arbre.
- **Une forêt se ferme par ses collisions, pas par sa densité** : ce que
  bloque un arbre se choisit pour qu'aucune colonne ne reste libre sous les
  cimes.
- **Un arbre large bloque sur toute sa largeur** : ses deux rangées du bas,
  sur ses trois cases — le tronc et la cime qui retombe de chaque côté. On ne
  se tient pas sur une case que la cime recouvre devant soi ; on passe
  derrière le haut de la cime, qui est au-dessus du sol (Ludovic, 17/11/2026).
- **Ce qu'on pose au sol passe derrière le décor, et reste visible.** Un
  objet à ramasser, un panneau ne se dessinent jamais par-dessus une cime :
  avec la règle d'avant, aucune case libre n'est recouverte par l'arbre de sa
  rangée. Et on ne les pose pas derrière une cime qui cache le centre de leur
  case : le générateur le mesure sur les pixels de l'arbre.
- **Une ombre ne se coupe pas au bord d'une case.** Avant de découper un arbre
  dans une planche, regarder les pixels juste hors de son cadre : l'ombre du
  sapin et de l'arbuste déborde d'une rangée sous leur pied. La tuile prend
  cette rangée de plus — même si l'exemple, lui, la coupe.
- **Un décor qui en cache un autre ne l'interrompt pas.** Un rebord qui file
  sous un arbre a son bout de l'autre côté ou dessous, une piste continue sous
  une ombre. Ce que l'exemple cache se complète par la tuile qui convient à ce
  qu'on en voit, jamais par du sol nu.
- **Une forêt reproduite d'un exemple a les essences de l'exemple** : une
  seule s'il n'en a qu'une. Le mélange d'une teinte sur cinq ou six vaut pour
  une carte qu'on compose soi-même.
- **Les arbres bordent** : ceinture de la marge, pied de falaise, flanc d'une
  maison, dessus d'une butte. Jamais semés au hasard sur une pelouse.
- **Sur une route, les arbres de l'intérieur forment des bosquets de 4 à 15
  arbres** (références), de forme irrégulière et allongée, qui séparent des
  couloirs de 3 à 6 cases. Une route peut avoir en plus **un ou deux arbres
  isolés ou en paire**, s'ils servent de repère : un arbre différent, à un
  carrefour, au bout d'un cul-de-sac.
- **Les petits sapins comblent les creux** (références) : au bout d'une
  rangée, dans un renfoncement de lisière, ou par paire de chaque côté d'une
  entrée. Environ un pour six à huit gros arbres.
- **Une ou deux souches ou troncs couchés au pied des lisières**, jamais en
  pleine pelouse (références).
- **Dans un village, un arbre isolé est permis en accent** à côté d'une
  maison (références) — jamais devant sa façade, règle ci-dessous.
- **Quand le jeu de tuiles a plusieurs teintes d'arbres, on en mêle une sur
  cinq ou six**, jamais par blocs (références).
- **Un arbre peut border un étang, jusqu'au contact de la berge**
  (références, 17/11/2026 — l'ancienne règle des trois cases ne vaut plus).
  Ce qui reste interdit, c'est le dessin qui déborde : le pied d'un arbre ou
  d'un palmier et sa touffe d'herbe tiennent tout entiers sur la terre, ni sur
  le rivage ni sur l'eau (H).
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

- **Les rochers ferment, et ils décorent** (références, 17/11/2026 —
  l'ancienne règle « seulement là où ils sont nécessaires » ne vaut plus).
  En décor : par grappes d'un gros et de deux ou trois petits en mer près des
  côtes, un rocher dans un étang, des blocs épars sur une plage ou une
  montagne (un pour une vingtaine de cases), jamais en grille.
- **Pour fermer**, une lisière se ferme d'abord avec des arbres ; le rocher
  vient là où un arbre ne peut pas pousser (le sable, l'eau) : en travers
  d'une passe, au bout d'une plage qui sort de la carte.
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
- **Un rocher a la matière de ce qui le porte** (Ludovic, 17/11/2026 : des
  rochers gris au sommet d'une montagne brune, « deux styles différents et qui
  n'ont rien à voir »). Gris dans l'eau, bruns sur une roche brune. Avant de
  poser un rocher, regarder sa couleur à côté de celle du sol.
- **Ce qui dépasse d'une rivière est un rocher, pas un îlot de terre.** Sur un
  relevé, une tache sans classe au milieu de l'eau est un rocher : on la
  relève à part, au pixel, et la case reste de l'eau.

### G. Raccords de terrain

- **Une matière ne se raccorde qu'avec le jeu de tuiles fait pour elle** :
  sable à vagues `5:10-14,13-15`, son rivage `5:15-19,31-33`, l'eau claire.
  Mélanger deux sables ou deux eaux donne une couture droite.
- **Un seul sable par carte** : sentiers et plages dans la même matière.
- **Un chemin est du sable ou de la terre posés sur l'herbe** (références,
  17/11/2026 — l'ancienne règle « pas de sable pour un chemin » ne vaut
  plus). Ce qui faisait « bizarre », c'était la bande étroite et droite : la
  largeur et le tracé d'un chemin sont en N.
- **Le rivage est dessiné sur la case de sable, jamais dans la case d'eau.**
  Sinon la mer, solide, a l'air de sable et le joueur bute dessus.
- **Une plage fait au moins deux cases de large** entre l'herbe et l'eau.
- **Aucune matière d'une seule case de large** : les raccords ne savent pas la
  dessiner.
- **Deux teintes d'eau se raccordent par leurs tuiles de transition**, jamais
  par une marche nette (Ludovic, 17/11/2026 : « nettes et moches »). L'eau
  profonde a ses coins arrondis ; on ne pose pas une case d'eau profonde seule
  contre de l'eau claire ([tilesets.md](tilesets.md)). Avant d'utiliser deux
  variantes d'une matière, **chercher dans l'atlas les tuiles qui mêlent les
  deux** — un balayage par couleurs les trouve.
- **Ce qu'un coin arrondi laisse voir doit avoir du sens** : sous une roche
  qui tombe dans l'eau, du sable, pas de l'herbe.
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
  toutes les maisons, y compris celles de la première carte — **sauf celle
  qui touche un mur** : son toit recouvre le pied de la falaise, il n'y a pas
  de « derrière ».
- **Avant de toucher une tuile partagée**, lister les cartes qui s'en servent
  et comparer leurs grilles dans le moteur, avant et après.
- **Un même dessin, une même collision partout** : les cailloux sont solides
  sur la première carte, ils le sont donc aussi sur les plages de l'île.

### K. Objets et personnages

- **Un lampadaire éclaire quelque chose** : une porte, un escalier, un
  débarcadère, un coin de place, un carrefour, un virage. Jamais deux côte à
  côte, jamais au milieu d'une pelouse. Chaque lampadaire porte sa raison dans
  le générateur.
- **Un lampadaire se pose sur l'herbe au bord du chemin, jamais dessus**
  (références) : aux entrées, aux carrefours, et par paire **de part et
  d'autre** d'un escalier ou d'une sortie — ce n'est pas « côte à côte ». Six
  pour un village de 37 × 48. **Aucun en pleine nature** ; un seul est permis
  sur une route près d'un lieu habité : une maison isolée, une aire de repos,
  l'entrée d'un pont.
- **Un panneau se lit depuis un chemin et ne le coupe pas.** Il y en a un à
  chaque entrée de ville, à chaque bifurcation d'une route, devant une grotte
  ou un bâtiment notable : à une case du chemin, adossé à des arbres
  (références).
- **Une boîte aux lettres par maison d'habitation**, sur l'herbe, à une case à
  côté de la porte (références).
- **Les étals se regroupent dans un coin de place** ; sur la plage, parasols
  et transats vont **par grappes de deux ou trois** (références).
- **Aucun objet solide ne ferme ni n'étrangle un passage.** Contrôle : ses
  cases voisines libres se rejoignent encore entre elles sans passer par lui.
- **Rien sur un débarcadère, un escalier, ni la case devant.**
- **Un personnage immobile suit les mêmes règles qu'un objet** : jamais sur
  le trajet d'un personnage qui marche (le tour de la place), ni devant un
  escalier, ni dans un passage de deux cases.
- **Un passage gardé l'est à son endroit le plus étroit** : les gardes tiennent
  la trouée de la falaise, un contre chaque paroi, pas le milieu d'une plage.
- **Les dresseurs se tiennent aux étranglements** d'une route (références).
- **Le mobilier a sa place, et c'est ce qu'il a l'air d'être** : un banc est un
  banc (le banc de bois, `10:4-5,5-6` de face, `10:8,3-5` et `10:9,3-5` de
  profil — ni une dalle de pierre, ni le banc blanc bas `5:74-75,25` : « tu as
  de meilleures options ailleurs »), au bord d'un chemin ou face à
  quelque chose ; un parasol et sa serviette vont sur le sable sec ; des
  caisses sur le quai à côté du lampadaire ; **un pot de fleurs de chaque côté
  d'une porte, jamais devant** — et l'on mesure dans le dessin où est la porte.
  Aucun ne coupe quoi que ce soit du reste de la carte.
- **Un objet à ramasser est une Poké Ball posée au sol**, au bout d'un recoin
  ou d'un détour : c'est la récompense du curieux. Son image est celle de la
  planche des intérieurs (`sources/public_indoor.png`), choisie par Ludovic.
  **Trois à huit par route** selon sa taille, chacune dans un cul-de-sac,
  derrière un rebord ou sur un îlot (références).
- **Chaque coin de la carte a quelqu'un**, près de ce qui l'occupe : un banc,
  un parasol, un ponton, des herbes. Et **pas de foule** : une dizaine de
  personnes au plus au même endroit, les autres répartis ailleurs.
- **Des Pokémon dans le décor** : quelques oiseaux de mer au-dessus de l'eau,
  chacun dans sa zone, sans collision — ils font vivre la carte sans gêner
  personne ([npcs.md](npcs.md), « Les Pokémon du décor »).
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

### M. Hautes herbes

*D'après les cartes de référence (17/11/2026).*

- **Par plaques de 10 à 40 cases, au contour déchiqueté, avec des trous** :
  une case manquante sur cinq ou six. Jamais un rectangle plein. De **petites
  touffes de 3 à 6 cases** sont permises en accent, et **une grande étendue**
  si c'est le thème de la carte.
- **Adossées à un bosquet, un étang ou une ligne de falaise** : elles
  remplissent le couloir entre deux obstacles. Elles peuvent s'en écarter
  d'une case ; ce qui est interdit, c'est la plaque posée seule au milieu d'un
  espace ouvert.
- **Elles coupent le trajet d'une route, mais un détour existe souvent** : le
  joueur choisit entre les traverser et faire le tour.
- **Aucune au centre d'un village** ; une plaque est permise en lisière, là
  où le village devient la route.
- **Sur le sable, des herbes de plage d'une autre teinte**, selon la même
  logique.

### N. Chemins

*D'après les cartes de référence (17/11/2026). La matière est en G.*

- **Trois cases de large pour l'axe principal, deux pour un sentier
  secondaire** (vers une maison à l'écart, un point de vue). Jamais une : nos
  raccords ne savent pas la dessiner (G).
- **Des bords ondulés** : un décrochement d'une case toutes les deux à quatre
  cases, des virages en escalier diagonal.
- **Dans un village, le réseau relie chaque porte** — en T, en croix ou d'un
  tracé plus libre — et l'on y lit un axe principal ; il s'élargit en placette
  devant les bâtiments importants.
- **Sur une route, le chemin est en pointillés** : des tronçons de 4 à 10
  cases orientés dans le sens du trajet, séparés par de l'herbe. Variante :
  une piste continue d'herbe plus claire. Un seul des deux par carte.
- **Un chemin mène quelque part** : une porte, un escalier, un pont, une
  sortie.

### O. Eau

*D'après les cartes de référence (17/11/2026). Les barrières de rochers sont
en F, les pontons en I.*

- **Un étang fait 12 à 60 cases, au contour en escalier**, jamais un
  rectangle, avec sa berge brune en haut et à gauche.
- **Un à trois décors par étang moyen ou grand** : un rocher, un ou deux
  nénuphars. Un petit étang peut rester nu.
- **Un étang est adossé** à un bosquet, une maison ou une falaise, et longé
  par un chemin.
- **Sur une route de plaine ou de forêt, un étang toutes les 12 à 20 cases.**
  Une route sèche — montagne, plage — peut n'en avoir aucun : un autre motif,
  d'eau ou de roche, prend le relais.
- **Une mer ou une rivière a au moins deux tons** : une bande d'eau claire le
  long de chaque rive, large d'une à trois cases, puis l'eau profonde. Le
  contour de l'eau profonde suit la rive en la simplifiant, par marches, et
  ses coins sont arrondis (G).
- **Un étang n'a qu'une teinte**, plus vive que celle d'une rivière, et sa
  berge à lui.
- **Un îlot de sable avec un objet derrière une chaîne de rochers** récompense
  celui qui saura nager.
- **Un pont est perpendiculaire à l'eau, large de trois cases, au point le
  plus étroit**, avec un chemin de chaque côté.

### P. Rebords à sens unique

*D'après les cartes de référence (17/11/2026). Pas encore dans le jeu : à
relire quand la mécanique existera, avec la règle « aucun endroit d'où l'on
ne ressort pas » (A).*

- **Des segments droits de 3 à 5 cases, horizontaux, qu'on saute vers le
  bas.** Un rebord latéral est permis si la tuile existe et que le saut se lit
  sans ambiguïté.
- **En travers d'un couloir secondaire**, comme raccourci de retour — jamais
  sur le seul passage de l'aller.
- **Ses deux bouts butent sur un arbre ou une falaise** : on ne le contourne
  pas.
- **Souvent par deux, encadrant une plaque d'herbes.** Trois à six sur une
  route qui a du relief ; aucun n'est obligatoire sur une carte plate ou dans
  un village.

### Q. Fleurs

*D'après les cartes de référence (17/11/2026).*

- **Par touffes de deux ou trois cases, en diagonale ou en L**, d'une couleur
  ou de deux assorties. Une fleur seule de temps en temps, au pied d'un
  panneau ou d'une boîte aux lettres.
- **Au bord d'un chemin, au pied d'un arbre, à l'angle d'une maison, sur une
  berge, dans une trouée d'herbes.** Jamais sur un chemin.
- **Une touffe pour 40 à 60 cases praticables** dans le style sobre, jusqu'à
  une pour 15 dans un style chargé. Un seul style par carte.
- **Les grandes fleurs — tournesols — vont en massifs clôturés**, symétriques
  de chaque côté d'une maison ou le long d'un axe.

### R. Clôtures

*D'après les cartes de référence (17/11/2026).*

- **Une clôture entoure quelque chose** — un jardin, un champ, un massif —
  **ou sert de garde-corps** le long d'un étang ou d'un bord de terrasse :
  deux ou trois tronçons courts avec des vides, pas une ligne continue. Jamais
  un tronçon isolé qui ne garde rien.
- **Droite, appuyée sur une maison ou un mur, avec une ouverture d'une ou
  deux cases.**
- **Un champ est un bloc clôturé traversé d'allées de terre.**

---

## Quand Ludovic donne une carte d'exemple

**On la reproduit, on ne l'interprète pas** (Ludovic, 17/11/2026, sur la route
du nord : « tu n'as rien gardé de l'image initiale »). La première version
avait gardé l'idée — une rivière, deux ponts — et perdu tout le reste : terres
au niveau de l'eau, forêts clairsemées, montagne minuscule, eau d'une teinte.

0. **Chercher d'abord de quelle planche l'exemple est fait.** Comparer sa
   palette à celles des planches de `assets/levels/sources/` : la route du
   nord avait exactement les couleurs de `town_compilation.png`, et l'on a
   passé deux versions à l'imiter avec d'autres tuiles avant de le voir. Si
   la planche est là, **on relève l'exemple par tuiles** : chaque tuile est
   retrouvée au pixel près, couche par couche, du dessus vers le dessous
   (`tools/maps/route_1/survey.py`, décrit dans [levels.md](levels.md)),
   et la carte est posée avec ces tuiles-là. Deux styles ne se mélangent pas
   sur une carte : on prend toute la planche de l'exemple, ou rien.
1. Sans la planche, **relever l'image case par case** avant de dessiner quoi
   que ce soit : une classe par case (eau profonde, eau claire, falaise,
   herbe, piste, hautes herbes, arbre, pont, escalier, roche), par ses
   couleurs. Dans les deux cas le relevé est le plan ; on ne redessine pas la
   carte de tête. Ce qui ne tient pas dans une case — un rocher, une Poké
   Ball — se relève à part, au pixel.
2. **Lire tous les niveaux de détail, du plus gros au plus fin** : les masses
   (terre, eau), le relief (à quelle hauteur est la terre ? atteint-on
   l'eau ?), ce qui remplit (forêt pleine ou clairière ?), puis les matières
   (combien de teintes d'eau ? quel liseré ?), puis les objets (de quelle
   matière ? de quelle largeur ?).
3. **Chercher la tuile avant de dire qu'elle manque.** Le liseré de sable et
   les coins d'eau profonde étaient dans l'atlas ; ils n'étaient simplement
   pas encore posés sur une carte. Balayer l'atlas par couleurs, puis les
   planches de `sources/`, puis fabriquer.
4. **Dire ce que nos tuiles ne savent pas rendre**, et le nommer en rendant la
   carte — pas le remplacer en silence par autre chose.
5. **Comparer zone par zone** le rendu du moteur à l'exemple, agrandi, pas
   seulement l'ensemble. Quand la carte est faite des tuiles de l'exemple,
   **on compte** : `generate.py --compare` donne les cases qui diffèrent au
   pixel près, et chacune doit avoir sa raison.

### Ce que le générateur doit savoir avant de poser une tuile

Chaque question a une réponse lue sur l'exemple ou dans ce document. **Une
question sans réponse se pose à Ludovic** ; on n'y répond pas par défaut.

| Question | Où est la réponse |
|---|---|
| De quelle planche l'exemple est-il fait ? L'a-t-on ? | comparer les palettes à `sources/` ; sinon la demander à **Ludovic** |
| Qu'est-ce que l'exemple suppose que le jeu sait faire (sauter un rebord, couper un arbuste, surfer) ? | l'exemple ; ce que ça ferme se dit en rendant la carte (D) |
| À quelle hauteur est la terre par rapport à l'eau ? Y accède-t-on ? | l'exemple : une plage se foule, une falaise non (D) |
| Combien de teintes a l'eau, et avec quelles tuiles se raccordent-elles ? | l'exemple pour les teintes, l'atlas pour les raccords (G, [tilesets.md](tilesets.md)) |
| Qu'y a-t-il au pied d'une falaise qui touche l'eau ? | un liseré de sable : sous la paroi, et son bord dans la case d'eau (D) |
| Ce qui dépasse de l'eau : rocher ou terre ? De quelle couleur ? | l'exemple ; un rocher a la matière de ce qui le porte (F) |
| La forêt est-elle pleine ? De quelle essence ? À quel pas ? | l'exemple, mesuré arbre par arbre ; pleine par défaut (E) |
| Quelle largeur ont les ponts, les escaliers, les chemins ? | l'exemple, mesuré en cases ; sinon N et D |
| Où sont les sorties, et lesquelles mènent quelque part ? | l'exemple pour leur place ; Ludovic pour ce qu'il y a derrière |
| Quelle musique, quels Pokémon sauvages, quels personnages ? | **Ludovic** : l'exemple ne le dit pas |
| Quels objets à ramasser, et où ? | l'exemple pour ceux qu'il montre ; K pour le nombre |
| Que voit-on sous un coin arrondi, sous un pont, derrière un toit ? | regarder le rendu agrandi : c'est le contrôle des jonctions |

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
7. Aucune pelouse nue de plus de 4 × 4, hors la respiration voulue (B).
8. Nommer à Ludovic les écarts voulus aux règles chiffrées — un ou deux par
   carte, chacun avec sa raison.
