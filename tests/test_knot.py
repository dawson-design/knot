"""Tests for scripts/knot.py against docs/project-contract.md.

Each rule test starts from `base_files()`, a small project that passes every
rule with no warnings, changes one thing, and asserts which codes fire. The
base passing cleanly is the "doesn't fire" half for every code; most tests
also check a near miss. Fixtures are written to temporary folders and read
back through the same path the commands use. Run with:

    uv run python -m unittest discover tests
"""

import contextlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "knot.py"


def load_script():
    """Import scripts/knot.py as a module, since scripts/ isn't a package."""
    spec = importlib.util.spec_from_file_location("knot", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["knot"] = module
    spec.loader.exec_module(module)
    return module


knot = load_script()

KNOT = "knot.toml"
CAST = "story/canon/cast.md"
TIMELINE = "story/canon/timeline.md"
KNOWLEDGE = "story/canon/knowledge.toml"
CLUES = "story/canon/clues.toml"
STATE = "story/canon/state.toml"
P1_BEAT = "story/beats/office_p1_first_day.md"
P3_BEAT = "story/beats/office_p3_confrontation.md"
SCENE = "story/scenes/office_p1_first_day.md"
GLOBALS = "story/ink/globals.ink"
MAIN = "story/ink/main.ink"
EARLY = "story/treatment/b_early.md"
LATE = "story/treatment/a_late.md"

BASE = {
    KNOT: """\
[project]
name = "Mini"
root = "story"

[timeline]
points = ["p1", "p2", "p3"]

[ink]
knot = "^(office|depot)_{point}_[a-z0-9_]+$"
tags = ["speaker"]

[review.cold_read]
before = "p3"
layers = ["treatment"]
sections = ["What happens"]
must_not_predict = "that the mentor covered up the secret"

[review.solver]
must_prove = ["d_cover"]
must_not_prove = ["d_ordered"]

[[rules]]
id = "no_villains"
ask = "Does anyone act from malice?"
see = ["story/canon/cast.md"]
""",
    CAST: "# Cast\n\n## player\n\nThe player.\n\n## mentor\n\nThe mentor.\n",
    TIMELINE: "# Timeline\n\n## p1\n\n## p2\n\n## p3\n",
    "story/canon/changelog.md": "# Changelog\n\n- 2026-10-03: Seeded.\n",
    KNOWLEDGE: """\
[facts.secret]
text = "What the mentor hides."
true_from = "p1"
reveal = "p3"
knows = [{ who = "mentor", from = "p1" }]

[deductions.d_cover]
claim = "The mentor covered it up."

[deductions.d_ordered]
claim = "Someone else ordered the cover-up."
""",
    CLUES: """\
[clues.c_record]
text = "A record with one entry removed."
proves = ["d_cover"]
required = true
innocent = "The mentor says the record was damaged."
plant = { point = "p1", where = "the office" }
finds = [
  { point = "p3", how = "Read the record." },
  { point = "p3", how = "Ask the clerk." },
]
""",
    STATE: """\
[state.rel_mentor]
type = "int"
kind = "relationship"
default = 0
meaning = "How far the mentor trusts the player."

[state.evidence]
type = "list"
kind = "evidence"
items = ["c_record"]
default = []
meaning = "What the player holds."
""",
    "story/beats/index.md": "# Scene index\n",
    P1_BEAT: """\
+++
id = "office_p1_first_day"
point = "p1"
status = "draft"
plants = ["c_record"]
finds = []
reads = ["rel_mentor"]
sets = ["evidence"]
pattern = ["foldback"]
+++

# Beat: first day
""",
    P3_BEAT: """\
+++
id = "office_p3_confrontation"
point = "p3"
status = "draft"
plants = []
finds = ["c_record"]
reads = ["evidence"]
sets = ["rel_mentor"]
pattern = ["gate"]
+++

# Beat: confrontation
""",
    "story/treatment/b_early.md": """\
+++
points = ["p1"]
status = "approved"
+++

# Treatment: the first part

## What happens

The player arrives and starts work.

<!-- Note to self: the record matters later. -->

## Clues

- c_record: planted.
""",
    "story/treatment/a_late.md": """\
+++
points = ["p2"]
status = "draft"
+++

## What happens

The rival checks the accounts.
""",
    "story/treatment/c_end.md": """\
+++
points = ["p3"]
status = "draft"
+++

## What happens

The truth comes out.
""",
    SCENE: """\
+++
id = "office_p1_first_day"
point = "p1"
status = "draft"
+++

The player opens the office.
""",
    GLOBALS: """\
// Global state. Mirrors canon/state.toml.
VAR rel_mentor = 0
LIST evidence = c_record
""",
    MAIN: """\
INCLUDE globals.ink

-> office_p1_first_day

=== office_p1_first_day ===
Time to start. # speaker: player
~ rel_mentor = rel_mentor + 1
~ evidence += c_record
-> END
""",
}


def base_files() -> dict[str, str]:
    """Return a copy of the clean base project."""
    return dict(BASE)


def edit(files: dict[str, str], path: str, old: str, new: str) -> dict[str, str]:
    """Replace the first `old` in a file with `new`. Fails if `old` is absent."""
    text = files[path]
    if old not in text:
        raise AssertionError(f"{old!r} is not in {path}")
    files[path] = text.replace(old, new, 1)
    return files


def append(files: dict[str, str], path: str, text: str) -> dict[str, str]:
    """Add text to the end of a file."""
    files[path] = files[path] + text
    return files


@contextlib.contextmanager
def project_dir(files: dict[str, str]):
    """Write the files to a temporary folder and yield its path."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for relative, text in files.items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        yield root


def open_files(files: dict[str, str]):
    """Write the files, then open them as `knot.py` does."""
    with project_dir(files) as root:
        return knot.open_project(root)


def check(files: dict[str, str]) -> tuple:
    """Return every `check` issue for the files."""
    result = open_files(files)
    if isinstance(result, knot.Rejected):
        return result.issues
    return knot.check_project(result)


def ink(files: dict[str, str]) -> tuple:
    """Return every `ink` issue for the files, without compiling."""
    result = open_files(files)
    if isinstance(result, knot.Rejected):
        return result.issues
    return knot.ink_issues(result)


def run_cli(*argv: str) -> tuple[int, str, str]:
    """Run knot.py's main. Returns (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = knot.main(list(argv))
    return code, out.getvalue(), err.getvalue()


def run(files: dict[str, str], *argv: str) -> tuple[int, str, str]:
    """Write the files and run a command against them with `--project`."""
    with project_dir(files) as root:
        return run_cli(*argv, "--project", str(root))


def codes(issues) -> set[str]:
    """Return the set of rule codes among issues."""
    return {issue.code for issue in issues}


class IssueAssertions(unittest.TestCase):
    """Assertions shared by the rule tests."""

    def assert_only(self, issues, *expected: str):
        """Assert exactly these codes fire, and at least one issue does."""
        self.assertTrue(issues, "expected at least one issue")
        self.assertEqual(codes(issues), set(expected), knot.format_report(issues))

    def assert_fires(self, issues, code: str):
        """Assert this code is among the issues."""
        self.assertIn(code, codes(issues), knot.format_report(issues))

    def assert_quiet(self, issues, code: str):
        """Assert this code is not among the issues."""
        self.assertNotIn(code, codes(issues), knot.format_report(issues))


class BaseTests(IssueAssertions):
    """The fixture every other test starts from."""

    def test_base_passes_check(self):
        self.assertEqual(check(base_files()), ())

    def test_base_passes_ink(self):
        self.assertEqual(ink(base_files()), ())


class CheckErrorTests(IssueAssertions):
    """E1 to E13, each firing and, where there is a near miss, not firing."""

    def test_e1_knot_toml_is_malformed(self):
        files = edit(base_files(), KNOT, "[project]\n", "[project\n")
        self.assert_only(check(files), "E1")

    def test_e1_required_key_is_missing(self):
        files = edit(base_files(), KNOT, 'name = "Mini"\n', "")
        self.assert_only(check(files), "E1")

    def test_e1_value_has_wrong_type(self):
        files = append(base_files(), KNOT, '\n[clues]\nmin_routes = "2"\n')
        self.assert_only(check(files), "E1")
        files = append(base_files(), KNOT, "\n[clues]\nmin_routes = 2\n")
        self.assertEqual(check(files), ())

    def test_e1_knot_pattern_is_not_a_regex(self):
        files = edit(base_files(), KNOT, 'knot = "^(office', 'knot = "^((office')
        self.assert_only(check(files), "E1")

    def test_e1_cold_read_layer_is_unknown(self):
        files = edit(base_files(), KNOT, 'layers = ["treatment"]', 'layers = ["spine"]')
        self.assert_only(check(files), "E1")

    def test_e1_extra_id_source_is_missing(self):
        extra = '[ids]\nextra = [{ file = "people.toml", table = "people" }]\n\n'
        files = edit(base_files(), KNOT, "[ink]", extra + "[ink]")
        self.assert_only(check(files), "E1")
        files["people.toml"] = "[people.clerk]\nname = 'the clerk'\n"
        self.assertEqual(check(files), ())

    def test_e1_path_is_not_relative(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            (Path(elsewhere) / "treatment").mkdir()
            (Path(elsewhere) / "treatment" / "a.md").write_text("x\n", encoding="utf-8")
            (Path(elsewhere) / "x.ink").write_text("x\n", encoding="utf-8")
            cases = [
                ('root = "story"', f'root = "{elsewhere}"'),
                ("[ink]\n", f'[ink]\ndir = "{elsewhere}"\n'),
            ]
            for old, new in cases:
                files = edit(base_files(), KNOT, old, new)
                with self.subTest(new=new):
                    self.assert_only(check(files), "E1")
                    for argv in (["config"], ["check"], ["ink"], ["packet", "solver"]):
                        code, out, err = run(files, *argv)
                        self.assertEqual(code, 1)
                        self.assertIn("isn't relative", out + err)

    def test_e1_deduction_in_both_solver_lists(self):
        old = 'must_not_prove = ["d_ordered"]'
        files = edit(
            base_files(), KNOT, old, 'must_not_prove = ["d_ordered", "d_cover"]'
        )
        self.assert_only(check(files), "E1")

    def test_e2_point_is_duplicated_or_badly_formed(self):
        files = edit(base_files(), KNOT, '"p3"]', '"p3", "p2"]')
        self.assert_only(check(files), "E2")
        files = edit(base_files(), KNOT, '"p3"]', '"p3", "Winter"]')
        self.assert_only(check(files), "E2")

    def test_e2_point_named_anywhere_is_in_the_timeline(self):
        cases = [
            (CLUES, '{ point = "p3", how = "Ask', '{ point = "winter", how = "Ask'),
            (P3_BEAT, 'point = "p3"', 'point = "winter"'),
            (KNOT, 'before = "p3"', 'before = "winter"'),
            (KNOWLEDGE, 'reveal = "p3"', 'reveal = "winter"'),
        ]
        for path, old, new in cases:
            with self.subTest(path=path):
                self.assert_only(check(edit(base_files(), path, old, new)), "E2")

    def test_e3_ledger_is_malformed(self):
        files = edit(base_files(), CLUES, "[clues.c_record]", "[clues.c_record")
        self.assert_only(check(files), "E3")

    def test_e3_entry_misses_a_field_or_has_the_wrong_type(self):
        cases = [
            (KNOWLEDGE, '\n[facts.extra]\ntrue_from = "p1"\n'),
            (KNOWLEDGE, "\n[deductions.d_extra]\nclaim = 5\n"),
            (KNOWLEDGE, '\n[deductions.d_extra]\nclaim = "x"\nstatus = "approved"\n'),
            (
                STATE,
                '\n[state.x]\ntype = "float"\nkind = "flag"\ndefault = 0\nmeaning = "x"\n',
            ),
            (
                STATE,
                '\n[state.x]\ntype = "list"\nkind = "flag"\ndefault = []\nmeaning = "x"\n',
            ),
            (CLUES, '\n[clues.x]\ntext = "x"\nplant = { where = "x" }\n'),
        ]
        for path, text in cases:
            with self.subTest(text=text):
                self.assert_only(check(append(base_files(), path, text)), "E3")

    def test_e3_malformed_entry_is_not_unknown(self):
        old = 'claim = "Someone else ordered the cover-up."'
        files = edit(base_files(), KNOWLEDGE, old, "claim = 5")
        self.assert_only(check(files), "E3")
        files = edit(base_files(), CLUES, "required = true", 'required = "yes"')
        self.assert_only(check(files), "E3")

    def test_e3_proposed_status_is_allowed(self):
        text = '\n[deductions.d_extra]\nclaim = "x"\nstatus = "proposed"\n'
        self.assertEqual(check(append(base_files(), KNOWLEDGE, text)), ())

    def test_e4_id_is_badly_formed_or_duplicated(self):
        rule = '\n[[rules]]\nid = "no_villains"\nask = "Again?"\n'
        self.assert_only(check(append(base_files(), KNOT, rule)), "E4")
        files = edit(base_files(), KNOT, 'id = "no_villains"', 'id = "No-Villains"')
        self.assert_only(check(files), "E4")
        fact = '\n[facts.Secret]\ntext = "x"\ntrue_from = "p1"\n'
        self.assert_only(check(append(base_files(), KNOWLEDGE, fact)), "E4")
        files = edit(
            base_files(),
            STATE,
            'items = ["c_record"]',
            'items = ["c_record", "c_record"]',
        )
        self.assert_only(check(files), "E4")
        self.assert_only(check(append(base_files(), CAST, "\n## mentor\n")), "E4")

    def test_e5_heading_is_not_an_id_or_point(self):
        self.assert_only(check(append(base_files(), CAST, "\n## Old Tom\n")), "E5")
        self.assert_only(check(append(base_files(), TIMELINE, "\n## winter\n")), "E5")
        self.assertEqual(check(append(base_files(), CAST, "\n### Old Tom\n")), ())

    def test_e5_ignores_fences_and_closing_hashes(self):
        files = append(
            base_files(), CAST, "\n```\n## Old Tom\n```\n\n~~~\n## Bad Id\n~~~\n"
        )
        self.assertEqual(check(files), ())
        files = edit(base_files(), CAST, "## mentor\n", "## mentor ##\n")
        self.assertEqual(check(files), ())

    def test_e6_who_is_unknown(self):
        files = edit(base_files(), KNOWLEDGE, 'who = "mentor"', 'who = "ghost"')
        self.assert_only(check(files), "E6")

    def test_e6_extra_ids_count(self):
        files = edit(base_files(), KNOWLEDGE, 'who = "mentor"', 'who = "ghost"')
        extra = '[ids]\nextra = [{ file = "world.toml", table = "people" }]\n\n'
        edit(files, KNOT, "[ink]", extra + "[ink]")
        files["world.toml"] = '[people.ghost]\nname = "a ghost"\n'
        self.assertEqual(check(files), ())

    def test_e6_waits_for_cast(self):
        files = edit(base_files(), KNOWLEDGE, 'who = "mentor"', 'who = "ghost"')
        del files[CAST]
        self.assert_only(check(files), "W1")

    def test_e7_clue_proves_unknown_deduction(self):
        files = edit(base_files(), CLUES, 'proves = ["d_cover"]', 'proves = ["secret"]')
        self.assert_only(check(files), "E7")

    def test_e7_solver_names_unknown_deduction(self):
        files = edit(
            base_files(), KNOT, 'must_prove = ["d_cover"]', 'must_prove = ["d_x"]'
        )
        self.assert_only(check(files), "E7")

    def test_e8_fact_reveals_before_true(self):
        files = edit(base_files(), KNOWLEDGE, 'true_from = "p1"', 'true_from = "p2"')
        edit(files, KNOWLEDGE, 'reveal = "p3"', 'reveal = "p1"')
        self.assert_only(check(files), "E8")
        files = edit(base_files(), KNOWLEDGE, 'reveal = "p3"', 'reveal = "p1"')
        self.assert_quiet(check(files), "E8")

    def test_e8_clue_found_before_planted(self):
        files = edit(base_files(), CLUES, 'point = "p1", where', 'point = "p2", where')
        edit(
            files,
            CLUES,
            '{ point = "p3", how = "Ask',
            '{ point = "p1", how = "Ask',
        )
        self.assert_fires(check(files), "E8")
        files = edit(
            base_files(),
            CLUES,
            '{ point = "p3", how = "Ask',
            '{ point = "p1", how = "Ask',
        )
        self.assert_quiet(check(files), "E8")

    def test_e9_default_does_not_fit(self):
        files = edit(base_files(), STATE, "default = 0", 'default = "0"')
        self.assert_only(check(files), "E9")
        files = edit(base_files(), STATE, "default = []", 'default = ["map"]')
        self.assert_only(check(files), "E9")
        files = edit(base_files(), STATE, "default = []", 'default = ["c_record"]')
        self.assertEqual(check(files), ())

    def test_e9_date_default_is_reported_not_a_crash(self):
        files = edit(base_files(), STATE, "default = 0", "default = 1979-05-27")
        self.assert_only(check(files), "E9")
        self.assert_only(ink(files), "I4")
        code, out, _err = run(files, "check")
        self.assertEqual(code, 1)
        self.assertIn("1979-05-27", out)

    def test_e10_front_matter_is_missing_or_bad(self):
        beat = "story/beats/depot_p2_extra.md"
        good = '+++\nid = "depot_p2_extra"\npoint = "p2"\nstatus = "draft"\n+++\n'
        cases = [
            "# Beat with no front matter\n",
            '+++\nid = "depot_p2_extra"\n',
            '+++\nid = "depot_p2_extra\n+++\n',
            '+++\nid = "depot_p2_extra"\npoint = "p2"\n+++\n',
            good.replace('"draft"', '"done"'),
            good.replace('point = "p2"', "point = 3"),
        ]
        for text in cases:
            with self.subTest(text=text):
                files = base_files()
                files[beat] = text
                self.assert_only(check(files), "E10")
        files = base_files()
        files[beat] = good
        self.assertEqual(check(files), ())

    def test_e10_treatment_needs_front_matter(self):
        files = base_files()
        files["story/treatment/extra/notes.md"] = "## What happens\n"
        self.assert_only(check(files), "E10")

    def test_e11_id_matches_file_and_knot(self):
        files = base_files()
        files["story/beats/depot_p2_x.md"] = (
            '+++\nid = "depot_p2_y"\npoint = "p2"\nstatus = "draft"\n+++\n'
        )
        self.assert_only(check(files), "E11")
        files = base_files()
        files["story/beats/shed_p2_x.md"] = (
            '+++\nid = "shed_p2_x"\npoint = "p2"\nstatus = "draft"\n+++\n'
        )
        self.assert_only(check(files), "E11")
        files = base_files()
        files["story/scenes/other.md"] = (
            '+++\nid = "office_p1_first_day"\npoint = "p1"\nstatus = "draft"\n+++\n'
        )
        self.assert_only(check(files), "E11")

    def test_e12_front_matter_names_unknown_clue_or_state(self):
        files = edit(
            base_files(),
            P3_BEAT,
            'finds = ["c_record"]',
            'finds = ["c_record", "ghost"]',
        )
        self.assert_only(check(files), "E12")
        files = edit(
            base_files(),
            P3_BEAT,
            'reads = ["evidence"]',
            'reads = ["evidence", "nope"]',
        )
        self.assert_only(check(files), "E12")

    def test_e12_waits_for_the_ledger(self):
        files = edit(
            base_files(),
            P3_BEAT,
            'finds = ["c_record"]',
            'finds = ["c_record", "ghost"]',
        )
        del files[CLUES]
        self.assert_only(check(files), "W5")

    def test_e13_scene_has_no_beat_sheet(self):
        files = base_files()
        files["story/scenes/office_p2_none.md"] = (
            '+++\nid = "office_p2_none"\npoint = "p2"\nstatus = "draft"\n+++\n'
        )
        self.assert_only(check(files), "E13")


class CheckWarningTests(IssueAssertions):
    """W1 to W9, each firing and not firing."""

    def test_w1_required_canon_file_missing(self):
        for path in (CAST, TIMELINE, "story/canon/changelog.md"):
            with self.subTest(path=path):
                files = base_files()
                del files[path]
                self.assert_only(check(files), "W1")

    def test_w1_optional_canon_file_missing_is_fine(self):
        files = base_files()
        self.assertNotIn("story/canon/voices.md", files)
        self.assertEqual(check(files), ())

    def test_w2_required_clue_has_too_few_finds(self):
        files = edit(
            base_files(), CLUES, '  { point = "p3", how = "Ask the clerk." },\n', ""
        )
        self.assert_only(check(files), "W2")
        append(files, KNOT, "\n[clues]\nmin_routes = 1\n")
        self.assertEqual(check(files), ())
        files = edit(
            base_files(), CLUES, '  { point = "p3", how = "Ask the clerk." },\n', ""
        )
        edit(files, CLUES, "required = true", "required = false")
        self.assertEqual(check(files), ())

    def test_w3_early_clue_has_no_innocent_reading(self):
        files = edit(
            base_files(),
            CLUES,
            'innocent = "The mentor says the record was damaged."\n',
            "",
        )
        self.assert_only(check(files), "W3")

    def test_w3_reads_the_earliest_reveal(self):
        clue = knot.Clue(
            "c", "t", ("d",), False, None, knot.Place("x", None), (), False
        )
        self.assertTrue(knot.needs_innocent(clue, plant=0, reveal=2))
        self.assertFalse(knot.needs_innocent(clue, plant=2, reveal=2))
        self.assertTrue(knot.needs_innocent(clue, plant=2, reveal=None))
        no_proves = knot.Clue(
            "c", "t", (), False, None, knot.Place("x", None), (), False
        )
        self.assertFalse(knot.needs_innocent(no_proves, plant=0, reveal=2))

    def test_w4_clue_not_planted_or_found_by_beats(self):
        clue = (
            '\n[clues.map]\ntext = "A map."\ninnocent = "x"\nplant = { point = "p2" }\n'
        )
        self.assert_only(check(append(base_files(), CLUES, clue)), "W4")
        files = edit(base_files(), P3_BEAT, 'finds = ["c_record"]', "finds = []")
        self.assert_only(check(files), "W4")

    def test_w4_and_w6_wait_for_beats(self):
        files = base_files()
        for path in (P1_BEAT, P3_BEAT, SCENE):
            del files[path]
        clue = (
            '\n[clues.map]\ntext = "A map."\ninnocent = "x"\nplant = { point = "p2" }\n'
        )
        append(files, CLUES, clue)
        append(
            files,
            STATE,
            '\n[state.x]\ntype = "bool"\nkind = "flag"\ndefault = false\nmeaning = "x"\n',
        )
        self.assertEqual(check(files), ())

    def test_w5_beat_names_a_missing_ledger(self):
        files = base_files()
        del files[STATE]
        self.assert_only(check(files), "W5")

    def test_w6_state_entry_unused_by_beats(self):
        entry = '\n[state.x]\ntype = "bool"\nkind = "flag"\ndefault = false\nmeaning = "x"\n'
        self.assert_only(check(append(base_files(), STATE, entry)), "W6")

    def test_w7_planted_clue_point_differs(self):
        files = edit(base_files(), CLUES, 'point = "p1", where', 'point = "p2", where')
        self.assert_only(check(files), "W7")

    def test_w8_unknown_pattern(self):
        files = edit(
            base_files(),
            P1_BEAT,
            'pattern = ["foldback"]',
            'pattern = ["flashback"]',
        )
        self.assert_only(check(files), "W8")
        files = edit(
            base_files(),
            P1_BEAT,
            'pattern = ["foldback"]',
            'pattern = ["hard_split"]',
        )
        self.assertEqual(check(files), ())

    def test_w9_unknown_key(self):
        cases = [
            (KNOT, 'root = "story"', 'root = "story"\ncolour = "red"'),
            (KNOT, "[ink]", "[colour]\nx = 1\n\n[ink]"),
            (CLUES, "required = true", "required = true\ncolour = 'red'"),
            (KNOWLEDGE, "[facts.secret]", "[colour]\nx = 1\n\n[facts.secret]"),
            (P1_BEAT, 'status = "draft"', 'status = "draft"\ncolour = "red"'),
        ]
        for path, old, new in cases:
            with self.subTest(path=path, new=new):
                self.assert_only(check(edit(base_files(), path, old, new)), "W9")


class InkTests(IssueAssertions):
    """I0 to I8."""

    def test_i1_declaration_outside_globals(self):
        files = append(base_files(), MAIN, "VAR stray = 1\n")
        self.assert_only(ink(files), "I1")

    def test_comments_are_not_declarations(self):
        files = append(base_files(), MAIN, "// VAR stray = 1\n/* LIST odd = a\n*/\n")
        self.assertEqual(ink(files), ())

    def test_i2_globals_declaration_has_no_state_entry(self):
        files = append(base_files(), GLOBALS, "VAR extra = 1\n")
        append(files, MAIN, "~ extra = 2\n")
        self.assert_only(ink(files), "I2")

    def test_i2_gives_way_to_a_malformed_entry(self):
        old = 'meaning = "How far the mentor trusts the player."\n'
        files = edit(base_files(), STATE, old, "")
        self.assert_only(ink(files), "E3")
        files = edit(base_files(), STATE, "[state.rel_mentor]", "[state.rel_mentor")
        self.assert_only(ink(files), "E3")

    def test_ink_dir_dot_under_root_dot(self):
        files = {path.removeprefix("story/"): text for path, text in BASE.items()}
        knot_toml = files[KNOT].replace('root = "story"', 'root = "."')
        knot_toml = knot_toml.replace("[ink]\n", '[ink]\ndir = "."\n')
        files[KNOT] = knot_toml.replace("story/canon", "canon")
        files["globals.ink"] = files.pop("ink/globals.ink")
        files["main.ink"] = files.pop("ink/main.ink")
        self.assertEqual(ink(files), ())
        self.assertEqual(check(files), ())

    def test_i3_approved_entry_not_declared(self):
        entry = '\n[state.x]\ntype = "bool"\nkind = "flag"\ndefault = false\nmeaning = "x"\n'
        self.assert_only(ink(append(base_files(), STATE, entry)), "I3")

    def test_i8_proposed_entry_not_declared(self):
        entry = '\n[state.x]\ntype = "bool"\nkind = "flag"\ndefault = false\nmeaning = "x"\nstatus = "proposed"\n'
        issues = ink(append(base_files(), STATE, entry))
        self.assert_only(issues, "I8")
        self.assertFalse(knot.has_errors(issues))

    def test_i4_declaration_differs_from_state(self):
        cases = [
            ("VAR rel_mentor = 0", "VAR rel_mentor = 1"),
            ("VAR rel_mentor = 0", 'VAR rel_mentor = "0"'),
            ("VAR rel_mentor = 0", "VAR rel_mentor = false"),
            ("VAR rel_mentor = 0", "LIST rel_mentor = a"),
            ("LIST evidence = c_record", "LIST evidence = c_record, map"),
            ("LIST evidence = c_record", "LIST evidence = (c_record)"),
            ("LIST evidence = c_record", "VAR evidence = 0"),
        ]
        for old, new in cases:
            with self.subTest(new=new):
                self.assert_only(ink(edit(base_files(), GLOBALS, old, new)), "I4")

    def test_i4_matching_list_default(self):
        files = edit(
            base_files(),
            GLOBALS,
            "LIST evidence = c_record",
            "LIST evidence = (c_record)",
        )
        edit(files, STATE, "default = []", 'default = ["c_record"]')
        self.assertEqual(ink(files), ())

    def test_i5_tag_not_allowed(self):
        files = edit(
            base_files(), MAIN, "# speaker: player", "# speaker: player # mood: grim"
        )
        self.assert_only(ink(files), "I5")
        files = edit(base_files(), MAIN, "# speaker: player", "\\# not a tag")
        self.assertEqual(ink(files), ())

    def test_i5_skips_logic_lines(self):
        files = append(base_files(), MAIN, '~ temp label = "#1"\n{label}\n')
        self.assertEqual(ink(files), ())

    def test_i6_knot_name_does_not_match(self):
        files = append(base_files(), MAIN, "\n=== start_here ===\n-> END\n")
        issues = ink(files)
        self.assert_only(issues, "I6")
        self.assertFalse(knot.has_errors(issues))
        files = append(
            base_files(), MAIN, "\n=== function double(x) ===\n~ return x * 2\n"
        )
        self.assertEqual(ink(files), ())

    def test_i7_declared_variable_never_mentioned(self):
        files = append(base_files(), GLOBALS, "VAR unused = 0\n")
        append(
            files,
            STATE,
            '\n[state.unused]\ntype = "int"\nkind = "flag"\ndefault = 0\nmeaning = "x"\n',
        )
        issues = ink(files)
        self.assert_only(issues, "I7")
        self.assertFalse(knot.has_errors(issues))

    def test_i0_compiler_output_becomes_errors(self):
        output = "ERROR: 'scenes/a.ink' line 3: Unexpected token\nWARNING: 'main.ink' line 1: x\n"
        issues = knot.compiler_issues(output, 1, "story/ink/main.ink")
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "I0")
        self.assertEqual(issues[0].file, "story/ink/scenes/a.ink")
        self.assertEqual(issues[0].entry, "line 3")
        self.assertEqual(knot.compiler_issues("", 0, "story/ink/main.ink"), ())
        self.assertEqual(codes(knot.compiler_issues("crash", 134, "m.ink")), {"I0"})

    def test_i0_reports_a_repeated_error_once(self):
        line = "ERROR: 'main.ink' line 4: Expected some kind of logic\n"
        issues = knot.compiler_issues(line + line, 1, "story/ink/main.ink")
        self.assertEqual(len(issues), 1)

    def test_i0_runs_inklecate_from_path(self):
        script = "#!/bin/sh\necho \"ERROR: 'main.ink' line 2: Bad thing\"\nexit 1\n"
        with tempfile.TemporaryDirectory() as tools:
            fake = Path(tools) / "inklecate"
            fake.write_text(script, encoding="utf-8")
            fake.chmod(0o755)
            path = tools + os.pathsep + os.environ.get("PATH", "")
            with mock.patch.dict(os.environ, {"PATH": path}):
                code, out, _err = run(base_files(), "ink")
        self.assertEqual(code, 1)
        self.assertIn("I0 story/ink/main.ink line 2: Bad thing.", out)
        self.assertNotIn(knot.COMPILE_SKIPPED, out)

    def test_compile_is_skipped_without_inklecate(self):
        with mock.patch.object(knot.shutil, "which", return_value=None):
            code, out, _err = run(base_files(), "ink")
        self.assertEqual(code, 0)
        self.assertEqual(out, "No issues.\n" + knot.COMPILE_SKIPPED + "\n")

    @unittest.skipUnless(shutil.which("inklecate"), "inklecate not on PATH")
    def test_base_compiles_with_inklecate(self):
        code, out, _err = run(base_files(), "ink")
        self.assertEqual(code, 0, out)


class ConfigTests(unittest.TestCase):
    """The `config` command's JSON."""

    def config(self, files: dict[str, str]) -> dict:
        code, out, err = run(files, "config")
        self.assertEqual(code, 0, err)
        return json.loads(out)

    def test_keys_and_paths(self):
        data = self.config(base_files())
        expected = {
            "project",
            "project_dir",
            "plugin_root",
            "root",
            "truth",
            "points",
            "paths",
            "canon",
            "templates",
            "clues",
            "ink",
            "checks",
            "rules",
            "review",
        }
        self.assertEqual(set(data), expected)
        self.assertEqual(data["project"], "Mini")
        self.assertEqual(data["plugin_root"], str(ROOT))
        self.assertEqual(data["truth"], ["story/canon/"])
        self.assertEqual(data["paths"]["beats"], "story/beats")
        self.assertEqual(data["paths"]["reviews"], "story/reviews")
        self.assertEqual(data["ink"]["dir"], "story/ink")
        self.assertEqual(data["clues"], {"min_routes": 2})
        self.assertEqual(data["rules"][0]["id"], "no_villains")
        self.assertEqual(data["review"]["solver"]["must_not_prove"], ["d_ordered"])

    def test_canon_lists_every_file_and_whether_it_exists(self):
        data = self.config(base_files())
        self.assertEqual(set(data["canon"]), set(knot.CANON_FILES))
        self.assertEqual(data["canon"]["cast"], {"path": CAST, "exists": True})
        self.assertFalse(data["canon"]["voices"]["exists"])

    def test_templates_default_to_the_plugin_and_honour_overrides(self):
        data = self.config(base_files())
        self.assertEqual(
            data["templates"]["beat"], str(ROOT / "skills/beats/references/beat.md")
        )
        files = edit(
            base_files(), KNOT, 'root = "story"', 'root = "story"\ntemplates = "tpl"'
        )
        files["tpl/beat.md"] = "# Beat\n"
        data = self.config(files)
        self.assertEqual(data["templates"]["beat"], "tpl/beat.md")
        self.assertTrue(Path(data["templates"]["spine"]).is_absolute())

    def test_unset_ink_and_review_values(self):
        files = edit(base_files(), KNOT, 'tags = ["speaker"]\n', "")
        files[KNOT] = files[KNOT].split("[review.cold_read]")[0]
        data = self.config(files)
        self.assertIsNone(data["ink"]["tags"])
        self.assertEqual(data["ink"]["main"], "main.ink")
        self.assertEqual(data["review"], {"cold_read": {}, "solver": {}})

    def test_bad_knot_toml_exits_1_with_report(self):
        code, out, err = run(
            edit(base_files(), KNOT, "[project]\n", "[project\n"), "config"
        )
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("E1 knot.toml", err)


class PacketTests(unittest.TestCase):
    """`packet cold-read` and `packet solver`, with and without `--key`."""

    def test_cold_read_shows_chosen_sections_as_parts(self):
        code, out, _err = run(base_files(), "packet", "cold-read")
        self.assertEqual(code, 0)
        self.assertLess(out.index("The player arrives"), out.index("The rival checks"))
        self.assertTrue(out.startswith("# Part 1\n\n## What happens"))
        self.assertIn("# Part 2", out)
        for leak in (
            "inquiry",
            "+++",
            "status",
            "Note to self",
            "## Clues",
            "b_early",
            ".md",
            "first part",
        ):
            self.assertNotIn(leak, out)

    def test_cold_read_with_no_sections_keeps_the_body(self):
        files = edit(base_files(), KNOT, 'sections = ["What happens"]\n', "")
        _code, out, _err = run(files, "packet", "cold-read")
        self.assertIn("# Treatment: the first part", out)
        self.assertIn("## Clues", out)
        self.assertNotIn("Note to self", out)

    def test_cold_read_key(self):
        code, out, _err = run(base_files(), "packet", "cold-read", "--key")
        self.assertEqual(code, 0)
        self.assertIn("- Part 1: story/treatment/b_early.md", out)
        self.assertIn("- Part 2: story/treatment/a_late.md", out)
        self.assertNotIn("c_end", out)
        self.assertIn("Must not predict: that the mentor covered up the secret", out)

    def test_solver_shows_clue_text_and_claims_only(self):
        code, out, _err = run(base_files(), "packet", "solver")
        self.assertEqual(code, 0)
        self.assertIn("1. A record with one entry removed.", out)
        self.assertIn("- Claim A: The mentor covered it up.", out)
        self.assertIn("- Claim B: Someone else ordered the cover-up.", out)
        for leak in (
            "d_cover",
            "d_ordered",
            "c_record",
            "proves",
            "damaged",
            "the office",
            "provable",
            "p1",
        ):
            self.assertNotIn(leak, out)

    def test_solver_falls_back_to_ledger_finds(self):
        files = edit(base_files(), P3_BEAT, 'finds = ["c_record"]', "finds = []")
        _code, out, _err = run(files, "packet", "solver")
        self.assertIn("A record with one entry removed.", out)
        files = edit(files, CLUES, "finds = [", "finds = []\nold_finds = [")
        _code, out, _err = run(files, "packet", "solver")
        self.assertNotIn("A record with one entry removed.", out)

    def test_solver_key(self):
        code, out, _err = run(base_files(), "packet", "solver", "--key")
        self.assertEqual(code, 0)
        self.assertIn("| A | `d_cover` | provable |", out)
        self.assertIn("| B | `d_ordered` | not provable |", out)

    def test_packets_exit_2_without_review_tables(self):
        files = base_files()
        files[KNOT] = files[KNOT].split("[review.cold_read]")[0]
        for kind in ("cold-read", "solver"):
            for key in ((), ("--key",)):
                with self.subTest(kind=kind, key=key):
                    code, out, _err = run(files, "packet", kind, *key)
                    self.assertEqual(code, 2)
                    self.assertEqual(out, "")

    def test_solver_with_unknown_claim_exits_1(self):
        files = edit(
            base_files(), KNOT, 'must_prove = ["d_cover"]', 'must_prove = ["d_x"]'
        )
        code, out, err = run(files, "packet", "solver")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn('E7 knot.toml review.solver: names unknown deduction "d_x".', err)

    def test_solver_with_unreadable_claim_exits_1(self):
        old = 'claim = "Someone else ordered the cover-up."'
        files = edit(base_files(), KNOWLEDGE, old, "claim = 5")
        code, out, err = run(files, "packet", "solver")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("E3", err)
        files = edit(base_files(), KNOWLEDGE, "[facts.secret]", "[facts.secret")
        code, out, err = run(files, "packet", "solver", "--key")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("E3", err)

    def test_packets_exit_1_on_knot_toml_errors(self):
        cases = [
            ('before = "p3"', 'before = "winter"', "E2"),
            ('"p3"]', '"p3", "p2"]', "E2"),
            ("[project]\n", "[project\n", "E1"),
        ]
        for old, new, code_name in cases:
            files = edit(base_files(), KNOT, old, new)
            for argv in (["cold-read"], ["cold-read", "--key"], ["solver"]):
                with self.subTest(new=new, argv=argv):
                    code, out, err = run(files, "packet", *argv)
                    self.assertEqual((code, out), (1, ""))
                    self.assertIn(code_name, err)

    def test_cold_read_hides_an_unclosed_comment(self):
        note = "<!-- Note to self: the record matters later. -->"
        leak = "<!-- Note to self.\n\n## What happens\n\nSECRET-LEAK"
        _code, out, _err = run(
            edit(base_files(), EARLY, note, leak), "packet", "cold-read"
        )
        self.assertIn("The player arrives", out)
        self.assertNotIn("SECRET-LEAK", out)

    def test_cold_read_ignores_headings_in_fences(self):
        for fence in ("```", "~~~"):
            block = f"- c_record: planted.\n\n{fence}\n## What happens\n{fence}\n\nFENCE-LEAK"
            files = edit(base_files(), EARLY, "- c_record: planted.", block)
            with self.subTest(fence=fence):
                _code, out, _err = run(files, "packet", "cold-read")
                self.assertNotIn("FENCE-LEAK", out)
                self.assertIn("The player arrives", out)

    def test_cold_read_accepts_closing_hashes(self):
        files = edit(base_files(), LATE, "## What happens", "## What happens ##")
        _code, out, _err = run(files, "packet", "cold-read")
        self.assertIn("The rival checks the accounts.", out)

    def test_letters(self):
        labels = [knot.letters(i) for i in (0, 1, 25, 26, 27)]
        self.assertEqual(labels, ["A", "B", "Z", "AA", "AB"])


class ExitCodeTests(unittest.TestCase):
    """0 clean, 1 errors, 2 usage error or no knot.toml."""

    def test_clean_check_exits_0(self):
        self.assertEqual(run(base_files(), "check"), (0, "No issues.\n", ""))

    def test_warnings_exit_0_unless_strict(self):
        files = base_files()
        del files[CAST]
        code, out, _err = run(files, "check")
        self.assertEqual(code, 0)
        self.assertIn("Warnings (1):\n  W1 story/canon/cast.md:", out)
        code, out, _err = run(files, "check", "--strict")
        self.assertEqual(code, 1)
        self.assertIn("Errors (1):\n  W1 story/canon/cast.md:", out)

    def test_errors_exit_1_in_report_format(self):
        files = edit(base_files(), CLUES, 'proves = ["d_cover"]', 'proves = ["d_x"]')
        code, out, _err = run(files, "check")
        self.assertEqual(code, 1)
        expected = (
            "Errors (1):\n"
            '  E7 story/canon/clues.toml clues.c_record: proves unknown deduction "d_x".\n'
            "1 error(s), 0 warning(s).\n"
        )
        self.assertEqual(out, expected)

    def test_bad_knot_toml_exits_1(self):
        files = edit(base_files(), KNOT, "[project]\n", "[project\n")
        self.assertEqual(run(files, "check")[0], 1)
        self.assertEqual(run(files, "ink")[0], 1)

    def test_no_knot_toml_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            for command in ("config", "check", "ink"):
                code, _out, err = run_cli(command, "--project", tmp)
                self.assertEqual(code, 2)
                self.assertIn("no knot.toml", err)

    def test_usage_error_exits_2(self):
        self.assertEqual(run_cli("bogus")[0], 2)
        self.assertEqual(run_cli("packet", "story")[0], 2)
        self.assertEqual(run_cli()[0], 2)

    def test_project_is_found_by_walking_up(self):
        with project_dir(base_files()) as root:
            nested = root / "story" / "beats"
            self.assertEqual(knot.find_project(nested.resolve()), root.resolve())
            self.assertEqual(knot.locate(None, nested), root.resolve())
            self.assertIsNone(knot.locate(nested, root))


if __name__ == "__main__":
    unittest.main()
