---
name: canon
description: "Answers what is true in a branching game's story as of a story point: who knows what and from when, what each character wants, where they are, and which secrets the player may learn yet. Records changes to the story's canon (cast, timeline, and the knowledge, clue, and state ledgers) with a changelog line, marking new facts proposed. Sets up knot.toml for a new game. Use in a project with a knot.toml for any question about a character, fact, or secret at a point in the story, even without the word canon."
---

# Canon

## Iron Law

`EVERY ANSWER CITES ITS FILE AND ENTRY. NO FACT ENTERS CANON UNLESS THE USER DECIDED IT.`

Canon is the project's record of what is true in its story, point by point: the cast and their wants, the timeline, and the ledgers of facts, secrets, clues, and state. This skill does three jobs. It answers "what's true as of point X" from those files. It records a change to them, with a changelog line and a list of the drafts the change now contradicts. And it sets up a new project's `knot.toml`. It writes canon and nothing below it: the story, beats, scene, and ink skills own those layers.

## Before you start

1. Run `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/knot.py" config` and read every path from its JSON. Exit code 2 means there's no `knot.toml`: stop, and offer to draft one with the setup procedure below.
2. Read `points` from the config. Points are ordered by their place in that list, never by name.
3. Note the `truth` list, highest first, and which canon files exist (`canon.<name>.exists`). A missing required file is a gap to report, not an error.
4. Read the `rules` list. A change that would break a rule goes to the user before it is written.
5. Read the truth sources the task needs, by the order in `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/as-of.md`.

## Workflow

Pick the job the request asks for.

### Answer what's true as of a point

1. Fix the point. Take it from the question, or from the front matter of the draft in hand. If neither gives one, ask. Confirm it is in `points`.
2. Read the sources in the order `as-of.md` gives, and filter each by the point.
3. Answer only what was asked, in the answer shape from `as-of.md`. Cite the file and entry for every claim.
4. Label proposed entries as proposed. Say where canon is silent, and name the file an entry would go in.
5. If two sources disagree, answer from the higher one, report the conflict, and offer to record a change.

### Record a change

1. State the change in one sentence, and who decided it: the user, or a skill or agent. Only a change the user decided is written as approved.
2. Follow `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/changes.md`: edit every affected canon file, add the changelog line, sweep the lower layers, and run `knot.py check`.
3. Report the changelog line, the files edited, the proposed entries, the lower-layer files that now contradict canon, and the check result.

### Set up a project

1. Follow `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/setup.md`: interview the user, write `knot.toml`, create the required canon files as stubs, and run `config` and `check`.
2. Show the user the file and the stubs before going further.

## Rules

- Answer from the files: not from memory of the conversation, and not from a lower layer. If a fact appears only in a draft, say so and offer to record it in canon.
- The higher source wins: the `truth` list in order, then spine, treatment, beats, scenes, and Ink.
- A new entry a skill or agent originates is proposed: `status = "proposed"` in a ledger, or a `[proposed]` mark and a line in the file's Proposed section in prose.
- Never promote a proposed entry yourself. Remove its status or mark only when the user approves that entry.
- Change or remove an approved entry only on the user's decision. If a draft needs one changed, put it to the user first.
- Every change gets one dated changelog line naming the files it touched and the files it now contradicts.
- Ids are stable. A name changes in the body. Changing an id is a change in its own right, with every reference listed.
- Keep the shapes in the contract (`${CLAUDE_PLUGIN_ROOT}/docs/project-contract.md` §3 and §4). A field `knot.py` doesn't know raises W9; add one only with the user's agreement.
- Wants, not plot. If a change would make a character act against their want at a point, raise it with the user. Change the action, not the want.
- Don't edit the spine, treatments, beats, scenes, or Ink. List what they now contradict and hand it on.

## References

- `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/as-of.md`: the point, the read order, the five questions, citations, and the answer shape.
- `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/changes.md`: who decided, the files a change touches, the changelog line, and the sweep of lower layers.
- `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/setup.md`: the interview, `knot.toml`, and the canon stubs.
- `${CLAUDE_PLUGIN_ROOT}/docs/project-contract.md`: §1 layout, §2 `knot.toml`, §3 canon prose files, §4 ledgers, §7 `knot.py`.

## Hand-off

- After an answer: back to the skill or person that asked.
- After a change: each contradicting file goes to the skill that owns its layer: story for the spine and treatments, then beats, scene, or ink. Then the review skill checks the result with its `canon` lens.
- After setup: the story skill, to draft the spine.
