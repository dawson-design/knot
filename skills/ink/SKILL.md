---
name: ink
description: "Writes and fixes the .ink files of a branching game with a knot.toml: turns an approved beat sheet, or its scene, into Ink knots, stitches, choices, checks, and tags, with state only from globals.ink and state.toml, then runs knot.py ink and the inklecate compiler. Use to write the Ink for a scene, convert a scene or beat sheet to Ink, or revise or debug any .ink file in the project. Proposes new state rather than inventing variables."
---

# Ink

## Iron Law

`NO VARIABLE OUTSIDE GLOBALS, NO TAG OUTSIDE THE PROJECT'S LIST, NO HAND-OFF UNTIL KNOT.PY INK IS CLEAN.`

The ink skill writes the playable form of a scene: one Ink knot per beat sheet, in the project's ink folder. It drafts from an approved beat sheet, and from the scene when `scenes/<id>.md` exists. A scene converts element by element, by the table in `ink-conventions.md`; branches the scene only summarized are written out here, in the speakers' voices. State lives in `globals.ink`, mirroring `state.toml`, and tags come only from `[ink] tags`. The skill runs `knot.py ink`, which checks both and compiles with inklecate when it is installed.

## Before you start

1. Run `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/knot.py" config` and read every path from its JSON. Exit code 2 means there's no `knot.toml`: stop, and offer to draft one with the canon skill's setup procedure in `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/setup.md`.
2. Read the `ink` block of the config: `dir`, `main`, `globals`, the `knot` pattern, and the `tags` list. Read the `rules` list.
3. Read the beat sheet, `<paths.beats>/<id>.md`. If its `status` isn't `approved`, stop: name its status and offer the beats skill. Go on only if the user overrides in so many words.
4. If `<paths.scenes>/<id>.md` exists, read it. If it isn't `approved`, ask whether to wait for it or work from the beat sheet.
5. Read `canon.conventions`: tag meanings, stitch naming, the layout under the ink folder, and how a check resolves.
6. Read `canon.state` and the globals file. Read `main` to see the running order and the INCLUDEs.
7. Load the voice skill when any line must be written rather than converted: a summarized branch, or Ink drafted straight from a beat sheet.
8. Read `${CLAUDE_PLUGIN_ROOT}/skills/ink/references/ink-conventions.md` and `patterns.md`.

## Workflow

1. **Place the file.** Default path: `<ink dir>/<point>/<id>.ink`, unless `conventions.md` sets another layout. One scene per file. The knot name is the beat's id, and it must match `[ink] knot`.
2. **Check the state.** List every state name the beat reads and sets. Each must be in `state.toml` and declared in globals. If one is missing from `state.toml`, stop: that is the beat's gap, and it goes to the beats or canon skill.
3. **Keep scene-local things local.** Which branch ran is a stitch's read count. A value needed only inside the scene is a `temp`. Neither needs state.
4. **Propose, don't invent.** If later scenes truly need state the beat lacks, add a `state.toml` entry with `status = "proposed"` (type, kind, default, meaning), declare it in globals, log it with the canon skill's `changes.md`, and tell the user.
5. **Convert or draft.** From a scene, convert each element with the table in `ink-conventions.md` § "Scene to Ink". Expand each `[SUMMARY]` into full lines, in voice, keeping its structure lines. From a beat sheet alone, write the scene's lines in voice, with the scene format's elements in mind.
6. **Apply the patterns.** Build each pattern the beat names with the idiom in `patterns.md`.
7. **Tag every line** as `conventions.md` says: a speaker tag on each line of dialogue, a voice tag on each inner-voice line, a check tag before each check. Use no tag outside `[ink] tags`.
8. **Wire it in.** Add `INCLUDE <path>` to the main file, and the scene's call in play order (`beats/index.md` order), as `ink-conventions.md` describes.
9. **Run** `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/knot.py" ink`. Fix every error, I0 to I5. Fix each warning or say why it stands. I7 is expected for state that only later, unwritten scenes use.
10. **Report the compile.** `knot.py ink` compiles with inklecate when it's on PATH. If it prints `Compile skipped: inklecate not found on PATH.`, say so: the Ink is checked by `knot.py` but not by the compiler.
11. **Hand over.** List the file, any proposed state, any line that differs from the scene and why, and the `knot.py ink` result.

## Rules

- **Globals only.** `VAR` and `LIST` appear only in the globals file, one for one with `state.toml`, with matching types, defaults, and items.
- **No invented state.** A new variable starts as a proposed `state.toml` entry. Only the user approves it.
- **Tags from the list.** Only names in `[ink] tags`, with the meanings in `conventions.md`. No tags on choice lines.
- **The Ink mirrors the scene.** A written-out line converts unchanged. If the Ink must differ, change the scene with the scene skill first, or name the difference at hand-over.
- **Every path ends.** Each stitch and branch ends in a divert, a tunnel return, or an end. No loose ends.
- **Failure leads somewhere.** A failed check plays its own content.
- **Standard Ink.** Only syntax inklecate 1.x compiles. Nothing engine-specific beyond the project's tags.
- **The beat is the contract.** No choice, check, clue, or state change the beat lacks.

## References

- `${CLAUDE_PLUGIN_ROOT}/skills/ink/references/ink-conventions.md`: file layout, knots and stitches, globals, tags, checks, and the scene-to-Ink table.
- `${CLAUDE_PLUGIN_ROOT}/skills/ink/references/patterns.md`: the Ink idiom for each branching pattern.
- `${CLAUDE_PLUGIN_ROOT}/skills/beats/references/patterns.md`: what each pattern is, and how it fails.
- `${CLAUDE_PLUGIN_ROOT}/skills/scene/references/scene.md` § Format: the scene elements.
- `${CLAUDE_PLUGIN_ROOT}/docs/project-contract.md` §4 (`state.toml`) and §7 (`ink` and codes I0 to I8).

## Hand-off

- **After the Ink:** the review skill (`/knot:review`), with its state and voice lenses at least.
- **When state must be added or changed:** the canon skill (`/knot:canon`), which owns `state.toml`.
- **When the scene or beat is wrong:** the scene skill (`/knot:scene`) or the beats skill (`/knot:beats`).
