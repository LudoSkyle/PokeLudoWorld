#!/usr/bin/env python3
"""Compte, calque par calque, les cases qui diffèrent entre deux cartes.

    python3 tools/mapgen/compare.py <scène d'origine.tscn> <scène refaite.tscn>

Une case compte dès que sa tuile, ou sa variante (avec ou sans collision), n'est pas la même. Sort en erreur s'il en
reste une : c'est le contrôle qui dit si le constructeur sait refaire une carte **sans faute**.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene_to_plan import layers  # noqa: E402

if __name__ == '__main__':
    if len(sys.argv) != 3: sys.exit(__doc__)
    a = {name: cells for name, _, cells in layers(sys.argv[1])}
    b = {name: cells for name, _, cells in layers(sys.argv[2])}
    total = 0
    for name in list(a) + [n for n in b if n not in a]:
        one, two = a.get(name, {}), b.get(name, {})
        if not one and not two: continue
        diff = sorted(c for c in set(one) | set(two) if one.get(c) != two.get(c))
        total += len(diff)
        print('%-12s %5d cases, %4d écarts%s' % (name, len(one), len(diff), ('  ex. %s : %s -> %s' % (diff[0], one.get(diff[0]), two.get(diff[0]))) if diff else ''))
    order_a, order_b = [n for n, _, c in layers(sys.argv[1]) if c], [n for n, _, c in layers(sys.argv[2]) if c]
    print('ordre des calques : %s' % ('le même' if order_a == order_b else '%s\n            contre : %s' % (order_a, order_b)))
    print('%d cases diffèrent' % total)
    sys.exit(1 if total or order_a != order_b else 0)
