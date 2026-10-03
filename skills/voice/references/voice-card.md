# Voice cards

A voice card says how one speaker sounds. The cards live in the project's `canon/voices.md`. Characters get cards, and so do inner voices: a skill that speaks, a conscience, a memory. The scene, ink, and review skills read the cards, and a line that breaks its speaker's card is a finding.

## The file

`voices.md` holds these sections, in this order:

1. `# Voices`, then a line or two on what the file covers.
2. `## House style` (optional): what every voice in the project shares. The setting's words, the grammar that carries the place and period, and anything nobody in the story says easily.
3. One `## <id>` section per card. Characters come first, in `cast.md` order, then inner voices.
4. `## Distinctness test`: the last run of the test in `dialogue.md`.
5. `## Proposed`: new cards, changed fields, and anything a card implies that canon lacks.

A card's heading is the bare id and nothing else, so `cast.md` can link to it as `voices.md#<id>`. For a character, the id is the cast id. For an inner voice, it is the id the project's Ink uses for that voice, named in `conventions.md`. Every other section has a name in words with a capital letter, so it can't be mistaken for an id.

## A character's card

```markdown
## <id>

- **Status:** [proposed]
- **Kind:** character
- **Who:** Name, role, the want that drives the voice, and what they hide. Link: `cast.md#<id>`.
- **Vocabulary:** The words they reach for: their trade, their place, their class, their age. Three to six examples in quotes.
- **Rhythm:** Sentence length. Orders, questions, or statements. How a line opens and ends.
- **Never says:** Words, subjects, and turns of phrase they avoid. Hard rules.
- **Dodges and lies:** How they avoid a question. How they lie, and the tell.
- **Under pressure:**
  - **Wanting something:** how they ask.
  - **Questioned:** how they answer, or don't.
  - **Caught out or cornered:** what gives.
  - **Moved:** grief, fear, or tenderness.
  - **Angry:** how it comes out, and at whom.
- **By point:** (optional) one line per point where the voice shifts.
- **Sample lines:**
  1. "A line." (point, situation, pressure)
  2. "A line." (point, situation, pressure)
  3. "A line." (point, situation, pressure)
```

**Status** appears only while the card or a field is proposed. Delete it when the user approves the card.

**Under pressure** gives a register, not a mood: the shape a line takes when that pressure lands. Different pressures should change sentence shape, not only word choice. One speaker gets shorter when cornered; another gets longer and more polite.

**By point** is for voices that change with the story. Tie each shift to the want in `cast.md` for that point. Leave the field out when the voice holds steady.

**Sample lines** come from real situations in the story, at real points, each under a different pressure. Each line must pass its own card and the line check in `dialogue.md`. They are the first thing a writer reads, so they carry the most weight.

## An inner voice's card

An inner voice speaks only to the player. Its card swaps the pressure registers for the moments it speaks in, and adds what it may know.

```markdown
## <id>

- **Status:** [proposed]
- **Kind:** inner voice
- **Who:** What it is, and its state entry if it has one (a skill's `state.toml` entry). How the Ink tags it, from `conventions.md`.
- **Knows:** Only what the player could perceive or remember. Name the limits.
- **Speaks when:** The triggers: a check, a quiet moment, a choice. How often.
- **Vocabulary:** As for a character.
- **Rhythm:** As for a character.
- **Never says:** As for a character. Always includes any conclusion or secret.
- **Registers:**
  - **Quiet:** nothing at stake.
  - **Something doesn't fit:** a detail that jars.
  - **On a pass:** a check succeeds.
  - **On a fail:** a check fails. It still says something, and what it says leads somewhere.
- **By point:** (optional) how it grows, for instance as a skill rises.
- **Sample lines:**
  1. "A line." (point, situation, register)
  2. "A line." (point, situation, register)
  3. "A line." (point, situation, register)
```

An inner voice notices; it never knows. It may set two details side by side. It never says what they mean, and it never states a secret, before its reveal or after.

## Building a card

1. **Start from the want.** Read the speaker's want and secret in `cast.md`, point by point. Ask what that want makes them say, and what it makes them avoid. The never-says and the dodges come from the secret.
2. **Take words from the world.** Vocabulary comes from their work and their place, and from any glossary the project keeps. Don't invent archaic words.
3. **Make the never-says do work.** The word a character won't use tells the player most. A mentor who never mentions the removed entry says more than one who explains it at length.
4. **Give every lie a tell.** The tell is what a careful player can learn to hear: the same words every time, one sentence too many, sudden warmth.
5. **Write the samples last,** and test each against the card. If a sample needs a word the card doesn't allow, fix the card or the sample, and say which.
6. **Run the distinctness test** across every card in the file, not only the new one.

## When a card changes

- A card follows its cast entry. When a want changes in `cast.md`, check the card's "Who", "By point", and pressure registers.
- A changed field is `[proposed]` until the user approves it, like a new card.
- Changing a card can make old lines wrong. List the scenes and Ink files with that speaker's lines, and hand them to the review skill's voice lens.

## Example

A placeholder card, trimmed:

```markdown
## mentor

- **Kind:** character
- **Who:** The player's mentor, named in `cast.md`. Wants to keep the secret hidden, and hides `secret`. Link: `cast.md#mentor`.
- **Never says:** what the removed entry held; "sorry" on its own.
- **Dodges and lies:** Answers a question with a task. The lies are short, in the same words every time. That is the tell.
- **Sample lines:**
  1. "That page was damaged." (p1, `office_p1_first_day`, questioned)
```
