"""Verifie que chaque texte affiche par le jeu a sa traduction dans locale/*.po.

Les textes sont ecrits en francais dans les scenes et le code ; on les releve
ici et on cherche chacun parmi les msgid. Usage : tests/run.sh i18n
"""
import glob, re, sys

ROOT = "src/main/kotlin/fr/skyle/pokeludoworld/"
# Libelles qui se lisent pareil dans toutes les langues.
SAME = re.compile(r"^(x[0-9.]+|Français|English|Options|Debug|[0-9:]+|)$")


def boxes(text):
    return [part.strip() for part in text.split("|") if part.strip()]


def sources():
    found = {}

    def add(text, where):
        for box in boxes(text):
            # "@give:objet " en tete d'une boite est une consigne, pas du texte.
            box = re.sub(r"^@give:\w+(\*\d+)? ", "", box)
            if not SAME.match(box):
                found.setdefault(box, where)

    for path in sorted(glob.glob(ROOT + "scenes/**/*.tscn", recursive=True)):
        body = open(path, encoding="utf-8").read()
        for text in re.findall(r'^text = "((?:[^"\\]|\\.)*)"$', body, re.M):
            add(text.replace('\\"', '"').replace("\\n", "\n"), path)
        # Textes selon l'histoire : "drapeau > texte", le drapeau n'est pas du texte.
        for states in re.findall(r"^states = PackedStringArray\((.*)\)$", body, re.M):
            for text in re.findall(r'"((?:[^"\\]|\\.)*)"', states):
                add(re.sub(r"^\s*\w+\s*>", "", text).replace('\\"', '"').replace("\\n", "\n"), path)
        for text in re.findall(r'^metadata/location = "(.*)"$', body, re.M):
            add(text, path)

    for path in sorted(glob.glob(ROOT + "scripts/**/*.kt", recursive=True)):
        body = open(path, encoding="utf-8").read()
        for text in re.findall(r'\b[TN]\("((?:[^"\\]|\\.)*)"\)', body):
            add(text.replace("\\n", "\n"), path)
        # Listes de textes dits tels quels par la boite de dialogue.
        for block in re.findall(r"// i18n\n(.*?)\n\t\t\)", body, re.S):
            for text in re.findall(r'"((?:[^"\\]|\\.)*)"', block):
                add(text, path)
    return found


def msgids(path):
    ids, current, target = {}, None, None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        m = re.match(r'^(msgid|msgstr) "(.*)"$', line)
        if m:
            target = m.group(1)
            if target == "msgid":
                current = [m.group(2), ""]
                ids_key = None
            else:
                current[1] = m.group(2)
        elif line.startswith('"') and current is not None:
            current[0 if target == "msgid" else 1] += line[1:-1]
        if current is not None and (line == "" or target == "msgstr"):
            ids[current[0].replace("\\n", "\n").replace('\\"', '"')] = current[1]
    return ids


def main():
    wanted = sources()
    ok = True
    for po in sorted(glob.glob("locale/*.po")):
        known = msgids(po)
        missing = [t for t in wanted if not known.get(t)]
        unused = [t for t in known if t and t not in wanted]
        print("%s : %d textes, %d traduits" % (po, len(wanted), len(wanted) - len(missing)))
        for text in missing:
            ok = False
            print("  !! sans traduction : %r  (%s)" % (text, wanted[text].replace(ROOT, "")))
        for text in unused:
            print("  -- traduction qui ne sert plus : %r" % text)
    print("I18N : TOUT EST TRADUIT" if ok else "I18N : IL MANQUE DES TRADUCTIONS")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
