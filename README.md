# knot

knot is a set of Claude skills for writing branching narrative games. It takes a story from canon to Ink in layers: a spine, treatments, beat sheets, key scenes, then Ink. At every layer it checks the same things: what's true at this point in the story, whether each character acts from their want, whether a secret shows too early, whether every clue the player needs can actually be found, and whether every choice matters.

It is generic. A game tells knot where its story lives, and what its own rules are, in one file: `knot.toml`.

## How it works

Two layers:

- **Mechanical** (`scripts/knot.py`): one Python script, standard library only. It reads `knot.toml` and the story's TOML ledgers and front matter, and checks what a script can check:
  - ids resolve
  - clues are planted before they're found
  - every required clue has enough ways to find it
  - the Ink's variables match the state ledger

  It also builds the inputs for two fresh-reader tests, so nobody builds them by hand and leaks the answer.
- **Judgment** (the skills): Claude plans, drafts, and reviews each layer to the project's templates and rules, and runs the script at each step.

Facts live in the project's files, not in the skills. When the story changes, you edit canon, not four skills.

## Install

In Claude Code, add this repo as a plugin marketplace, then install knot. Choose project scope, so knot loads only in your game's repo:

```
/plugin marketplace add kreek/knot
/plugin install knot@knot
```

Run `/plugin marketplace update knot` to pick up new versions.

The script runs with [uv](https://docs.astral.sh/uv/). Ink compiles with [inklecate](https://github.com/inkle/ink/releases) when it's on your PATH; without it, `knot.py ink` runs its other checks and says the compile was skipped.

## Set up a project

Ask Claude to set up knot in your game's repo. The canon skill interviews you, writes `knot.toml`, creates the canon files it needs, and checks the result. Or write `knot.toml` yourself: `docs/project-contract.md` defines it, from the story root and the story points in play order to Ink settings, your own checks, and your review rules.

The skills run `knot.py` for you. To run it yourself, from a clone of this repo:

```bash
uv run scripts/knot.py check --project path/to/your/game
```

## Skills

| Skill | What it does |
|---|---|
| `/knot:canon` | Answers "what's true as of point X". Records canon changes with a changelog line, and flags what they contradict. Sets up new projects. |
| `/knot:story` | Plans the spine, backward from the central secret, then one treatment per unit. |
| `/knot:beats` | Writes the scene index and one beat sheet per scene, with front matter the script checks. |
| `/knot:voice` | Writes voice cards and holds the dialogue rules. Scene, ink, and review load it. |
| `/knot:scene` | Writes a scene in prose from its approved beat sheet, in a format that maps onto Ink. |
| `/knot:ink` | Turns a beat or scene into Ink, then checks and compiles it. |
| `/knot:review` | Reviews any layer through knot's lenses and the project's rules. It can run one lens at a time, and runs the cold-read and solver tests. |

The layers run top-down, and each waits for the user's sign-off on the one above. New facts are proposed, never written into canon silently.

If you also use Terse, keep the two apart. knot's skills and voice cards govern the story's own files, including in-world text. Terse's style rules govern design docs and everything else.

## Tests

```bash
uv run python -m unittest discover tests
```

```bash
uvx ruff check scripts tests && uvx ruff format --check scripts tests
```

```bash
claude plugin validate . --strict
```

## Further reading

- `docs/project-contract.md`: the contract between a project, the skills, and the script.
- `CHANGELOG.md`: what changed in each version.

## License

MIT. See `LICENSE`.
