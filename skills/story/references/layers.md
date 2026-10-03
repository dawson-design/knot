# The story layers

What the spine and a treatment must settle, how long each runs, and the rules that keep the layers in step. The layout and front matter are in `${CLAUDE_PLUGIN_ROOT}/docs/project-contract.md` §1 and §5. Examples use the contract's placeholder project.

## The order

The layers run top-down: spine, treatment, beats, scenes, Ink. The story skill writes the first two.

Write the whole story at one layer before going deep on the next. The spine covers every unit before any treatment starts, and every unit has a treatment before any beats start. Contradictions then surface while they are cheap to fix. A project may approve a layer in batches, such as one act at a time, and start the next layer on the approved batch.

## Status

| Status | Set by | Means |
|---|---|---|
| `draft` | the skill, while writing | Not ready to read. |
| `review` | the skill, at hand-over | Ready for the user and the review skill. |
| `approved` | the user only | Binding on every layer below it. |

A treatment holds its status in front matter. The spine holds it in a `**Status:**` line under the title, because the spine has no front matter.

Write `approved` only when the user says so in chat. When the user asks for a change to an approved file, make it and set the file back to `review`.

## Units

A unit is the span one treatment covers. Usually it is one point: the placeholder project's units are `p1`, `p2`, and `p3`. A strand that runs beside the main story, such as a side quest, is its own unit and spans every point it touches. The endings may share one unit or take one each.

Every point in `[timeline] points` belongs to at least one unit. A treatment's front matter `points` lists every point its unit spans.

## The spine

**It settles:**
- the secret or the turn, in one paragraph, with the `knowledge.toml` facts behind it
- the units, in play order, each with its points
- for each unit, the main path and whose want drives it
- for each unit, who learns what, matching `knows` in `knowledge.toml`
- for each unit, each clue planted or found, with a plant's innocent reading
- the endings: what decides each one, and what it costs or gives each main character

**It leaves open:** the scene list, the player's choices in detail, state names, and lines.

**Length:** one or two paragraphs per unit. The whole spine reads in one sitting.

### Building backward

A story with a secret is built from the secret back to the start, so every plant is in place before the player needs it.

1. State the secret plainly: what happened, who hid it, who was blamed. Name the facts behind it. A placeholder spine opens with `secret`: what the mentor hides, and the record entry the mentor removed to hide it.
2. Write the endings: the ways the player can come to know the secret, and what the player does with it.
3. Take the last unit. Name what the player must be able to find there: the deductions to prove, and the clue finds that prove them.
4. Step back one unit at a time. Ask what must be planted here, and who must learn what, so the later unit works. The placeholder project plants `c_record` at p1 and `c_receipt` at p2 so p3 can put them together.
5. Give every plant an innocent reading for a first play. `c_record` reads as a damaged page; `c_receipt` reads as a quiet season.
6. Write the sections in play order. Then read them forward as a first-time player would, and check that nothing points at the secret before its `reveal` point.

A story built to a turn rather than a secret works the same way. Start from the turn and ask what each earlier unit must set up so the turn lands.

## A treatment

**It settles:**
- the main path, as the player lives it, in present-tense prose
- every place used
- every real choice, with its cost now and later
- each character's want and turn at these points, as `cast.md` gives them
- what changes in the world, whatever the player chooses
- each clue planted or found
- what the player's choices carry into the next unit
- each new fact, marked proposed

**It leaves open:** the cut into scenes, the exact checks and state names, and every line. The beats skill settles those.

**Length:** one to five pages, most of it in "What happens". It needs enough for the beats skill to cut scenes from without inventing plot.

"What changed" and "Carries forward" divide the unit's consequences. "What changed" is what holds whatever the player chose: at p2, the rival knows the secret. "Carries forward" is what the player's choices leave behind: whether the player pocketed the receipt, and what the player told the rival.

## Top-down rules

1. A lower layer never contradicts a higher one, or canon. When a lower layer needs a fact changed, the change goes to canon first, through the canon skill's procedure in `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/changes.md`. Then fix the higher layers, then the lower ones.
2. No treatment for a unit until the spine is approved. No beats for a point until the treatment it comes from is approved. The user may override this in so many words. Say so in the hand-over, and keep the file at `review` or below.
3. A new fact is marked `[proposed]` where it appears and listed in the file's Proposed section. A new ledger entry gets `status = "proposed"`. Only the user approves either.
4. Every character action traces to that character's want at that point. When it doesn't, change the action, not the want. A want changes only through canon.
5. A clue planted before the reveal of what it proves needs an innocent reading.

## The cold read

When the project has `[review.cold_read]`, `knot.py packet cold-read` hands a fresh reader the named `sections` of the named `layers`, for every unit before the `before` point. The reader then predicts the story. If they predict `must_not_predict`, the secret leaked.

So write those sections as the player meets the story. Plants appear as ordinary things. Nobody on stage names the secret before its reveal, and a line that brushes it reads as ordinary on a first pass. The placeholder project's cold read keeps only "What happens". Its p1 and p2 treatments never name the secret; the receipt is only a paper the rival reads and sets aside.
