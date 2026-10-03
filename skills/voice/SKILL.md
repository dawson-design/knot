---
name: voice
description: "Keeps the voice cards in canon/voices.md and the dialogue rules for a branching game with a knot.toml: how each character and inner voice speaks, what they never say, how they dodge and lie, and the distinctness test. Use to write or revise a voice card, to check that a game's dialogue, narration, or choice text sounds like its speaker, or when the scene, ink, or review skill needs the voices. In-world text follows the voice cards, not general prose style rules."
---

# Voice

## Iron Law

`EVERY LINE SOUNDS LIKE ITS SPEAKER'S CARD AND WANTS SOMETHING. THE CARD OUTRANKS GENERAL STYLE RULES.`

The voice skill owns how the story's people sound. It keeps one voice card per speaker in the project's `canon/voices.md`, inner voices included, and the craft rules every in-world line follows. In-world text is dialogue, narration, choice text, and inner voices. The scene, ink, and review skills load this skill before they write or judge a line. For in-world text the cards and these rules decide, not a general prose style guide: a fragment, a dialect word, or a liar's hedge is often right in a character's mouth. Design notes, beat sheets, and voice cards themselves stay plain.

## Before you start

1. Run `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/knot.py" config` and read every path from its JSON. Exit code 2 means there's no `knot.toml`: stop, and offer to draft one with the canon skill's setup procedure in `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/setup.md`.
2. Read the `rules` list from the config. Every line answers to them.
3. Read `canon.voices` if it exists, and `canon.cast`: each speaker's want by point, their secret, and their turns.
4. Read `canon.conventions` for the project's inner voices, its Ink tags, and any house rules for speech. Read any other canon file the project keeps for words, such as a glossary or a list of passages a voice may echo.
5. When the work sits at a story point, read canon as of that point with the canon skill's `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/as-of.md`: who knows what, and which secrets the player may not learn yet.
6. Read `${CLAUDE_PLUGIN_ROOT}/skills/voice/references/dialogue.md`. Read `voice-card.md` beside it when writing a card.

## Workflow

Pick the job the request asks for.

### Write or revise a voice card

1. Find the speaker in `cast.md`. For an inner voice, find it in `conventions.md` and its entry in `state.toml`. A speaker canon lacks goes to the canon skill first.
2. Fill every field of the card shape in `voice-card.md`. Build the card from the speaker's want and secret: the voice is how the want leaks into speech.
3. Write three sample lines from situations in the story, each under a different pressure. Each must pass the card and `dialogue.md`.
4. Mark a new card, or a changed field, `[proposed]`, and list it in the file's `## Proposed` section. Anything a card implies that canon lacks, such as a habit, a past, or a tie to someone, is proposed too.
5. Run the distinctness test across every card (`dialogue.md`) and record it under `## Distinctness test`. If two voices blur, sharpen the cards, not only the lines.
6. Show the user. Only the user approves a card. When they do, remove its mark and its Proposed line.

### Check lines against the cards

The scene, ink, and review skills use this job. A user can ask for it directly.

1. For each line, find its speaker's card. A line whose speaker has no card is a finding.
2. Ask the questions in `dialogue.md` § "Checking a line": the card's words, rhythm, and never-says; the register for this pressure; the want; what the speaker knows; the setting's words; the project rules.
3. Report each failing line with its file, its place (stitch or section), the rule it breaks, and a rewrite in the speaker's voice. Change the draft only when the user or the calling skill's workflow asks.

## Rules

- **The card decides.** In-world text follows its speaker's card and `dialogue.md`. Where a general style rule disagrees, the card wins.
- **The cast entry comes first.** A card follows the speaker's want in `cast.md`. A voice that needs a new want, past, or secret goes to the canon skill.
- **Wants in every line.** Each line wants something from its listener. If it doesn't, give it a want or cut it.
- **Never-says are hard rules.** One broken never-say is a finding, even in a good line.
- **Secrets hold.** No line gives away a fact before its `reveal` point, except a planted clue in its innocent reading. A speaker says only what they know at that point (`knows` in `knowledge.toml`).
- **Inner voices notice; they never know.** They speak only to the player, perceive only what the player could, and never state a secret.
- **No pastiche, no modern idiom, no therapy language,** unless the setting is modern or a card calls for a heightened register.
- **The user decides canon.** Cards live in canon. A new card is proposed until the user approves it.

## References

- `${CLAUDE_PLUGIN_ROOT}/skills/voice/references/voice-card.md`: the layout of `voices.md`, the card's fields, and inner-voice cards.
- `${CLAUDE_PLUGIN_ROOT}/skills/voice/references/dialogue.md`: the craft rules, the line check, and the distinctness test.
- `${CLAUDE_PLUGIN_ROOT}/docs/project-contract.md` §3 (canon prose files) and §4 (`knowledge.toml`).

## Hand-off

- **After a card:** the user approves it. Then the scene skill (`/knot:scene`) or the ink skill (`/knot:ink`) can write the speaker's lines.
- **After a line check:** back to the skill or person that asked.
- **When a voice needs canon changed:** the canon skill (`/knot:canon`).
