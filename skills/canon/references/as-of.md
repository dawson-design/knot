# Answering "what's true as of point X"

How the canon skill answers a question about the story at one point. Other skills follow the same procedure when they need canon as of a point: story and beats before planning, scene and ink before drafting, and review for every lens.

## The point

- Points come from `points` in the `config` JSON, in play order. "Before", "after", and "as of" compare positions in that list. Never compare point names as strings: "p10" sorts before "p2".
- "As of X" means at X. Every entry whose point is X or earlier holds. An entry whose point is later doesn't hold yet.
- A point is the smallest unit of story time knot knows. Canon doesn't order events inside a point unless `timeline.md` does. If a question needs that order ("before the audit?"), answer from `timeline.md` or say canon doesn't settle it.
- A draft gives its own point: the `point` of a beat sheet or scene, the `points` of a treatment, or the point an Ink knot name matches under `[ink] knot`. For a treatment that spans several points, answer per point.

## Read order

Read only what the question needs, in this order.

1. **Truth sources above canon.** The config's `truth` list runs highest first. Anything listed before the canon folder, such as a design bible, holds rules and settled decisions that outrank canon.
2. **`timeline.md`:** the section for X and every section before it. It gives the shape of the point: what happens, what's public, and what's hidden.
3. **`knowledge.toml`:** facts, who knows them, and secrets.
4. **`cast.md`:** each character's want by point, secret, and turn.
5. **`clues.toml`:** what is planted and what can be found by X.
6. **`state.toml`:** only when the question is about what the player may have done or holds.
7. **Project extras:** any other file in the canon folder, or a truth source listed after it, when the question touches it: places, a glossary, a list of communities. knot has no model of places. A project that needs one brings it as a truth source.
8. **Lower layers, last, and never as a source of fact.** Read the spine, treatments, or beats only to say where something is shown, or to report that a draft states something canon doesn't.

If two sources disagree, the one higher in `truth` wins, and canon outranks every layer below it. Answer from the winner and report the conflict.

## The five questions

Most questions are one of these, or a mix. Each has a filter.

### Who is where, and what happens

- Read `timeline.md` `## X`: **Happens**, **Public**, and **Hidden**.
- Read each character's role and their **By point** line for X in `cast.md`.
- Read the project's place source, if it has one.
- Keep what is public at X apart from what is hidden.

### What each character wants

- Read the character's **By point** line for X in `cast.md`.
- If there's no line for X, the latest earlier line holds. Say that you carried it forward. If there's no earlier line, give the overall **Want** and say so.
- A **Turn** at or before X can change the want. Check for one.

### Which facts hold

- A fact holds at X when its `true_from` is X or earlier.
- A fact with a later `true_from` isn't true yet. Don't state it as true. If it matters to the question, say when it becomes true.
- The **Hidden** lines in `timeline.md` often state the same facts in prose. If they disagree with `knowledge.toml`, report it.

### Who knows what

- A character knows a fact at X when a `knows` entry has their id as `who` and a `from` of X or earlier. `via` says how they learned it.
- A character with no `knows` entry for a fact doesn't know it. Say so plainly when asked: "the rival doesn't know" is an answer.
- `who` is a cast id or an `[ids] extra` id.
- A `knows.from` earlier than the fact's `true_from` is an error in canon. `knot.py check` doesn't catch it, so report it.
- Nobody "knows" a deduction. A deduction is a claim the player can try to prove.

### What the player may know

Keep three things apart.

1. **What the player character knows:** `knows` entries with `who = "player"` and a `from` of X or earlier.
2. **What the player may be shown:** any fact without `reveal` that the story has reached, and any fact whose `reveal` is X or earlier.
3. **What is hidden from the player:** every fact whose `reveal` is after X. Nothing the player sees at X may give it away. A clue planted at X or earlier that points toward it may appear, read only by its `innocent` reading.

Some knowledge depends on choices. A clue can be found at X when one of its `finds` has a point of X or earlier. Whether the player has found it depends on play. Name the state that records it, such as an evidence list or a flag, and say "may", not "does".

If a `knows` entry gives the player character a secret before its `reveal`, the character knows something the player may not be told. That can be deliberate. Ask the user rather than resolve it.

## Citations

Every claim in an answer names its source, so it can be checked without searching.

- **Ledgers:** the path relative to `project_dir`, then the table and key: `story/canon/knowledge.toml facts.secret`. Point to a field when it matters: `facts.secret knows (rival)`.
- **Prose canon:** the path, the `## ` heading, and the field: `story/canon/cast.md ## rival, By point: p2`.
- After a file's first full citation in an answer, its name alone will do: `knowledge.toml facts.secret`.
- Mark a proposed entry with `(proposed)` after its citation.
- Cite a fact found only in a lower layer as such: "stated in `story/treatment/p2.md` ## What happens, not in canon."

## The answer shape

Lead with the point and its position. Then give only the parts the question asks for.

```markdown
As of <point> (point <n> of <total>):

- **Where:** ...
- **Wants:** ...
- **Knows:** ...
- **Doesn't know:** ...
- **The player may know:** ...
- **Proposed, not yet canon:** ...
- **Canon is silent on:** ..., which would go in <file>
```

## Worked example

"What does the rival know at p2?"

> As of p2 (point 2 of 3):
>
> - **Knows:** what the mentor hides. The rival learned it from the receipt (`story/canon/knowledge.toml facts.secret knows (rival)`, from p2).
> - **Doesn't know:** nothing else. No other `knows` entry names the rival.
> - **Wants:** the rival's line for p2 (`story/canon/cast.md ## rival, By point: p2`).
> - **Where:** the depot (`story/canon/timeline.md ## p2, Happens`).
> - **The player may know:** not `secret`, which reveals at p3. At p2 the player meets only the receipt, read as a quiet season (`story/canon/clues.toml clues.c_receipt`, innocent).
