# Ce qui diffère de gdUnit4 6.2.3

gdUnit4 (Mike Schulze, licence MIT) est copié ici tel quel depuis
github.com/MikeSchulze/gdUnit4, étiquette `v6.2.3`, sans son dossier `test/`.
**Une seule retouche**, à refaire après une mise à jour :

gdUnit4 **réduit la fenêtre** au lancement et après chaque suite. Nos quelques
tests qui lisent l'image à l'écran ont besoin d'une fenêtre dessinée, et la
rouvrir à chaque test la ramène devant tout ce qu'on fait. Avec la variable
d'environnement `GDUNIT_KEEP_WINDOW`, gdUnit4 ne la réduit plus : elle s'ouvre
une fois et reste où elle est. Les trois appels à
`DisplayServer.window_set_mode(WINDOW_MODE_MINIMIZED)` sont gardés derrière ce
test :

- `bin/GdUnitCmdTool.gd`
- `src/core/runners/GdUnitTestSessionRunner.gd`
- `src/core/execution/stages/GdUnitTestSuiteAfterStage.gd`

`tests/gdunit/run.sh` ne pose cette variable que pour son passage en fenêtre.
