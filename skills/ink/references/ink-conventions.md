# Ink conventions

knot's defaults for a project's Ink. A project changes any of them in its `conventions.md`; where the two differ, `conventions.md` wins. Examples use the contract's placeholder project.

## File layout

Everything sits under the ink folder (`[ink] dir`, under the story root):

```
ink/
  main.ink                      the main file: INCLUDEs, the running order, shared functions
  globals.ink                   every VAR and LIST, and nothing else
  p1/
    office_p1_first_day.ink     one scene per file, in a folder per point
```

- The main and globals file names come from `[ink] main` and `[ink] globals`.
- A scene's file is `<point>/<id>.ink`, named for its beat sheet. A project may group by place, or keep a folder of recurring conversations; `conventions.md` says so.
- INCLUDE paths are relative to the main file. INCLUDE lines go at the top of the main file, after its header comment.
- Start every file with a `//` comment: what it holds, and the scene or ledger it mirrors.

## The main file

The main file includes everything, then plays the scenes in story order. Each scene is a tunnel: the main file calls it, and it returns with `->->` when it ends. Scenes then don't need to know what comes after them.

```
INCLUDE globals.ink
INCLUDE p1/office_p1_first_day.ink

-> office_p1_first_day ->
-> END
```

Add each scene's INCLUDE and its call in play order, the order of `beats/index.md`. Where the story branches between scenes, the main file branches on the state the scene set. Here `chose_a` is a made-up flag:

```
{ chose_a:
    -> office_p3_side_a ->
- else:
    -> office_p3_side_b ->
}
```

Shared functions, such as the check function below, go after `-> END` in the main file unless `conventions.md` names another file.

## Knots and stitches

- **One knot per scene.** Its name is the beat sheet's id: `=== office_p1_first_day ===`. It must match `[ink] knot`, where `{point}` stands for any point; `knot.py ink` warns on a knot that doesn't (I6).
- **Stitches** split a scene into named parts: `= day_end`. Use one per branch, per check outcome that has its own lines, and per meeting point. Name them as `conventions.md` says; knot's default is short verbs, such as `= keep` or `= read_back`.
- **No name clashes.** A stitch name is never a state name, a list item, a knot name, or a function name. Ink reads them all from one namespace.
- **Functions** are `=== function name(args) ===`. They are exempt from the knot pattern.
- **Every path ends.** Each stitch ends in a divert to another stitch, a tunnel return (`->->`), or `-> END`. A path that runs out of content is a loose end; inklecate warns, and the game stops there.

## State

All state is declared in the globals file and nowhere else (`knot.py ink` I1). The globals file mirrors `state.toml` one for one (I2, I3, I4):

| `state.toml` | Globals |
|---|---|
| `type = "int"`, `default = 0` | `VAR rel_mentor = 0` |
| `type = "bool"`, `default = false` | `VAR saw_record = false` |
| `type = "string"`, `default = "calm"` | `VAR mood = "calm"` |
| `type = "list"`, `items = ["c_record", "c_receipt"]`, `default = []` | `LIST evidence = c_record, c_receipt` |
| the same, `default = ["c_record"]` | `LIST evidence = (c_record), c_receipt` |

- Group declarations by the kinds in `conventions.md`, each group under a `//` comment. Keep comments on their own lines.
- A new variable starts as a `state.toml` entry with `status = "proposed"`, then a declaration. `knot.py ink` warns on a proposed entry not yet declared (I8).
- **Not state:** which branch ran in this scene is a stitch's read count (`{see_gap: ...}`). A value used only inside one scene is a temporary: `~ temp tries = 0`.
- Set state with `~`: `~ saw_record = true`, `~ rel_mentor += 1`, `~ evidence += c_record`.
- Test it in conditions: `saw_record`, `rel_mentor >= 2`, `evidence has c_record`, `not saw_record`.

## Tags

- Use only the names in `[ink] tags` (`knot.py ink` I5). Their meanings are in `conventions.md`.
- Write a tag as `# name: value`.
- A tag goes at the end of the line it describes, or alone on the line just above it. A tag alone on a line applies to the next line of text.
- knot's default tags: `speaker` on every line of dialogue, with the cast id; `voice` on every inner-voice line, with the voice's id; `check` before a check, with the skill and difficulty.
- No tags on choice lines. When the player character speaks a choice aloud, the branch opens with a separate line tagged with the player's speaker id.
- Line ids for localization or voice-over are a tag like any other. Use one only if the project lists it in `[ink] tags`.

## Checks

A check is a `check` tag, then a conditional that calls the project's check function, then one branch per outcome:

```
# check: notice 2
{ check(notice, 2):
    -> see_gap
- else:
    -> spoil
}
```

- The tag sits alone above the conditional, so it applies to the first line of whichever outcome plays.
- The function holds the project's rule for resolving a check, so the Ink plays the same in Inky as in the game. knot's default name is `check(skill, difficulty)`, returning true on a pass.
- `conventions.md` states the rule. If it doesn't, propose one to the user and mark the function's comment `[proposed]`. Don't settle a game-design rule silently.
- Both outcomes lead to content (see `patterns.md`, failed check as content).

## Scene to Ink

Each scene element has one Ink form. Convert top to bottom.

| Scene | Ink |
|---|---|
| Front matter `id` | `=== <id> ===` at the top of the file |
| Header list, `## Proposed`, `[proposed]` marks | Not converted |
| Narration paragraph | One line of text |
| `MENTOR: line` (a cast id) | `line # speaker: mentor` |
| `NOTICE: line` (an inner voice) | `line # voice: notice` |
| `### read_back` | `= read_back` |
| `> CHOICE` | Nothing; the options follow |
| `> 1. [Text] -> keep` | `* [Text]`, then `-> keep` indented on the next line |
| `> 2. {condition} [Text] -> gap` | `* {condition} [Text]`, then `-> gap` |
| `> 3. (sticky) [Text] -> small_talk` | `+ [Text]`, then `-> small_talk` |
| `-> day_end` | `-> day_end` |
| `[SET x = v]`, `[SET x += v]` | `~ x = v`, `~ x += v` |
| `[CHECK notice 2]` | `# check: notice 2`, then `{ check(notice, 2):` |
| `[PASS]` | Nothing; its lines follow the opening |
| `[FAIL]` | `- else:` |
| `[END CHECK]` | `}` |
| `[IF c]` | `{`, then `- c:` on the next line |
| `[ELSE IF c]` | `- c:` |
| `[ELSE]` | `- else:` |
| `[END IF]` | `}` |
| `[SFX: door]` (any cue) | `# sfx: door`, alone on the line above the next line of text |
| `[SUMMARY] ...` | The branch's lines, written out in full |
| `[END SCENE]` | `->->` |
| `[END STORY]` | `-> END` |

A project's own scene elements take the Ink its `conventions.md` gives them.

## Safe text

Ink reads some characters as syntax. In a line of text:

- Don't start a line with `*`, `+`, `-`, `=`, or `~`.
- Avoid `{`, `}`, `|`, `#`, `//`, `->`, and `<>` inside text. In choice text, square brackets also mean something.
- Escape a character you need with a backslash: `\#`, `\{`.
- Keep `TODO` out of comments; inklecate reports it.

## Example

One stitch of a placeholder scene, `office_p1_first_day`, and its Ink.

Scene:

```
### spoil

NOTICE: Nothing out of place.

The player's sleeve smears today's entry.

-> day_end
```

Ink:

```
= spoil
Nothing out of place. # voice: notice
The player's sleeve smears today's entry.
-> day_end
```
