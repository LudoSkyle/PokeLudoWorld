"""Verifie chaque interieur : case d'arrivee libre, toutes les portes atteignables."""
import sys, collections

rooms, cur = {}, None
for line in open(sys.argv[1]):
    line = line.rstrip("\n")
    if line.startswith("ROOM "):
        cur = line[5:].strip()
        rooms[cur] = {"grid": [], "doors": []}
    elif line.startswith("GRID "):
        rooms[cur]["grid"].append(line[5:])
    elif line.startswith("DOOR "):
        n, x, y, ex, ey, qx, qy = line[5:].split()
        rooms[cur]["doors"].append((n, int(x), int(y), int(ex), int(ey), int(qx), int(qy)))

ok = True
for name, r in rooms.items():
    g = r["grid"]
    free = lambda x, y: 0 <= y < len(g) and 0 <= x < len(g[0]) and g[y][x] == "."
    print("=== %s ===" % name)
    for row in g:
        print("   " + row)
    arrivals = {}
    for n, x, y, ex, ey, qx, qy in r["doors"]:
        is_exit = (qx, qy) != (0, 0)
        ax, ay = (x, y) if is_exit else (x + ex, y + ey)
        arrivals[n] = (ax, ay)
        state = []
        if is_exit and free(x + qx, y + qy):
            state.append("LA SORTIE NE BUTE SUR RIEN"); ok = False
        if not free(x, y):
            state.append("PORTE SUR CASE SOLIDE"); ok = False
        if not free(ax, ay):
            state.append("ARRIVEE SUR CASE SOLIDE"); ok = False
        print("   porte %-11s case (%d,%d)  arrivee (%d,%d)  %-7s %s"
              % (n, x, y, ax, ay, "sortie" if is_exit else "contact", " / ".join(state) or "ok"))
    # depuis chaque arrivee, toutes les portes doivent etre atteignables
    for n, start in arrivals.items():
        if not free(*start):
            continue
        seen, todo = {start}, collections.deque([start])
        while todo:
            cx, cy = todo.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = cx + dx, cy + dy
                if free(nx, ny) and (nx, ny) not in seen:
                    seen.add((nx, ny)); todo.append((nx, ny))
        # une carte peut etre faite de boyaux separes (sous-sol de grotte) :
        # chaque porte doit mener a au moins une AUTRE porte, pas a toutes
        others = [m for m, x, y, ex, ey, qx, qy in r["doors"] if m != n and (x, y) in seen]
        if len(r["doors"]) > 1 and not others:
            print("   !! depuis %s, aucune autre porte n'est accessible" % n); ok = False
        # aucune fuite : une case libre ne doit jamais toucher le bord de la grille
        doors_at = {(d[1], d[2]) for d in r["doors"]}
        leak = [c for c in seen if (c[0] in (0, len(g[0]) - 1) or c[1] in (0, len(g) - 1)) and c not in doors_at]
        if leak:
            print("   !! fuite vers le bord depuis %s : %s" % (n, leak[:3])); ok = False
    print("   cases accessibles depuis l'entree : %d" % len(seen))
print()
print("AUDIT : %s" % ("TOUT EST BON" if ok else "DES DEFAUTS RESTENT"))
