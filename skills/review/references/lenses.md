# Review lenses

Each lens asks one question of a draft. This file gives the generic lenses in the order a review runs them, then says how a project's `[[rules]]` join. For each lens: its id, its question, what to read, and what it means at each layer.

"The point" means the draft's point or points, as the review skill's Before you start fixes them. "Canon as of the point" follows `${CLAUDE_PLUGIN_ROOT}/skills/canon/references/as-of.md`.

## Which lenses apply

| Lens | Spine | Treatment | Beats | Scene | Ink |
|---|---|---|---|---|---|
| `canon` | yes | yes | yes | yes | yes |
| `fidelity` | yes | yes | yes | yes | yes |
| `wants` | yes | yes | yes | yes | yes |
| `reveal` | yes | yes | yes | yes | yes |
| `fair_play` | yes | yes | yes | yes | yes |
| `choices` | endings | yes | yes | yes | yes |
| `failure` | no | light | yes | yes | yes |
| `voice` | no | quoted lines | sample lines | yes | yes |
| `state` | no | no | yes | light | yes |
| each `[[rules]]` id | yes | yes | yes | yes | yes |

"Light" means: check only what the layer names. `fair_play` runs only when `clues.toml` exists. `checks` isn't a lens. It is the id for findings from the project's `[checks]` commands and from `knot.py`.

## What reaches the player

Several lenses ask what the player sees, so settle it once for each layer.

- **Spine:** the events of each unit. The spine names its secret openly: that is design, not a leak.
- **Treatment:** **What happens**, **The player's options**, and the **What changed** bullets marked Public. **Wants and turns**, **Clues**, **Carries forward**, **Proposed**, and the What changed bullets marked Hidden are notes to the writer. Anything stated in What happens counts as shown unless the text marks it as unseen.
- **Beat sheet:** the choices, the check outcomes, the variants, the entry conditions as the player meets them, and each clue's first-play reading. The purpose, the wants, the second-play reading, and the rule checks are notes to the writer.
- **Scene:** every line, the narration, each choice label, each inner voice, and each presentation cue. A summarized branch stands for the lines it summarizes.
- **Ink:** every line of output and every choice on every path, and anything a tag displays.

A project template may add sections. Treat an added section as player-facing unless the template says otherwise.

## `canon`: canon consistency

**Question:** Does anything in the draft contradict canon as of its point?

**Read:** canon as of the point: `timeline.md`, `cast.md`, `knowledge.toml`, `clues.toml`, `state.toml`, the project extras, and the truth sources above canon.

**At each layer:**
- **Spine:** each unit's events against `timeline.md` for its points. Each ending against the cast's secrets and turns.
- **Treatment:** What happens, and Wants and turns, against `timeline.md` and each character's **By point** line. What changed against canon as of the unit's last point. Places and who is present, against the project's place source if it has one.
- **Beats:** the front matter `point` against `plant.point` and the `finds` points of each clue in `clues.toml`. State names against `state.toml`. Each character's stated want against `cast.md`.
- **Scene:** every stated fact, name, date, and place. Who knows what: a character who speaks of, hints at, or acts on a fact before their `knows.from` is a finding.
- **Ink:** as for the scene, on every path, plus anything the Ink adds that the scene lacks.

A draft that depends on a fact canon doesn't hold is a finding. Either the fact goes to canon as proposed, or the draft changes.

## `fidelity`: fidelity to the layer above

**Question:** Does the draft do everything the layer above asks of it, and nothing that contradicts it?

**Read:** the layer above. For the spine, canon and the truth sources above it. For a treatment, the spine's sections for its points. For a beat sheet, the treatment for its point and its row in `beats/index.md`. For a scene, its beat sheet. For Ink, its scene, or its beat sheet when there's no scene.

**At each layer:**
- **Spine:** every point in `points` falls in a unit, and every ending the truth sources name is there.
- **Treatment:** every event, clue, and turn the spine gives these points appears, and nothing contradicts the spine.
- **Beats:** the beat delivers its share of the treatment. Read all the beat sheets for the point together: each event, option, and clue in the treatment has a beat. The index row's point, status, and summary match the beat sheet.
- **Scene:** every choice, check, variant, state change, and clue in the beat sheet is in the scene. A choice or check the beat sheet lacks is a finding.
- **Ink:** every element of the scene is in the Ink, by the ink skill's mapping table. The knot name is the beat id.

Added detail is fine. An added fact is a canon change, and goes to canon as proposed.

## `wants`: wants trace

**Question:** Does every character action trace to that character's want at this point? Flag any action that only serves the plot.

**Read:** `cast.md`: each character's **Want**, their **By point** line for the point, and any **Turn**.

**At each layer:**
- **Spine:** each turn and each cover-up follows from a want.
- **Treatment:** each action in What happens traces to a want, and Wants and turns matches `cast.md`.
- **Beats:** "each one's want right now" matches `cast.md`. Each character's response to each choice follows from that want. The player's want is stated.
- **Scene:** each line of dialogue wants something. A character who volunteers what their want would make them hide is a finding.
- **Ink:** as for the scene, in every variant.

The fix changes the action, not the want. A want that should change goes through canon.

Suppose the p2 treatment has the mentor show the rival the receipt. That breaks the mentor's want at p2: to keep the secret hidden.

## `reveal`: reveal discipline

**Question:** Before a secret's reveal point, does anything that reaches the player give it away?

**Read:** every fact in `knowledge.toml` whose `reveal` is after the point; the `innocent` reading of every clue planted at or before it; `must_not_predict` in `[review.cold_read]`; and any project rule that guards a secret.

**How:**
1. List the secrets still hidden at the point: the facts whose `reveal` is after it. For a spine, or a treatment that spans several points, list them per point.
2. Read what reaches the player (see above) for each one.
3. Grade each hit:
   - It states the secret, or makes it the only sensible reading: **blocker**.
   - It hints so a careful first-time reader would likely guess right: **should fix**.
   - It foreshadows with a working innocent reading: fine. A thin innocent reading is a **note**.

Common leaks: a character who knows the secret says too much; narration tells the player what a knowing character thinks; a clue arrives with its meaning instead of its innocent reading; a choice label or check outcome names the secret; an inner voice knows more than the player character.

**At each layer:**
- **Spine:** the events planned for the units before the reveal.
- **Treatment:** What happens, The player's options, and the Public bullets of What changed. Each clue planted before the reveal has an innocent reading under Clues.
- **Beats:** the choices, check outcomes, variants, and each plant's first-play reading.
- **Scene:** every line, the narration, and every inner voice, on the main branch and in each summary.
- **Ink:** every path that can run before the reveal, including conditional lines.

The cold-read test (`fresh-readers.md`) checks the same thing across a whole layer, with a reader who knows nothing.

**Worked check: a p2 treatment.** `story/treatment/p2.md` has `points = ["p2"]`. The only fact whose `reveal` is after p2 is `secret`, revealed at p3. Read What happens, The player's options, and the Public bullets of What changed for it.
- Suppose What happens has the mentor name the secret aloud. That states `secret` at p2. It is a blocker under `reveal`, against `story/canon/knowledge.toml facts.secret` (`reveal = "p3"`).
- Suppose it has the player work out the secret from the receipt. The player character reaches the secret early: also a blocker. Canon has no `knows` entry for `player` on `secret`, so `canon` finds it too. Merge the two into one finding.
- Suppose instead the rival reads the receipt twice, sets it aside, and changes manner. The player sees the rival's manner, not the reason, and the receipt reads as a quiet season. That passes. The rival's turn is named under Wants and turns, which is a note to the writer, not a leak.

## `fair_play`: fair play

Runs only when `clues.toml` exists.

**Question:** Can the player reach every deduction the story needs from clues it actually plants, with each required clue findable `min_routes` ways, and without proving what must stay unproven?

**Read:** `clues.toml`; the deductions in `knowledge.toml`; `min_routes` in `[clues]`; `[review.solver]`; and the `plants` and `finds` in every beat sheet's front matter.

`knot.py check` counts routes and plants (E7, E8, W2, W3, W4, W7). This lens checks what counting can't:
- the player can perceive the plant where it is planted, on every path, or a gate guarantees another route;
- the find routes are different routes, not two variants of one scene;
- each route can be reached: whatever gates it is set somewhere earlier;
- the clue's `text` supports what it `proves`;
- no findable clue, alone or with others, proves a `must_not_prove` deduction.

**At each layer:**
- **Spine:** each `must_prove` deduction has clues planted before its reveal and found after it. The plan doesn't rest on a single route.
- **Treatment:** Clues names each plant and find at its point, and What happens gives each one a place to happen.
- **Beats:** the front matter `plants` and `finds` match the body's **Clues planted** and **Clues found** lines. A plant on one choice path has a second route or a gate.
- **Scene:** the plant is on the page, with its `text` recognizable. A find happens where the beat sheet puts it.
- **Ink:** no plant sits behind a condition the beat sheet didn't ask for. Each gate's variable is set on some path before it is read.

The solver test (`fresh-readers.md`) checks the whole set, with a reader who sees only the findable clues.

## `choices`: choices that matter

**Question:** Does every choice change state, a relationship, or a later line? Flag funnels: options that differ in wording but lead to the same place and leave no trace.

**Read:** the target's choices; `state.toml`; and the beat sheets that read what this one sets.

**At each layer:**
- **Spine:** each ending is reached by decisions the player makes, not by the story deciding for them.
- **Treatment:** each item under The player's options costs something now or later, and Carries forward names what is remembered.
- **Beats:** each choice says what it costs and names the state it sets in `sets`. A later beat `reads` that state, or the treatment names the payoff. A delayed consequence the beat promises has a later beat that delivers it.
- **Scene:** the options in each choice block go somewhere different, or set something different.
- **Ink:** each option diverts or sets a variable, and later content reads it.

A choice that changes only the next reply is a **note**. A funnel presented as a decision that matters is **should fix**.

## `failure`: failure as content

**Question:** Does every failed check lead somewhere revealing, never to a dead end or to nothing?

**Read:** the target's checks, and the check format in `conventions.md`.

**At each layer:**
- **Spine:** doesn't apply.
- **Treatment:** only where it names a test the player can fail. The story goes on, with a cost or a different truth.
- **Beats:** each check names what failure reveals: about a character, about the world, or another route. A required clue behind a check has another route.
- **Scene:** the failure branch is written or summarized, with what it reveals and the state it sets.
- **Ink:** the failure path exists, can be reached, and neither ends the story nor loops back with nothing gained.

## `voice`: voice

**Question:** Does every line sound like its speaker's voice card, and can the speakers be told apart?

**Read:** load the voice skill (`${CLAUDE_PLUGIN_ROOT}/skills/voice/SKILL.md`) and its references, and the project's `canon/voices.md`.

**At each layer:**
- **Spine, treatment, and beats:** only quoted lines and sample lines.
- **Scene and Ink:** every line, inner voices included. Apply the voice skill's dialogue rules, and its distinctness test on a sample of lines from each speaker.

In-world text follows the voice cards. Don't apply general prose style rules to dialogue or narration.

## `state`: state hygiene

**Question:** Is every variable in `state.toml`, set somewhere and read somewhere, used as its `meaning` says, and not a duplicate of another?

**Read:** `state.toml`; the state kinds in `conventions.md`; the `reads` and `sets` of each beat sheet; and `globals.ink`.

`knot.py check` (E9, E12, W5, W6) and `knot.py ink` (I1 to I4, I7, I8) cover declarations and coverage. This lens checks the rest:
- a variable used against its `meaning` or its `kind`;
- a flag that duplicates an evidence item, a knowledge entry, or another flag;
- a variable read on a path where nothing has set it yet, when its default would be wrong there;
- a beat sheet whose body names state its front matter lacks, or the reverse;
- new state written as approved instead of proposed.

**At each layer:**
- **Spine and treatment:** don't apply. Items under Carries forward become state at the beat layer.
- **Beats:** the front matter `reads` and `sets` match the body's **State touched** line. New state is in `state.toml` as proposed.
- **Scene:** each summarized branch names the state it sets.
- **Ink:** each `VAR` and `LIST` in the globals file mirrors `state.toml`. Each variable set is read later. Each conditional tests the right variable.

## Project rules

Each `[[rules]]` entry in `knot.toml` joins the review as a lens.

- **Id:** the rule's `id`. Its findings carry that id as their lens.
- **Question:** the rule's `ask`. A rule is phrased so one answer is a finding. In knot's examples, that answer is "yes".
- **Read:** the files in its `see`, and the target.
- **Layers:** every layer, unless the `ask` limits itself. A beat sheet answers each rule under **Rule checks**. Answer the rule yourself, then compare: a self-check that misses a problem is part of the finding.
- **Severity:** a rule broken in what reaches the player is a **blocker**. A rule bent, or broken only in a note to the writer, is **should fix**.

Project rules run after the generic lenses, in the order `knot.toml` lists them. Generic lens ids are reserved. If a rule reuses one, run both, and ask the user to rename the rule.
