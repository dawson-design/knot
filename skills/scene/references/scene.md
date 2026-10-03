+++
id = ""            # the beat sheet's id: this file's name without .md, matching [ink] knot
point = ""         # the beat sheet's point
status = "draft"   # draft | review | approved. The skill sets review at hand-over; only the user sets approved
+++

# Scene: <id>

<!--
knot's default scene template. Copy everything above "## Format" to <scenes path>/<id>.md,
with the front matter first in the file (contract §5). Replace each comment with what it
asks for, and delete the comments as you go. The Format section stays here as the reference.
-->

- **Beat sheet:** <!-- `beats/<id>.md` -->
- **Point and place:** <!-- From the beat sheet. Cite the project's place ids when it defines them. -->
- **Present:** <!-- Cast ids of everyone on stage, and when each arrives or leaves. Inner voices that speak. -->
- **Patterns:** <!-- The beat's patterns, and the stitch where the branches meet. -->
- **Branches:** <!-- "main written out; others summarized", or "all written out". Name the main branch's stitch. -->

## Scene

<!-- The scene, in the format below. Content before the first ### heading opens the scene. -->

## Proposed

<!-- Each new fact the scene needs: what it is, the stitch it's in, and why other files must agree. Write "None." when there are none. -->

## Format

The format is a script. Each element has exactly one Ink form, given in the ink skill's `references/ink-conventions.md` § "Scene to Ink". Put a blank line between elements, so each is its own paragraph.

### Narration

Plain prose in the present tense, close to the player character, in short paragraphs. One paragraph becomes one line of Ink, so keep each one to a beat. A narration paragraph never starts with a speaker label, `>`, `[`, `###`, or `->`.

### Dialogue

```
MENTOR: That page was damaged.
```

The label is the speaker's cast id in capitals, then a colon and a space. The player character's label is `PLAYER:`. One paragraph per line of speech: a speech of several lines repeats the label.

### Inner voices

```
NOTICE: One entry is missing.
```

The same form, with an inner voice's id. An id is an inner voice when its card in `voices.md` says `Kind: inner voice`. The Ink tags it as a voice, not a speaker.

### Stitches

```
### read_back
```

A `###` heading starts a stitch: a named part of the scene that a choice or divert can reach. Name stitches as `conventions.md` says. A stitch name is never also a state name, a list item, or a scene id. Content before the first stitch opens the scene.

### Choices

```
> CHOICE
> 1. [Keep to today's work.] -> keep
> 2. [Read back through the record.] -> read_back
> 3. {saw_record} [Go straight to the gap.] -> gap
> 4. (sticky) [Make small talk.] -> small_talk
```

- Each option: its number, an optional condition in braces, the option text in square brackets, and a divert to the stitch that holds its branch.
- The text in brackets is what the player picks. It isn't repeated as dialogue. If the player character says it aloud, the branch opens with a `PLAYER:` line.
- An option is offered once. `(sticky)` keeps it on offer after it's chosen, for a menu the player comes back to.
- Keep at least one option without a condition, so the player always has a choice.

### Diverts

```
-> day_end
```

On a line of its own: play goes to that stitch. Every branch ends in a divert, `[END SCENE]`, or `[END STORY]`.

### State

```
[SET saw_record = true]
[SET rel_mentor += 1]
[SET evidence += c_record]
```

On a line of its own, where the change happens. Use `=` for a value, `+=` and `-=` for numbers and list items. Names come from `state.toml` and the beat's `sets`.

### Checks

```
[CHECK notice 2]

[PASS]

NOTICE: One entry is missing.

[FAIL]

NOTICE: Nothing out of place.

[END CHECK]
```

The skill is a `state.toml` entry of the project's skill kind; the number is the difficulty from the beat. `[PASS]` and `[FAIL]` each hold that outcome's lines, or a divert to a stitch that holds them. Both outcomes lead on. How a check resolves is the project's rule, in `conventions.md`.

### Conditions and variants

```
[IF see_gap]

MENTOR: You've been reading back.

[ELSE IF spoil]

MENTOR: What happened here?

[ELSE]

MENTOR: That will do.

[END IF]
```

A condition can use:
- a state name: `saw_record`, `rel_mentor >= 2`
- a list item: `evidence has c_record`
- a stitch of this scene, true once it has played: `see_gap`
- `not`, `and`, `or`, and parentheses

`[ELSE IF]` and `[ELSE]` are optional. Close every `[IF]` with `[END IF]`.

### Presentation cues

```
[SFX: door]
```

A cue is a tag from `[ink] tags`, in capitals, then a colon and its value. It sits on its own line just before the paragraph it goes with, or at the start of that paragraph. `conventions.md` gives each tag's meaning. Use cues sparingly: the scene is for words.

### Ends

- `[END SCENE]`: the scene is over, and play returns to the story's running order.
- `[END STORY]`: the game ends here. For endings only.

### Summarized branches

```
### read_back

[SET saw_record = true]

[SUMMARY] The player reads back through the older entries. The mentor asks why, wanting the player back on today's work.

[CHECK notice 2]

[PASS]

-> see_gap

[FAIL]

-> spoil

[END CHECK]
```

A summarized branch keeps every structure line: its heading, `[SET]`, `[CHECK]`, `[IF]`, choices, diverts, and ends. Its narration and dialogue become `[SUMMARY]` paragraphs: a sentence or two on what happens, who speaks, and what they want. The ink skill writes those lines out in full.

### Proposed facts

Put `[proposed]` at the end of the paragraph that holds a new fact, and list the fact under `## Proposed`. The mark never reaches the Ink.

### Project extensions

Any tag in `[ink] tags` works as a cue without changing this template. A project that needs another kind of element adds it to the Format section of its own `scene.md` override (contract §6), and gives its Ink form in `conventions.md`.
