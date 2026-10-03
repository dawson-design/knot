# CLAUDE.md

This repo is **knot**, a Claude Code plugin of skills for writing branching narrative games. `README.md` covers what it is and how to install it.

## The contract comes first

`docs/project-contract.md` is the contract between a game project, the skills, and `scripts/knot.py`. Change it before changing either side.

## Layout

- `skills/<name>/SKILL.md`, plus `references/`, for each of the seven skills. Each SKILL.md has an Iron Law, a Workflow, Rules, References, and a Hand-off, and stays under about 150 lines.
- `scripts/knot.py` is the mechanical layer: standard library only, a pure core that returns issues as data, and thin `cmd_*` functions for I/O. Tests are in `tests/`.

## Rules for skill content

- Generic: nothing from any one game, and no sample story. Examples use the contract's placeholder project: `mentor`, `secret`, points `p1` to `p3`.
- The user decides canon. Skills mark new facts proposed and never promote them.
- Descriptions name the story artifact and the `knot.toml` condition, so they don't fire on general writing, where Terse's skills belong.
- Plain, short sentences, with no em dashes.

## Commands

```bash
uv run python -m unittest discover tests
```

```bash
uvx ruff check scripts tests && uvx ruff format --check scripts tests
```

```bash
claude plugin validate . --strict
```

## Git

Work on a `feature/`, `fix/`, or `refactor/` branch off `main`, and merge it when the user approves. Commits are one logical change each, with no attribution trailers. The repo is public at github.com/kreek/knot, so nothing from a private game goes in.
