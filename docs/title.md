# Écran titre

`scenes/ui/title_screen.tscn`, script `TitleScreen.kt`, instancié dans
`game_manager.tscn`. C'est ce qu'on voit au lancement : aucune carte n'est
chargée tant que le joueur n'a pas choisi.

## Trois images indépendantes

L'écran superpose trois créations qui ne savent rien l'une de l'autre. **On en
change une sans toucher aux deux autres** : remplacer le fichier, ou donner une
autre texture au nœud dans la scène.

| Nœud | Image (`assets/ui/title/`) | Fabriquée par | Ce que fait l'écran |
|---|---|---|---|
| `Backdrop` | le fond, en quatre calques de 320×240 (voir plus bas) | `tools/title_background.py` | étire chaque calque sur tout l'écran ; les nuages défilent, des Goélise passent |
| `Logo` | `logo.png`, fond transparent, deux fois sa taille à l'écran | `tools/title_logo.py` | le ramène dans un cadre de 1000×350 sans le déformer ; il arrive en grossissant, flotte, et un reflet le traverse |
| `Prompt` | `prompt.png` (« PRESS ENTER »), en pixels de jeu | `tools/title_prompt.py` | l'affiche à l'échelle 4 ; il clignote |

Les trois scripts de `tools/` redonnent le même fichier à chaque lancement.
Seul le logo a des dépendances : `rsvg-convert` (`brew install librsvg`) et la
police Gill Sans de macOS.

## Le fond : le sommet d'une tour, au-dessus des nuages

Les enfants de `Backdrop`, du plus lointain au plus proche :

| Nœud | Image | Rôle |
|---|---|---|
| `Sky` | `background.png` | le ciel — clair à hauteur d'yeux, plus profond vers le bas, où l'on regarde dans le vide — et les grands nuages immobiles |
| `FarClouds` | `clouds_far.png` | des nuages qui passent **derrière** la tour, lentement |
| `FarFlyers` | — | les Goélise du lointain, petits et pâlis |
| `Tower` | `tower.png` | la tour : pierre usée, mousse, créneaux tombés, un sceau runique qui luit |
| `NearFlyers` | — | les Goélise proches, qui passent **devant** la tour |
| `NearClouds` | `clouds_near.png` | la mer de nuages où le pied de la tour se perd ; elle défile plus vite |

Les deux images de nuages se raccordent d'un bord à l'autre ; leur vitesse est
le `speed` de leur matériau (`title_clouds.gdshader`), en largeurs d'écran par
seconde.

**Les Goélise** sont créés par `TitleScreen` à partir de la planche
`assets/pokemon/overworld/<flyer_species>.png`, la même que sur l'île
([levels.md](levels.md)). Chacun traverse l'écran d'un bord à l'autre en
ondulant, puis revient quelques secondes plus tard, à une autre hauteur, dans
un sens tiré au hasard. `far_flyers` et `near_flyers` en règlent le nombre ;
`flyer_species` vide n'en met aucun. Ceux du lointain sont à l'échelle 2
(`far_flyer_scale`) au lieu de 4 : c'est le seul endroit du jeu où un pixel
n'a pas la taille des autres, pour dire la distance.

**Le sceau de la tour** est un signe runique gravé à même les pierres, sans
cadre : un anneau traversé d'une croix, quatre branches qui portent chacune un
peigne de traits, le même dessin tourné d'un quart de tour à chaque branche
(`seal()` dans le script). Le sillon luit ; sous chaque trait, l'ombre de la
gravure le détache de la pierre claire.

## Le logo

`tools/title_logo.py` assemble trois morceaux :

- **le logo Pokémon**, lu dans `assets/ui/title/sources/pokemon_logo.png` (le
  jeu ne lit jamais ce fichier). **Sa forme n'est pas retouchée** : seules ses
  couleurs changent — le jaune devient blanc, son ombre dorée bleu ciel, le
  cerne bleu reste (`tint`, `FACE`, `RELIEF`). Un halo clair le détache du
  ciel, sans toucher au dessin ;
- **l'emblème**, lu dans `assets/ui/title/sources/emblem_reference.png` et
  repris **trait pour trait** : son fond est retiré, ses traits noirs passent
  au bleu nuit, ses gris et ses jaunes aux bleus du ciel (`recolour`,
  `SHADES`). Seul son centre est refait : un disque de ciel et un nuage à la
  place de la bille dorée. Il est posé bas, à cheval entre les deux mots, et
  dessiné avant eux : le logo Pokémon et MIRAGE passent par-dessus là où ils
  se croisent ;
- **le mot MIRAGE** : du ciel dans les lettres, des nuages à leur pied. La
  dernière valeur de chaque ligne de `LETTERS` rapproche une lettre de la
  précédente (le G se glisse sous la jambe du A).

```bash
python3 tools/title_background.py
python3 tools/title_logo.py
python3 tools/title_prompt.py
```

Le logo est la seule image qui n'est pas du pixel art : son nœud est filtré
(`texture_filter = 4`) et `logo.png.import` demande des mipmaps. Sans eux il
scintille quand il bouge.

**Un autre fond** : une seule image de 320×240 donnée à `Sky` suffit ; vider
la texture des autres calques, ou les cacher. N'importe quelle taille convient,
l'image couvre l'écran.

## Les morceaux, gardés à part

Le jeu affiche `logo.png` et `tower.png` d'un bloc, mais leurs morceaux sont
aussi écrits séparément par les mêmes scripts, dans `assets/ui/title/parts/`,
chacun **sur la toile de l'image entière** : posés l'un sur l'autre dans
l'ordre, ils la redonnent au pixel près.

| Fichier | Ce que c'est | Se pose sur |
|---|---|---|
| `parts/emblem.png` | l'emblème ailé, recoloré, avec son nouveau centre | — (le premier) |
| `parts/pokemon.png` | le logo Pokémon bleuté et son halo | `emblem.png` |
| `parts/mirage.png` | le mot MIRAGE et son ombre | `pokemon.png` → `logo.png` |
| `parts/tower_bare.png` | la tour sans son sceau | — |
| `parts/seal.png` | le sceau seul | `tower_bare.png` → `tower.png` |

Pour animer ou remplacer un seul morceau (faire luire le sceau, faire arriver
l'emblème avant les mots), donner ces images à des nœuds distincts à la place
de `Logo` ou de `Tower` : aucune mise en place n'est à refaire, elles sont déjà
calées.

Les originaux fournis, avant recoloration, sont dans `assets/ui/title/sources/`
(`pokemon_logo.png`, `emblem_reference.png`). Les Goélise ne sont pas dans ce
dossier : c'est la planche `assets/pokemon/overworld/wingull.png`, quatre
images de profil (deux par sens de vol).

## Le déroulé

1. Le noir se lève (`fade_in_seconds`), le logo arrive (`logo_in_seconds`).
   Une pression d'interaction abrège l'arrivée, sans ouvrir le menu.
2. « Press Enter » clignote. La touche d'**interaction** (Entrée ou Espace)
   ouvre le menu.
3. Le menu, une `ChoiceBox` comme les autres :

| Entrée | Effet |
|---|---|
| **Continuer** | reprend la sauvegarde ; **n'apparaît que s'il y en a une**, et vient alors en premier |
| **Nouvelle partie** | repart de zéro, sur la carte de départ. La sauvegarde reste en place tant qu'on ne sauvegarde pas par-dessus |
| **Options** | ouvre l'écran des options ([menu.md](menu.md)) ; au retour le menu est réécrit dans la langue choisie, le curseur sur Options |
| **Retour**, ou la touche du menu | referme le menu : on revient à « Press Enter » |

4. L'écran part au noir, la carte se charge, le noir se lève
   (`SceneManager.title_fade_seconds`, 0,6 s à l'aller comme au retour).
   L'écran titre s'efface pendant que tout est noir.

## Qui fait quoi

`SceneManager` ne charge rien tant que `show_title` est vrai : il attend
`start(resume)`, appelé par l'écran titre. `resume` reprend la sauvegarde
([save.md](save.md)), sinon le sac et les drapeaux sont vidés. Le temps de jeu
ne tourne pas sur l'écran titre.

**La touche d'interaction n'a toujours qu'un lecteur.** Tant que la partie n'a
pas commencé, le joueur n'est dans aucune carte et ne lit rien : c'est
`TitleScreen` qui la lit. Une fois la partie lancée il ne lit plus rien, et
c'est `Player` qui reprend ([menu.md](menu.md)).

Les sons sont ceux des menus : `confirm` pour ouvrir et valider, `cancel` pour
Retour, `cursor` quand le curseur bouge ([audio.md](audio.md)).

## Ce qui manque

- **Une musique** : l'écran titre joue `assets/audio/music/title` dès que ce
  fichier existe (`TitleScreen.music`) ; sans lui, il est silencieux.
- **Revenir à l'écran titre** depuis le menu de pause.
- Le résumé de la sauvegarde (lieu, temps de jeu) à côté de « Continuer ».

## Tests

Lancés par `tests/run.sh`, les tests **sautent l'écran titre** et arrivent
directement sur leur carte (`show_title = false`, posé par `boot()`). Un test
qui veut l'écran titre répond `true` à `title()` ; les outils sont dans
`tests/lib.gd` : `title_ready`, `title_pick`, `title_gone`, `title_entries`,
`title_selected`.

```bash
tests/run.sh ui/title
```

| Test | Ce qu'il joue |
|---|---|
| `title_new_game` | l'écran au lancement, le clignotement, le menu sans sauvegarde, Nouvelle partie |
| `title_continue` | avec une sauvegarde : Continuer en premier, et la reprise sur la même case |
| `title_new_over_save` | Nouvelle partie par-dessus une sauvegarde, qui reste en place |
| `title_back` | Retour et la touche du menu ramènent à « Press Enter » |
| `title_options` | les options depuis l'écran titre, la langue qui change le menu |
