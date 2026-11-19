#!/bin/bash
# Lance les tests portes sur gdUnit4 (tests/gdunit/).
#
#   tests/gdunit/run.sh                 tout
#   tests/gdunit/run.sh moves           un dossier
#   tests/gdunit/run.sh moves/run.gd    un fichier
#   WINDOW=1 tests/gdunit/run.sh ...    tout dans une fenetre, pour regarder
#   REALTIME=1 tests/gdunit/run.sh ...  au rythme de l'horloge (avec WINDOW=1)
#   IMPORT=1 tests/gdunit/run.sh ...    refaire l'import meme si rien n'a change
#
# Un seul Godot pour tous les tests. Le jeu avance d'un soixantieme de seconde par image
# (--fixed-fps 60), et les images s'enchainent aussi vite que la machine le peut.
#
# Deux passages : **sans fenetre** (--headless) pour tout ce qui ne lit pas l'image — rien ne
# s'ouvre, rien ne passe devant ce qu'on fait —, puis **dans une fenetre** pour les quelques tests
# qui la lisent (ceux qui repondent true a reads_screen()).
#
# Avant de jouer, le lanceur met le projet a jour, et dit ce qu'il fait :
#   - il recompile le Kotlin si une source est plus recente que jvm/main.jar ;
#   - il fait importer le projet par Godot si un fichier a change depuis le dernier import.
# L'import est un demarrage d'editeur, greffons compris. **On ne le fait donc jamais quand un
# editeur est deja ouvert sur le projet** : c'est lui qui importe, et un second lui prendrait son
# inscription aupres du serveur MCP.
#
# Chaque Godot est lance a part et attendu : Ctrl-C l'arrete toujours (la JVM du jeu retient un
# simple INT), et un import qui n'ecrit plus rien pendant IMPORT_STALL secondes est arrete.
#
# « -- --test » : le jeu ecrit ses reglages et sa sauvegarde dans des fichiers de test (GameFiles.kt).
cd -P "$(dirname "$0")/../.." || exit 1
GODOT="${GODOT:-/Users/godart/Downloads/Godot.app/Contents/MacOS/Godot}"
where="tests/gdunit${1:+/$1}"
speed="--fixed-fps 60 --disable-vsync"
[ -n "$REALTIME" ] && speed=""
classes=".godot/global_script_class_cache.cfg"
stamp=".godot/tests_import.stamp"
stall="${IMPORT_STALL:-90}"

say() { echo "tests/gdunit : $*" >&2; }

if [ ! -e "$where" ]; then say "$where n'existe pas."; exit 1; fi

# --- arret --------------------------------------------------------------------------------------
pid=""
stop() {
  [ -n "$pid" ] && kill -9 "$pid" 2> /dev/null
  echo >&2; say "interrompu."
  exit 130
}
trap stop INT TERM

# --- le Kotlin ----------------------------------------------------------------------------------
# (gradle ne reecrit pas le jar quand le contenu des sources n'a pas bouge — apres un changement de
# branche, par exemple : on note donc a part quand on a compile.)
compiled="build/tests_kotlin.stamp"
ref="jvm/main.jar"; [ "$compiled" -nt "$ref" ] && ref="$compiled"
if [ ! -f jvm/main.jar ] || [ -n "$(find src/main/kotlin build.gradle.kts -newer "$ref" \( -name '*.kt' -o -name '*.kts' \) -print -quit 2> /dev/null)" ]; then
  say "le Kotlin a change : compilation (./gradlew build -x test)..."
  ./gradlew build -x test -q &
  pid=$!; wait "$pid"; built=$?; pid=""
  if [ "$built" -ne 0 ] || [ ! -f jvm/main.jar ]; then say "la compilation a echoue : rien n'est joue."; exit 1; fi
  mkdir -p build && touch "$compiled"
fi

# --- l'import -----------------------------------------------------------------------------------
# Un editeur Godot ouvert sur ce dossier ? Son dossier courant est celui du projet, liens resolus.
# (ps -ww : dans un terminal, ps coupe ses lignes a sa largeur, et « --editor » est au bout.)
editor_open() {
  local here p
  here="$(pwd -P)"
  for p in $(ps -axwwo pid=,command= | grep -E '/Godot( .*)? (--editor|-e)( |$)' | awk '{print $1}'); do
    [ "$(lsof -a -p "$p" -d cwd -Fn 2> /dev/null | sed -n 's/^n//p')" = "$here" ] && return 0
  done
  return 1
}

# Un fichier que Godot importe, plus recent que le fichier $1 ?
changed_since() {
  [ -n "$(find project.godot src tests addons -newer "$1" -type f -not -name '*.kt' -not -name '*.sh' -not -name '*.py' -not -name '*.md' -not -name '.DS_Store' -print -quit 2> /dev/null)" ]
}

# Faut-il importer ? Oui si un fichier a change depuis le dernier import fait d'ici.
import_needed() {
  [ -n "$IMPORT" ] && return 0
  [ -f "$stamp" ] && [ -f "$classes" ] || return 0
  changed_since "$stamp"
}

# L'editeur ouvert a-t-il du retard ? Oui si un fichier a change depuis son dernier releve du projet
# (il le refait quand sa fenetre reprend la main, et le note dans .godot/editor/filesystem_cache*).
editor_behind() {
  local seen
  seen="$(ls -t .godot/editor/filesystem_cache* 2> /dev/null | head -1)"
  [ -n "$seen" ] || return 0
  [ -f "$stamp" ] && [ "$stamp" -nt "$seen" ] && seen="$stamp"
  changed_since "$seen"
}

import_project() {
  local log="${TMPDIR:-/tmp}/pokemon_mirage_import.log" size last=-1 quiet=0 started=$SECONDS code
  say "import du projet (journal : $log)..."
  "$GODOT" --headless --path "$PWD" --import > "$log" 2>&1 &
  pid=$!
  while kill -0 "$pid" 2> /dev/null; do
    sleep 1
    size=$(wc -c < "$log" 2> /dev/null || echo 0)
    if [ "$size" = "$last" ]; then quiet=$((quiet + 1)); else quiet=0; last="$size"; fi
    if [ "$quiet" -ge "$stall" ]; then
      kill -9 "$pid" 2> /dev/null; wait "$pid" 2> /dev/null; pid=""
      say "l'import n'ecrit plus rien depuis $stall s : arrete. Ses dernieres lignes :"
      tail -5 "$log" >&2
      say "relancer ; si cela se repete, ouvrir le projet dans l'editeur, le laisser importer, puis relancer."
      return 1
    fi
  done
  wait "$pid"; code=$?; pid=""
  if [ "$code" -ne 0 ]; then
    say "l'import a echoue (code $code). Ses dernieres lignes :"
    tail -15 "$log" >&2
    return 1
  fi
  touch "$stamp"
  say "import fait en $((SECONDS - started)) s."
}

if editor_open; then
  if ! grep -q 'GdUnitTestSuite' "$classes" 2> /dev/null; then
    say "un editeur Godot est ouvert sur ce projet et n'a pas fini de l'importer."
    say "lui donner la main le temps qu'il importe, puis relancer."
    exit 1
  fi
  say "un editeur Godot est ouvert sur ce projet : c'est lui qui importe, on ne le fait pas."
  if editor_behind; then
    say "attention : des fichiers ont change depuis son dernier releve du projet (il le refait quand sa"
    say "fenetre reprend la main). Tant qu'il ne les a pas importes, les tests jouent sur l'ancien etat."
  fi
elif import_needed; then
  import_project || exit 1
fi

# --- les tests ----------------------------------------------------------------------------------
play() {   # play <--headless ou rien> <arguments de gdUnit4...>
  local window="$1" code; shift
  "$GODOT" $window $speed --path "$PWD" -s -d --remote-debug tcp://127.0.0.1:0 res://addons/gdUnit4/bin/GdUnitCmdTool.gd "$@" -c --ignoreHeadlessMode -- --test &
  pid=$!; wait "$pid"; code=$?; pid=""
  return $code
}

if [ -n "$WINDOW" ]; then GDUNIT_KEEP_WINDOW=1 play "" -a "res://$where"; exit $?; fi

screen=$(grep -rl "^func reads_screen" "$where" 2> /dev/null | grep -v game_suite.gd)
ignore=""; add=""
for f in $screen; do ignore="$ignore -i res://$f"; add="$add -a res://$f"; done
code=0
if [ -d "$where" ] || [ -z "$screen" ]; then play --headless -a "res://$where" $ignore || code=$?; fi
# (GDUNIT_KEEP_WINDOW : gdUnit4 ne reduit pas la fenetre, on n'a donc pas a la rouvrir — addons/gdUnit4/PATCHES.md)
if [ -n "$screen" ]; then GDUNIT_KEEP_WINDOW=1 play "" $add || code=$?; fi
# 101 : tout passe, avec des avertissements de gdUnit4 (des noeuds que le jeu laisse derriere lui en se demontant).
[ "$code" -eq 101 ] && code=0
exit $code
