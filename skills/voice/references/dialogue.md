# Dialogue rules

These rules hold for all in-world text: dialogue, narration, choice text, and inner voices. The voice cards set how each speaker sounds; these rules hold for every speaker. Where a general prose rule disagrees, these win inside the game's text. Examples use the contract's placeholder project.

## Every line wants something

Each line wants something from its listener: an answer, an end to the talk, comfort, time, a favor, to be believed. Name the want before writing the line. It traces to the speaker's want at this point in `cast.md`.

A line that wants nothing is exposition in a costume. Give it a want or cut it.

> "That page was damaged."

The mentor wants the talk to end. A plain excuse closes it.

## People dodge

People rarely answer the question they were asked. They:

- answer a smaller or different question
- ask one back
- give an order or start a job
- talk about the weather, the work, or the price of things
- go silent, shown by a line of narration

Direct answers are rarer, and land harder for it. Each card says how its speaker dodges; use that way, not a general one.

## People interrupt and trail off

They cut in, lose the thread, and leave things unsaid. In a game, text arrives a box at a time, so use it sparingly. Cut a line at its last whole word, and let the next speaker start. Mark the cut the way `conventions.md` says; without a rule, end the line with an ellipsis.

## Subtext

What a character wants and what they say are different. The line carries the want sideways, and the player supplies the feeling. A character who explains their own feelings in full sentences has stopped being a person. Save the plain statement for a turn, where its plainness is the point.

> "Every entry in that record is mine."

The mentor is proud, and afraid for the one entry that isn't there. The line says neither.

## The setting flavors the words

The setting shows in a few chosen words: the trade, the place, the period. One such word every few lines is plenty. Ordinary words do most of the work.

- Take setting words from the project's canon (a glossary, `voices.md` § House style), not from memory of other books.
- Carry dialect in word choice and grammar, never in spelling. No dropped letters marked with apostrophes, no phonetic spellings.
- Check a doubtful word's first use in a dictionary when the period matters.

## No pastiche

Pastiche copies the surface of a period's writing: archaic grammar, stock phrases, ornament. Write people who sound like themselves in their time, plainly. A heightened register is allowed only where a card calls for it, and then it is sincere, kept to that card, and used sparingly.

## No modern idiom or therapy language

Unless the setting is modern, flag phrases like these:

- "reach out", "on the same page", "at the end of the day", "move on", "no worries", "it is what it is"
- "process" or "unpack" a feeling, "boundaries", "closure", "trauma", "toxic", "validate", "I hear you"

People in most settings show feeling through action and sideways talk, not by naming it in clinical terms.

## Keep lines short

One to three sentences per line. A longer speech becomes several lines with the same speaker, each one a beat the player clicks through. A line that needs a fourth sentence usually holds two beats.

## Narration

- Present tense, plain, in short paragraphs.
- Close to the player character: what they see, hear, and do.
- It shows; it doesn't explain what the dialogue already showed.
- It never names a feeling the player character couldn't see in someone else. "He looks at the window, not at her," not "He is ashamed."

## Choice text

- Written in the player character's voice card.
- Each option is a different intent, not a rewording of the same one.
- Short: what the player does or says, never what will happen.
- A choice that the player character says aloud follows the scene format: the option text, then a spoken line in the branch.

## Inner voices

- They speak only to the player.
- They know only what the player could perceive or remember.
- They notice; they never know. Two details side by side, never what they mean.
- They never state a secret, before its reveal or after.
- They speak rarely. A voice that comments on everything stops being heard.

## Secrets hold

- No line gives away a fact before its `reveal` point in `knowledge.toml`. A planted clue may appear, in its innocent reading.
- A speaker says only what they know at this point, by `knows` in `knowledge.toml`.
- A character may lie. The lie follows their card's "Dodges and lies", and canon records what is true.

## Project rules

Every `[[rules]]` ask in `knot.toml` applies to every line. The placeholder project's `no_villains`, for instance, asks whether anyone acts from malice rather than from a want they could explain. A mentor who sneers at the player for no reason fails it. A mentor who sends the player off on a task, to keep the record out of reach, passes.

## Checking a line

Ask these questions of each line. A "no" is a finding.

1. **Card.** Does it use the speaker's words and rhythm? Does it keep every never-say?
2. **Pressure.** Which pressure is the speaker under here? Does the line take that register?
3. **Want.** What does the line want from its listener? Does that trace to the speaker's want at this point?
4. **Knowledge.** Does the speaker know this at this point? Does the line keep every secret whose reveal is later?
5. **Setting.** Are the setting's words in proportion? Is it free of pastiche, modern idiom, and therapy language?
6. **Length.** Is it one to three sentences?
7. **Rules.** Does it pass every project rule?

For narration, choice text, and inner voices, ask the questions their sections above add.

## The distinctness test

Every voice must be recognizable without its speaker tag.

1. Pick one plain line any speaker could say, such as a remark on the weather or a refusal.
2. Render it in each voice, following each card. Characters and inner voices both.
3. List the renderings without speaker tags, in shuffled order. Put the key after the list.
4. A reader who knows the cards should match every rendering to its speaker. Each rendering should also show its speaker's want.
5. If two renderings blur, sharpen the cards: vocabulary, rhythm, never-says. Then render again.

Record the latest run in `voices.md` under `## Distinctness test`: the plain line, the shuffled renderings, the key, and the result. Run it whenever a card is added or changed, and before a voice review.

The same test works on a scene. Strip the speaker labels from a page of dialogue. If you can't tell who speaks, the voices have blurred.

A placeholder run, on the line "Something has changed":

1. "I count three changes since yesterday. I'll note each one."
2. "Nothing has changed. Back to work."
3. "A chair moved. A drawer open."
4. "Something's different. I'll ask about it."

Key: 1 rival, 2 mentor, 3 notice, 4 player.
