#!/bin/bash
# Lance les tests joues au clavier.
#
#   tests/run.sh                 tous les tests
#   tests/run.sh cave lab        seulement ceux-la  (tests/test_<nom>.gd)
#   tests/run.sh audit           l'audit d'accessibilite des cartes fermees
#
# Ne relancer que les tests des zones touchees par la modification.
# Chaque test ouvre une fenetre Godot : il lui faut un ecran.

cd "$(dirname "$0")/.." || exit 1
GODOT="${GODOT:-/Users/godart/Downloads/Godot.app/Contents/MacOS/Godot}"
LOGS="${TMPDIR:-/tmp}/pokeludoworld-tests"
mkdir -p "$LOGS"

# La fenetre de jeu ignore SIGTERM : on filtre sur l'executable et on tue net.
kill_godot() {
  for pid in $(ps -axo pid,command | awk '$2 ~ /MacOS\/Godot$/ {print $1}'); do kill -9 "$pid" 2>/dev/null; done
}

# run_script <script res://> <log> <motif de fin> <secondes max>
run_script() {
  kill_godot
  ("$GODOT" --path "$PWD" --script "$1" > "$2" 2>&1 &)
  local waited=0
  while [ "$waited" -lt "$4" ]; do
    sleep 2; waited=$((waited + 2))
    grep -q "$3" "$2" 2>/dev/null && break
  done
  kill_godot
}

names=("$@")
if [ ${#names[@]} -eq 0 ]; then
  names=(audit)
  for f in tests/test_*.gd; do n="${f#tests/test_}"; names+=("${n%.gd}"); done
fi

"$GODOT" --headless --path "$PWD" --import > "$LOGS/import.log" 2>&1
errors=$(grep -cE "ERROR|SCRIPT ERROR" "$LOGS/import.log")
[ "$errors" -ne 0 ] && { echo "IMPORT : $errors erreur(s), voir $LOGS/import.log"; exit 1; }

failed=0
for name in "${names[@]}"; do
  log="$LOGS/$name.log"
  if [ "$name" = "audit" ]; then
    run_script res://tests/audit.gd "$log" "^FIN" 90
    result=$(python3 tests/audit.py "$log" | tee "$LOGS/audit.txt" | grep -E "!!|SOLIDE|BUTE|^AUDIT")
    echo "$result" | sed 's/^/  /'
    echo "$result" | grep -q "TOUT EST BON" || failed=1
    continue
  fi
  [ -f "tests/test_$name.gd" ] || { echo "$name : test inconnu"; failed=1; continue; }
  run_script "res://tests/test_$name.gd" "$log" "^RESULTAT" 240
  grep -E "^FAIL|SCRIPT ERROR" "$log" | sed 's/^/  /'
  ok=$(grep -c "^OK" "$log"); ko=$(grep -c "^FAIL" "$log")
  if grep -q "TOUT PASSE" "$log"; then
    echo "$name : $ok controles, tous bons"
  else
    echo "$name : ECHEC ($ok bons, $ko en echec) — $log"; failed=1
  fi
done
exit $failed
