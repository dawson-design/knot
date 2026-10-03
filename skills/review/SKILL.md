---
name: review
description: "Reviews a branching game's story drafts (spine, treatment, beat sheet, scene, or Ink) against canon as of their story point and the project's own rules in knot.toml. Reports findings by severity through lenses: canon, fidelity to the layer above, character wants, secret leaks, fair-play clues, choices, failed checks, voice, and state. Runs one lens alone, or the cold-read and solver tests with fresh readers. Use in a project with a knot.toml whenever a story draft or a story gate needs review."
---

# Review

## Iron Law

`JUDGE THE DRAFT AGAINST THE FILES AS OF ITS POINT. EVERY FINDING NAMES ITS LENS, ITS PLACE, AND ITS SOURCE. FIX NOTHING UNASKED.`

Review reads a story draft against everything above it: canon as of the draft's point, and the layer the draft came from. It runs the project's checks, applies a set of lenses, and writes findings ranked by severity to the project's reviews folder. The lenses are generic, plus one for each of the project's `[[rules]]`. Review also runs two tests with fresh readers. The cold read asks whether a secret leaks before its reveal. The solver asks whether the findable clues prove what they must, and nothing more. Review reports; fixes go back through the skill that owns each file.

## Before you start

1. Run `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/knot.py" config` and read every path from its JSON. Exit code 2 means there's no `knot.toml`: stop, and offer to draft one with the canon skill's setup procedure (`${CLAUDE_PLUGIN_ROOT}/skills/canon/references/setup.md`).
2. Fix the target: its files, their layer, and their points. Points come from front matter (`point` for a beat sheet or scene, `points` for a treatment), from the knot name for Ink, or from the whole of `points` for the spine.
3. Read canon as of those points, by the canon skill's procedure (`${CLAUDE_PLUGIN_ROOT}/skills/canon/references/as-of.md`), with the truth sources in `truth` order.
4. Read the layer above the target: the spine for a treatment, the treatment for a beat sheet, the beat sheet for a scene, and the scene (or the beat sheet, without one) for Ink.
5. Read the `rules` list. Each rule joins the review as a lens under its own id.
6. Note the mode: a full review, one lens (`--lens <id>`), or a fresh-reader test (`cold-read` or `solver`).

## Workflow

1. **Run the project's checks.** Run each `checks` command from `project_dir`, in order. A non-zero exit is a blocker under the lens id `checks`, quoting the command and the tail of its output.
2. **Run knot's checks.** Run `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/knot.py" check`, with `--strict` before a beat gate or story lock. For Ink, also run `knot.py ink`. Turn each issue into a finding by the table in `findings.md`.
3. **Choose the lenses.** Take the generic lenses that apply to the target's layer, from the table in `lenses.md`, then every project rule. Drop `fair_play` when there's no `clues.toml`. With `--lens <id>`, keep that one lens and skip steps 1 and 2 unless the user asks for them. In a fanned-out review, the parent session runs them once.
4. **Decide how to run them.** For a big review (a whole layer, several files, or a gate), the top-level session fans out one subagent per lens, by `fan-out.md`. Inside a subagent, or for a small review, run the lenses in sequence, in the order `lenses.md` gives.
5. **Apply each lens.** Ask its question of the target at its layer, read what it says to read, and record each problem as a finding. Check every finding against its cited source before keeping it.
6. **Run the fresh-reader tests** when the user asks, or when the review covers a whole layer before a gate and the config has the matching `[review]` table. Follow `fresh-readers.md`. They need fresh subagents, so a review inside a subagent lists them under Not checked.
7. **Merge and rank.** One problem is one finding. Merge duplicates, keep the higher severity, and list every lens that found it. Rank most severe first.
8. **Write the report** to the config's `reviews` path, named and laid out as `findings.md` says. A single-lens subagent returns its findings instead of writing a file.
9. **Tell the user** the counts by severity, each blocker in one line, and the report's path. Stop there.

## Rules

- Report only. Write nothing but the report unless the user asks for fixes.
- When the user asks for fixes, fix top-down. A fix that needs a canon change goes through the canon skill first.
- Judge as of the draft's point. A fact that becomes true later isn't a canon error in an earlier draft. Showing it to the player early is a leak.
- The higher layer wins. A lower layer that contradicts it is the finding, even when the lower version reads better. If the user prefers the new version, that is a canon change.
- No finding without a source. Each cites its lens and the entry or section it breaks. Taste isn't a finding unless a lens or a project rule covers it.
- A failing project check or a `knot.py` error is always a blocker.
- A draft that rests on a proposed entry gets a note naming the entry, so the gate approves both together.
- A writer's note may name a secret. A leak is what reaches the player: events, lines, choices, check outcomes, and clue text. `lenses.md` says which parts of each layer reach the player.
- Review never changes a draft's `status`.
- Fresh readers get the packet from `knot.py packet` and the prompt in `fresh-readers.md`, and nothing else.
- Generic lens ids are reserved. If a project rule reuses one, run both, and tell the user to rename the rule.

## References

- `${CLAUDE_PLUGIN_ROOT}/skills/review/references/lenses.md`: which lenses apply to which layer, what reaches the player, and each lens's id, question, reading, and use at each layer. How project rules join.
- `${CLAUDE_PLUGIN_ROOT}/skills/review/references/findings.md`: severity, the finding format, `knot.py` issues as findings, ranking, de-duplication, and the report's path, name, and layout.
- `${CLAUDE_PLUGIN_ROOT}/skills/review/references/fan-out.md`: one subagent per lens, then merge. What changes inside a subagent.
- `${CLAUDE_PLUGIN_ROOT}/skills/review/references/fresh-readers.md`: the cold-read and solver tests, their prompts, and how to grade them.
- `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/as-of.md`: reading canon as of a point.
- `${CLAUDE_PLUGIN_ROOT}/skills/voice/SKILL.md`: the voice skill, which the `voice` lens loads.
- `${CLAUDE_PLUGIN_ROOT}/docs/project-contract.md`: §2 `[review]` and `[[rules]]`, §4 ledgers, §5 front matter, §7 `check`, `ink`, and `packet`.

## Hand-off

- Findings go to the user, who decides what to fix.
- Each fix goes to the skill that owns the file: canon for canon, story for the spine and treatments, then beats, scene, or ink.
- After the fixes, run review again with the lenses that found problems.
- A clean review of a whole layer goes to the user's gate. Only the user sets `status = "approved"`.
