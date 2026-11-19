#!/bin/bash
# Lance les tests portes sur gdUnit4 (tests/gdunit/).
#
#   tests/gdunit/run.sh                 tout
#   tests/gdunit/run.sh moves           un dossier
#   tests/gdunit/run.sh moves/run.gd    un fichier
#   WINDOW=1 tests/gdunit/run.sh ...    tout dans une fenetre, pour regarder
#   REALTIME=1 tests/gdunit/run.sh ...  au rythme de l'horloge (avec WINDOW=1)
#
# Un seul Godot pour tous les tests. Le jeu avance d'un soixantieme de seconde par image
# (--fixed-fps 60), et les images s'enchainent aussi vite que la machine le peut.
#
# Deux passages : **sans fenetre** (--headless) pour tout ce qui ne lit pas l'image — rien ne
# s'ouvre, rien ne passe devant ce qu'on fait —, puis **dans une fenetre** pour les quelques tests
# qui la lisent (ceux qui repondent true a reads_screen()).
#
# « -- --test » : le jeu ecrit ses reglages et sa sauvegarde dans des fichiers de test (GameFiles.kt).
cd "$(dirname "$0")/../.." || exit 1
GODOT="${GODOT:-/Users/godart/Downloads/Godot.app/Contents/MacOS/Godot}"
where="tests/gdunit${1:+/$1}"
speed="--fixed-fps 60 --disable-vsync"
[ -n "$REALTIME" ] && speed=""
"$GODOT" --headless --path "$PWD" --import > /dev/null 2>&1

play() {   # play <--headless ou rien> <arguments de gdUnit4...>
  local window="$1"; shift
  "$GODOT" $window $speed --path "$PWD" -s -d --remote-debug tcp://127.0.0.1:0 res://addons/gdUnit4/bin/GdUnitCmdTool.gd "$@" -c --ignoreHeadlessMode -- --test
}

if [ -n "$WINDOW" ]; then GDUNIT_KEEP_WINDOW=1 play "" -a "res://$where"; exit $?; fi

screen=$(grep -rl "^func reads_screen" "$where" 2>/dev/null | grep -v game_suite.gd)
ignore=""; add=""
for f in $screen; do ignore="$ignore -i res://$f"; add="$add -a res://$f"; done
code=0
if [ -d "$where" ] || [ -z "$screen" ]; then play --headless -a "res://$where" $ignore || code=$?; fi
# (GDUNIT_KEEP_WINDOW : gdUnit4 ne reduit pas la fenetre, on n'a donc pas a la rouvrir — addons/gdUnit4/PATCHES.md)
if [ -n "$screen" ]; then GDUNIT_KEEP_WINDOW=1 play "" $add || code=$?; fi
# 101 : tout passe, avec des avertissements de gdUnit4 (des noeuds que le jeu laisse derriere lui en se demontant).
[ "$code" -eq 101 ] && code=0
exit $code
