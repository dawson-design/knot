+++
id = ""            # the scene id: the file name without .md, matching [ink] knot
point = ""         # one of [timeline] points
status = "draft"   # draft | review | approved. The skill sets review at hand-over; only the user sets approved
plants = []        # clue ids from clues.toml planted here
finds = []         # clue ids from clues.toml found here
reads = []         # state names from state.toml read here
sets = []          # state names from state.toml set here
pattern = []       # any of: foldback, delayed_consequence, gate, failed_check, hard_split
+++

# Beat: <id>

<!--
knot's default beat-sheet template. Copy it to <beats path>/<id>.md. Keep the front matter
first in the file (contract §5). Replace each comment with what it asks for, and delete the
comments as you go. Keep every field; write "none." in one that has nothing.
-->

- **Point / place:** <!-- The point, a comma, then the place. Cite the project's place ids when it defines them. -->
- **Purpose in the story:** <!-- One sentence: what this scene does for its treatment. -->
- **Characters present, and each one's want right now:** <!-- One sub-bullet each, "Name: want", from cast.md "By point", narrowed to this scene. Mark anyone offstage. -->
- **What the player wants here:** <!-- The player character's want at this point, narrowed to this scene. -->
- **Entry conditions:** <!-- When the scene can play. Any gate, and the route for a player who doesn't meet it. -->
- **Choices, and what each costs:** <!-- Two to four, as a numbered sub-list. Each costs something now or later, and names the state it sets. -->
- **Skill checks, and what failure reveals:** <!-- One sub-bullet per check: the skill and difficulty, what success gives, and what failure reveals. -->
- **Variants:** <!-- One sub-bullet per branch, a line or two each: how the scene plays on that path, and where the paths meet. -->
- **State touched:** <!-- "reads ...; sets ...", with the same names as the front matter, and how each changes. -->
- **Delayed consequences:** <!-- What pays off later, at which point, and in which beat when it exists. -->
- **Clues planted:** <!-- The ids in plants. For each: how it reads on a first play, and on a second. -->
- **Clues found:** <!-- The ids in finds, and the route by which each is found here. -->
- **Branching pattern:** <!-- The patterns in the front matter, in words, with where the branches meet. -->
- **Rule checks:** <!-- One sub-bullet per project rule: the rule id in backticks, the answer to its ask, and why, in a line. -->
- **Estimated words:** <!-- Rough length of the finished scene. -->
- **Proposed:** <!-- Each new fact, clue, or state entry this beat needs, marked [proposed]. -->
