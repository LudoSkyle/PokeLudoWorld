# Quêtes et drapeaux d'histoire

> **Ce document décrit une quête à implémenter.** Le socle technique — la
> première section — est en place et décrit au présent. Le scénario qui suit,
> lui, n'est pas encore dans le jeu : il sert de cahier des charges, et devra
> être réécrit au présent une fois la quête en place.

La première quête du jeu ne donne ni Pokémon ni objet utile. Elle sert à deux
choses : **donner une raison d'être** à ce que la carte contient déjà (une
grotte vide, deux ouvriers qui bloquent une route, un pêcheur qui attend), et
**ouvrir la route de l'ouest** — c'est-à-dire la suite du jeu.

## Le socle : ce que le moteur sait faire

### Les drapeaux d'histoire

`scripts/gameplay/story/StoryFlags.kt` : un ensemble de noms. Un drapeau est
posé ou ne l'est pas, et une fois posé il le reste.

```kotlin
StoryFlags.has("bell_told")
StoryFlags.set("bell_told")
```

Ils sont écrits dans la sauvegarde, section `[flags]` ([save.md](save.md)), et
remis à zéro quand une partie démarre sans sauvegarde.

Un script Godot — un test, une sonde — passe par l'autoload :
`Globals.has_flag("bell_told")`, `Globals.set_flag("bell_told")`. Dans un test,
ce sont `flag(nom)` et `set_flag(nom)` de `tests/lib.gd`.

Tests : `tests/run.sh quests`.

### Les textes conditionnels : `states`

Un `Npc` ou un `Readable` porte, en plus de `text`, un export `states` : un
`PackedStringArray`, une entrée par état, `drapeau > texte`. Il est lu **de bas
en haut** : la dernière étape atteinte gagne. `text` reste le texte par
défaut, quand aucun de ces drapeaux n'est posé (`StoryText.kt`).

```gdscript
text = "Bienvenue à la bibliothèque.|Tout ce qui est écrit sur le village est ici."
states = PackedStringArray(
    "bell_told > La cloche ? Ta grand-mère en parle encore ?|...",
    "bell_register > Tu l'as trouvé ! Je le cherchais depuis des années.",
    "bell_hung > J'ai fermé la bibliothèque pour ce soir.")
```

Tout tient dans le `.tscn`, il n'y a pas de ressource de dialogue à écrire. La
barre `|` sépare toujours deux boîtes. Les entrées se rangent **dans l'ordre de
l'histoire** : c'est leur place dans la liste qui départage deux drapeaux posés,
pas l'ordre dans lequel le joueur les a obtenus.

Le texte est choisi **à chaque fois qu'on parle** : un drapeau posé pendant
qu'on est sur la carte change la réplique suivante, sans rien recharger.

Chaque état se traduit boîte par boîte dans `locale/en.po`, comme `text` ;
`tests/run.sh i18n` relève les `states` des scènes ([i18n.md](i18n.md)).

### La présence conditionnelle : `required_flag`, `forbidden_flag`

Sur `Npc`, `Readable`, `Sign` et `Roadblock` :

| Propriété | Le nœud est sur la carte… |
|---|---|
| `required_flag` | seulement **si** ce drapeau est posé |
| `forbidden_flag` | seulement **tant que** ce drapeau ne l'est pas |

Les deux peuvent se combiner. Un nœud qui n'a pas sa place se retire de
lui-même (`queueFree()` dans `_ready`) : il ne bloque plus, ne parle plus, et
un passage gardé retiré laisse passer.

**La présence se décide au chargement de la carte.** Un drapeau posé pendant
qu'on s'y trouve ne fait disparaître ni apparaître personne sous nos yeux : le
changement se voit à la prochaine entrée sur la carte, ou après un fondu qui
la recharge.

Deux nœuds `Npc` pour un même personnage — l'un `forbidden_flag`, l'autre
`required_flag` sur le même drapeau — le font changer de place, d'itinéraire
et de texte d'un coup.

> **Rappel.** Un `@Export` Kotlin devient du `snake_case` côté Godot :
> `requiredFlag` s'écrit `required_flag` dans le `.tscn`.

### Poser un drapeau dans un dialogue : `@flag:`

Une boîte qui commence par **`@flag:<drapeau>`** pose ce drapeau **au moment où
elle s'affiche**, sur le modèle de `@give:` ([bag.md](bag.md)). La consigne ne
s'affiche pas. Les deux se combinent, dans n'importe quel ordre, chacune suivie
d'une espace :

```gdscript
text = "Te voilà debout.|@flag:bell_told Demande à Alix, à la bibliothèque."
text = "Tiens, prends ça.|@flag:bell_ribbon @give:vigil_ribbon Vous recevez le Ruban de la Veillée !"
```

Elle vaut partout où un texte passe par la boîte de dialogue : `text`, une
entrée de `states`, un panneau. Un dialogue ne s'interrompt pas : poser le
drapeau sur la première ou la dernière boîte revient au même pour l'histoire.

### La question avant d'agir : `ask`

Un `Npc` ou un `Readable` peut poser une question Oui / Non avant de dire son
texte. La question s'écrit dans la boîte de dialogue, puis **Oui / Non**
apparaît au-dessus d'elle, le curseur sur Oui — la même `ChoiceBox` que pour la
sauvegarde.

| `ask` | La question est posée… |
|---|---|
| `"Question ?"` | avant le texte par défaut, `text` |
| `"drapeau > Question ?"` | avant le texte de **cet état-là**, quand c'est lui qui est en vigueur |

```gdscript
text = "Une machine de soin.|Elle n'a personne à soigner."
states = PackedStringArray(
    "bell_tarnished > @flag:bell_clean La machine s'allume et chante trois notes.|...",
    "bell_clean > ...")
ask = "bell_tarnished > Poser la Cloche ternie dans la machine ?"
```

- **Oui** enchaîne sur le texte : c'est lui qui agit, par ses consignes `@flag:`
  et `@give:`.
- **Non**, ou la touche du menu, referme la boîte : rien n'est dit, rien n'est
  fait, et la question se reposera.
- Hors de l'étape visée, le nœud parle sans rien demander.

Une seule question par nœud. C'est `MessageBox.ask(question, suite)` qui la
pose ([dialogue.md](dialogue.md)).

### Les trouvailles : `kind = "item"`

Un `Readable` de `kind = "item"` est un objet à ramasser. Il reste un corps
invisible posé sur une case : l'objet n'a pas de sprite sur la carte.

| Propriété | Rôle |
|---|---|
| `flag` | le drapeau de **cette** trouvaille — un par trouvaille, c'est lui qui dit qu'elle est prise |
| `text` | ce qu'on lit en la prenant ; **une de ses boîtes donne l'objet par `@give:`** |
| `states` | ce qu'on lit ensuite, en réexaminant la case |
| `ask` | une question avant de prendre, si l'on veut |

```gdscript
kind = "item"
flag = "bell_tarnished"
text = "Quelque chose est à moitié enfoncé dans la vase.|@give:tarnished_bell Vous trouvez la Cloche ternie !"
states = PackedStringArray("bell_tarnished > ...")
```

- Tant que `flag` n'est pas posé, il dit `text`, et **pose `flag` dès la
  première boîte** — après le Oui s'il y a une question. Il n'y a rien d'autre à
  écrire pour qu'on ne ramasse pas deux fois.
- Une fois pris, `text` ne se redit plus : il ne dit que ses `states`.
- **Sans `states`**, il quitte la carte dès qu'il est pris — sa case se
  libère — et n'y revient pas aux chargements suivants. C'est la forme d'un
  objet posé au sol.

L'objet lui-même est une ligne du catalogue ([bag.md](bag.md)) : la trouvaille
ne fait que le donner. Un objet rare est montré au centre de l'écran, comme
pour tout `@give:`. Une trouvaille sans `flag` ou sans `@give:` est signalée
dans les logs au chargement.

### Tests

`tests/run.sh quests` : un fichier par brique, sur des nœuds que le test pose
lui-même avec `spawn()` et des drapeaux `test_…`. Aucun de ces nœuds n'est
dans une carte du jeu.

### Ce que le socle ne fait pas

- **Retirer un objet du sac dans un dialogue.** `@give:` donne, rien ne
  reprend : le jour où la Cloche ternie devient la Cloche claire, il faudra une
  consigne sœur (`@take:<id>`), ou accepter que les deux restent dans le sac.
- **Faire apparaître ou disparaître un nœud sans recharger la carte** : la
  présence se décide au chargement.
- **Une condition sur le contenu du sac** : tout passe par les drapeaux.

---

# La Cloche de Bourg-Ludo

## Pitch

Autrefois, le dernier soir de l'été, on sonnait la cloche sur la place de
Bourg-Ludo. On venait des villages voisins, et — c'est ce que racontent les
vieux — les Pokémon de la forêt descendaient écouter. Puis la cloche a disparu,
la Veillée s'est arrêtée, et le socle est resté vide au milieu de la place.

Personne n'attend rien du joueur. C'est juste une grand-mère qui regrette, et un
village qui a oublié pourquoi il a un socle vide.

## Les personnages

| Qui | Apparence | Où | Rôle |
|---|---|---|---|
| **Mémé Odile** | `socialite` (voir *À trancher*) | salon de `ludo_house`, puis la place | **notre grand-mère.** Elle lance la quête et reçoit la cloche |
| **Alix** | `aroma_girl` | la bibliothèque | oriente vers le rayon des archives |
| **Roland** | `ruin_maniac` | devant l'entrée de la grotte | confirme qu'il y a quelque chose en bas |
| **Le Professeur** | `professor_elm` | `lab_house` — **à ajouter, le labo n'a aucun PNJ** | identifie le bronze, envoie vers la machine de soin |
| *Le chasseur d'insectes* | `bug_catcher` | existe déjà | témoin, puis commentaire final |
| *Le pêcheur* | `fisher` | existe déjà | témoin, puis monte à la fête |
| *Le coureur* | `triathlete_m` | existe déjà | change de parcours à la fin |
| *Les deux ouvriers* | `worker` | existent déjà | réparent la route **pour la Veillée** ; disparaissent à la fin |

## Les six drapeaux

Un par étape. `bell_hung` est le seul qui change la carte.

| Drapeau | Posé par | Ce qu'il débloque |
|---|---|---|
| `bell_told` | Mémé, chez nous | le dialogue d'Alix, et les archives de la bibliothèque |
| `bell_register` | le rayon des archives | le dialogue de Roland |
| `bell_tarnished` | la cloche au bord du lac du B2F | le dialogue du Professeur |
| `bell_clean` | la machine de soin du labo | le don à Mémé |
| `bell_ribbon` | Mémé, qui rend la cloche | le socle |
| `bell_hung` | le socle, sur la place | **la Veillée** |

## Le déroulé

### 1 — La rumeur · salon de `ludo_house`

Mémé est assise chez nous. Le salon est vide d'habitants aujourd'hui ; elle y
donne une raison de descendre de sa chambre, comme la mère dans les jeux
d'origine.

> Te voilà debout. J'ai gardé du pain pour toi.
> |Tu as vu le socle vide, sur la place ? Il y avait une cloche dessus.
> |On la sonnait le dernier soir de l'été. Tout le village venait.
> |Même les Pokémon descendaient écouter, disait ma mère.
> |Personne ne sait où elle est passée. Demande à Alix, à la bibliothèque.

→ `bell_told`

*Avec `bell_told`, sans `bell_clean` :*
> Alors ? Alix t'a trouvé quelque chose ?
> |Prends ton temps. Moi, je ne bouge plus d'ici.

### 2 — L'enquête · la bibliothèque

Alix, sans `bell_told` :
> Bienvenue à la bibliothèque.
> |Tout ce qui est écrit sur le village est ici.

Avec `bell_told` :
> La cloche ? Ta grand-mère en parle encore ?
> |Le registre des Veillées doit être quelque part dans ces rayons.
> |Cherche au fond, à gauche : c'est là que dorment les vieux papiers.
> |Si tu le trouves, il est à toi. Moi, je ne grimpe plus à l'échelle.

**Le rayon doit être montré du doigt.** Une bibliothèque entière à examiner case
par case devient une corvée : la zone des archives fait **quatre cases**, au
fond à gauche, et porte son propre texte pour qu'on sente qu'on est au bon
endroit.

Les quatre cases, avec `bell_told` :
> Des registres reliés, rangés par année.

La troisième, en plus :
> L'un d'eux est beaucoup plus poussiéreux que les autres.

→ ramassage, `bell_register`

### 3 — L'indice · au moment du ramassage

Le Registre est un **objet rare** : il entre dans le sac par `@give:`, et son
texte se lit au moment où on le prend. Le sac n'a pas d'action « lire » : on
n'y retrouve que sa description.

> Vous trouvez le Registre poussiéreux !
> |« ...la cloche a été descendue à l'abri pour l'hiver, »
> |« au frais, là où l'eau dort sous la pierre. »
> |« On la remontera pour la Veillée prochaine. »

La dernière ligne promet une fête qui n'a jamais eu lieu. Et « l'eau qui dort
sous la pierre » désigne `cave_b2f` sans le nommer.

*Le rayon, après :*
> C'est de là que venait le registre.
> |Le vide dans la rangée se voit encore.

### 4 — La descente · devant la grotte, puis `cave_b2f`

Roland, sans `bell_register` :
> Cette grotte, j'y ai passé vingt ans.
> |Elle a encore des choses à dire, je le sens.

Avec `bell_register` :
> Tout en bas, près du lac souterrain...
> |...il y a quelque chose qui accroche la lumière.
> |Moi, j'y descends plus. Trop de noir, trop de cailloux qui bougent.

Au bord du lac de `cave_b2f` — une salle qui ne contient **rien** aujourd'hui :
> Quelque chose est à moitié enfoncé dans la vase.
> |Vous trouvez la Cloche ternie !
> |Quelque chose file le long de la paroi et disparaît dans le noir.

→ `bell_tarnished`

La silhouette est le premier Pokémon du jeu : on le voit, on ne peut rien en
faire. C'est exactement ce qu'on veut tant qu'il n'y a pas de combat.

*Roland, après :*
> Alors c'était ça qui brillait.
> |Une cloche. Vingt ans que je passe devant.

### 5 — Le nettoyage · `lab_house`

Le Professeur, avec `bell_tarnished` :
> Fais voir ça... Du bronze de l'ancienne mine.
> |On n'en coule plus depuis bien avant moi.
> |Pose-la dans la machine de soin, là-bas. Elle nettoie tout.

**La machine de soin**, pas la machine aux trois Poké Balls : contre le mur du
fond, le bloc 2×3 à `x 16-17, y 5-7` du calque `Props`. Elle n'a aujourd'hui
aucun `Readable` — il faut l'ajouter.

Sans `bell_tarnished` :
> Une machine de soin.
> |Elle n'a personne à soigner.

Avec `bell_tarnished`, question `ChoiceBox` : **« Poser la Cloche ternie dans la machine ? »**
> La machine s'allume et chante trois notes.
> |Vous récupérez la Cloche claire !

→ `bell_clean`

Le fait que la machine n'ait rien à soigner tant qu'il n'y a pas de Pokémon est
précisément ce qui justifie qu'on s'en serve pour autre chose.

### 6 — Le don · retour chez nous

Mémé, avec `bell_clean`, question : **« Montrer la cloche à Mémé ? »**
> Oh...
> |Elle est comme dans mon souvenir. Exactement comme ça.
> |Non, garde-la. Mes jambes ne montent plus jusque là-haut.
> |Tiens, prends aussi ça. Je l'ai porté à la dernière Veillée.
> |Vous recevez le Ruban de la Veillée !
> |Allez, va. Et sonne fort, que je l'entende d'ici.

→ `bell_ribbon` — **elle rend la cloche**, c'est au joueur de la raccrocher.

Le Ruban n'a aucun usage, et n'en aura jamais. C'est le genre d'objet que les
jeux d'origine donnent et qu'on garde vingt ans.

### 7 — La Veillée · le socle, sur la place

Sans `bell_ribbon` :
> Un socle de pierre. Il manque quelque chose dessus.

Avec `bell_ribbon`, question : **« Accrocher la Cloche claire ? »**
> Vous accrochez la cloche. Elle tient.

Puis la sonnerie et un fondu court. → `bell_hung`

*Après :*
> La cloche est à sa place.
> |Elle bouge un peu quand le vent passe.

## Ce qui change avec `bell_hung`

Tout passe par `required_flag` / `forbidden_flag` : les nœuds d'avant
disparaissent, ceux d'après apparaissent. Deux nœuds `Npc` pour un même
personnage quand il bouge **et** change de texte.

| Nœud | Avant | Après |
|---|---|---|
| `Triggers/WestRoadblock`, `GuardNorth`, `GuardSouth` | ferment la route ouest | **supprimés** — la route est ouverte |
| un ouvrier, sur la place | — | « La route est prête. On a fini juste à temps. » |
| `Runner` | boucle de 52 cases entre les deux maisons | **nouvelle `route`, en sens inverse, passant par la place** |
| `GrassWatcher` | erre dans les hautes herbes | y reste, et change de texte |
| `Fisher` | au bord de l'eau profonde | sur la place, face au socle |
| Mémé Odile | salon de `ludo_house` | **dehors, au pied du socle** |
| Alix | la bibliothèque | dehors |
| Roland | devant la grotte | dehors |
| Visiteurs | — | `backpacker_m`, `backpacker_f`, `kalos_hiker`, `preschooler`, `festival_girl`, `painter`, `waitress`, `black_belt` |
| Silhouette | — | un Pokémon visible dans les hautes herbes, qui s'enfuit quand on approche |

Les répliques d'après :

**Le coureur** — il ne s'arrête surtout pas de courir :
> Cette cloche m'a ouvert les yeux !
> |J'ai couru dans le mauvais sens pendant dix ans !

**Le chasseur d'insectes** — content pour nous, bredouille pour lui :
> Il paraît que c'est toi qui as retrouvé la cloche ! Bravo !
> |Moi, toujours pas le moindre insecte.

**Le pêcheur** :
> J'ai laissé ma canne là-bas. Pour une fois.

**Mémé Odile**, sous la cloche :
> Je l'ai entendue. De mes propres oreilles, encore une fois.
> |Merci.

**Alix** :
> J'ai fermé la bibliothèque pour ce soir.
> |Il y a des choses qu'on n'apprend pas dans les livres.

**Roland** :
> Vingt ans que je passais devant sans la voir.

**L'ouvrier** :
> La route de l'ouest est ouverte.
> |On a fini juste à temps pour la Veillée.

## Les objets à trouver en asset

| Objet | À quoi ça ressemble | Rôle |
|---|---|---|
| **Registre poussiéreux** | vieux livre relié, tranche abîmée | l'indice |
| **Cloche ternie** | petite cloche de bronze noircie | la trouvaille |
| **Cloche claire** | la même, dorée — un recolor suffit | après la machine de soin |
| **Ruban de la Veillée** | ruban de tissu, bleu ou rouge | le souvenir, sans usage |
| **Socle** *(décor)* | pilier de pierre, **deux versions : vide et avec cloche** | la place |
| **Statue de Pokémon** *(décor)* | n'importe laquelle, devant le labo | décor, sans rapport avec la quête |
| **Silhouette de Pokémon** | un sprite, même sans animation | la grotte et les herbes |

Les quatre premiers ne sont jamais posés sur la carte, mais ce sont de **vrais
objets rares** : une ligne chacun dans le catalogue (`Items.kt`, poche
`KEY_ITEMS`), donnés par `@give:` et montrés au centre de l'écran quand on les
reçoit ([bag.md](bag.md)). Il leur faut donc à chacun :

- un identifiant, un nom et une description, avec leurs traductions ;
- une **icône** : une référence dans l'un des deux atlas de `assets/items/`
  (267 icônes officielles, 1382 de l'ItemDex — voir leur `CREDITS.md`). Un
  livre, une cloche et un ruban s'y trouvent sans doute ; sinon, un asset à
  fournir. Une référence fausse affiche un point d'interrogation.

## Les retouches de carte

### La bibliothèque

La maison du centre devient la bibliothèque du village. Son intérieur actuel
(`neighbor_house.tscn`) est déjà fait de deux bibliothèques et deux télés : il
est réaménagé en bibliothèque pour de vrai, et renommé `library.tscn`. Les
voisins auront une maison neuve plus tard.

À reprendre : `target_scene` de la porte `MaisonVoisins` dans `start_town`, le
texte de `SignNeighbors`, et `metadata/location` (« Bibliothèque » tient dans
les vingt caractères du bandeau).

La pièce actuelle fait 12 colonnes, mur en `y 5-7`, sol en `y 8-13`. Pour une
bibliothèque, l'élargir à **14 colonnes sur 7 rangées de sol** ; le cadre de
32 × 20 cases de noir reste inchangé.

Intention d'aménagement — les cases exactes se calent dans l'éditeur :

```
mur    ██████████████     rangée haute, presque vide
mur    █████  fe  █████   fenêtre dans la trouée, seul endroit sans meuble haut
adossé AA AA BB ..  .. BB BB BB   archives à gauche, rayonnages à droite
adossé AA AA BB ..  .. BB BB BB
sol    .  .  .  .  .  .  .  .     allée du fond
sol    .  BB BB .  BB BB .  CC    rangée centrale, deux allées, comptoir d'Alix
sol    .  BB BB .  BB BB .  CC
sol    .  .  .  .  .  .  .  .
sol    PL TT TT .  .  .  .  PL    table de lecture, plantes aux coins
sol    .  tb tb .  MM .  .  .     tabourets franchissables, paillasson centré
```

`AA` = les **quatre cases d'archives**, au fond à gauche, texte propre, le
Registre dans la troisième. `BB` = rayonnages ordinaires, texte générique. Les
règles de composition de [levels.md](levels.md) s'appliquent telles quelles :
meuble adossé à partir de la rangée 2 du mur, fenêtre seulement au-dessus d'une
colonne sans meuble haut, aucune poche de sol fermée, paillasson rouge centré
sur la dernière rangée.

### La place

Une place dallée au centre du village, dans le triangle maison de Ludo (8,15) /
bibliothèque (21,13) / labo (28,7). Elle porte le socle, un banc, et la statue.

**Vérifier qu'elle ne coupe pas la boucle du coureur** : sa `route` de 52 cases
passe par ce tronçon de chemin, et deux points consécutifs doivent rester reliés
par un trajet libre ([npcs.md](npcs.md)).

### Le laboratoire

Ajouter le Professeur sous `World/Entities`, et un `Readable` sur les cases
solides de la machine de soin (`x 16-17, y 5-7` du calque `Props`), examinable
depuis la première rangée de sol.

### La grotte

Rien à redessiner. Poser la Cloche ternie au bord du lac de `cave_b2f`, et
Roland dans `start_town`, à côté de la porte `Grotte`.

## Ordre d'implémentation

Six lots, chacun testable seul. Les trois premiers servent à toutes les quêtes
suivantes et ne contiennent pas une ligne de scénario.

1. **Les drapeaux** (brique 1) — **fait**.
2. **Textes conditionnels et présence conditionnelle** (briques 2 et 5) — **fait**.
3. **Objets ramassables et question** (briques 3 et 4) — **fait**.
4. **La bibliothèque** : la carte, Alix, les archives, le Registre.
5. **Le reste de la chaîne** : Mémé chez nous, Roland, le Professeur, la machine
   de soin, la cloche au B2F.
6. **La place et la Veillée** : le socle, et tout ce que `bell_hung` change.

Chaque lot ajoute ses textes à `locale/en.po` **boîte par boîte** et passe
`tests/run.sh i18n` ([i18n.md](i18n.md)). La carte se vérifie comme les autres :
accessibilité et parcours réel ([levels.md](levels.md),
[verification.md](verification.md)).

## À trancher

- **Le prénom de la mémé.** « Odile » est un bouche-trou.
- **Son apparence.** Le catalogue n'a aucune planche de personne âgée.
  `socialite` est la plus proche (cheveux gris, tenue sobre) ; sinon, déposer
  une planche de 128×192 dans `assets/characters`, voir [npcs.md](npcs.md).
- **La silhouette de Pokémon.** Le dépôt n'en contient aucun sprite aujourd'hui.
  Sans lui, la quête tient quand même : la ligne « quelque chose file le long de
  la paroi » se suffit à elle-même.
