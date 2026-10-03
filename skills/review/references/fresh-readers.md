# Fresh-reader tests

Two tests use a reader who has seen nothing of the project. The cold read asks whether a secret leaks before its reveal. The solver asks whether the clues the player can find prove what they must, and nothing more. The reviewer can't run either test on itself: once you have read canon, you can't unknow it.

## Rules for both tests

- **The packet comes only from `knot.py`.** Run `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/knot.py" packet cold-read` or `packet solver`. Don't build, trim, annotate, or summarize the packet. If it looks wrong, fix the project or its config and run the command again.
- **A fresh subagent.** Start a new general-purpose subagent with nothing but the prompt below, with the packet pasted into it. Never use a fork, or any agent that inherits this conversation. Don't name the project, its genre, or what you are testing.
- **No tools.** The reader works from the packet alone. The prompt tells it not to open files or search, because a subagent with file access in the project could read canon.
- **The key stays with the reviewer.** Run `packet <test> --key` only after the reader answers, and never show it to the reader.
- **No coaching.** If an answer is unusable, start a new reader with the same prompt. Don't follow up with hints.
- **How many readers.** One reader is enough for a routine review. Before a gate, run three in parallel. A fail from any one of them is a fail.
- **Top-level only.** A review running inside a subagent can't start a reader. It lists the test under Not checked and hands it back.
- **No table, no test.** Both commands exit 2 when their `[review]` table is missing. Skip the test and say why.

## Cold read

**Needs:** `[review.cold_read]`, with `before`, `layers`, `sections`, and `must_not_predict`.

**Packet:** `packet cold-read` prints the chosen sections of every file in the chosen layers whose points all come before `before`. Parts are labelled "Part 1", "Part 2", and so on, never by file name.

**Prompt:**

```
You are reading the outline of a story for a game you have never seen. The parts
below come in order. Use only what is written here. Don't open any file, search,
or use any tool.

Answer these questions in order.

1. What kind of story is this? Name its genre in a few words.
2. What do you expect to happen next, and how do you expect it to end? Answer in
   three to five sentences.
3. Which details do you expect to matter later, and why? Quote them.

<the packet, exactly as printed>
```

**Grade:** run `packet cold-read --key` for the map from parts to files and the `must_not_predict` line. Then grade answers 1 and 2 against that line.

| Result | When | Finding |
|---|---|---|
| **Pass** | Neither answer predicts what `must_not_predict` describes | none |
| **Fail** | Either answer predicts it in substance, whatever the wording | blocker, lens `reveal` |
| **Near miss** | It appears hedged, or as one guess among several | should fix, lens `reveal` |

For a fail or a near miss, find the lines the reader leaned on, and name each one's file and section through the key.

Answer 3 is diagnostic. A plant the reader quotes with its true meaning is a **should fix** on that clue's innocent reading, lens `reveal`. A plant quoted for an innocent reason is fine: the player will notice it, which is the point of a plant.

In the placeholder project, `must_not_predict` is "that the mentor covered up the secret". A reader who answers "the mentor is hiding something, and removed part of the record to keep it quiet" fails the test, however the words differ.

## Solver

**Needs:** `[review.solver]`, with `must_prove` and `must_not_prove`, and the deductions they name in `knowledge.toml`.

**Packet:** `packet solver` prints the `text` of every findable clue and the claims to weigh, labelled "Claim A", "Claim B", and so on. It never prints what a clue proves, or which claims should hold.

**Prompt:**

```
Below is evidence gathered in a story, and some claims about what happened. Use
only what is written here. Don't open any file, search, or use any tool.

For each claim, decide whether the evidence proves it, makes it likely, or leaves
it open. "Proved" means the evidence, taken together, leaves no reasonable doubt.
Don't guess beyond the evidence.

Answer for each claim in this form:

Claim A: proved | likely | open
Evidence: the pieces you relied on
Reasoning: two or three sentences

<the packet, exactly as printed>
```

**Grade:** run `packet solver --key` for which claim is which deduction, and which claims must and must not be provable.

| Claim | Proved | Likely | Open |
|---|---|---|---|
| A `must_prove` deduction | pass | should fix: the case is thin | blocker: the case can't be made |
| A `must_not_prove` deduction | blocker: too much is findable | should fix: the evidence leans too far | pass |

The test passes when every claim passes. Each finding names the deduction, the reader's verdict, and the clues the reader relied on, or the clue that is missing. The lens is `fair_play`. Its fixes are to plant a clue, add a route to one, or weaken what a clue's text shows.

## Recording the result

In the report's **Fresh-reader tests** section, give:
- the test, the date, and the number of readers;
- each reader's answer, verbatim;
- the key: parts to files, or claims to deductions;
- the verdict, and the findings it raised. Those findings also go in the ranked list.
