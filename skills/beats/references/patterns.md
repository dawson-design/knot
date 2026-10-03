# Branching patterns

Every beat sheet names its branching patterns, in its front matter `pattern` list and in its "Branching pattern" field. These are the five patterns knot knows (contract §5). A beat may use several. `knot.py check` warns (W8) on a name not in this list.

For each pattern: what it is, when to use it, how it shows in a beat sheet, and how it fails. The Ink for each pattern belongs to the ink skill. Examples use the contract's placeholder project.

## Foldback

**Front matter:** `foldback`

**What it is.** The player's choices split the scene, then the paths meet again. A state variable remembers which path the player took.

**When to use it.** By default. It lets the player choose without doubling the content that follows.

**In the beat sheet.**
- "Variants" gives each path and the moment they meet.
- `sets` names the state that remembers the path, and "State touched" says how it changes.
- A later beat reads that state, or "Delayed consequences" says where one will.

In `office_p1_first_day`, the player keeps to today's work or reads back through the record. All paths meet at the day's end. `saw_record` and `rel_mentor` remember which.

**How it fails.** The paths meet and nothing remembers them, so the choice was cosmetic. Or the state is set and never read; `knot.py check` warns on that (W6) once beat sheets exist. Every foldback either changes state that something later reads, or changes how the scene itself plays.

## Delayed consequence

**Front matter:** `delayed_consequence`

**What it is.** A choice sets state that pays off one or more points later. It is how the world remembers the player.

**When to use it.** Often. The payoff lands hardest after the player has stopped thinking about the choice.

**In the beat sheet.**
- "Choices, and what each costs" names the later cost, not only the cost now.
- "Delayed consequences" says what pays off, at which point, and in which beat once that beat exists.
- `sets` names the state; the paying-off beat lists it in `reads`.

In `depot_p2_audit`, pocketing the receipt adds `c_receipt` to `evidence`. At p3, `office_p3_confrontation` reads it. A player who left the receipt must go back to the depot for it before the clues fit together.

**How it fails.** The payoff is never planned, so no later beat reads the state. Or the payoff can't be traced to the choice, and the player feels punished at random. The later scene should let the player see what they did: a remembered line, a changed manner.

## Gate

**Front matter:** `gate`

**What it is.** A scene, a route, or a line needs state to open: something the player knows, holds, or has earned with someone.

**When to use it.** To reward attention, and to let an earlier choice open a shorter or richer route.

**In the beat sheet.**
- "Entry conditions" states the gate in state names, and the route for a player who doesn't meet it.
- `reads` names the state the gate tests.
- "Variants" gives the scene with and without the gate met.

In `office_p3_confrontation`, the direct route to the gap needs `saw_record`, or `c_record` in `evidence`. Without either, the player reaches the gap only after the rival points it out.

**How it fails.** A gate on the main path with no other route, so a player who missed one thing is stuck. A required clue behind a single gate breaks fair play: `[clues] min_routes` asks for at least two finds, and a gate counts as one route at most. Every gate on the main path needs a second way through.

## Failed check as content

**Front matter:** `failed_check`

**What it is.** A skill check whose failure goes somewhere that reveals something: a character, a cost, another route. Failure is never a dead end or a bare "you fail".

**When to use it.** For every skill check. A check worth making is worth failing well.

**In the beat sheet.**
- "Skill checks, and what failure reveals" gives the skill, the difficulty, what success gives, and what failure reveals.
- "Variants" gives the failed path its own line.
- `reads` names the skill's state.

In `office_p1_first_day`, the player makes a Notice 2 check on the record. Success spots the removed entry and adds `c_record` to `evidence`. Failure smears today's entry, and the mentor's sharpness at the day's end shows how much the record matters.

**How it fails.** Failure blocks the scene until the player retries, or it plays the same as not trying. Worst, a required clue sits only behind a check's success. Then a failed roll can break the story.

## Hard split

**Front matter:** `hard_split`

**What it is.** A branch that never rejoins. Each side has content the other never sees.

**When to use it.** Rarely: endings, and a few set pieces worth their cost. Every hard split multiplies the content after it.

**In the beat sheet.**
- "Variants" gives each branch and where each one ends.
- "Delayed consequences" names the later beats that exist on only one branch.
- `sets` names the state that records the branch, so later beats and the endings can test it.

Suppose the endings are a hard split: reporting the secret, telling the rival alone, or keeping it each lead to a different close. The beat sheets before the endings use none.

**How it fails.** Splits early in the story double every later layer, and the cost lands in beats, scenes, and Ink. A split that quietly rejoins is a foldback; name it as one. A split the player can't see coming feels arbitrary, so the choice that causes it should look like it matters when it is made.
