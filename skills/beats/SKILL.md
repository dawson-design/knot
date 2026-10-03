---
name: beats
description: "Plans the scenes of a branching game: the scene index (beats/index.md) and one beat sheet per scene, with TOML front matter for clues planted and found, state read and set, and branching patterns, plus each character's want, the player's choices and their costs, skill checks, variants, and consequences. Use to plan, break down, or revise the beats or scenes of a story point or an approved treatment in a project with a knot.toml. Plans scenes; never writes their prose or Ink."
---

# Beats

## Iron Law

`NO BEAT SHEET WITHOUT AN APPROVED TREATMENT. EVERY ACTION TRACES TO A WANT, AND EVERY CHOICE COSTS.`

This skill cuts an approved treatment into scenes and plans each one. It keeps the scene index, `beats/index.md`, and writes one beat sheet per scene, `beats/<id>.md`. A beat sheet says who is present and what each one wants, what the player can choose and what each choice costs, the checks and what failure reveals, the variants, and what pays off later. Its front matter lists the clues planted and found, the state read and set, and the branching patterns, so `knot.py check` can test the sheets against the clue and state ledgers. The sheet plans the scene; the scene and ink skills write it.

## Before you start

1. Run `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/knot.py" config` and read every path from its JSON. Exit code 2 means there's no `knot.toml`: stop, and offer to draft one with the canon skill's setup procedure in `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/setup.md`.
2. Read the `rules` list from the config. Every beat sheet answers each rule's `ask` in its "Rule checks" field.
3. Find the treatment the scenes come from: a file under `paths.treatment` whose `points` include the point. When several do, such as a main unit and a side strand, take the one the scenes belong to. Read its front matter `status`. If it isn't `approved`, stop. Name the file and its status, and offer the story skill. Go on only if the user overrides in so many words.
4. Read canon as of the point, following the canon skill's `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/as-of.md`: each character's want "By point" in `cast.md`, the facts and who knows them, and the ledgers `clues.toml` and `state.toml` when they exist. Read `conventions.md` for the project's state kinds and naming.
5. Read `beats/index.md` and the beat sheets for this point and the points either side, so the new sheets read and set state the others expect.
6. Load the beat template from the config's `templates.beat`. A project's override may add fields. The front matter follows contract §5 whatever the template holds.
7. Read `${CLAUDE_PLUGIN_ROOT}/skills/beats/references/patterns.md` and `${CLAUDE_PLUGIN_ROOT}/skills/beats/references/index.md`.

## Workflow

1. **Cut the scenes.** To revise one existing sheet, skip to step 4. Otherwise split the treatment's "What happens" into scenes: one place, one stretch of time, one Ink knot each. Every option in "The player's options" and every clue in "Clues" lands in a scene. Give each scene an id that matches `[ink] knot` and the naming in `conventions.md`.
2. **Update the index.** Add a `planned` row per scene to `beats/index.md`, in play order. When you cut a whole unit, show the user the list before writing the sheets.
3. **Start each sheet.** Copy the template to `beats/<id>.md`. Set `id` to the file name, `point`, and `status = "draft"`.
4. **Fill the fields in order.** Take each character's want from `cast.md` for this point and narrow it to the scene. Give two to four choices, each with its cost now or later. Give every skill check a failure that reveals something.
5. **Name the patterns.** Pick from `patterns.md`. The front matter `pattern` and the "Branching pattern" field name the same ones.
6. **Name the state.** Use names from `state.toml`. When the beat needs state that doesn't exist, add an entry with `status = "proposed"`: its `type`, a `kind` from `conventions.md`, a `default`, and its `meaning`. List it under "Proposed".
7. **Place the clues.** Use ids from `clues.toml`. A plant's `plant.point` is this beat's point. A find matches an entry in the clue's `finds` at this point. When the beat needs a new clue, add it to `clues.toml` with `status = "proposed"`, with its `text`, `proves`, `innocent`, `plant`, and `finds`. List it under "Proposed".
8. **Log ledger changes.** Every entry you add follows the canon skill's `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/changes.md`, changelog line included. Never edit an approved ledger entry here. That is a canon change; send it to the canon skill.
9. **Answer each rule.** Under "Rule checks", one line per project rule: its id, the answer, and why. Fix the beat when an answer is a finding.
10. **Check the sheet against the rules below.** Then set the sheet's row in `beats/index.md`: its status and a one-line summary.
11. **Run the check.** Run `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/knot.py" check`. Fix every error. While the story is only partly beaten, coverage warnings are expected: W4 (a clue no beat plants or finds) and W6 (state no beat reads or sets). Name the warnings you leave and why. At a beat gate, run `check --strict`.
12. **Hand over.** Set each finished sheet to `status = "review"` and its index row with it. Tell the user which sheets are ready, list the proposed entries, and ask any open question. Approval is theirs.

## Rules

- **The treatment comes first.** No beat for a point whose treatment isn't approved, unless the user overrides in so many words. No beat adds plot the treatment lacks; a scene that needs it goes back to the story skill.
- **Wants, not plot.** Every character action traces to that character's want at this point. If it doesn't, change the action, not the want.
- **Every choice costs.** Each choice costs something now or later: state, trust, a route, a line. A choice that changes nothing is a funnel. Give it a cost or cut it.
- **Every failed check reveals.** Failure leads somewhere that shows a character, a cost, or another route. Never a dead end, and never the only route to a required clue.
- **Plants read innocently.** A clue planted before the reveal of what it proves has an innocent reading in `clues.toml`, and the sheet gives its first-play and second-play readings.
- **Required clues have routes.** A clue with `required = true` needs `[clues] min_routes` finds across the beats. A player who misses one gate or fails one check still has a route.
- **Front matter and body agree.** `plants` and `finds` match the clue fields. `reads` and `sets` match "State touched". `pattern` matches "Branching pattern".
- **Ids exact.** Clue ids, state names, cast ids, and points appear exactly as in canon, in backticks. A new one exists only as a proposed ledger entry.
- **The user decides canon.** A new fact is marked `[proposed]` and listed under "Proposed". Only the user approves it.
- **Only the user approves a sheet.** Write `approved` only when the user says so in chat. A change to an approved sheet, made at the user's request, sets it and its index row back to `review`.
- **Plan, don't write.** A beat sheet holds no dialogue beyond a phrase the scene must carry.

## References

- `${CLAUDE_PLUGIN_ROOT}/skills/beats/references/beat.md`: knot's default beat-sheet template.
- `${CLAUDE_PLUGIN_ROOT}/skills/beats/references/patterns.md`: the five branching patterns, how each shows in a sheet, and how each fails.
- `${CLAUDE_PLUGIN_ROOT}/skills/beats/references/index.md`: the shape of `beats/index.md`.
- `${CLAUDE_PLUGIN_ROOT}/docs/project-contract.md` §4 (ledgers), §5 (front matter), §6 (templates), §7 (`check` and its codes).
- The canon skill's `as-of.md` and `changes.md`, under `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/`.

## Hand-off

- **After the sheets:** the review skill (`/knot:review`), one review per unit or gate. Its solver test checks the clues the sheets make findable.
- **After the user approves a sheet:** the scene skill (`/knot:scene`) for a key scene's full prose, or the ink skill (`/knot:ink`) straight from the sheet.
- **When canon must change:** the canon skill (`/knot:canon`). **When the treatment is wrong:** the story skill (`/knot:story`).
