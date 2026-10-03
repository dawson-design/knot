---
name: story
description: "Plans a branching game's story layers above the scene: the spine (the whole story, built backward from its secret, one section per unit plus the endings) and each unit's treatment (what happens, where, the player's options, wants and turns, clues, what carries forward). Use to write, revise, or plan a spine or a treatment for a story point, season, act, chapter, or side quest in a project with a knot.toml. Not for general outlines, documents, or scene prose."
---

# Story

## Iron Law

`BUILD BACKWARD FROM THE SECRET. WRITE NO LAYER UNTIL THE ONE ABOVE IS APPROVED.`

This skill plans a branching story from the top down. The spine tells the whole story, a paragraph or two per unit plus the endings, built backward from the secret the story hides or the turn it builds to. A treatment tells one unit in present-tense prose: what happens, where, the player's options, each character's want and turn, what changed, the clues, and what carries forward. Both are plans for the user and the writers to read. Neither cuts scenes or writes lines; the beats skill cuts scenes from an approved treatment.

## Before you start

1. Run `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/knot.py" config` and read every path from its JSON. Exit code 2 means there's no `knot.toml`: stop, and offer to draft one with the canon skill's setup procedure in `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/setup.md`.
2. Read the `rules` list from the config. Each rule's `ask` is a question the draft must survive.
3. Read the truth sources in `truth`, highest first, as the task needs. Always read `cast.md` and `timeline.md`. Read `knowledge.toml` and `clues.toml` when they exist, and `conventions.md` for the project's naming and any extras it points to. To answer "what's true as of point X", follow the canon skill's `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/as-of.md`.
4. Load the template for the layer from the config's `templates.spine` or `templates.treatment`. A project's override may add sections. A treatment's front matter follows contract §5 whatever the template holds.
5. Read `${CLAUDE_PLUGIN_ROOT}/skills/story/references/layers.md`: what each layer must settle, how long it runs, and the top-down rules.

## Workflow

1. **Name the job.** Say which layer, which unit, and which points. A spine is one file, `spine.md` under `paths.spine`. A treatment is `<unit>.md` under `paths.treatment`, or in a subfolder for strands and endings.
2. **Check the layer above.** A treatment needs the spine's `**Status:** approved`. A spine needs `cast.md`, `timeline.md`, and the secret settled in canon. The secret is the user's call: if canon doesn't settle it, ask. If the layer above isn't approved, stop. Name the file and its status, and offer to finish it first. Go on only if the user overrides in so many words.
3. **Gather canon as of the unit's points.** For each character on stage: their want and turn "By point" in `cast.md`. The facts that hold, who knows them, and each secret's `reveal` point. The clues planted or found in these points. The previous unit's "Carries forward". For the spine, gather the whole timeline and every secret.
4. **Draft from the template.**
   - Spine: build backward, as `layers.md` describes. Write the secret paragraph first, then the endings, then the units from last to first. Then read it forward as a first-time player.
   - Treatment: write "What happens" first, from the unit's section of the spine. Fill the other sections from it. Set `points` to every point the unit spans and `status = "draft"`.
5. **Trace every action to a want.** For each thing a character does, find the want at that point that drives it. An action that only serves the plot gets changed. A want that has to change goes to canon first, through the canon skill.
6. **Mark what's new.** Mark a fact that isn't in canon `[proposed]` where it appears, and list it under Proposed. A new fact, deduction, or clue the story needs goes into its ledger with `status = "proposed"`, following the canon skill's `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/changes.md`.
7. **Check the reveals.** Nothing the player sees gives away a secret before its `reveal` point. Every clue planted before the reveal of what it proves has an innocent reading. When the project has `[review.cold_read]`, read the named sections as that fresh reader would.
8. **Answer each rule.** Put each `rules` ask to the draft. Fix every answer that is a finding before you hand over.
9. **Run the check.** Run `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/knot.py" check`. Fix every error in the files you wrote. A treatment's usual errors are E2 (a point not in `[timeline] points`) and E10 (bad front matter). Name any warning you leave and why.
10. **Hand over.** Set the status to `review`: the front matter for a treatment, the `**Status:**` line for the spine. Tell the user what the draft settles, list the proposed facts, and ask any open question. Approval is theirs.

## Rules

- **Only the user approves.** Write `approved` only when the user says so in chat. A change to an approved file, made at the user's request, sets it back to `review`.
- **Top-down.** Never contradict canon or a higher layer. A needed change goes to canon first, then the spine, then down. Name the lower files the change now contradicts.
- **Wants, not plot.** Every action traces to that character's want at that point. Change the action, not the want.
- **The user decides canon.** No new fact goes in silently. Proposed facts stay proposed until the user approves them at a gate.
- **The whole story covered.** The spine has a unit for every point in `[timeline] points`. A treatment's `points` lists every point it spans.
- **What happens is the player's view.** Present tense, the main path, nothing the player can't see. Plants appear as ordinary things.
- **Every option costs.** A choice in "The player's options" costs something now or later, or it comes out.
- **Ids exact.** Cast ids, clue ids, fact ids, and points appear exactly as in canon, in backticks. Cite the project's place ids when it defines them.
- **Plain prose.** Short sentences, active voice, present tense. Character voice and period flavor belong to the scene and voice skills.

## References

- `${CLAUDE_PLUGIN_ROOT}/skills/story/references/spine.md`: knot's default spine template.
- `${CLAUDE_PLUGIN_ROOT}/skills/story/references/treatment.md`: knot's default treatment template.
- `${CLAUDE_PLUGIN_ROOT}/skills/story/references/layers.md`: what each layer settles, its length, statuses, building backward, and the top-down rules.
- `${CLAUDE_PLUGIN_ROOT}/docs/project-contract.md` §1 (layout and layers), §4 (ledgers), §5 (front matter), §6 (templates and overrides).
- The canon skill's `as-of.md`, `changes.md`, and `setup.md`, under `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/`.

## Hand-off

- **After a draft:** the review skill (`/knot:review`). For treatments before a secret's reveal, ask for its cold-read test.
- **After the user approves a treatment:** the beats skill (`/knot:beats`) cuts it into scenes.
- **When canon must change:** the canon skill (`/knot:canon`), before this skill touches the file again.
