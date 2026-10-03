# The scene index

`beats/index.md` lists every scene in the story, one row per beat sheet, in play order. It is the scene list the user approves before the beat sheets are written, and the map from the treatments to the sheets afterwards. It has no front matter (contract §5), and `knot.py` doesn't read it.

## Shape

```markdown
# Scene index

| Id | Point | Status | Summary |
|---|---|---|---|
| `office_p1_first_day` | p1 | approved | The player's first day in the office; `c_record` planted |
| `depot_p2_audit` | p2 | draft | The player helps with the audit; `c_receipt` planted |
| `office_p3_confrontation` | p3 | draft | The player puts the record and the receipt together; the mentor turns |
```

That is the whole index for a three-point placeholder project. The file holds the title and the one table, nothing else.

## Columns

| Column | Holds |
|---|---|
| Id | The scene id in backticks. It matches `[ink] knot`, and it is the beat sheet's file name without `.md`. |
| Point | One point from `[timeline] points`: the beat sheet's `point`. |
| Status | The beat sheet's `status`: `draft`, `review`, or `approved`. A scene listed before its sheet exists is `planned`. |
| Summary | One line: who does what, and the turn or the clue it carries. |

## Rules

- **Play order.** Rows run by point, in `[timeline] points` order. Within a point, they run in the order the player meets them on the main path. A scene the player can meet in any order sits where the treatment first mentions it.
- **One row per scene.** Every beat sheet has a row, and every row has a beat sheet or the status `planned`.
- **Status mirrors the sheet.** When a sheet's status changes, change its row in the same edit. Only the user approves a sheet; the row follows.
- **Cut from an approved treatment.** Every row comes from a treatment that is approved, or that the user said to go ahead on.
- **Ids are stable.** Once a beat sheet exists, its id doesn't change without the user's word. Ink knots and scene files share it.
