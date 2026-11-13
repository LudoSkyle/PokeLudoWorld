#!/bin/bash
# Lance les tests joues au clavier. Un test = un petit fichier, un seul sujet.
#
#   tests/run.sh dialogue/fisher        un test
#   tests/run.sh fisher lab_clock       pareil, par leur nom seul
#   tests/run.sh doors                  tout un dossier
#   tests/run.sh doors/cave             tous ceux dont le chemin commence ainsi
#   tests/run.sh audit                  l'audit d'accessibilite des cartes fermees
#   tests/run.sh --list                 la liste
#   tests/run.sh                        tout (long : a eviter)
#
# Ne lancer que les tests de ce qu'on vient de toucher.
# Chaque test ouvre une fenetre Godot : il lui faut un ecran.

cd "$(dirname "$0")/.." || exit 1
GODOT="${GODOT:-/Users/godart/Downloads/Godot.app/Contents/MacOS/Godot}"
LOGS="${TMPDIR:-/tmp}/pokeludoworld-tests"
mkdir -p "$LOGS"

all_tests() {
  find tests -mindepth 2 -name '*.gd' -not -path 'tests/audit/*' | sed 's|^tests/||; s|\.gd$||' | sort
}

if [ "$1" = "--list" ]; then all_tests; echo audit; exit 0; fi

# La fenetre de jeu ignore SIGTERM : on filtre sur l'executable et on tue net.
kill_godot() {
  for pid in $(ps -axo pid,command | awk '$2 ~ /MacOS\/Godot$/ {print $1}'); do kill -9 "$pid" 2>/dev/null; done
}

# run_script <script res://> <log> <motif de fin> <secondes max>
run_script() {
  kill_godot
  ("$GODOT" --path "$PWD" --script "$1" > "$2" 2>&1 &)
  local ticks=0
  while [ "$ticks" -lt $(($4 * 2)) ]; do
    sleep 0.5; ticks=$((ticks + 1))
    grep -q "$3" "$2" 2>/dev/null && break
  done
  kill_godot
}

# Un argument designe un test (chemin ou nom seul), un dossier, ou un debut de chemin.
names=()
if [ $# -eq 0 ]; then
  names=(audit)
  while read -r t; do names+=("$t"); done < <(all_tests)
else
  for arg in "$@"; do
    if [ "$arg" = "audit" ]; then names+=(audit); continue; fi
    found=0
    while read -r t; do
      case "$t" in
        "$arg"|"$arg"/*|"$arg"*) names+=("$t"); found=1 ;;
        */"$arg") names+=("$t"); found=1 ;;
      esac
    done < <(all_tests)
    [ "$found" -eq 0 ] && { echo "$arg : test inconnu (tests/run.sh --list)"; exit 1; }
  done
fi

"$GODOT" --headless --path "$PWD" --import > "$LOGS/import.log" 2>&1
errors=$(grep -cE "ERROR|SCRIPT ERROR" "$LOGS/import.log")
[ "$errors" -ne 0 ] && { echo "IMPORT : $errors erreur(s), voir $LOGS/import.log"; exit 1; }

failed=0
for name in "${names[@]}"; do
  log="$LOGS/$(echo "$name" | tr '/' '_').log"
  began=$(date +%s)
  if [ "$name" = "audit" ]; then
    run_script res://tests/audit/audit.gd "$log" "^FIN" 90
    result=$(python3 tests/audit/audit.py "$log" | tee "$LOGS/audit.txt" | grep -E "!!|SOLIDE|BUTE|^AUDIT")
    echo "$result" | sed 's/^/  /'
    echo "$result" | grep -q "TOUT EST BON" || failed=1
    continue
  fi
  run_script "res://tests/$name.gd" "$log" "^RESULTAT" 120
  grep -E "^FAIL|SCRIPT ERROR" "$log" | sed 's/^/  /'
  ok=$(grep -c "^OK" "$log"); ko=$(grep -c "^FAIL" "$log"); took=$(( $(date +%s) - began ))
  # Une erreur de script arrete le test avant ses controles : ce n'est pas un succes.
  if grep -q "SCRIPT ERROR" "$log" || ! grep -q "^RESULTAT" "$log"; then
    echo "$name : ERREUR, le test ne s'est pas termine — $log"; failed=1
  elif grep -q "TOUT PASSE" "$log"; then
    echo "$name : $ok controles, tous bons (${took} s)"
  else
    echo "$name : ECHEC ($ok bons, $ko en echec) — $log"; failed=1
  fi
done
exit $failed
