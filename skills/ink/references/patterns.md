# Branching patterns in Ink

The Ink idiom for each of the five branching patterns. What each pattern is, when to use it, and how it fails in a beat sheet are in the beats skill's `references/patterns.md`. This file covers how to build each one in Ink, and the mistakes Ink makes easy. Examples use the contract's placeholder project. Stitch names, and anything else the contract lacks, are made up for the example.

## Foldback

Choices split the scene, then the paths meet. Something remembers the path: state a later scene reads, or a read count this scene reads.

**Short branches: a gather.** When each branch is a few lines, nest them under their choices and meet at a gather (`-`):

```
* [Keep to today's work.]
    The player keeps to today's entries.
* [Read back through the record.]
    ~ saw_record = true
    The player turns back through older entries.
- The day ends.
```

**Long branches: stitches.** When a branch has its own choices or checks, give it a stitch and divert to a meeting stitch. This is the shape the scene format produces:

```
* [Keep to today's work.]
    -> keep
* [Read back through the record.]
    -> read_back

= keep
The player keeps to today's entries.
-> day_end

= read_back
~ saw_record = true
The player turns back through older entries.
-> day_end

= day_end
{ read_back: The mentor looks at the record before speaking. }
The mentor closes the record.
```

**Ink mistakes.**
- A branch that never diverts to the meeting point runs out of content.
- A remembered path that nothing reads. `knot.py ink` warns when a variable is never used outside globals (I7), and `knot.py check` when no beat reads it (W6).
- Using state for something only this scene needs. A read count (`{read_back: ...}`) already remembers it.

## Delayed consequence

A choice sets state now; a later scene reads it. The two halves live in different files, joined only by the variable.

At p1, `office_p1_first_day`:

```
= read_back
~ saw_record = true
```

At p3, `office_p3_confrontation`:

```
{ saw_record:
    The player knows where the gap is before opening the record.
- else:
    The player has to search the record a page at a time.
}
```

**Ink mistakes.**
- The later scene can play before the earlier one, so it reads the default. Check the running order in the main file.
- Testing a number for one exact value. Relationships move; test thresholds (`rel_mentor >= 2`), not `== 2`.
- A payoff the player can't trace. Give the later line a detail from the earlier choice.

## Gate

Content, a route, or a choice opens only on state. Three forms:

A conditional choice:

```
* {saw_record or (evidence has c_record)} [Go straight to the gap.]
    -> gap
* [Ask the rival about the record.]
    -> ask_rival
```

A conditional line or block:

```
{ rel_mentor >= 2: The mentor waits for the player. }
```

A conditional divert, at a stitch's start:

```
= gap
{ not saw_record and not (evidence has c_record): -> ask_rival }
The gap is where the player left it.
```

(`gap` and `ask_rival` are stitches in the p3 scene.)

**Ink mistakes.**
- Every choice gated, and none open. With no choice left, play runs out of content. Keep one choice without a condition, or add a fallback choice (`* -> elsewhere`).
- A gate on a once-only choice inside a loop. Once the player takes it, it's gone; use `+` if it must stay.
- Mixing `and`, `or`, and `has` without parentheses. Bracket each list test.

## Failed check as content

A check routes to two outcomes, and both play content. The check tag sits alone above the conditional, so it applies to the first line of whichever outcome plays. The function holds the project's rule (see `ink-conventions.md` § Checks).

```
= read_back
~ saw_record = true
The player turns back through older entries.
# check: notice 2
{ check(notice, 2):
    -> see_gap
- else:
    -> spoil
}

= see_gap
One entry is missing. # voice: notice
~ evidence += c_record
-> day_end

= spoil
Nothing out of place. # voice: notice
The player's sleeve smears today's entry.
-> day_end
```

On a fail the player smears today's entry, and at the day's end the mentor's sharpness shows how much the record matters. The failure is a scene of its own, not a bare "you fail".

**Ink mistakes.**
- An `else` with nothing in it, or one that diverts straight to where the pass goes.
- Comparing the skill to a number inline (`{notice >= 2: ...}`), bypassing the project's rule. A check the player can never pass on a first play is a gate, not a check.
- The only find of a required clue behind the pass. The clue needs its other routes in `clues.toml`.

## Hard split

A branch that never rejoins. In Ink it diverts to separate knots that never come back. Endings are the usual case, and each ending knot ends the game:

```
* [Report it.]
    -> office_p3_ending_report
* [Tell the rival alone.]
    -> depot_p3_ending_rival
* [Keep it.]
    -> office_p3_ending_kept

=== office_p3_ending_kept ===
The secret stays kept.
-> END
```

(The ending knots are made up. Each name still matches the `[ink] knot` pattern.)

A split in the middle of the story works differently, because scenes are tunnels. The splitting scene sets state and returns with `->->`. The main file then branches on that state and calls a different run of scenes on each side (see `ink-conventions.md` § The main file).

**Ink mistakes.**
- A scene that diverts straight into the next scene instead of returning. The main file then calls that next scene again, and it plays twice. Leave a scene with `->->`, or end the game with `-> END`.
- A split that quietly rejoins later. That is a foldback; name it as one in the beat sheet.
- Ending knots whose names break `[ink] knot`. An ending is a scene too.
