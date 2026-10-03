---
name: scene
description: "Turns an approved beat sheet into a scene script for a branching game with a knot.toml: present-tense narration, SPEAKER: dialogue in the cast's voices, choice blocks, skill checks, inner voices, and state changes, in a format that converts line for line to Ink. Use to draft, expand, or revise a file in the story's scenes folder, or when asked to write or draft a scene from a beat sheet. Writes scenes only; beat sheets and Ink belong to other skills."
---

# Scene

## Iron Law

`NO SCENE WITHOUT AN APPROVED BEAT SHEET. NOTHING THE BEAT LACKS, NOTHING IT HOLDS LEFT OUT, AND EVERY LINE MAPS ONTO INK.`

The scene skill writes one scene as a script: `scenes/<id>.md`, with its beat sheet's id. The beat sheet decides what happens; the scene decides the words. Narration, dialogue, choices, checks, and state changes each have exactly one Ink form, so the ink skill converts a scene without rewriting it. By default the main branch is written out in full and the other branches are summarized with the state they set. The user can ask for every branch in full.

## Before you start

1. Run `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/knot.py" config` and read every path from its JSON. Exit code 2 means there's no `knot.toml`: stop, and offer to draft one with the canon skill's setup procedure in `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/setup.md`.
2. Read the `rules` list from the config. Every line answers to them.
3. Read the beat sheet, `<paths.beats>/<id>.md`. If its `status` isn't `approved`, stop: name its status and offer the beats skill. Go on only if the user overrides in so many words.
4. Load the scene template from the config's `templates.scene`: the project's override, or knot's default. Its `## Format` section defines the elements. Read `canon.conventions` for the project's tag meanings and any extensions to the format.
5. Read the treatment the beat comes from: the file under `paths.treatment` whose `points` include the beat's point. It sets what surrounds the scene.
6. Read canon as of the beat's point, with the canon skill's `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/as-of.md`: each present character's want and what they know, the secrets the player may not learn yet, and the `clues.toml` and `state.toml` entries the beat's front matter names.
7. Load the voice skill. Read the cards in `canon.voices` for everyone who speaks, the player and inner voices included. If a speaker has no card, write one with the voice skill first, or ask.

## Workflow

1. **Restate the beat** for yourself, not in the file: who wants what, each choice and its cost, each check and what failure reveals, each variant and where paths meet, the state read and set, and the clues. Every item appears in the scene.
2. **Lay out the stitches.** One `###` section per branch, per check outcome that needs its own lines, and per meeting point. Name them by `conventions.md`. Pick the main branch: the first choice in the beat, unless the beat or the user names another.
3. **Copy the template** to `<paths.scenes>/<id>.md`, everything above its `## Format` section. Fill the front matter (contract §5): `id`, `point`, and `status = "draft"`. Fill the header list.
4. **Write the main branch in full,** in the format. Open on the place and the player character. Every line takes its speaker's voice.
5. **Summarize the other branches** with `[SUMMARY]`, keeping every structure line: the stitch heading, `[SET]`, `[CHECK]`, `[IF]`, choices, and diverts. Write them in full instead when the user asks.
6. **Plant clues as the beat says.** Show a planted clue's `text` in the player's terms, no more. Let the scene support the clue's `innocent` reading.
7. **Voice pass.** Run the voice skill's line check over every line. Fix what fails.
8. **Mark new facts.** Staging is the scene's own: a cup, the weather, a gesture. A fact another file must agree with, such as a date, a habit someone could mention later, or a past event, gets `[proposed]` and a line under `## Proposed`.
9. **Check the structure.** Every branch ends in a divert or an end. Every `[SET]` and condition names state from the beat's front matter. Every choice and check from the beat is there.
10. **Run** `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/knot.py" check`. Fix every error naming this file (E10, E11, E13).
11. **Hand over.** Set `status = "review"`. Tell the user the file, which branches are in full, and the proposed facts. Approval is theirs.

## Rules

- **The beat is the contract.** No choice, check, state change, clue, or speaker the beat lacks, and nothing it holds left out. A scene that needs a change goes back to the beats skill; a new fact goes to the canon skill.
- **Wants, not plot.** Every character action traces to that character's want at this point. If it doesn't, change the action, not the want.
- **Secrets hold.** Nothing gives away a fact before its `reveal` point, except a planted clue in its innocent reading.
- **Failure leads somewhere.** Each check's fail outcome has its own content and reveals something, as the beat says.
- **The format is exact.** Use only the elements in the template's `## Format` section and the extensions in `conventions.md`. One narration paragraph is one Ink line. A speaker label is an id in capitals.
- **State by name.** `[SET]` and conditions use `state.toml` names exactly, and only those in the beat's `reads` and `sets`. A condition may also name a stitch of this scene.
- **Project rules hold for every line.** Answer each `[[rules]]` ask before hand-over.
- **Only the user approves a scene.** Write `approved` only when the user says so. A change to an approved scene sets it back to `review`.

## References

- `${CLAUDE_PLUGIN_ROOT}/skills/scene/references/scene.md`: knot's default scene template and its `## Format` section.
- `${CLAUDE_PLUGIN_ROOT}/skills/ink/references/ink-conventions.md` § "Scene to Ink": the Ink each element becomes.
- `${CLAUDE_PLUGIN_ROOT}/skills/voice/references/dialogue.md` and `voice-card.md`: the voice rules and cards.
- `${CLAUDE_PLUGIN_ROOT}/skills/beats/references/patterns.md`: the branching patterns the beat names.
- `${CLAUDE_PLUGIN_ROOT}/docs/project-contract.md` §5 (front matter) and §6 (templates).

## Hand-off

- **After the draft:** the review skill (`/knot:review`), with its voice lens at least.
- **After the user approves the scene:** the ink skill (`/knot:ink`).
- **When the beat is wrong:** the beats skill (`/knot:beats`). **When canon must change:** the canon skill (`/knot:canon`).
