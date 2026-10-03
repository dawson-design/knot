# The knot project contract

This is the contract between a game's story files and the knot plugin. The skills (`skills/*/SKILL.md`) and the script (`scripts/knot.py`) both read projects through it. Change this document before changing either.

A project is a repo with a `knot.toml` at its root. The skills find it by walking up from the working directory, as git finds `.git`. The examples in the reference use one placeholder project, called Example. §8 sketches a larger project.

## 1. Layout

Everything lives under the story root (`[project] root`). The names are fixed.

```
<root>/
  canon/
    cast.md           required: one "## <id>" per character
    timeline.md       required: one "## <point>" per story point
    changelog.md      required: dated lines, newest last
    voices.md         voice cards (the voice skill)
    conventions.md    the project's Ink tags, state kinds, and naming
    knowledge.toml    optional ledger: facts, secrets, deductions
    clues.toml        optional ledger: clues, plants, finds
    state.toml        optional ledger: game state, mirrors globals.ink
    *.md              any other file is a project extra, read when relevant
  spine/              the whole story on a page per unit (the story skill)
  treatment/          one file per unit, plus any subfolders (the story skill)
  beats/              index.md, then one beat sheet per scene: <id>.md (the beats skill)
  scenes/             full prose of key scenes: <id>.md (the scene skill)
  ink/                the .ink files (the ink skill); the folder name is set in [ink]
```

The layers run top-down: spine, treatment, beats, scenes, ink. A lower layer never contradicts a higher one. When a lower layer needs a fact changed, the canon skill changes canon first and logs it.

A required canon file that doesn't exist yet is a warning, not an error. Projects adopt knot before their canon is written.

## 2. `knot.toml`

```toml
[project]
name = "Example"                  # required
root = "story"                    # required: the story root, relative to knot.toml
truth = ["story/canon/"]          # sources of truth, highest first. Default: [<root>/canon/]
templates = ""                    # optional folder of template overrides (see §6)
reviews = "story/reviews"         # where review findings go. Default: <root>/reviews

[timeline]
points = ["p1", "p2", "p3"]       # required: story points in play order

[ids]
# Optional extra id sources for "who" fields, beyond the cast.md headings.
# Each names a TOML file and a table; that table's keys become valid ids.
extra = []

[clues]
min_routes = 2                    # finds a required clue needs. Default: 2

[ink]
dir = "ink"                       # under root. Default: "ink"
main = "main.ink"                 # default: "main.ink"
globals = "globals.ink"           # default: "globals.ink"
knot = "^(office|depot)_{point}_[a-z0-9_]+$"   # scene knot names; {point} matches any point
tags = ["speaker", "check", "voice"]           # tag names the project allows

[checks]
commands = []                     # the project's own checks, run before a review

[review.cold_read]
before = "p3"                     # include material from points before this one
layers = ["treatment"]            # which layers to include
sections = ["What happens"]       # which "## " sections to keep; empty keeps the whole body
must_not_predict = "that the mentor covered up the secret"

[review.solver]
must_prove = ["d_secret", "d_cover"]   # deduction ids
must_not_prove = ["d_ordered"]          # deduction ids

[[rules]]
id = "no_villains"                # required: lowercase, digits, underscores
ask = "Does anyone act from malice rather than from a want they could explain?"   # required
see = ["story/canon/cast.md"]     # optional pointers for the reviewer
```

**Rules for the file:**
- Points are unique and match `^[a-z][a-z0-9_]*$`.
- Every point named anywhere in the project (ledgers, front matter, `[review]`) is one of `[timeline] points`.
- `[ink] knot` is a regular expression. `{point}` expands to an alternation of every point.
- Rule ids are unique. A rule's `ask` is phrased so that "yes" is a finding.
- `[checks] commands` run from the project root, in order. A non-zero exit is a review blocker.
- `[review.cold_read]` and `[review.solver]` are optional. Without them, review skips those tests. When present, `cold_read` needs `before`, `layers`, and `must_not_predict` (`sections` defaults to all), and `solver` needs `must_prove` (`must_not_prove` defaults to none). Cold-read `layers` are `treatment`, `beats`, or `scenes`; the spine has no points to filter by. A deduction can't be in both `must_prove` and `must_not_prove`.
- `root` and `[ink] dir` are relative paths. When `[ink] knot` or `[ink] tags` is unset, the checks that use it are skipped.
- Unknown keys are warnings, so a typo is caught without breaking the project.

## 3. Canon prose files

**`cast.md`.** One `## <id>` heading per character, and nothing else on the heading line. The id matches `^[a-z][a-z0-9_]*$`. Names, which change, go in the body. The body covers, for each character: their want by point, their secret, their turns, and a link to their voice card. The player gets an entry too, with the id `player`.

```markdown
## mentor

- **Name:** the name the player sees, which may change
- **Want:** to keep the secret hidden
- **Secret:** `secret`
- **By point:**
  - p1: wants the player to be useful and incurious
```

**`timeline.md`.** One `## <point>` heading per point, in order. Under each: what happens, what's public, and what's hidden.

**`changelog.md`.** One line per change, newest last:

```markdown
- 2026-10-03: The rival learns the secret at p2, not p3. Files: canon/knowledge.toml, treatment/p2.md.
```

**`voices.md`.** Voice cards. The voice skill defines their shape.

**`conventions.md`.** The project's choices that knot leaves open: Ink tag meanings, state kinds, stitch naming, file layout under `ink/`, and any scene-format extensions.

## 4. Ledgers

The ledgers are TOML so `knot.py check` can read them. Each entry may carry `status = "proposed"`. An entry without a status is approved canon. Only the user approves a proposed entry, at a gate.

Ids in every ledger match `^[a-z][a-z0-9_]*$`.

### `knowledge.toml`

```toml
[facts.secret]
text = "What the mentor hides."
true_from = "p1"              # required: first point the fact holds
reveal = "p3"                 # optional: makes it a secret. The player can't learn it before this point
knows = [
  { who = "mentor", from = "p1" },
  { who = "rival", from = "p2", via = "the receipt" },
]

[deductions.d_secret]
claim = "The mentor hid the secret."   # required
```

- A fact is something true in the story. `knows` lists who knows it and from when. `who` is a cast id or an `[ids] extra` id. Each `knows` entry needs `who` and `from`; `via` is optional.
- A fact with `reveal` is a secret. Before its reveal point, nothing the player sees may give it away, except clues planted with an innocent reading.
- A deduction is a claim the player can try to prove. Clues point at deductions.
- `reveal` can't precede `true_from`.

### `clues.toml`

```toml
[clues.c_record]
text = "A record with one entry removed."
proves = ["d_cover"]                 # deduction ids
required = true                      # the case depends on it; needs min_routes finds. Default: false
innocent = "The mentor says the page was damaged."
plant = { point = "p1", where = "the office" }
finds = [
  { point = "p3", how = "Compare the record with a second copy." },
  { point = "p3", how = "The rival points out the gap." },
]
```

- `text` is what the player sees or holds, in the player's terms. The solver test shows this field and nothing else.
- `proves` names deduction ids, never fact ids.
- `innocent` is how the clue reads on a first play. A clue planted before the reveal point of what it proves needs one.
- `plant.point` and every `finds[].point` are points. No find comes before the plant. `text` and `plant` are required; `proves`, `finds`, `where`, and `how` are optional.
- `where` is free text. A project with its own place ids uses them here.

### `state.toml`

```toml
[state.rel_mentor]
type = "int"                  # required: int | bool | string | list
kind = "relationship"         # required: a word from conventions.md
default = 0                   # required, of the given type
meaning = "How far the mentor trusts the player."   # required

[state.evidence]
type = "list"
kind = "evidence"
items = ["c_record", "c_receipt"]     # required for lists: the LIST's items
default = []                          # items switched on at the start
meaning = "What the player holds. Each item doubles as a key."
```

`state.toml` mirrors `globals.ink`. Every `VAR` and `LIST` there has an entry here, and every approved entry here is declared there. A beat sheet that needs a new variable adds it here as proposed.

## 5. Front matter

Beat sheets, treatments, and scenes start with a TOML block fenced by `+++` lines. It holds the fields a script reads; everything below it is Markdown.

**Beat sheet** (`beats/<id>.md`; the file name is the id):

```toml
+++
id = "office_p1_first_day"          # matches [ink] knot
point = "p1"
status = "draft"                    # draft | review | approved
plants = ["c_record"]               # clue ids planted here
finds = []                          # clue ids found here
reads = []                          # state names read here
sets = ["rel_mentor", "saw_record"]   # state names set here
pattern = ["foldback", "failed_check"]
+++
```

Patterns: `foldback`, `delayed_consequence`, `gate`, `failed_check`, `hard_split`. The beats skill's references define them.

**Treatment** (`treatment/**/*.md`):

```toml
+++
points = ["p1"]                     # every point the unit spans
status = "approved"                 # draft | review | approved
+++
```

**Scene** (`scenes/<id>.md`; the id matches a beat sheet):

```toml
+++
id = "office_p1_first_day"
point = "p1"
status = "draft"
+++
```

The spine has no front matter. Its status is a `**Status:** draft | review | approved` line under the title, which the skills read and `knot.py` doesn't.

`beats/index.md` has no front matter either. It is a table of scene id, point, status, and summary, in play order, where a scene can also be `planned` before its sheet exists. `knot.py` doesn't read it.

## 6. Templates

knot ships a default template for each layer. A project overrides one by putting a file with the same name in its `[project] templates` folder:

| Layer | File | knot's default |
|---|---|---|
| spine | `spine.md` | `skills/story/references/spine.md` |
| treatment | `treatment.md` | `skills/story/references/treatment.md` |
| beat sheet | `beat.md` | `skills/beats/references/beat.md` |
| scene | `scene.md` | `skills/scene/references/scene.md` |

An override keeps the front matter fields above. It may add sections.

## 7. `knot.py`

One script, standard library only, Python 3.11 or later. Skills run it as:

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/knot.py" <command> [--project DIR]
```

`--project` points at a folder holding `knot.toml`. Without it, the script walks up from the working directory.

**Exit codes:** 0 clean (warnings allowed), 1 errors found, 2 usage error or no `knot.toml`.

**Report format** (`check` and `ink`):

```
Errors (1):
  E7 clues.toml clues.c_record: proves unknown deduction "d_covered".
Warnings (1):
  W2 clues.toml clues.c_receipt: required clue has 1 find; min_routes is 2.
1 error(s), 1 warning(s).
```

Each issue names its rule code, its file, and the entry, so it can be fixed without searching. A clean run prints `No issues.`

### `config`

Prints the resolved configuration as JSON. Every skill runs it first and reads paths from it rather than guessing.

```json
{
  "project": "Example",
  "project_dir": "/abs/path/to/project",
  "plugin_root": "/abs/path/to/knot",
  "root": "story",
  "truth": ["story/canon/"],
  "points": ["p1", "p2", "p3"],
  "paths": {
    "canon": "story/canon", "spine": "story/spine", "treatment": "story/treatment",
    "beats": "story/beats", "scenes": "story/scenes", "ink": "story/ink", "reviews": "story/reviews"
  },
  "canon": {
    "cast": {"path": "story/canon/cast.md", "exists": true},
    "knowledge": {"path": "story/canon/knowledge.toml", "exists": true}
  },
  "templates": {
    "spine": "/abs/path/to/knot/skills/story/references/spine.md",
    "beat": "/abs/path/to/knot/skills/beats/references/beat.md"
  },
  "clues": {"min_routes": 2},
  "ink": {"dir": "story/ink", "main": "main.ink", "globals": "globals.ink", "knot": "^(office|depot)_{point}_[a-z0-9_]+$", "tags": ["speaker", "check", "voice"]},
  "checks": [],
  "rules": [{"id": "no_villains", "ask": "…", "see": ["story/canon/cast.md"]}],
  "review": {"cold_read": {}, "solver": {}}
}
```

`canon` lists every fixed canon file (cast, timeline, changelog, voices, conventions, knowledge, clues, state). `templates` lists all four layers. Project paths are relative to `project_dir`; plugin paths are absolute.

### `check [--strict]`

**Errors** (integrity, at every stage):

| Code | Rule |
|---|---|
| E1 | `knot.toml` is malformed TOML, misses a required key, or has a value of the wrong type; a regex is invalid; a path isn't relative; an `[ids] extra` source can't be read; or the `[review]` settings break §2's rules |
| E2 | A point is duplicated or badly formed, or a point named anywhere isn't in `[timeline] points` |
| E3 | A ledger file is malformed TOML, or an entry misses a required field or has the wrong type |
| E4 | An id is badly formed, or duplicated within its kind |
| E5 | A `cast.md` heading isn't an id, or a `timeline.md` heading isn't a point |
| E6 | A `who` names no cast id and no `[ids] extra` id |
| E7 | A clue `proves` an unknown deduction, or `[review.solver]` names one |
| E8 | A fact reveals before it's true, or a clue is found before it's planted |
| E9 | A state default doesn't fit its type, or a list default names an item the list lacks |
| E10 | A beat sheet, treatment, or scene has no front matter, or bad front matter |
| E11 | A beat or scene id doesn't match its file name, or a beat id doesn't match `[ink] knot` |
| E12 | A front-matter clue id isn't in `clues.toml`, or a state name isn't in `state.toml`, when that ledger exists |
| E13 | A scene id has no beat sheet |

**Warnings** (coverage; `--strict` makes them errors, for beat gates and story lock):

| Code | Rule |
|---|---|
| W1 | A required canon file doesn't exist yet |
| W2 | A required clue has fewer than `min_routes` finds in `clues.toml` |
| W3 | A clue planted before the reveal of a deduction it proves has no `innocent` reading |
| W4 | Beat sheets exist, and a clue is planted by none of them, or a required clue is found by none |
| W5 | A beat names clues or state and that ledger doesn't exist yet |
| W6 | Beat sheets exist, and a state entry is read or set by none of them |
| W7 | A beat's planted clue has a different `plant.point` from the beat's point |
| W8 | A beat names an unknown pattern |
| W9 | An unknown key in `knot.toml`, a ledger entry, or front matter |

"Before the reveal of a deduction" (W3) means: before the earliest `reveal` among facts. When no fact has a `reveal`, every clue that proves something needs an innocent reading. knot doesn't link facts to deductions, so W3 errs toward asking for one.

### `ink`

Reads every `.ink` file under the ink folder. When `state.toml` or one of its entries can't be read, `ink` reports that E3 instead of the I codes that depend on it.

| Code | Rule | Severity |
|---|---|---|
| I1 | A `VAR` or `LIST` declared outside the globals file | error |
| I2 | A globals `VAR` or `LIST` with no `state.toml` entry | error |
| I3 | An approved `state.toml` entry not declared in globals | error |
| I4 | A declaration's value or items don't match its `state.toml` type, default, or items | error |
| I5 | A tag name not in `[ink] tags` | error |
| I6 | A knot name that doesn't match `[ink] knot` (functions are exempt) | warning |
| I7 | A declared variable never mentioned outside the globals file | warning |
| I8 | A proposed `state.toml` entry not yet declared in globals | warning |

Then it compiles `main` with `inklecate` if it's on PATH, and reports the compiler's errors as `I0` errors. Without inklecate it prints `Compile skipped: inklecate not found on PATH.` and the exit code reflects the other checks only. Reads of undeclared variables are left to the compiler.

### `packet cold-read` and `packet solver [--key]`

Print the inputs for review's two fresh-reader tests, so nobody builds them by hand and leaks.

- **`cold-read`** prints, as Markdown, the chosen `sections` of every file in the chosen `layers` whose points all come before `before`. Files are ordered by their earliest point, then path, and labelled "Part 1", "Part 2", and so on, never by file name. Front matter and HTML comments are stripped.
- **`solver`** prints the `text` of every findable clue and the claims to weigh. A clue is findable when a beat sheet lists it in `finds`; while no beat sheet lists any finds, a clue with at least one ledger find counts. Claims are the `must_prove` and `must_not_prove` deductions together, sorted by id and labelled "Claim A", "Claim B", and so on. It never prints `proves`, `innocent`, `plant`, or which claims should hold.
- **`--key`** prints the answer key instead. For `cold-read`: which part is which file, and the `must_not_predict` text. For `solver`: which claim is which deduction id, and which claims must and must not be provable. Only the reviewer sees it.

Both exit 2 when their `[review]` table is missing, and 1, printing the issues, when `knot.toml` has E1 or E2 errors or the solver's deductions are unknown (E7).

## 8. A second example: a larger project

Example, the placeholder project above, keeps everything under one story root. A larger game often keeps its world data and templates beside the story, and runs tools of its own. This sketch is a game told in chapters, whose places and townspeople live in a separate world file.

```toml
[project]
name = "Saltmarsh"
root = "narrative"
truth = ["docs/design.md", "narrative/canon/", "narrative/world/places.toml"]
templates = "production/templates"
reviews = "production/reviews"

[timeline]
points = ["ch1", "ch2", "ch3", "ch4", "epilogue"]

[ids]
extra = [{ file = "narrative/world/places.toml", table = "people" }]

[ink]
knot = "^(quay|chapel|manor)_{point}_[a-z0-9_]+$"
tags = ["speaker", "portrait", "check", "voice", "sfx", "music"]

[checks]
commands = ["uv run tools/places.py check"]

[[rules]]
id = "world"
ask = "Does a scene use a place that doesn't exist in its chapter, or someone who can't be there?"
see = ["narrative/world/places.toml"]
```

knot doesn't read `places.toml` itself. `[ids] extra` lets townspeople from it appear in `knows` entries, `[checks]` runs the project's own tool on it, and the `world` rule asks the reviewer to check places against it.
