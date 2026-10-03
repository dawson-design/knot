# Recording a change to canon

How the canon skill writes a change: a new fact, a moved point, a new character, a changed want. The change lands in canon first. The lower layers follow later, through their own skills.

## Who decided it

Every change has an origin, and the origin sets its status.

| Origin | How it's written |
|---|---|
| The user states the change, or approves a proposed entry by name | Approved: no `status`, no `[proposed]` mark |
| A skill or agent needs a fact canon lacks, for instance while planning a beat | Proposed: `status = "proposed"` in a ledger; a `[proposed]` mark and a Proposed line in prose |
| A skill or agent wants an approved entry changed or removed | Not written. Put it to the user first |

Approval is explicit. "Looks good" about a whole draft doesn't approve the proposed entries in it unless the user says so. When unsure, ask which entries the user approves.

A proposed entry stays editable while it is proposed. Log each revision like any other change.

## Steps

### 1. State the change

Write one sentence in story terms, with the point: "The rival learns the secret at p1, not p2." Name the ids it touches.

### 2. Find every affected canon file

A change rarely touches one file. Grep the canon folder for each id, and for the names and key nouns the change involves: prose names a fact more often than it cites its id. Then work through this table.

| The change | Check these |
|---|---|
| A character's want or turn | `cast.md` (Want, By point, Turn); `timeline.md` if the turn is public |
| Who knows a fact, or from when | `knowledge.toml` `knows`; `cast.md` (Secret, By point); `timeline.md` (Hidden) |
| When a fact becomes true, or its reveal | `knowledge.toml`; `timeline.md` (Public, Hidden); the `innocent` readings in `clues.toml`; `[review.cold_read]` in `knot.toml` |
| A clue | `clues.toml`; the deductions it proves in `knowledge.toml`; `[review.solver]` |
| A deduction | `knowledge.toml`; every clue that proves it; `[review.solver]` |
| Game state | `state.toml`; `conventions.md` if it needs a new kind. `globals.ink` belongs to the ink skill |
| A new character | `cast.md`: a `## <id>` heading with the fields in contract §3. The voice card belongs to the voice skill |
| A point added, removed, or renamed | `[timeline]` in `knot.toml`, the headings in `timeline.md`, every point in every ledger and in front matter, and `[review]`. Confirm the whole list with the user first |
| A project extra | the extra file, and any truth source that states the same fact |

### 3. Edit

- Keep the shapes in contract §3 and §4. Ids match `^[a-z][a-z0-9_]*$`, and every point is a name from `points`.
- Keep ids stable. If an id must change, every reference to it is part of the change.
- A ledger entry the change creates carries `status = "proposed"` unless the user decided it.
- In prose, mark each proposed fact `[proposed]` where it appears. List it under `## Proposed` at the end of the file, one dated line each. Add the section if the file has none.
- Edit canon, and `[review]` in `knot.toml` when the change requires it. Edit nothing below canon.

A proposed fact in prose looks like this:

```markdown
- **Family:** a sibling who writes each season [proposed]

## Proposed

- 2026-10-03: the mentor's sibling. From the scene skill, drafting office_p1_first_day.
```

### 4. Add the changelog line

Append one line to `changelog.md`, newest last:

```markdown
- 2026-10-03: The rival learns the secret at p1, not p2. Files: canon/knowledge.toml, canon/cast.md, canon/timeline.md, spine/spine.md, treatment/p2.md, beats/depot_p2_audit.md.
```

- The date is today's, as `YYYY-MM-DD`.
- One sentence says what is now true. Add why only when the user gave a reason worth keeping.
- `Files:` lists every file the change touched, then every lower-layer file it now contradicts. Paths are relative to the story root, as in the contract's example. A truth source outside the root is given relative to `project_dir`.
- A proposed change starts its sentence with "Proposed:".

### 5. Sweep the lower layers

Grep the config's `spine`, `treatment`, `beats`, `scenes`, and `ink` paths for:
- every id the change touched: fact, deduction, clue, state, and cast ids;
- the names and plain words the fact goes by in prose.

Read each hit in context. A hit contradicts canon when the draft states, assumes, or acts on the old version. List each one with its place and the conflict:

```markdown
- `story/treatment/p2.md` ## Wants and turns: the rival's turn comes from the receipt at p2. Canon now has the rival knowing at p1.
```

Don't fix them. Each belongs to the skill that owns its layer. A contradicted draft with `status = "approved"` needs the user's attention: say so, and leave its status alone.

### 6. Run the check

Run `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/knot.py" check`. Fix every error your edit caused, and report any new warning. Report errors that were there before; don't fix them silently.

### 7. Report

- the changelog line
- the files edited, with the entries in each
- every proposed entry, by file and id
- the contradiction list, grouped by layer
- the check result

## Worked example

The user decides the rival learns the secret at p1, not p2.

1. **The change:** `secret` is known to `rival` from p1. Ids: `secret`, `rival`.
2. **Canon files:**
   - `knowledge.toml facts.secret`: the rival's `knows` entry gets `from = "p1"`.
   - `cast.md ## rival`: **Secret** says "from p2 the rival knows".
   - `timeline.md`: the line about the rival and the receipt moves from `## p2` Hidden to `## p1` Hidden.
3. **Knock-on questions for the user,** before writing:
   - The rival's `via` is "the receipt", but `clues.toml clues.c_receipt` is planted at p2. How does the rival learn at p1?
   - The rival's p1 want may not survive knowing. Does it change?
4. **The changelog line:** the example in step 4 above.
5. **The sweep** finds `spine/spine.md ## p2: the audit`, `treatment/p2.md` (What happens, Wants and turns), and `beats/depot_p2_audit.md` (Purpose). Each has the rival learn the secret at p2.
6. **The check** should run clean: p1 is a valid point, and no rule code covers when a `knows` entry starts.
