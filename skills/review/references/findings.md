# Findings

The shape of a review's output: severity, the finding format, ranking, and the report file. One finding per problem, ranked most severe first.

## Severity

| Severity | Meaning | Examples |
|---|---|---|
| **blocker** | The draft can't pass its gate | a failing check; a contradiction of approved canon or of the layer above; a secret that reaches the player before its reveal; a required clue with no working route; a project rule broken in what the player sees |
| **should fix** | A real problem a reader or player would hit, though the draft still stands | an action that only serves the plot; a funnel; a failed check that leads nowhere; a slip of voice; an innocent reading a careful reader sees through |
| **note** | Worth knowing; no change required | a draft resting on a proposed entry; a gap in canon to fill; a route that works but is thin; a question for the user |

When unsure between two severities, pick the higher, and say why in the problem.

## A finding

```markdown
### 1. The mentor names the secret at p2

- **Severity:** blocker
- **Lens:** reveal, canon
- **Where:** `story/treatment/p2.md`, ## What happens, paragraph 2
- **Problem:** The mentor tells the player the secret aloud. That is `secret`, which reveals at p3 (`story/canon/knowledge.toml facts.secret`), and canon gives the player no `knows` entry for it.
- **Suggested fix:** cut the line and let the mentor deflect instead. The player sees the mentor avoid the question, and the receipt still reads as a quiet season.
```

- **Severity:** blocker, should fix, or note.
- **Lens:** the generic lens id or the project rule id. When several lenses found the same problem, list them all, the most specific first.
- **Where:** the path relative to `project_dir`, then the `## ` section, field, line, or Ink knot and stitch. A problem in several places lists every place.
- **Problem:** one or two sentences. Cite the entry or section it breaks, by file and entry, as the canon skill cites (`${CLAUDE_PLUGIN_ROOT}/skills/canon/references/as-of.md`).
- **Suggested fix:** one or two sentences. If the fix needs a canon change, say so and name the canon skill. Suggest the fix; don't write the replacement.

## `knot.py` issues as findings

| Source | Severity |
|---|---|
| A `[checks]` command exits non-zero | blocker |
| A `check` error (E1 to E13), or any issue under `--strict` | blocker |
| An `ink` error (I0 to I5) | blocker |
| W1: a required canon file doesn't exist yet | note |
| W2 to W9 | should fix |
| I6 to I8 | should fix |
| `Compile skipped: inklecate not found on PATH.` | note: the Ink wasn't compiled |

All of these use the lens id `checks`. Quote each issue line as `knot.py` printed it. Group issues with the same code into one finding, listing each entry.

## Ranking

1. Blockers, then should fix, then notes.
2. Within a severity, in story order: by the earliest point the finding touches, then by layer from spine down to Ink, then by file and position.
3. Number the findings in that order, so the user can answer "fix 1 to 4".

## De-duplication

- One problem is one finding, however many lenses caught it. Keep the highest severity, and list every lens.
- The same problem in several places is one finding, with every place listed.
- A cause and its symptoms are one finding. A wrong date in canon that three drafts repeat is one `canon` finding, with the three drafts listed under Where.

## The report file

- **Folder:** the config's `paths.reviews`, relative to `project_dir`. Create it if it doesn't exist.
- **Name:** `review-<target>-<YYYY-MM-DD>.md`, with today's date.
  - For one file, `<target>` is its stem: `review-depot_p2_audit-2026-10-03.md`, `review-spine-2026-10-03.md`.
  - For a batch, it is the layer and the points: `review-beats-p2-2026-10-03.md`, `review-treatment-p1-p2-2026-10-03.md`.
  - A single-lens review the user asked for adds the lens after the target: `review-p2-reveal-2026-10-03.md`.
  - Fresh-reader tests run on their own write `cold-read-<YYYY-MM-DD>.md` or `solver-<YYYY-MM-DD>.md`. When they run as part of a review, they go in its report.
  - If the name is taken, add `-2`, then `-3`.

## Report layout

```markdown
# Review: <target>

- **Date:** <YYYY-MM-DD>
- **Target:** <files>; <layer>; points <points>
- **Lenses:** <ids run>, in sequence or fanned out
- **Checks:** <each command and its result>; `knot.py check`: <n> errors, <n> warnings
- **Result:** <n> blockers, <n> should fix, <n> notes

<One or two sentences on what holds: the lenses that found nothing, and what the draft does well.>

## Findings

### 1. <short title>

...

## Fresh-reader tests

<Only when run: per fresh-readers.md.>

## Not checked

<Each lens or test skipped, and why. For example: "fair_play: no clues.toml".>
```

The report names the secrets it checks. It is for the writers and the user, never for a fresh reader.
