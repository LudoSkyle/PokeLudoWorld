# Commits, branches et PRs

## Format

```
type(scope): message à l'impératif
```

**Les titres de commit sont en anglais**, même si les échanges et la
documentation sont en français. Scope en minuscules, pas de point final.

| Type | Pour quoi | Exemple |
|---|---|---|
| `feat` | gameplay, nouvelle mécanique | `feat(combat): add dodge with invulnerability window` |
| `fix` | correction de bug | `fix(physics): stop the player clipping through sloped walls` |
| `art` | assets graphiques, atlas, sprites | `art(character): import the hero run animations` |
| `level` | contenu de map, level design | `level(forest): add save points before the boss` |
| `balance` | équilibrage de valeurs | `balance(weapons): cut plasma rifle fire rate by 15%` |
| `audio` | sons et musique | `audio(ui): add a confirm sound to the pause menu` |
| `perf` | optimisation | `perf(rendering): enable frustum culling on vegetation` |
| `refactor` | réorganisation sans changement de comportement | `refactor(scripts): extract logging into its own package` |
| `docs` | documentation | `docs(project): add CLAUDE.md and contributor guides` |
| `chore` | outillage, config, ignore | `chore(repo): ignore macOS metadata files` |

Scopes courants : `tileset`, `start-town`, `scripts`, `project`, `repo`,
`rendering`, `ui`. Un scope par commit — s'il en faut deux, c'est deux commits.

## Séparer le code et les assets lourds

**Un commit ne mélange jamais des scripts et des fichiers binaires.** Une
texture ou un atlas part dans son propre commit `art(...)`, pour qu'un revert
sur du code ne rejoue pas des centaines de kilo-octets de binaire, et
inversement.

Un fichier `.import` est l'exception qui confirme la règle : il voyage **avec**
son asset, puisqu'il porte son UID.

## Branches et PRs

- `main` reste stable. **On travaille sur `develop`**, qui est la cible des PRs.
- Une branche par PR, nommée `type/sujet-court` : `art/environments-atlas`,
  `level/start-town`, `fix/tree-sorting`.
- **Une PR = un commit.** Plus simple à relire, et le titre de la PR est celui
  du commit. Beaucoup de petites PRs vaut mieux qu'une grosse.
- Quand des PRs dépendent les unes des autres, les empiler : chaque branche part
  de la précédente et la PR cible la précédente. GitHub recible
  automatiquement sur `develop` au fur et à mesure des merges, donc **il faut
  les fusionner dans l'ordre**.

## Ce qu'on ne commite pas

`.godot/`, `.DS_Store`, les dossiers de build, `.idea` — voir `.gitignore`. Si
un de ces fichiers apparaît dans un `git status`, c'est le `.gitignore` qu'on
corrige, pas le fichier qu'on supprime à la main.
