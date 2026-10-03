# Fanning out a big review

A big review runs one lens per subagent, in parallel, and merges what they return. Each subagent reads only what its lens needs, so no lens crowds out another.

## Who can fan out

Only the top-level session. A subagent can't spawn subagents. A review running inside a subagent, such as one a producer briefed to review a layer, runs its lenses in sequence, in one context, in the order `lenses.md` gives. It can't run the fresh-reader tests either: it lists them under Not checked and hands them back to the session that briefed it.

If you have no tool for starting subagents, you are inside one.

## When to fan out

Fan out when the review covers a whole layer, several files, or a gate, and more than three lenses apply. Review a single beat sheet or scene in sequence: starting subagents costs more than it saves.

## Steps

1. **Run the checks once.** The top-level session runs the `[checks]` commands, `knot.py check` (with `--strict` before a beat gate or story lock), and `knot.py ink` for Ink. It turns their issues into findings, per `findings.md`.
2. **List the lenses.** Take the generic lenses that apply to the layer (`lenses.md`), then each project rule. Drop any that can't run, and record why for Not checked.
3. **Brief one subagent per lens,** all in one message so they run in parallel. Start each as a new subagent, with only its brief. Use absolute paths from the config (`project_dir` and `plugin_root`), since a subagent may not have `${CLAUDE_PLUGIN_ROOT}` set:

   ```
   Review a story draft through one lens and return your findings as text.
   Don't edit any file, and don't write a report.

   Project: <project_dir>
   Target: <files>; layer <layer>; points <points>
   Lens: <id>

   Run: uv run "<plugin_root>/scripts/knot.py" config --project "<project_dir>"
   and read every path from its JSON.

   Then read <plugin_root>/skills/review/SKILL.md and follow it in single-lens
   mode (--lens <id>): skip the checks, and apply only this lens, as
   <plugin_root>/skills/review/references/lenses.md defines it. Use the finding
   format in <plugin_root>/skills/review/references/findings.md.

   Return every finding with its severity, lens, where, problem, and suggested
   fix, citing the source entry for each. If you find nothing, say
   "No findings" and list what you read.
   ```

   For a project rule, add its `ask` and `see` to the brief. For `voice`, add that the subagent loads the voice skill at `<plugin_root>/skills/voice/SKILL.md`.

4. **Merge.** Collect every subagent's findings with the check findings. De-duplicate per `findings.md`: one problem, one finding, the highest severity, every lens listed.
5. **Confirm the blockers.** Before a blocker goes in the report, read the source it cites. A subagent can misread a point or a `knows` entry. Drop or downgrade a finding that doesn't hold, and say so in the report.
6. **Rank and write** one report, per `findings.md`. Under **Lenses**, say the review fanned out.
7. **Run the fresh-reader tests** if they are due, per `fresh-readers.md`. Each needs its own fresh subagent.

## Sequence mode

Inside a subagent, or for a small review, run everything in one context:

1. Run the checks, as in step 1, unless the brief says the caller ran them.
2. Apply each lens in turn, in `lenses.md` order, then the project rules in `knot.toml` order. Read the target once, and re-read only what each lens adds.
3. Merge, rank, and write the report the same way. Under **Lenses**, say the review ran in sequence.

A review briefed inside a subagent returns its findings, or writes the report if its brief asks for one. It never starts the fresh-reader tests.
