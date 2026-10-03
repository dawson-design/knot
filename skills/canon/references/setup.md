# Setting up a project

How the canon skill drafts a `knot.toml` for a game that doesn't have one, and creates the canon files every project needs. Contract §1 and §2 (`${CLAUDE_PLUGIN_ROOT}/docs/project-contract.md`) define every key. This file says how to choose the values.

## 1. Confirm there's no project

- `knot.py config` exits 2 when there's no `knot.toml` at or above the working directory. If it exits 0, a project already exists: don't make a second one inside it.
- Find the folder the file belongs in, usually the game's repo root. Ask if the repo holds more than one game.
- Look for story files that already exist. A project that adopts knot late keeps its story, and setup maps it.

## 2. Interview

Ask in one message, with a default for each question, so the user can answer only what they care about.

1. **Name.** The game's name.
2. **Story root.** The folder that holds `canon/`, `spine/`, and the rest. Default: `story`. Contract §1 fixes the folder names under it. If existing files use other names, propose moves, and move nothing without the user's word.
3. **Story points.** The units of story time, in play order: chapters, days, seasons, acts. Choose the grain at which the truth changes. A secret's reveal, a clue's plant, and a character's turn each need a point to sit at. Too coarse, and a plant falls in the same point as its reveal. Too fine, and every ledger entry argues over neighbors. Ids match `^[a-z][a-z0-9_]*$`. Renaming a point later touches every ledger, so settle the names now.
4. **Sources of truth.** Any design document that outranks canon, and any data file canon depends on, highest first. Default: the canon folder alone.
5. **Reviews and templates.** Where review reports go (default `<root>/reviews`), and a templates folder if the project overrides knot's templates (contract §6).
6. **People outside `cast.md`.** If minor characters live in a TOML table elsewhere, the file and table for `[ids] extra`.
7. **Clues.** Does the player solve a mystery? If so, how many ways must a required clue be findable? `min_routes` defaults to 2.
8. **Ink.** The folder and the main and globals files (defaults `ink`, `main.ink`, `globals.ink`), how scene knots are named, and which tags the game uses. Propose a knot pattern from the naming: a place or act prefix, then `{point}`, then the scene, as in `^(office|depot)_{point}_[a-z0-9_]+$`.
9. **Checks.** Any command the project runs to check its own data, such as a map or world validator.
10. **Rules.** The story's own laws: what must never happen, the line of tone it won't cross, the secret it keeps. Each becomes a `[[rules]]` entry with an `id`, an `ask`, and the files that state the rule (`see`). Phrase each `ask` so "yes" is the finding: "Does anyone act from malice rather than from a want they could explain?"
11. **Fresh-reader tests.** If the story hides something until a point, the cold-read test needs that point (`before`), the layers and sections to show, and one line on what a reader must not predict. The solver test needs deductions in `knowledge.toml`, so it usually waits until the clue map exists.

## 3. Write `knot.toml`

- Follow contract §2. Write the required keys (`[project] name` and `root`, `[timeline] points`) and only the optional keys the user answered. The defaults cover the rest.
- Start the file with a comment that says what it is and where the contract lives.
- Leave `[review.solver]` out until `knowledge.toml` holds the deductions it names. Leave `[review.cold_read]` out until the user has named what must not be predicted.

A minimal file, for a placeholder project called Example:

```toml
# knot.toml: tells the knot skills where Example's story lives.
# The contract for this file is docs/project-contract.md in the knot plugin.

[project]
name = "Example"
root = "story"

[timeline]
points = ["p1", "p2", "p3"]

[[rules]]
id = "no_villains"
ask = "Does anyone act from malice rather than from a want they could explain?"
see = ["story/canon/cast.md"]
```

## 4. Create the canon stubs

Create the three required files from contract §1. Give them structure and no facts.

- **`canon/cast.md`:** a `# Cast` title, a line saying each heading is an id and names go in the body, and a `## player` section with the field labels from contract §3 left blank.
- **`canon/timeline.md`:** a `# Timeline` title, then one `## <point>` per point, in order. Each has blank **Happens**, **Public**, and **Hidden** lines.
- **`canon/changelog.md`:** a `# Canon changelog` title, a line on the format, and the first entry: `- <today>: Set up knot. Files: knot.toml, canon/cast.md, canon/timeline.md, canon/changelog.md.`

Write no names, wants, or events into the stubs. Facts come from the user, or go in as proposed.

Offer the optional files, and create them only if the user wants them now:
- `conventions.md`, which the scene and ink skills need before any Ink;
- `voices.md`, which the voice skill fills;
- the ledgers `knowledge.toml`, `clues.toml`, and `state.toml`. An empty ledger is valid. A stub holds only a header comment naming contract §4.

If the story already lives in other documents, don't convert it silently. Offer to draft canon from them, with every entry proposed until the user approves it.

## 5. Run `config` and `check`

1. Run `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/knot.py" config`. Confirm the root, the points, and every path resolve where the user expects.
2. Run `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/knot.py" check`. Fix every error, and report the warnings that remain.
3. Show the user `knot.toml` and the stubs, and say what comes next: the story skill drafts the spine.

## Worked example

- Contract §8: a project that adopted knot late, with canon in a design bible and a world data file, and its own checker under `[checks]`.
