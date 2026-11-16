# Personnages non joueurs

Repris du projet de référence, qui fait d'un PNJ un `CharacterBody2D` avec une
apparence au choix, une liste de messages et un mode de déplacement. Écarts :
pas de machine à états, pas de recherche de chemin (une ronde va en ligne
droite d'un point au suivant), et le tri se fait par le groupe trié en Y plutôt
que par un `ZIndex` recalculé.

## Un PNJ

`scenes/characters/npc.tscn`, script `Npc.kt`. Il réutilise les composants du
joueur : `CharacterMovement` pour les pas, `CharacterAnimation` pour le sprite.

| Propriété (`.tscn`) | Rôle |
|---|---|
| `appearance` | nom d'une planche de `assets/characters`, sans l'extension |
| `display_name` | son nom, s'il en a un : affiché au-dessus de la boîte quand il parle ([dialogue.md](dialogue.md)) |
| `gender` | `female` ou `male` : le nom s'écrit en rouge ou en bleu ; vide, à l'encre du texte |
| `facing` | direction regardée au repos |
| `text` | ce qu'il dit, avec `|` entre deux boîtes |
| `states` | ce qu'il dit selon l'histoire : `drapeau > texte`, voir [quests.md](quests.md) |
| `ask` | question Oui / Non posée avant de parler : `Question ?` ou `drapeau > Question ?` |
| `required_flag`, `forbidden_flag` | drapeau sans lequel, ou avec lequel, il n'est pas sur la carte |
| `movement` | `static` (défaut), `wander` ou `patrol` |
| `pace` | cases par seconde ; 4 = le joueur, 2 = les PNJ du projet de référence |
| `wander_layer` | errance : calque de tuiles dont il ne sort pas |
| `wander_pause` | errance : pause entre deux gestes, tirée entre x et y secondes |
| `route` | ronde : cases à rejoindre l'une après l'autre, en boucle |

- Il se pose sous **`World/Entities`**, comme le joueur, sur un **centre de
  case** : c'est ce qui le trie correctement devant ou derrière le décor.
- Il est sur le calque de collision 1 : il **bloque** comme un mur.
- Quand on lui parle, il **se tourne vers nous**, puis dit son texte. Le
  dialogue fini, un PNJ `static` **reprend sa direction de repos**. S'il est
  en train de marcher, il **termine son pas** puis répond.
- Personne ne bouge de soi-même pendant un dialogue ou un fondu.
- Dans les hautes herbes, il y est jusqu'à la taille et elles bruissent sous
  ses pas, comme pour le joueur ([tilesets.md](tilesets.md)).

### Errance (`wander`)

Après chaque pause, il se tourne dans une direction au hasard ; trois fois sur
dix il s'en tient là, sinon il avance d'une case **si elle est dessinée par
`wander_layer`**. `"Background/Grass"` le garde donc dans les hautes herbes,
quelle que soit la forme de la zone : rien à mesurer à la main. Sans calque, il
erre partout où il peut marcher.

### Ronde (`patrol`)

`route = PackedVector2Array(13, 16, 26, 16, ...)` : des **cases**, pas des
pixels. Il rejoint chaque point en ligne droite (d'abord en x, puis en y) et
recommence au premier. Deux points consécutifs doivent donc être reliés par un
trajet libre. Si quelqu'un est sur sa route, il **attend** sur place.

### Qui arrête qui

`CharacterMovement.obstacle_mask` : le joueur (calque 2) ne s'arrête que sur le
calque 1, un PNJ s'arrête sur 1 **et** 2 — sans ça il marcherait sur le joueur,
qui n'est pas un mur. Un pas ordonné par une scène (`Npc.walk`, voir le passage
gardé) ignore le joueur : c'est la scène qui règle leurs places.

Un corps n'occupe sa case d'arrivée qu'à la fin du pas. Le déplacement
**réserve** donc la case visée pendant le pas, pour tous les personnages : deux
marcheurs partis en même temps vers la même case ne s'y retrouvent pas.

### Ajouter une apparence

Les planches viennent du « FRLG Accurate NPC Megapack » : `appearance` est le
nom du fichier, préfixé par son dossier d'origine — `frlg_painter`,
`rse_blackbelt`, `hgss_fisherman`, `dppt_worker`, `anime_brock`,
`custom_npc_prof_elm`. Le catalogue, son origine et ses auteurs sont dans
`assets/characters/CREDITS.md`.

Pour en ajouter une : déposer dans `assets/characters/` une planche de 4
colonnes × 4 rangées (128×192 en cases de 32×48 ; rangées bas, gauche, droite,
haut ; pieds sur la ligne 45) et la laisser importer. `CharacterFrames` découpe
les animations à la volée au quart de la largeur, il n'y a pas de `.tres` à
écrire — une planche plus large (160 ou 192) marche donc aussi.

## Un passage gardé

`scenes/levels/roadblock.tscn`, script `Roadblock.kt` : une zone posée sur la
**case laissée libre à côté d'un garde**.

| Propriété | Rôle |
|---|---|
| `guard` | nom du garde sous `World/Entities` ; il doit être sur une case voisine |
| `push_direction` | direction dans laquelle le joueur est repoussé |
| `required_flag`, `forbidden_flag` | drapeau sans lequel, ou avec lequel, le passage n'est pas gardé ([quests.md](quests.md)) |

Si le joueur s'engage sur la case :

1. il est verrouillé et **recule d'une case sans se retourner** ;
2. le garde vient **à sa place**, face à lui, et dit son texte — le même que
   quand on lui parle ;
3. la boîte fermée, le garde **retourne à son poste** et le joueur reprend la
   main.

Ce n'est pas une collision : le joueur entre vraiment sur la case.

**C'est le joueur qui prévient le passage**, à l'instant où il termine son pas.
Un script qui observerait le joueur de l'extérieur ne le verrait jamais posé :
avec la touche tenue, il enchaîne le pas suivant dans la même image. D'où une
zone sur le calque des portes, retrouvée par `areaUnderfoot()`.

À la fin, la direction qui mène au passage est ignorée tant que sa touche reste
enfoncée, sinon la scène repartirait en boucle.

## Sur l'île (`start_island`)

La Veillée est un **moment** : elle commence quand la cloche est accrochée
(`bell_hung`) et finit dès qu'on quitte l'île (`vigil_over`, posé par
`metadata/on_leave`). Chaque personnage a donc trois temps. Un nœud n'a qu'un
drapeau requis et un drapeau interdit : un personnage qui change de place d'un
temps à l'autre est fait de plusieurs nœuds.

| Qui | Avant | Pendant la Veillée | Après |
|---|---|---|---|
| **Mémé Odile** | chez Ludo (`ludo_house`, `Odile`) : elle raconte la cloche, puis donne le Ruban | sur la place, devant la cloche (`OdileAfter`) : « …MON DOS !!! » | rentrée chez Ludo (`OdileBack`) : son dos va mieux, elle entend la cloche de chez elle |
| **Alix** | à la bibliothèque (`Alix`) : elle met sur la piste du Registre | sur la place (`AlixAfter`) : elle a fermé pour ce soir | rouverte (`AlixBack`) : le Registre a une page de plus, celle de ce soir — et **il reste au joueur** (« garde-le sur toi ») |
| **Roland** | au bord de l'eau, sous la bibliothèque (11,32) : il a plongé vingt ans dans ces eaux | sur la place, à côté du socle (`RolandAfter`) | **il reste près de la cloche** : « je peux bien la regarder une heure » |
| **le pêcheur** | au bout de la jetée (31,43) : ça ne mord pas | sur la place (`FisherAfter`) : il a laissé sa canne | de retour au bout de la jetée (`FisherLater`) : il entend la cloche d'ici |
| **le coureur** | fait le tour de la place | le fait dans l'autre sens (`RunnerAfter`) : dix ans dans le mauvais sens | **court toujours** : à chaque tour, il salue la cloche |
| **les deux ouvriers** | gardent la trouée (28,3) et (33,3) : le passage est fermé | sur la place (`WorkerAfter`, `WorkerAfter2`) : la route est ouverte | l'un surveille les éboulis à côté de la trouée (27,5), l'autre range le quai (33,39) |
| **le peintre** | — | sur la place (`VisitorPainter`) : la lumière sur le bronze | **il reste** jusqu'au dernier coup de pinceau |
| **les autres visiteurs** (randonneuse, enfant, serveuse, randonneur, jeune fille, karatéka) | — | trois sur la place ; un sur la route du nord (31,7), une vers la jetée (32,39), le karatéka sur la plage de la crique (29,9), bien en vue | repartis |
| **la dame du banc** (12,13) | vient s'asseoir tous les matins | *(à sa place)* | attend que la cloche sonne pour rentrer |
| **la baigneuse** (39,37), sur sa serviette | ne bouge plus avant la nuit | *(à sa place)* | a entendu la cloche, n'a pas bougé pour autant |
| **le nageur** (24,9), dans la crique | l'eau la plus calme de l'île | *(à sa place)* | était dans l'eau quand elle a sonné |
| **le petit aux coquillages** (28,9) | n'a trouvé que des cailloux | *(à sa place)* | a un coquillage qui fait le bruit de la cloche |
| **le marin** (53,18), au ponton du nord-est | les rochers ferment les passes | *(à sa place)* | une cloche, ça s'entend du large |
| **le gamin** (25,7), devant les hautes herbes | n'ose pas y entrer | *(à sa place)* | y entrera… demain |
| **la jardinière** (46,41), près de son banc | regarde pousser les fleurs | *(à sa place)* | jardine en fredonnant, faux |
| **le chasseur d'insectes**, dans les hautes herbes | n'a rien trouvé | *(à sa place)* | félicite, et n'a toujours rien trouvé |

Les sept derniers ne bougent pas : leur réplique change dès que la cloche est
accrochée (`states = "bell_hung > …"`). Sur la place : personne avant, dix
personnes pendant, deux après (Roland et le peintre), plus le coureur.

`Triggers/NorthRoadblock0..3` (29–32,3) : les quatre cases entre les deux
gardes ; chacune appelle le garde le plus proche.

**Un personnage immobile ne gêne personne** ([mapping.md](mapping.md), K) :
jamais sur le tour de la place, ni devant un escalier, ni dans un passage de
deux cases, ni caché derrière un palmier. Le générateur le contrôle dans les
trois temps, le test `island_quest` aussi.

## Dans les maisons orange

Une maison, un habitant, immobile près de ce qui l'occupe. Le plan des deux
pièces est dans [levels.md](levels.md).

| Nœud | Carte | Case | Rôle |
|---|---|---|---|
| `Anselme` | `orange_house_north` | (16,8), tourné vers la fenêtre | retraité (`hgss_gentleman`) posté à sa fenêtre, entre l'horloge et ses livres ; sa femme est la dame du banc, dehors (`BenchLady`) — lui « garde la maison » |
| `Solange` | `orange_house_south` | (11,8), tournée vers la porte | (`rse_npc_hoenn_mom`) devant son évier ; sa sœur est la jardinière du pied du plateau (`Gardener`) — elle, elle tient la maison, et s'excuse du désordre |

Tous deux portent un nom (`display_name`, `gender`) et un seul état
d'histoire : après la Veillée (`bell_hung`) ils **restent chez eux** et
changent de réplique — les vitres d'Anselme en ont tremblé, la sœur de
Solange fredonne faux. Aucun drapeau ne les fait apparaître ni disparaître.

## Les Pokémon du décor

Des Pokémon qui volent au-dessus de la carte : `scenes/levels/flyer.tscn`
(`Flyer.kt`), posés sous un nœud `Sky` (`z_index = 40` : au-dessus de tout le
décor, sous le voile du dehors). **Ce sont des décors** : aucun corps, on ne
les heurte pas, on ne leur parle pas, ils survolent la mer comme la terre. Une
ombre au sol, sous chacun, dit qu'il est en l'air.

Au-dessus de l'eau, **cette ombre bleuit** : elle passe du noir translucide à un
turquoise sombre (`WaterShadow.kt`, le nœud `Shade` de sa scène ; `on_land` et
`on_water` en règlent les deux couleurs). Elle garde sa forme et sa place sous
lui, et reprend sa couleur dès qu'il repasse au-dessus de la terre.

**Il n'a pas de reflet**, contrairement au joueur et aux PNJ
([player.md](player.md)). Deux raisons, trouvées en essayant : de lui on ne
voit déjà, sur terre, qu'une tache d'ombre — pas une silhouette dont l'eau
pourrait rendre le détail —, et il vole trop haut pour qu'un reflet au pixel
près veuille dire quelque chose. Ce qu'on voit sous lui reste donc une ombre,
mais l'eau ne l'avale pas comme la terre : elle la teinte. Le turquoise a été
choisi sur rendu parmi trois ; un bleu franc faisait une tache qui tirait l'œil
plus que l'oiseau.

`tests/run.sh visuals/flyer_shadow` pose deux volants qui planent sur place,
l'un sur l'étang, l'autre sur l'herbe.

| Réglage | Rôle |
|---|---|
| `species` | le fichier de `assets/pokemon/overworld/`, sans extension : `wingull` (Goélise), `pelipper` (Bekipan) |
| `zone` | la zone qu'il ne quitte pas, en cases (`Rect2i` : coin haut-gauche et taille) — dix sur dix sur l'île |
| `pace` | sa vitesse, en cases par seconde (2,5) |
| `rest` | le temps qu'il plane entre deux trajets, au moins et au plus (0,3 à 1,6 s) |
| `seed` | une graine pour un vol rejouable ; 0 : un vrai hasard |

**Son vol.** Il avance par **trajets d'une à trois cases** en ligne droite. À
chaque trajet le hasard est rejoué — le sens et la longueur — mais il **ne
rebrousse jamais chemin** : après être allé à gauche il peut monter, descendre
ou continuer à gauche, pas repartir à droite. Un trajet qui sortirait de la
zone est raccourci ; s'il ne reste aucune case dans ce sens, il en tire un
autre. Entre deux trajets, il plane sur place en battant des ailes.

Sur l'île : quatre Goélise (les deux moitiés de la baie, le bras de mer de
l'ouest, la plage du sud) et deux Bekipan (la mer de l'est, la passe du
nord-ouest). Un autre Pokémon volant demande son image dans
`assets/pokemon/overworld/` (`tools/pokemon_overworld.py` la sort des planches
de `sources/`) et un nœud sous `Sky`.

## Sur le terrain d'essai

Les tests du système ont leurs propres personnages, sur `tests/maps/field.tscn`
([verification.md](verification.md)) : deux gardes et leur passage, un
chasseur d'insectes qui erre dans les herbes, un coureur sur sa boucle, un
pêcheur les pieds dans l'eau. Ils ne font pas partie du jeu.

