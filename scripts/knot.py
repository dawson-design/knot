#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check a knot project's story files, and print what the skills need.

knot is a Claude Code plugin for writing branching narrative games. A game
configures it with a `knot.toml` at its root. `docs/project-contract.md` is
the contract between that file, the story files, the skills, and this script.
Its §2, §4, and §5 define the shapes read here; §7 defines the commands and
every rule code:

- `config` prints the resolved configuration as JSON. Every skill runs it first.
- `check [--strict]` reports errors E1 to E13 and warnings W1 to W9.
- `ink` reports I1 to I8 over the `.ink` files, then compiles them with
  inklecate when it is on PATH (I0).
- `packet cold-read|solver [--key]` prints the input for one of review's two
  fresh-reader tests, or its answer key.

The core is pure. The I/O layer reads `knot.toml` and the story files into a
snapshot of texts. `parse_config` and `build_project` parse them once into
frozen dataclasses, the checks return issues as data, and the packets are
strings. Each `cmd_*` function returns an `Output`, its exit code and text;
only `main` prints, and only `compile_ink` runs a process.

Usage:
    uv run scripts/knot.py config [--project DIR]
    uv run scripts/knot.py check [--strict] [--project DIR]
    uv run scripts/knot.py ink [--project DIR]
    uv run scripts/knot.py packet cold-read|solver [--key] [--project DIR]

Exit codes: 0 clean (warnings allowed), 1 errors found, 2 usage error or no
`knot.toml`.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import asdict, dataclass, replace
from enum import Enum
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Any

# ---------------------------------------------------------------------------
# Fixed vocabulary from the contract
# ---------------------------------------------------------------------------

KNOT_TOML = "knot.toml"
PLUGIN_ROOT = Path(__file__).resolve().parent.parent

ID_RE = re.compile(r"[a-z][a-z0-9_]*")
PATTERNS = ("foldback", "delayed_consequence", "gate", "failed_check", "hard_split")
DOC_STATUSES = ("draft", "review", "approved")
STATE_TYPES = ("int", "bool", "string", "list")
COLD_READ_LAYERS = ("treatment", "beats", "scenes")
DEFAULT_MIN_ROUTES = 2

# Every fixed canon file (§1), by the name `config` gives it.
CANON_FILES: Mapping[str, str] = MappingProxyType(
    {
        "cast": "cast.md",
        "timeline": "timeline.md",
        "changelog": "changelog.md",
        "voices": "voices.md",
        "conventions": "conventions.md",
        "knowledge": "knowledge.toml",
        "clues": "clues.toml",
        "state": "state.toml",
    }
)
REQUIRED_CANON = ("cast", "timeline", "changelog")

# Template file name, and knot's default under the plugin root (§6).
TEMPLATE_FILES: Mapping[str, tuple[str, str]] = MappingProxyType(
    {
        "spine": ("spine.md", "skills/story/references/spine.md"),
        "treatment": ("treatment.md", "skills/story/references/treatment.md"),
        "beat": ("beat.md", "skills/beats/references/beat.md"),
        "scene": ("scene.md", "skills/scene/references/scene.md"),
    }
)

COMPILE_SKIPPED = "Compile skipped: inklecate not found on PATH."
COMPILE_TIMEOUT = 300

# ---------------------------------------------------------------------------
# Issues
# ---------------------------------------------------------------------------


class Severity(Enum):
    """Errors make a command exit 1. Warnings exit 0 unless `--strict`."""

    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class Issue:
    """One finding from `check` or `ink`.

    `code` is the contract's rule code, such as "E7" or "I4". `file` is a path
    relative to the project dir. `entry` names the TOML key, field, heading
    line, or Ink line; it is empty when the whole file is meant.
    """

    code: str
    severity: Severity
    file: str
    entry: str
    message: str


def error(code: str, file: str, entry: str, message: str) -> Issue:
    """Build an error issue."""
    return Issue(code, Severity.ERROR, file, entry, message)


def warning(code: str, file: str, entry: str, message: str) -> Issue:
    """Build a warning issue."""
    return Issue(code, Severity.WARNING, file, entry, message)


def has_errors(issues: Sequence[Issue]) -> bool:
    """True if any issue is an error rather than a warning."""
    return any(issue.severity is Severity.ERROR for issue in issues)


def promote(issues: Sequence[Issue]) -> tuple[Issue, ...]:
    """Turn every warning into an error, for `check --strict`."""
    return tuple(replace(issue, severity=Severity.ERROR) for issue in issues)


def q(value: object) -> str:
    """Quote a value for a message: `q("spring")` is `"spring"`."""
    return f'"{value}"'


def show(value: object) -> str:
    """Show a decoded value the way TOML or Ink would write it.

    JSON covers strings, numbers, booleans, and lists. TOML dates and times,
    which JSON can't encode, fall back to `str()`.
    """
    if isinstance(value, InkExpression):
        return value.text
    try:
        return json.dumps(value)
    except TypeError:
        return str(value)


# ---------------------------------------------------------------------------
# Field shapes: one generic check for TOML tables, nested ones included
# ---------------------------------------------------------------------------


def is_str(value: object) -> bool:
    """True for a string."""
    return isinstance(value, str)


def is_bool(value: object) -> bool:
    """True for a boolean."""
    return isinstance(value, bool)


def is_int(value: object) -> bool:
    """True for an integer that isn't a boolean."""
    return isinstance(value, int) and not isinstance(value, bool)


def is_count(value: object) -> bool:
    """True for an integer of 0 or more."""
    return is_int(value) and value >= 0


def is_table(value: object) -> bool:
    """True for a TOML table."""
    return isinstance(value, dict)


def is_str_list(value: object) -> bool:
    """True for a list of strings, empty included."""
    return isinstance(value, list) and all(is_str(item) for item in value)


def is_points(value: object) -> bool:
    """True for a list of at least one string."""
    return is_str_list(value) and len(value) > 0


def is_table_list(value: object) -> bool:
    """True for a list of TOML tables, empty included."""
    return isinstance(value, list) and all(is_table(item) for item in value)


def is_proposed(value: object) -> bool:
    """True for the only status a ledger entry may carry."""
    return value == "proposed"


def is_doc_status(value: object) -> bool:
    """True for a front-matter status: draft, review, or approved."""
    return value in DOC_STATUSES


def is_state_type(value: object) -> bool:
    """True for a state type: int, bool, string, or list."""
    return value in STATE_TYPES


def is_anything(value: object) -> bool:
    """Accept any value; for fields checked later by their own rule."""
    return True


def is_id(value: str) -> bool:
    """True if a string matches the contract's id form, `^[a-z][a-z0-9_]*$`."""
    return ID_RE.fullmatch(value) is not None


@dataclass(frozen=True)
class Field:
    """How one TOML field must look.

    `test` checks the value's type and `expected` describes it for messages.
    When `fields` is set, the value is a table, or a list of tables, and each
    table is checked against those fields in turn.
    """

    key: str
    test: Callable[[object], bool]
    expected: str
    required: bool = False
    fields: tuple[Field, ...] = ()


def _child(entry: str, key: str) -> str:
    return f"{entry}.{key}" if entry else key


def _nested_issues(
    value: object, field: Field, code: str, file: str, entry: str
) -> list[Issue]:
    if not field.fields:
        return []
    if is_table(value):
        return shape_issues(value, field.fields, code, file, entry)
    issues = []
    for index, table in enumerate(value):
        name = f"{entry}[{index}]"
        issues.extend(shape_issues(table, field.fields, code, file, name))
    return issues


def _field_issues(
    table: Mapping, field: Field, code: str, file: str, entry: str
) -> list[Issue]:
    if field.key not in table:
        if field.required:
            return [error(code, file, entry, f"{q(field.key)} is required.")]
        return []
    value = table[field.key]
    if not field.test(value):
        return [error(code, file, entry, f"{q(field.key)} must be {field.expected}.")]
    return _nested_issues(value, field, code, file, _child(entry, field.key))


def shape_issues(
    table: Mapping, fields: Sequence[Field], code: str, file: str, entry: str
) -> list[Issue]:
    """Check a table's fields against a spec, nested tables included.

    Args:
        table: the decoded TOML table.
        fields: the fields it may hold.
        code: the error code for a missing or mistyped field (E1, E3, or E10).
        file: the file, for the issue.
        entry: the table's name, for the issue; empty for the top level.
    Returns:
        `code` errors for missing or mistyped fields, and a W9 warning for
        each key the spec doesn't know. A nested table is checked only when
        its own field has the right type.
    """
    issues = []
    for field in fields:
        issues.extend(_field_issues(table, field, code, file, entry))
    known = {field.key for field in fields}
    for key in table:
        if key not in known:
            issues.append(warning("W9", file, entry, f"unknown key {q(key)}."))
    return issues


def id_issues(
    items: Sequence[tuple[str, str]],
    file: str,
    noun: str,
    codes: tuple[str, str] = ("E4", "E4"),
) -> list[Issue]:
    """Flag badly formed and repeated ids.

    Args:
        items: (entry, id) pairs in file order.
        file: the file they come from.
        noun: what the ids are, for the message.
        codes: the codes for a badly formed id and for a repeat.
    """
    form_code, repeat_code = codes
    issues = []
    seen: set[str] = set()
    for entry, ident in items:
        if not is_id(ident):
            message = f"{noun} {q(ident)} is badly formed."
            issues.append(error(form_code, file, entry, message))
        elif ident in seen:
            message = f"{noun} {q(ident)} is duplicated."
            issues.append(error(repeat_code, file, entry, message))
        seen.add(ident)
    return issues


def join(*parts: str) -> str:
    """Join and normalize project-relative path parts, POSIX style."""
    return str(PurePosixPath(*parts))


# ---------------------------------------------------------------------------
# knot.toml (§2)
# ---------------------------------------------------------------------------

TEXT = "a string"
STRINGS = "a list of strings"
TABLE = "a table"
TABLES = "a list of tables"
POINT = "a point string"

PROJECT_FIELDS = (
    Field("name", is_str, TEXT, required=True),
    Field("root", is_str, TEXT, required=True),
    Field("truth", is_str_list, STRINGS),
    Field("templates", is_str, TEXT),
    Field("reviews", is_str, TEXT),
)
TIMELINE_FIELDS = (
    Field("points", is_points, "a list of at least one string", required=True),
)
EXTRA_FIELDS = (
    Field("file", is_str, TEXT, required=True),
    Field("table", is_str, TEXT, required=True),
)
IDS_FIELDS = (Field("extra", is_table_list, TABLES, fields=EXTRA_FIELDS),)
CLUES_CONFIG_FIELDS = (Field("min_routes", is_count, "a whole number, 0 or more"),)
INK_FIELDS = (
    Field("dir", is_str, TEXT),
    Field("main", is_str, TEXT),
    Field("globals", is_str, TEXT),
    Field("knot", is_str, "a regular expression string"),
    Field("tags", is_str_list, STRINGS),
)
CHECKS_FIELDS = (Field("commands", is_str_list, STRINGS),)
COLD_READ_FIELDS = (
    Field("before", is_str, POINT, required=True),
    Field("layers", is_str_list, STRINGS, required=True),
    Field("sections", is_str_list, STRINGS),
    Field("must_not_predict", is_str, TEXT, required=True),
)
SOLVER_FIELDS = (
    Field("must_prove", is_str_list, "a list of deduction ids", required=True),
    Field("must_not_prove", is_str_list, "a list of deduction ids"),
)
REVIEW_FIELDS = (
    Field("cold_read", is_table, TABLE, fields=COLD_READ_FIELDS),
    Field("solver", is_table, TABLE, fields=SOLVER_FIELDS),
)
RULE_FIELDS = (
    Field("id", is_str, TEXT, required=True),
    Field("ask", is_str, TEXT, required=True),
    Field("see", is_str_list, STRINGS),
)
CONFIG_FIELDS = (
    Field("project", is_table, TABLE, required=True, fields=PROJECT_FIELDS),
    Field("timeline", is_table, TABLE, required=True, fields=TIMELINE_FIELDS),
    Field("ids", is_table, TABLE, fields=IDS_FIELDS),
    Field("clues", is_table, TABLE, fields=CLUES_CONFIG_FIELDS),
    Field("ink", is_table, TABLE, fields=INK_FIELDS),
    Field("checks", is_table, TABLE, fields=CHECKS_FIELDS),
    Field("review", is_table, TABLE, fields=REVIEW_FIELDS),
    Field("rules", is_table_list, "an array of [[rules]] tables", fields=RULE_FIELDS),
)


@dataclass(frozen=True)
class ExtraIds:
    """One `[ids] extra` source: a TOML file and the table whose keys are ids."""

    file: str
    table: str


@dataclass(frozen=True)
class InkConfig:
    """The `[ink]` table. `knot` and `tags` are None when not set: unchecked."""

    dir: str
    main: str
    globals: str
    knot: str | None
    tags: tuple[str, ...] | None


@dataclass(frozen=True)
class Rule:
    """One `[[rules]]` entry: a question the review asks of every layer."""

    id: str
    ask: str
    see: tuple[str, ...]


@dataclass(frozen=True)
class ColdRead:
    """The `[review.cold_read]` table."""

    before: str
    layers: tuple[str, ...]
    sections: tuple[str, ...]
    must_not_predict: str


@dataclass(frozen=True)
class Solver:
    """The `[review.solver]` table."""

    must_prove: tuple[str, ...]
    must_not_prove: tuple[str, ...]


@dataclass(frozen=True)
class Config:
    """The whole of `knot.toml`, parsed, with the contract's defaults applied.

    Paths are as written, relative to the project dir. `cold_read` and
    `solver` are None when their tables are absent.
    """

    name: str
    root: str
    truth: tuple[str, ...]
    templates: str
    reviews: str
    points: tuple[str, ...]
    extra: tuple[ExtraIds, ...]
    min_routes: int
    ink: InkConfig
    checks: tuple[str, ...]
    rules: tuple[Rule, ...]
    cold_read: ColdRead | None
    solver: Solver | None

    @property
    def index(self) -> Mapping[str, int]:
        """Each point's position in play order."""
        return {point: position for position, point in enumerate(self.points)}


@dataclass(frozen=True)
class ConfigParsed:
    """A usable config, with the W9 warnings found while parsing it."""

    config: Config
    issues: tuple[Issue, ...]


@dataclass(frozen=True)
class Rejected:
    """A `knot.toml` that can't be used, and the E1 issues that explain why."""

    issues: tuple[Issue, ...]


def compile_knot(pattern: str, points: Sequence[str]) -> re.Pattern[str] | None:
    """Compile `[ink] knot`, expanding `{point}` to an alternation of the points.

    Returns:
        The compiled pattern, or None if it isn't a valid regular expression.
    """
    alternation = "(?:" + "|".join(re.escape(point) for point in points) + ")"
    try:
        return re.compile(pattern.replace("{point}", alternation))
    except re.error:
        return None


def _knot_issues(raw: Mapping) -> list[Issue]:
    pattern = raw.get("ink", {}).get("knot")
    if pattern is None or compile_knot(pattern, raw["timeline"]["points"]):
        return []
    return [error("E1", KNOT_TOML, "ink.knot", "isn't a valid regular expression.")]


def _relative_path_issues(raw: Mapping) -> list[Issue]:
    """`root` and `[ink] dir` must stay relative: every layer is read under them."""
    paths = (
        ("project.root", raw["project"]["root"]),
        ("ink.dir", raw.get("ink", {}).get("dir", "ink")),
    )
    return [
        error("E1", KNOT_TOML, entry, f"path {q(value)} isn't relative.")
        for entry, value in paths
        if PurePosixPath(value).is_absolute()
    ]


def _review_value_issues(raw: Mapping) -> list[Issue]:
    review = raw.get("review", {})
    layers = review.get("cold_read", {}).get("layers", [])
    allowed = ", ".join(COLD_READ_LAYERS)
    entry = "review.cold_read.layers"
    issues = [
        error("E1", KNOT_TOML, entry, f"layer {q(layer)} isn't one of {allowed}.")
        for layer in layers
        if layer not in COLD_READ_LAYERS
    ]
    solver = review.get("solver", {})
    both = set(solver.get("must_prove", [])) & set(solver.get("must_not_prove", []))
    message = "is in both must_prove and must_not_prove."
    issues += [
        error("E1", KNOT_TOML, "review.solver", f"deduction {q(ident)} {message}")
        for ident in sorted(both)
    ]
    return issues


def config_value_issues(raw: Mapping) -> list[Issue]:
    """Check what a type test can't: the knot regex, paths, and review settings.

    Args:
        raw: decoded `knot.toml` that passed `shape_issues`.
    Returns:
        E1 errors.
    """
    issues = _knot_issues(raw)
    issues += _relative_path_issues(raw)
    return issues + _review_value_issues(raw)


def _build_ink(raw: Mapping) -> InkConfig:
    tags = raw.get("tags")
    return InkConfig(
        dir=raw.get("dir", "ink"),
        main=raw.get("main", "main.ink"),
        globals=raw.get("globals", "globals.ink"),
        knot=raw.get("knot"),
        tags=None if tags is None else tuple(tags),
    )


def _build_cold_read(raw: Mapping | None) -> ColdRead | None:
    if raw is None:
        return None
    return ColdRead(
        before=raw["before"],
        layers=tuple(raw["layers"]),
        sections=tuple(raw.get("sections", [])),
        must_not_predict=raw["must_not_predict"],
    )


def _build_solver(raw: Mapping | None) -> Solver | None:
    if raw is None:
        return None
    return Solver(tuple(raw["must_prove"]), tuple(raw.get("must_not_prove", [])))


def build_config(raw: Mapping) -> Config:
    """Build a Config from decoded `knot.toml` that passed every E1 check."""
    project = raw["project"]
    root = project["root"]
    review = raw.get("review", {})
    extra = raw.get("ids", {}).get("extra", [])
    return Config(
        name=project["name"],
        root=root,
        truth=tuple(project.get("truth", [join(root, "canon") + "/"])),
        templates=project.get("templates", ""),
        reviews=project.get("reviews", join(root, "reviews")),
        points=tuple(raw["timeline"]["points"]),
        extra=tuple(ExtraIds(item["file"], item["table"]) for item in extra),
        min_routes=raw.get("clues", {}).get("min_routes", DEFAULT_MIN_ROUTES),
        ink=_build_ink(raw.get("ink", {})),
        checks=tuple(raw.get("checks", {}).get("commands", [])),
        rules=tuple(
            Rule(rule["id"], rule["ask"], tuple(rule.get("see", [])))
            for rule in raw.get("rules", [])
        ),
        cold_read=_build_cold_read(review.get("cold_read")),
        solver=_build_solver(review.get("solver")),
    )


def parse_config(text: str) -> ConfigParsed | Rejected:
    """Parse the text of `knot.toml`.

    Returns:
        ConfigParsed with the Config and any W9 warnings, or Rejected with the
        E1 errors that make it unusable. Never raises for bad data.
    """
    try:
        raw = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        return Rejected((error("E1", KNOT_TOML, "", f"TOML does not parse: {exc}."),))
    issues = shape_issues(raw, CONFIG_FIELDS, "E1", KNOT_TOML, "")
    if not has_errors(issues):
        issues += config_value_issues(raw)
    if has_errors(issues):
        return Rejected(tuple(issues))
    return ConfigParsed(build_config(raw), tuple(issues))


def knot_pattern(config: Config) -> re.Pattern[str] | None:
    """Return the compiled `[ink] knot` pattern, or None when it isn't set."""
    if config.ink.knot is None:
        return None
    return compile_knot(config.ink.knot, config.points)


# ---------------------------------------------------------------------------
# Layout (§1): where each layer lives, relative to the project dir
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Layout:
    """Project-relative folders and Ink files, resolved from the config."""

    canon: str
    spine: str
    treatment: str
    beats: str
    scenes: str
    ink: str
    reviews: str
    ink_main: str
    ink_globals: str

    def canon_file(self, name: str) -> str:
        """Return the path of a fixed canon file, by its `CANON_FILES` name."""
        return join(self.canon, CANON_FILES[name])


def layout(config: Config) -> Layout:
    """Resolve every folder in the contract's layout from the config."""
    root = config.root
    ink = join(root, config.ink.dir)
    return Layout(
        canon=join(root, "canon"),
        spine=join(root, "spine"),
        treatment=join(root, "treatment"),
        beats=join(root, "beats"),
        scenes=join(root, "scenes"),
        ink=ink,
        reviews=join(config.reviews),
        ink_main=join(ink, config.ink.main),
        ink_globals=join(ink, config.ink.globals),
    )


def template_overrides(config: Config) -> dict[str, str]:
    """Return where each layer's override template would be, if the project sets a folder."""
    if not config.templates:
        return {}
    return {
        layer: join(config.templates, file)
        for layer, (file, _default) in TEMPLATE_FILES.items()
    }


def files_under(
    files: Mapping[str, str], folder: str, suffix: str, recursive: bool
) -> list[str]:
    """Return snapshot paths under a folder with a suffix, sorted.

    Args:
        files: the snapshot.
        folder: a project-relative folder; "." is the project dir itself.
        suffix: such as ".md".
        recursive: False keeps only files directly in the folder.
    """
    prefix = "" if folder == "." else folder + "/"
    found = []
    for path in sorted(files):
        rest = path[len(prefix) :] if path.startswith(prefix) else ""
        if rest.endswith(suffix) and (recursive or "/" not in rest):
            found.append(path)
    return found


def beat_paths(files: Mapping[str, str], paths: Layout) -> list[str]:
    """Return every beat sheet: `.md` files in the beats folder except `index.md`."""
    index = join(paths.beats, "index.md")
    return [p for p in files_under(files, paths.beats, ".md", False) if p != index]


# ---------------------------------------------------------------------------
# Markdown: headings and fences, shared by canon prose and the cold read
# ---------------------------------------------------------------------------

HEADING_RE = re.compile(r"(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*")
FENCE_RE = re.compile(r" {0,3}(`{3,}|~{3,})")


@dataclass(frozen=True)
class Heading:
    """A Markdown heading: its line number, level, and text."""

    line: int
    level: int
    text: str


def parse_heading(number: int, line: str) -> Heading | None:
    """Read an ATX heading such as `## What happens ##`, closing hashes stripped."""
    match = HEADING_RE.fullmatch(line)
    if match is None:
        return None
    return Heading(number, len(match.group(1)), match.group(2) or "")


def fence_flags(lines: Sequence[str]) -> list[bool]:
    """Mark each line inside a ``` or ~~~ fenced code block, fence lines included."""
    flags = []
    fence = ""
    for line in lines:
        marker = FENCE_RE.match(line)
        if marker is None:
            flags.append(fence != "")
            continue
        flags.append(True)
        char = marker.group(1)[0]
        if not fence:
            fence = char
        elif char == fence:
            fence = ""
    return flags


def markdown_headings(text: str) -> list[Heading]:
    """Return every heading outside fenced code blocks."""
    lines = text.splitlines()
    found = []
    for number, (line, fenced) in enumerate(zip(lines, fence_flags(lines)), 1):
        heading = None if fenced else parse_heading(number, line)
        if heading is not None:
            found.append(heading)
    return found


def headings(text: str | None) -> tuple[Heading, ...] | None:
    """Return a canon file's `## ` headings, or None if there's no file."""
    if text is None:
        return None
    return tuple(h for h in markdown_headings(text) if h.level == 2)


# ---------------------------------------------------------------------------
# Ledgers (§4): missing, broken, or loaded
# ---------------------------------------------------------------------------

STATUS_FIELD = Field("status", is_proposed, q("proposed"))
KNOWS_FIELDS = (
    Field("who", is_str, "an id string", required=True),
    Field("from", is_str, POINT, required=True),
    Field("via", is_str, TEXT),
)
FACT_FIELDS = (
    Field("text", is_str, TEXT, required=True),
    Field("true_from", is_str, POINT, required=True),
    Field("reveal", is_str, POINT),
    Field("knows", is_table_list, TABLES, fields=KNOWS_FIELDS),
    STATUS_FIELD,
)
DEDUCTION_FIELDS = (Field("claim", is_str, TEXT, required=True), STATUS_FIELD)
PLANT_FIELDS = (
    Field("point", is_str, POINT, required=True),
    Field("where", is_str, TEXT),
)
FIND_FIELDS = (
    Field("point", is_str, POINT, required=True),
    Field("how", is_str, TEXT),
)
CLUE_FIELDS = (
    Field("text", is_str, TEXT, required=True),
    Field("proves", is_str_list, "a list of deduction ids"),
    Field("required", is_bool, "true or false"),
    Field("innocent", is_str, TEXT),
    Field("plant", is_table, TABLE, required=True, fields=PLANT_FIELDS),
    Field("finds", is_table_list, TABLES, fields=FIND_FIELDS),
    STATUS_FIELD,
)
STATE_FIELDS = (
    Field("type", is_state_type, "int, bool, string, or list", required=True),
    Field("kind", is_str, TEXT, required=True),
    Field("default", is_anything, "a value", required=True),
    Field("meaning", is_str, TEXT, required=True),
    Field("items", is_str_list, "a list of item ids"),
    STATUS_FIELD,
)


@dataclass(frozen=True)
class Knows:
    """One `knows` entry. `start` is the contract's `from` field."""

    who: str
    start: str
    via: str | None


@dataclass(frozen=True)
class Fact:
    """One `[facts.<id>]` entry. A fact with `reveal` is a secret."""

    id: str
    text: str
    true_from: str
    reveal: str | None
    knows: tuple[Knows, ...]
    proposed: bool


@dataclass(frozen=True)
class Deduction:
    """One `[deductions.<id>]` entry: a claim the player can try to prove."""

    id: str
    claim: str
    proposed: bool


@dataclass(frozen=True)
class Place:
    """A clue's `plant` or one of its `finds`: a point and free-text detail."""

    point: str
    detail: str | None


@dataclass(frozen=True)
class Clue:
    """One `[clues.<id>]` entry."""

    id: str
    text: str
    proves: tuple[str, ...]
    required: bool
    innocent: str | None
    plant: Place
    finds: tuple[Place, ...]
    proposed: bool


@dataclass(frozen=True)
class StateEntry:
    """One `[state.<id>]` entry. `default` is kept as decoded; E9 checks it."""

    id: str
    type: str
    kind: str
    default: object
    meaning: str
    items: tuple[str, ...]
    proposed: bool


@dataclass(frozen=True)
class Table:
    """One ledger table after parsing.

    `entries` holds the well-formed entries by id. `broken` holds the issues
    of each entry that exists but can't be read, by id, so a check can tell a
    malformed entry from an unknown one.
    """

    entries: Mapping[str, Any]
    broken: Mapping[str, tuple[Issue, ...]]

    def known(self) -> frozenset[str]:
        """Every id the table holds, well-formed or not."""
        return frozenset(self.entries) | frozenset(self.broken)


EMPTY_TABLE = Table(MappingProxyType({}), MappingProxyType({}))


@dataclass(frozen=True)
class Missing:
    """A ledger whose file doesn't exist yet."""


@dataclass(frozen=True)
class Broken:
    """A ledger whose file exists but can't be read as a whole (E3)."""

    issues: tuple[Issue, ...]


@dataclass(frozen=True)
class Loaded:
    """A ledger that was read: its tables by name, and every issue found."""

    tables: Mapping[str, Table]
    issues: tuple[Issue, ...]


Ledger = Missing | Broken | Loaded


def table(ledger: Ledger, name: str) -> Table:
    """Return one table of a ledger. It is empty unless the ledger loaded."""
    if isinstance(ledger, Loaded):
        return ledger.tables.get(name, EMPTY_TABLE)
    return EMPTY_TABLE


def ledger_issues(ledger: Ledger) -> tuple[Issue, ...]:
    """Return what was found while reading a ledger."""
    if isinstance(ledger, Missing):
        return ()
    return ledger.issues


def _proposed(raw: Mapping) -> bool:
    return raw.get("status") == "proposed"


def _build_fact(ident: str, raw: Mapping) -> Fact:
    knows = tuple(
        Knows(item["who"], item["from"], item.get("via"))
        for item in raw.get("knows", [])
    )
    return Fact(
        ident, raw["text"], raw["true_from"], raw.get("reveal"), knows, _proposed(raw)
    )


def _build_deduction(ident: str, raw: Mapping) -> Deduction:
    return Deduction(ident, raw["claim"], _proposed(raw))


def _build_clue(ident: str, raw: Mapping) -> Clue:
    plant = raw["plant"]
    finds = tuple(Place(f["point"], f.get("how")) for f in raw.get("finds", []))
    return Clue(
        id=ident,
        text=raw["text"],
        proves=tuple(raw.get("proves", [])),
        required=raw.get("required", False),
        innocent=raw.get("innocent"),
        plant=Place(plant["point"], plant.get("where")),
        finds=finds,
        proposed=_proposed(raw),
    )


def _build_state(ident: str, raw: Mapping) -> StateEntry:
    return StateEntry(
        id=ident,
        type=raw["type"],
        kind=raw["kind"],
        default=raw["default"],
        meaning=raw["meaning"],
        items=tuple(raw.get("items", [])),
        proposed=_proposed(raw),
    )


def _list_needs_items(raw: Mapping) -> str | None:
    """`items` is required only for lists: a rule across two fields."""
    if raw["type"] == "list" and "items" not in raw:
        return 'a list needs "items".'
    return None


@dataclass(frozen=True)
class TableSpec:
    """How to read one ledger table.

    `fields` is each entry's shape, `build` makes its dataclass from its id
    and table, and `rule` is an optional check across fields that returns a
    message when the entry breaks it.
    """

    name: str
    fields: tuple[Field, ...]
    build: Callable[[str, Mapping], object]
    rule: Callable[[Mapping], str | None] | None = None


KNOWLEDGE_SPECS = (
    TableSpec("facts", FACT_FIELDS, _build_fact),
    TableSpec("deductions", DEDUCTION_FIELDS, _build_deduction),
)
CLUE_SPECS = (TableSpec("clues", CLUE_FIELDS, _build_clue),)
STATE_SPECS = (TableSpec("state", STATE_FIELDS, _build_state, _list_needs_items),)


def _entry_issues(value: object, spec: TableSpec, path: str, entry: str) -> list[Issue]:
    if not is_table(value):
        return [error("E3", path, entry, "must be a table.")]
    issues = shape_issues(value, spec.fields, "E3", path, entry)
    if has_errors(issues) or spec.rule is None:
        return issues
    problem = spec.rule(value)
    if problem is None:
        return issues
    return issues + [error("E3", path, entry, problem)]


def parse_table(
    section: Mapping, spec: TableSpec, path: str
) -> tuple[Table, list[Issue]]:
    """Parse each entry of one ledger table.

    Returns:
        The Table, with well-formed entries built and malformed ones kept as
        their issues, and every E3 and W9 issue found.
    """
    entries = {}
    broken = {}
    issues = []
    for ident, value in section.items():
        found = _entry_issues(value, spec, path, f"{spec.name}.{ident}")
        issues += found
        if has_errors(found):
            broken[ident] = tuple(found)
        else:
            entries[ident] = spec.build(ident, value)
    return Table(MappingProxyType(entries), MappingProxyType(broken)), issues


def _top_level_issues(raw: Mapping, tables: Sequence[str], path: str) -> list[Issue]:
    issues = []
    for key, value in raw.items():
        if key not in tables:
            issues.append(warning("W9", path, "", f"unknown table {q(key)}."))
        elif not is_table(value):
            issues.append(error("E3", path, key, "must be a table."))
    return issues


def load_ledger(
    files: Mapping[str, str], path: str, specs: Sequence[TableSpec]
) -> Ledger:
    """Read one ledger file from the snapshot.

    Returns:
        Missing when the file doesn't exist; Broken when it isn't valid TOML
        or a top-level table has the wrong type; otherwise Loaded.
    """
    text = files.get(path)
    if text is None:
        return Missing()
    try:
        raw = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        return Broken((error("E3", path, "", f"TOML does not parse: {exc}."),))
    issues = _top_level_issues(raw, [spec.name for spec in specs], path)
    if has_errors(issues):
        return Broken(tuple(issues))
    tables = {}
    for spec in specs:
        parsed, found = parse_table(raw.get(spec.name, {}), spec, path)
        tables[spec.name] = parsed
        issues += found
    return Loaded(MappingProxyType(tables), tuple(issues))


def _extra_table(files: Mapping[str, str], extra: ExtraIds) -> frozenset[str] | str:
    """Return the ids in one extra source, or a message saying why there are none."""
    text = files.get(join(extra.file))
    if text is None:
        return f"file {q(extra.file)} doesn't exist."
    try:
        raw = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return f"file {q(extra.file)} isn't valid TOML."
    found = raw.get(extra.table)
    if not is_table(found):
        return f"file {q(extra.file)} has no [{extra.table}] table."
    return frozenset(found)


def extra_ids(
    config: Config, files: Mapping[str, str]
) -> tuple[frozenset[str], list[Issue]]:
    """Collect the `[ids] extra` ids. A source that can't be read is an E1 error."""
    ids: set[str] = set()
    issues = []
    for index, extra in enumerate(config.extra):
        found = _extra_table(files, extra)
        if isinstance(found, str):
            issues.append(error("E1", KNOT_TOML, f"ids.extra[{index}]", found))
        else:
            ids |= found
    return frozenset(ids), issues


# ---------------------------------------------------------------------------
# Front matter (§5): beat sheets, treatments, scenes
# ---------------------------------------------------------------------------

CLUE_IDS = "a list of clue ids"
STATE_NAMES = "a list of state names"
STATUS_WORDS = "draft, review, or approved"
BEAT_FIELDS = (
    Field("id", is_str, TEXT, required=True),
    Field("point", is_str, POINT, required=True),
    Field("status", is_doc_status, STATUS_WORDS, required=True),
    Field("plants", is_str_list, CLUE_IDS),
    Field("finds", is_str_list, CLUE_IDS),
    Field("reads", is_str_list, STATE_NAMES),
    Field("sets", is_str_list, STATE_NAMES),
    Field("pattern", is_str_list, "a list of pattern names"),
)
TREATMENT_FIELDS = (
    Field("points", is_points, "a list of at least one point", required=True),
    Field("status", is_doc_status, STATUS_WORDS, required=True),
)
SCENE_FIELDS = (
    Field("id", is_str, TEXT, required=True),
    Field("point", is_str, POINT, required=True),
    Field("status", is_doc_status, STATUS_WORDS, required=True),
)


@dataclass(frozen=True)
class Beat:
    """A beat sheet: its front matter and the Markdown below it."""

    path: str
    id: str
    point: str
    status: str
    plants: tuple[str, ...]
    finds: tuple[str, ...]
    reads: tuple[str, ...]
    sets: tuple[str, ...]
    pattern: tuple[str, ...]
    body: str


@dataclass(frozen=True)
class Treatment:
    """A treatment file: the points it spans, its status, and its body."""

    path: str
    points: tuple[str, ...]
    status: str
    body: str


@dataclass(frozen=True)
class Scene:
    """A scene file: its id, point, status, and body."""

    path: str
    id: str
    point: str
    status: str
    body: str


def split_front_matter(text: str) -> tuple[str, str] | None:
    """Split a file into its `+++` TOML block and the body below it.

    Returns:
        (TOML text, body), or None when the file doesn't open with a `+++`
        line or the block is never closed.
    """
    lines = text.lstrip("﻿").splitlines(keepends=True)
    if not lines or lines[0].strip() != "+++":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == "+++":
            return "".join(lines[1:index]), "".join(lines[index + 1 :])
    return None


def read_front_matter(
    path: str, text: str, fields: Sequence[Field]
) -> tuple[dict | None, str, list[Issue]]:
    """Parse a file's front matter against its fields.

    Returns:
        (the decoded table or None if it's unusable, the body, E10 and W9
        issues).
    """
    split = split_front_matter(text)
    if split is None:
        return None, text, [error("E10", path, "", "has no +++ front matter.")]
    toml_text, body = split
    try:
        raw = tomllib.loads(toml_text)
    except tomllib.TOMLDecodeError as exc:
        message = f"TOML does not parse: {exc}."
        return None, body, [error("E10", path, "front matter", message)]
    issues = shape_issues(raw, fields, "E10", path, "front matter")
    return (None if has_errors(issues) else raw), body, issues


def _build_beat(path: str, raw: Mapping, body: str) -> Beat:
    return Beat(
        path=path,
        id=raw["id"],
        point=raw["point"],
        status=raw["status"],
        plants=tuple(raw.get("plants", [])),
        finds=tuple(raw.get("finds", [])),
        reads=tuple(raw.get("reads", [])),
        sets=tuple(raw.get("sets", [])),
        pattern=tuple(raw.get("pattern", [])),
        body=body,
    )


def _build_treatment(path: str, raw: Mapping, body: str) -> Treatment:
    return Treatment(path, tuple(raw["points"]), raw["status"], body)


def _build_scene(path: str, raw: Mapping, body: str) -> Scene:
    return Scene(path, raw["id"], raw["point"], raw["status"], body)


def load_docs(
    files: Mapping[str, str],
    paths: Sequence[str],
    fields: Sequence[Field],
    build: Callable[[str, Mapping, str], object],
) -> tuple[tuple, list[Issue]]:
    """Parse the front matter of each file, keeping the usable ones.

    Returns:
        The built documents in path order, and every issue found.
    """
    docs = []
    issues = []
    for path in paths:
        raw, body, found = read_front_matter(path, files[path], fields)
        issues += found
        if raw is not None:
            docs.append(build(path, raw, body))
    return tuple(docs), issues


# ---------------------------------------------------------------------------
# The project: config plus every parsed file
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Project:
    """A whole knot project, parsed once.

    `files` is the snapshot of texts, keyed by project-relative path. `cast`
    and `timeline` are None when their files don't exist. `issues` holds what
    was found while parsing (E1 for extra ids, E3, E10, W9).
    """

    config: Config
    paths: Layout
    files: Mapping[str, str]
    cast: tuple[Heading, ...] | None
    timeline: tuple[Heading, ...] | None
    extra_ids: frozenset[str]
    knowledge: Ledger
    clues: Ledger
    state: Ledger
    beats: tuple[Beat, ...]
    treatments: tuple[Treatment, ...]
    scenes: tuple[Scene, ...]
    issues: tuple[Issue, ...]


def _load_layers(
    files: Mapping[str, str], paths: Layout
) -> tuple[tuple[Beat, ...], tuple[Treatment, ...], tuple[Scene, ...], list[Issue]]:
    """Parse the front matter of every beat sheet, treatment, and scene."""
    beats, beat_issues = load_docs(
        files, beat_paths(files, paths), BEAT_FIELDS, _build_beat
    )
    treatment_paths = files_under(files, paths.treatment, ".md", True)
    treatments, treatment_issues = load_docs(
        files, treatment_paths, TREATMENT_FIELDS, _build_treatment
    )
    scene_paths = files_under(files, paths.scenes, ".md", False)
    scenes, scene_issues = load_docs(files, scene_paths, SCENE_FIELDS, _build_scene)
    return beats, treatments, scenes, beat_issues + treatment_issues + scene_issues


def build_project(
    config: Config, files: Mapping[str, str], config_issues: Sequence[Issue] = ()
) -> Project:
    """Parse every file in a snapshot.

    Args:
        config: the parsed `knot.toml`.
        files: texts keyed by project-relative path, from `read_snapshot`.
        config_issues: warnings found while parsing `knot.toml`.
    """
    paths = layout(config)
    extra, extra_issues = extra_ids(config, files)
    knowledge = load_ledger(files, paths.canon_file("knowledge"), KNOWLEDGE_SPECS)
    clues = load_ledger(files, paths.canon_file("clues"), CLUE_SPECS)
    state = load_ledger(files, paths.canon_file("state"), STATE_SPECS)
    beats, treatments, scenes, layer_issues = _load_layers(files, paths)
    issues = [*config_issues, *extra_issues, *ledger_issues(knowledge)]
    issues += [*ledger_issues(clues), *ledger_issues(state), *layer_issues]
    return Project(
        config=config,
        paths=paths,
        files=files,
        cast=headings(files.get(paths.canon_file("cast"))),
        timeline=headings(files.get(paths.canon_file("timeline"))),
        extra_ids=extra,
        knowledge=knowledge,
        clues=clues,
        state=state,
        beats=beats,
        treatments=treatments,
        scenes=scenes,
        issues=tuple(issues),
    )


def canon_exists(project: Project, name: str) -> bool:
    """True if the fixed canon file exists, by its `CANON_FILES` name."""
    return project.paths.canon_file(name) in project.files


def _clue_refs(beat: Beat) -> list[tuple[str, str]]:
    """Return (field, clue id) for each clue a beat plants or finds."""
    return [("plants", c) for c in beat.plants] + [("finds", c) for c in beat.finds]


def _state_refs(beat: Beat) -> list[tuple[str, str]]:
    """Return (field, state name) for each state a beat reads or sets."""
    return [("reads", s) for s in beat.reads] + [("sets", s) for s in beat.sets]


# ---------------------------------------------------------------------------
# check: E2 and E4 to E13 (E1, E3, and E10 are found while parsing)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PointRef:
    """A point named outside `[timeline]`: where, which field, and the point."""

    file: str
    entry: str
    field: str
    point: str


def _knowledge_point_refs(project: Project) -> Iterator[PointRef]:
    path = project.paths.canon_file("knowledge")
    for fact in table(project.knowledge, "facts").entries.values():
        entry = f"facts.{fact.id}"
        yield PointRef(path, entry, "true_from", fact.true_from)
        if fact.reveal is not None:
            yield PointRef(path, entry, "reveal", fact.reveal)
        for index, knows in enumerate(fact.knows):
            yield PointRef(path, f"{entry}.knows[{index}]", "from", knows.start)


def _clue_point_refs(project: Project) -> Iterator[PointRef]:
    path = project.paths.canon_file("clues")
    for clue in table(project.clues, "clues").entries.values():
        entry = f"clues.{clue.id}"
        yield PointRef(path, f"{entry}.plant", "point", clue.plant.point)
        for index, find in enumerate(clue.finds):
            yield PointRef(path, f"{entry}.finds[{index}]", "point", find.point)


def _doc_point_refs(project: Project) -> Iterator[PointRef]:
    for beat in project.beats:
        yield PointRef(beat.path, "front matter", "point", beat.point)
    for scene in project.scenes:
        yield PointRef(scene.path, "front matter", "point", scene.point)
    for treatment in project.treatments:
        for point in treatment.points:
            yield PointRef(treatment.path, "front matter", "points", point)


def point_refs(project: Project) -> Iterator[PointRef]:
    """Yield every point the project names in knot.toml, ledgers, and front matter."""
    cold = project.config.cold_read
    if cold is not None:
        yield PointRef(KNOT_TOML, "review.cold_read", "before", cold.before)
    yield from _knowledge_point_refs(project)
    yield from _clue_point_refs(project)
    yield from _doc_point_refs(project)


def _e2_points(project: Project) -> list[Issue]:
    config = project.config
    timeline = [("timeline.points", point) for point in config.points]
    issues = id_issues(timeline, KNOT_TOML, "point", ("E2", "E2"))
    for ref in point_refs(project):
        if ref.point not in config.points:
            message = f"{ref.field} {q(ref.point)} isn't in [timeline] points."
            issues.append(error("E2", ref.file, ref.entry, message))
    return issues


def _ledger_id_issues(project: Project) -> list[Issue]:
    """E4 for every ledger id, malformed entries included, and each list's items."""
    groups = (
        (project.knowledge, "facts", "knowledge", "fact id"),
        (project.knowledge, "deductions", "knowledge", "deduction id"),
        (project.clues, "clues", "clues", "clue id"),
        (project.state, "state", "state", "state name"),
    )
    issues = []
    for ledger, name, file, noun in groups:
        idents = sorted(table(ledger, name).known())
        keyed = [(f"{name}.{ident}", ident) for ident in idents]
        issues += id_issues(keyed, project.paths.canon_file(file), noun)
    state_path = project.paths.canon_file("state")
    for entry in table(project.state, "state").entries.values():
        items = [(f"state.{entry.id}.items", item) for item in entry.items]
        issues += id_issues(items, state_path, "item")
    return issues


def _e4_ids(project: Project) -> list[Issue]:
    rules = [(f"rules[{i}]", rule.id) for i, rule in enumerate(project.config.rules)]
    issues = id_issues(rules, KNOT_TOML, "rule id")
    issues += _ledger_id_issues(project)
    for doc in (*project.beats, *project.scenes):
        if not is_id(doc.id):
            message = f"id {q(doc.id)} is badly formed."
            issues.append(error("E4", doc.path, "front matter", message))
    return issues


def _e5_headings(project: Project) -> list[Issue]:
    cast_path = project.paths.canon_file("cast")
    timeline_path = project.paths.canon_file("timeline")
    cast = [(f"line {h.line}", h.text) for h in project.cast or ()]
    issues = id_issues(cast, cast_path, "heading", ("E5", "E4"))
    for heading in project.timeline or ():
        if heading.text not in project.config.points:
            message = f"heading {q(heading.text)} isn't a point."
            issues.append(error("E5", timeline_path, f"line {heading.line}", message))
    return issues


def _e6_who(project: Project) -> list[Issue]:
    """Skipped while cast.md doesn't exist: W1 already says so."""
    if project.cast is None:
        return []
    known = {heading.text for heading in project.cast} | project.extra_ids
    path = project.paths.canon_file("knowledge")
    issues = []
    for fact in table(project.knowledge, "facts").entries.values():
        unknown = [(i, k) for i, k in enumerate(fact.knows) if k.who not in known]
        for index, knows in unknown:
            message = f"who {q(knows.who)} names no cast id and no [ids] extra id."
            entry = f"facts.{fact.id}.knows[{index}]"
            issues.append(error("E6", path, entry, message))
    return issues


def _unknown_claims(project: Project, known: frozenset[str]) -> list[Issue]:
    solver = project.config.solver
    claimed = (*solver.must_prove, *solver.must_not_prove) if solver else ()
    return [
        error("E7", KNOT_TOML, "review.solver", f"names unknown deduction {q(d)}.")
        for d in claimed
        if d not in known
    ]


def _e7_proves(project: Project) -> list[Issue]:
    """Skipped when knowledge.toml can't be read: its E3 says why.

    A deduction that exists but is malformed isn't unknown: its own E3 says
    what's wrong with it.
    """
    if isinstance(project.knowledge, Broken):
        return []
    known = table(project.knowledge, "deductions").known()
    path = project.paths.canon_file("clues")
    issues = []
    for clue in table(project.clues, "clues").entries.values():
        for ident in [d for d in clue.proves if d not in known]:
            message = f"proves unknown deduction {q(ident)}."
            issues.append(error("E7", path, f"clues.{clue.id}", message))
    return issues + _unknown_claims(project, known)


def _e8_order(project: Project) -> list[Issue]:
    index = project.config.index
    path = project.paths.canon_file("knowledge")
    issues = []
    for fact in table(project.knowledge, "facts").entries.values():
        start, reveal = index.get(fact.true_from), index.get(fact.reveal or "")
        if start is not None and reveal is not None and reveal < start:
            message = f"reveals in {fact.reveal}, before it's true in {fact.true_from}."
            issues.append(error("E8", path, f"facts.{fact.id}", message))
    for clue in table(project.clues, "clues").entries.values():
        issues += _early_finds(project, clue)
    return issues


def _early_finds(project: Project, clue: Clue) -> list[Issue]:
    index = project.config.index
    plant = index.get(clue.plant.point)
    if plant is None:
        return []
    path = project.paths.canon_file("clues")
    issues = []
    for number, find in enumerate(clue.finds):
        if index.get(find.point, plant) < plant:
            message = (
                f"found in {find.point}, before it's planted in {clue.plant.point}."
            )
            issues.append(
                error("E8", path, f"clues.{clue.id}.finds[{number}]", message)
            )
    return issues


def default_problem(entry: StateEntry) -> str | None:
    """Say why a state default doesn't fit its type, or None if it fits (E9)."""
    tests = {"int": is_int, "bool": is_bool, "string": is_str, "list": is_str_list}
    if not tests[entry.type](entry.default):
        return f"default {show(entry.default)} doesn't fit type {q(entry.type)}."
    if entry.type != "list":
        return None
    missing = [item for item in entry.default if item not in entry.items]
    if missing:
        return f"default names {q(missing[0])}, which isn't in items."
    return None


def _e9_defaults(project: Project) -> list[Issue]:
    path = project.paths.canon_file("state")
    issues = []
    for entry in table(project.state, "state").entries.values():
        problem = default_problem(entry)
        if problem is not None:
            issues.append(error("E9", path, f"state.{entry.id}", problem))
    return issues


def _name_issues(path: str, ident: str) -> list[Issue]:
    stem = PurePosixPath(path).stem
    if ident == stem:
        return []
    message = f"id {q(ident)} doesn't match the file name {q(stem)}."
    return [error("E11", path, "front matter", message)]


def _e11_names(project: Project) -> list[Issue]:
    pattern = knot_pattern(project.config)
    issues = []
    for beat in project.beats:
        issues += _name_issues(beat.path, beat.id)
        if pattern is not None and not pattern.fullmatch(beat.id):
            message = f"id {q(beat.id)} doesn't match [ink] knot."
            issues.append(error("E11", beat.path, "front matter", message))
    for scene in project.scenes:
        issues += _name_issues(scene.path, scene.id)
    return issues


def _unknown_refs(
    beat: Beat, refs: Sequence[tuple[str, str]], known: frozenset[str], ledger: str
) -> list[Issue]:
    return [
        error("E12", beat.path, field, f"{q(name)} isn't in {ledger}.")
        for field, name in refs
        if name not in known
    ]


def _e12_refs(project: Project) -> list[Issue]:
    """Each half runs only when its ledger loaded. A malformed entry isn't unknown."""
    clues = table(project.clues, "clues").known()
    state = table(project.state, "state").known()
    issues = []
    for beat in project.beats:
        if isinstance(project.clues, Loaded):
            issues += _unknown_refs(beat, _clue_refs(beat), clues, "clues.toml")
        if isinstance(project.state, Loaded):
            issues += _unknown_refs(beat, _state_refs(beat), state, "state.toml")
    return issues


def _e13_scenes(project: Project) -> list[Issue]:
    beat_ids = {PurePosixPath(p).stem for p in beat_paths(project.files, project.paths)}
    return [
        error("E13", scene.path, "front matter", f"id {q(scene.id)} has no beat sheet.")
        for scene in project.scenes
        if scene.id not in beat_ids
    ]


# ---------------------------------------------------------------------------
# check: W1 to W8 (W9 is found while parsing)
# ---------------------------------------------------------------------------


def _w1_canon(project: Project) -> list[Issue]:
    message = "required canon file doesn't exist yet."
    return [
        warning("W1", project.paths.canon_file(name), "", message)
        for name in REQUIRED_CANON
        if not canon_exists(project, name)
    ]


def _w2_routes(project: Project) -> list[Issue]:
    minimum = project.config.min_routes
    path = project.paths.canon_file("clues")
    issues = []
    for clue in table(project.clues, "clues").entries.values():
        count = len(clue.finds)
        if clue.required and count < minimum:
            noun = "find" if count == 1 else "finds"
            message = f"required clue has {count} {noun}; min_routes is {minimum}."
            issues.append(warning("W2", path, f"clues.{clue.id}", message))
    return issues


def earliest_reveal(project: Project) -> int | None:
    """Return the play-order index of the earliest fact `reveal`, or None."""
    index = project.config.index
    facts = table(project.knowledge, "facts").entries.values()
    reveals = [index[f.reveal] for f in facts if f.reveal in index]
    return min(reveals) if reveals else None


def needs_innocent(clue: Clue, plant: int | None, reveal: int | None) -> bool:
    """True if a clue needs an `innocent` reading and lacks one (W3).

    knot doesn't link facts to deductions, so "before the reveal" means before
    the earliest reveal of any fact. With no reveal at all, every clue that
    proves something counts as early: W3 errs toward asking.
    """
    if clue.innocent or not clue.proves or plant is None:
        return False
    return reveal is None or plant < reveal


def _w3_innocent(project: Project) -> list[Issue]:
    reveal = earliest_reveal(project)
    index = project.config.index
    path = project.paths.canon_file("clues")
    message = "is planted before the reveal and has no innocent reading."
    return [
        warning("W3", path, f"clues.{clue.id}", message)
        for clue in table(project.clues, "clues").entries.values()
        if needs_innocent(clue, index.get(clue.plant.point), reveal)
    ]


def _w4_beat_coverage(project: Project) -> list[Issue]:
    if not project.beats:
        return []
    planted = {c for beat in project.beats for c in beat.plants}
    found = {c for beat in project.beats for c in beat.finds}
    path = project.paths.canon_file("clues")
    issues = []
    for clue in table(project.clues, "clues").entries.values():
        entry = f"clues.{clue.id}"
        if clue.id not in planted:
            issues.append(warning("W4", path, entry, "no beat sheet plants it."))
        if clue.required and clue.id not in found:
            message = "required clue is found by no beat sheet."
            issues.append(warning("W4", path, entry, message))
    return issues


def _w5_missing_ledgers(project: Project) -> list[Issue]:
    issues = []
    for beat in project.beats:
        if _clue_refs(beat) and isinstance(project.clues, Missing):
            message = "names clues, and clues.toml doesn't exist yet."
            issues.append(warning("W5", beat.path, "front matter", message))
        if _state_refs(beat) and isinstance(project.state, Missing):
            message = "names state, and state.toml doesn't exist yet."
            issues.append(warning("W5", beat.path, "front matter", message))
    return issues


def _w6_state_coverage(project: Project) -> list[Issue]:
    if not project.beats:
        return []
    used = {name for beat in project.beats for _field, name in _state_refs(beat)}
    path = project.paths.canon_file("state")
    return [
        warning("W6", path, f"state.{entry.id}", "no beat sheet reads or sets it.")
        for entry in table(project.state, "state").entries.values()
        if entry.id not in used
    ]


def _w7_plant_points(project: Project) -> list[Issue]:
    clues = table(project.clues, "clues").entries
    planted = [(b, clues[c]) for b in project.beats for c in b.plants if c in clues]
    issues = []
    for beat, clue in planted:
        if clue.plant.point != beat.point:
            message = (
                f"clue {q(clue.id)} has plant.point {q(clue.plant.point)};"
                f" this beat is in {q(beat.point)}."
            )
            issues.append(warning("W7", beat.path, "plants", message))
    return issues


def _w8_patterns(project: Project) -> list[Issue]:
    return [
        warning("W8", beat.path, "pattern", f"unknown pattern {q(name)}.")
        for beat in project.beats
        for name in beat.pattern
        if name not in PATTERNS
    ]


CHECKS: tuple[Callable[[Project], list[Issue]], ...] = (
    _e2_points,
    _e4_ids,
    _e5_headings,
    _e6_who,
    _e7_proves,
    _e8_order,
    _e9_defaults,
    _e11_names,
    _e12_refs,
    _e13_scenes,
    _w1_canon,
    _w2_routes,
    _w3_innocent,
    _w4_beat_coverage,
    _w5_missing_ledgers,
    _w6_state_coverage,
    _w7_plant_points,
    _w8_patterns,
)


def check_project(project: Project) -> tuple[Issue, ...]:
    """Run every `check` rule on a parsed project.

    Returns:
        The parse issues, then each rule's issues. Rules never raise; an
        entry broken under one rule is skipped by the others where it would
        only repeat the same mistake.
    """
    issues = list(project.issues)
    for rule in CHECKS:
        issues.extend(rule(project))
    return tuple(issues)


# ---------------------------------------------------------------------------
# ink: I1 to I8 over the .ink files, I0 from the compiler
# ---------------------------------------------------------------------------

BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
LINE_COMMENT_RE = re.compile(r"//[^\n]*")
DECLARATION_RE = re.compile(r"\s*(VAR|LIST)\s+([A-Za-z_]\w*)\s*=\s*(.*?)\s*")
# Logic lines and declarations carry no tags, so a "#" in them is never one.
NO_TAGS_RE = re.compile(r"\s*(?:~|(?:VAR|CONST|LIST|INCLUDE)\b)")
TAG_RE = re.compile(r"(?<!\\)#([^#]*)")
KNOT_RE = re.compile(r"\s*={2,}\s*(function\s+)?([A-Za-z_]\w*)")
INT_RE = re.compile(r"-?\d+")


@dataclass(frozen=True)
class InkLine:
    """One line of an `.ink` file with comments removed."""

    path: str
    number: int
    text: str


@dataclass(frozen=True)
class InkExpression:
    """A `VAR` value that isn't a plain int, bool, or string literal."""

    text: str


@dataclass(frozen=True)
class Declaration:
    """A `VAR` or `LIST` declaration.

    For a VAR, `value` is an int, bool, str, or InkExpression. For a LIST,
    `items` names every item in order and `on` the ones switched on at the
    start; `value` is None.
    """

    path: str
    line: int
    keyword: str
    name: str
    value: object
    items: tuple[str, ...]
    on: tuple[str, ...]


def strip_comments(text: str) -> str:
    """Remove Ink `//` and `/* */` comments, keeping line numbers."""
    without_blocks = BLOCK_COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    return LINE_COMMENT_RE.sub("", without_blocks)


def ink_lines(project: Project) -> list[InkLine]:
    """Return every line of every `.ink` file under the ink folder."""
    lines = []
    for path in files_under(project.files, project.paths.ink, ".ink", True):
        text = strip_comments(project.files[path])
        for number, line in enumerate(text.splitlines(), start=1):
            lines.append(InkLine(path, number, line))
    return lines


def ink_value(text: str) -> object:
    """Read a `VAR` value: an int, bool, string literal, or other expression."""
    if INT_RE.fullmatch(text):
        return int(text)
    if text in ("true", "false"):
        return text == "true"
    if len(text) >= 2 and text.startswith('"') and text.endswith('"'):
        return text[1:-1]
    return InkExpression(text)


def list_items(text: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Read a `LIST` body such as `a, (b), c = 3`.

    Returns:
        (every item name in order, the names in parentheses, which start on).
    """
    items = []
    on = []
    for raw in text.split(","):
        part = raw.strip()
        name = part.strip("()").split("=")[0].strip()
        items.append(name)
        if part.startswith("("):
            on.append(name)
    return tuple(items), tuple(on)


def parse_declaration(line: InkLine) -> Declaration | None:
    """Parse a `VAR` or `LIST` line, or return None for any other line."""
    match = DECLARATION_RE.fullmatch(line.text)
    if match is None:
        return None
    keyword, name, value = match.groups()
    if keyword == "LIST":
        items, on = list_items(value)
        return Declaration(line.path, line.number, keyword, name, None, items, on)
    return Declaration(line.path, line.number, keyword, name, ink_value(value), (), ())


def tag_names(text: str) -> list[str]:
    """Return the name of each tag on a line: the text after `#` up to a colon or space."""
    names = []
    for match in TAG_RE.finditer(text):
        name = re.split(r"[:\s]", match.group(1).strip(), maxsplit=1)[0]
        if name:
            names.append(name)
    return names


def _i1_outside_globals(
    declarations: Sequence[Declaration], globals_path: str
) -> list[Issue]:
    name = PurePosixPath(globals_path).name
    return [
        error(
            "I1",
            d.path,
            f"line {d.line}",
            f"{d.keyword} {d.name} is declared outside {name}.",
        )
        for d in declarations
        if d.path != globals_path
    ]


def _i2_unledgered(
    declared: Sequence[Declaration], state: Mapping[str, StateEntry]
) -> list[Issue]:
    return [
        error("I2", d.path, d.name, f"{d.keyword} {d.name} has no state.toml entry.")
        for d in declared
        if d.name not in state
    ]


def _i3_i8_undeclared(
    project: Project, declared: Sequence[Declaration], state: Mapping[str, StateEntry]
) -> list[Issue]:
    names = {d.name for d in declared}
    path = project.paths.canon_file("state")
    globals_name = PurePosixPath(project.paths.ink_globals).name
    issues = []
    for entry in [e for e in state.values() if e.id not in names]:
        if entry.proposed:
            message = f"proposed entry isn't declared in {globals_name} yet."
            issues.append(warning("I8", path, f"state.{entry.id}", message))
        else:
            message = f"isn't declared in {globals_name}."
            issues.append(error("I3", path, f"state.{entry.id}", message))
    return issues


def _list_mismatch(declaration: Declaration, entry: StateEntry) -> str | None:
    if declaration.keyword != "LIST":
        return 'declared as a VAR; state.toml type is "list".'
    if declaration.items != entry.items:
        found, expected = show(list(declaration.items)), show(list(entry.items))
        return f"items are {found}; state.toml items are {expected}."
    expected_on = set(entry.default) if is_str_list(entry.default) else None
    if set(declaration.on) != expected_on:
        found = show(sorted(declaration.on))
        return f"starts with {found} on; state.toml default is {show(entry.default)}."
    return None


def declaration_mismatch(declaration: Declaration, entry: StateEntry) -> str | None:
    """Say how a declaration differs from its state entry, or None (I4)."""
    if entry.type == "list":
        return _list_mismatch(declaration, entry)
    if declaration.keyword != "VAR":
        return f"declared as a LIST; state.toml type is {q(entry.type)}."
    tests = {"int": is_int, "bool": is_bool, "string": is_str}
    value = declaration.value
    if tests[entry.type](value) and value == entry.default:
        return None
    return f"declared as {show(value)}; state.toml default is {show(entry.default)}."


def _i4_mismatches(
    declared: Sequence[Declaration], state: Mapping[str, StateEntry]
) -> list[Issue]:
    issues = []
    for declaration in [d for d in declared if d.name in state]:
        problem = declaration_mismatch(declaration, state[declaration.name])
        if problem is not None:
            issues.append(error("I4", declaration.path, declaration.name, problem))
    return issues


def _state_ink_issues(project: Project, declared: Sequence[Declaration]) -> list[Issue]:
    """I2, I3, I4, and I8 against state.toml.

    When state.toml can't be read, its E3 comes instead of all four. When one
    entry can't be read, its E3 comes instead of the I codes for that name.
    """
    if isinstance(project.state, Broken):
        return list(project.state.issues)
    rows = table(project.state, "state")
    issues = [issue for found in rows.broken.values() for issue in found]
    readable = [d for d in declared if d.name not in rows.broken]
    issues += _i2_unledgered(readable, rows.entries)
    issues += _i3_i8_undeclared(project, declared, rows.entries)
    return issues + _i4_mismatches(readable, rows.entries)


def _tags(lines: Sequence[InkLine]) -> Iterator[tuple[InkLine, str]]:
    for line in lines:
        if NO_TAGS_RE.match(line.text):
            continue
        for name in tag_names(line.text):
            yield line, name


def _i5_tags(config: Config, lines: Sequence[InkLine]) -> list[Issue]:
    allowed = config.ink.tags
    if allowed is None:
        return []
    return [
        error(
            "I5",
            line.path,
            f"line {line.number}",
            f"tag {q(name)} isn't in [ink] tags.",
        )
        for line, name in _tags(lines)
        if name not in allowed
    ]


def _i6_knots(config: Config, lines: Sequence[InkLine]) -> list[Issue]:
    pattern = knot_pattern(config)
    if pattern is None:
        return []
    issues = []
    for line in lines:
        match = KNOT_RE.match(line.text)
        if match and not match.group(1) and not pattern.fullmatch(match.group(2)):
            message = f"knot {q(match.group(2))} doesn't match [ink] knot."
            issues.append(warning("I6", line.path, f"line {line.number}", message))
    return issues


def _i7_unused(
    declared: Sequence[Declaration], lines: Sequence[InkLine], globals_path: str
) -> list[Issue]:
    elsewhere = "\n".join(line.text for line in lines if line.path != globals_path)
    name = PurePosixPath(globals_path).name
    issues = []
    for d in declared:
        if not re.search(rf"\b{re.escape(d.name)}\b", elsewhere):
            message = f"{d.keyword} {d.name} is never mentioned outside {name}."
            issues.append(warning("I7", d.path, d.name, message))
    return issues


def ink_issues(project: Project) -> tuple[Issue, ...]:
    """Run I1 to I8 over every `.ink` file. The compiler (I0) runs separately."""
    lines = ink_lines(project)
    declarations = [d for d in map(parse_declaration, lines) if d is not None]
    globals_path = project.paths.ink_globals
    declared = [d for d in declarations if d.path == globals_path]
    issues = _i1_outside_globals(declarations, globals_path)
    issues += _state_ink_issues(project, declared)
    issues += _i5_tags(project.config, lines)
    issues += _i6_knots(project.config, lines)
    issues += _i7_unused(declared, lines, globals_path)
    return tuple(issues)


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
COMPILER_RE = re.compile(
    r"ERROR:\s*(?:'(?P<file>[^']*)'\s*)?(?:line (?P<line>\d+):\s*)?(?P<message>.*)"
)


def _compiler_issue(match: re.Match[str], main: str) -> Issue:
    folder = str(PurePosixPath(main).parent)
    file = join(folder, match["file"]) if match["file"] else main
    entry = f"line {match['line']}" if match["line"] else ""
    return error("I0", file, entry, match["message"].rstrip(".") + ".")


def compiler_issues(output: str, returncode: int, main: str) -> tuple[Issue, ...]:
    """Turn inklecate's output into I0 errors.

    Args:
        output: inklecate's stdout and stderr together.
        returncode: its exit code.
        main: the main ink file, relative to the project dir. inklecate names
            files relative to the main file's folder.
    Returns:
        One I0 error per distinct `ERROR:` line; inklecate can print the same
        error twice. A failed run with no such line still gives one I0 error.
    """
    issues = []
    for line in ANSI_RE.sub("", output).splitlines():
        match = COMPILER_RE.fullmatch(line.strip())
        if match:
            issues.append(_compiler_issue(match, main))
    if returncode != 0 and not issues:
        message = f"inklecate exited with code {returncode}."
        issues.append(error("I0", main, "", message))
    return tuple(dict.fromkeys(issues))


def compile_ink(project_dir: Path, main: str, inklecate: str) -> tuple[Issue, ...]:
    """Compile the main ink file with inklecate. Runs a process.

    The compiled JSON goes to a temporary folder, so the project is never
    written to.
    """
    source = project_dir / main
    if not source.is_file():
        return (error("I0", main, "", "the main ink file doesn't exist."),)
    with tempfile.TemporaryDirectory() as scratch:
        command = [inklecate, "-o", str(Path(scratch) / "story.json"), source.name]
        try:
            result = subprocess.run(
                command,
                cwd=source.parent,
                capture_output=True,
                text=True,
                timeout=COMPILE_TIMEOUT,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return (error("I0", main, "", f"inklecate could not run: {exc}."),)
    return compiler_issues(result.stdout + result.stderr, result.returncode, main)


# ---------------------------------------------------------------------------
# Packets: inputs for review's fresh-reader tests
# ---------------------------------------------------------------------------

# An unclosed comment hides the rest of the file when rendered, so it runs to the end.
HTML_COMMENT_RE = re.compile(r"<!--.*?(?:-->|\Z)", re.DOTALL)


@dataclass(frozen=True)
class LayerDoc:
    """A file from a story layer, as the cold read sees it."""

    path: str
    points: tuple[str, ...]
    body: str


def packet_issues(project: Project, kind: str) -> list[Issue]:
    """Return what stops a packet from being built (contract §7).

    Both packets stop on knot.toml's E1 and E2 errors. The solver also stops
    on unknown claims (E7), and on claims whose deduction can't be read: it
    has no claim text to print, so that deduction's E3 is returned.
    """
    codes = ("E1", "E2", "E7") if kind == "solver" else ("E1", "E2")
    issues = [
        issue
        for issue in check_project(project)
        if issue.file == KNOT_TOML and issue.code in codes
    ]
    if kind != "solver":
        return issues
    if isinstance(project.knowledge, Broken):
        return issues + list(project.knowledge.issues)
    broken = table(project.knowledge, "deductions").broken
    claimed = [ident for _label, ident in claims(project.config.solver)]
    return issues + [issue for ident in claimed for issue in broken.get(ident, ())]


def layer_docs(project: Project, layers: Sequence[str]) -> list[LayerDoc]:
    """Return the usable files of the chosen layers."""
    docs = []
    if "treatment" in layers:
        docs += [LayerDoc(t.path, t.points, t.body) for t in project.treatments]
    if "beats" in layers:
        docs += [LayerDoc(b.path, (b.point,), b.body) for b in project.beats]
    if "scenes" in layers:
        docs += [LayerDoc(s.path, (s.point,), s.body) for s in project.scenes]
    return docs


def cold_read_parts(project: Project) -> list[LayerDoc]:
    """Return the cold read's files: all points before `before`, in order.

    Files are ordered by their earliest point, then path. A file naming an
    unknown point is left out.
    """
    cold = project.config.cold_read
    index = project.config.index
    limit = index.get(cold.before)
    if limit is None:
        return []
    chosen = [
        doc
        for doc in layer_docs(project, cold.layers)
        if doc.points and all(index.get(p, limit) < limit for p in doc.points)
    ]
    return sorted(chosen, key=lambda doc: (min(index[p] for p in doc.points), doc.path))


def keep_sections(text: str, names: Sequence[str]) -> str:
    """Keep only the `## ` sections whose heading is one of `names`.

    A section runs to the next `#` or `##` heading; `###` and deeper stay in
    it. Lines inside fenced code blocks are never headings.
    """
    lines = text.splitlines()
    kept = []
    keeping = False
    for number, (line, fenced) in enumerate(zip(lines, fence_flags(lines)), 1):
        heading = None if fenced else parse_heading(number, line)
        if heading is not None and heading.level <= 2:
            keeping = heading.level == 2 and heading.text in names
        if keeping:
            kept.append(line)
    return "\n".join(kept)


def clean_body(body: str, sections: Sequence[str]) -> str:
    """Strip HTML comments, then keep the chosen sections (all when empty)."""
    text = HTML_COMMENT_RE.sub("", body)
    if sections:
        text = keep_sections(text, sections)
    return text.strip()


def cold_read_packet(project: Project) -> str:
    """Build the cold-read packet: each file's chosen sections, as Part 1, 2, ..."""
    parts = cold_read_parts(project)
    if not parts:
        return "No parts.\n"
    sections = project.config.cold_read.sections
    blocks = [
        f"# Part {number}\n\n{clean_body(doc.body, sections)}"
        for number, doc in enumerate(parts, start=1)
    ]
    return "\n\n".join(blocks) + "\n"


def cold_read_key(project: Project) -> str:
    """Build the cold-read key: which part is which file, and what mustn't be guessed."""
    parts = cold_read_parts(project)
    lines = ["# Cold-read key", ""]
    lines += [
        f"- Part {number}: {doc.path}" for number, doc in enumerate(parts, start=1)
    ]
    lines += ["", f"Must not predict: {project.config.cold_read.must_not_predict}"]
    return "\n".join(lines) + "\n"


def findable_clues(project: Project) -> list[Clue]:
    """Return the clues a player can find, sorted by id.

    A clue is findable when a beat sheet lists it in `finds`. While no beat
    sheet lists any finds, a clue with at least one ledger find counts.
    """
    clues = table(project.clues, "clues").entries
    in_beats = {c for beat in project.beats for c in beat.finds}
    if in_beats:
        chosen = [ident for ident in in_beats if ident in clues]
    else:
        chosen = [ident for ident, clue in clues.items() if clue.finds]
    return [clues[ident] for ident in sorted(chosen)]


def letters(index: int) -> str:
    """Label a zero-based index as A, B, ..., Z, AA, AB, ..."""
    label = ""
    number = index + 1
    while number:
        number, remainder = divmod(number - 1, 26)
        label = chr(ord("A") + remainder) + label
    return label


def claims(solver: Solver) -> list[tuple[str, str]]:
    """Return (label, deduction id) for every claim, sorted by id."""
    idents = sorted(set(solver.must_prove) | set(solver.must_not_prove))
    return [(letters(index), ident) for index, ident in enumerate(idents)]


def solver_packet(project: Project) -> str:
    """Build the solver packet: clue texts and claims, never what proves what.

    Call it only when `packet_issues` finds nothing, so every claim's
    deduction is readable.
    """
    deductions = table(project.knowledge, "deductions").entries
    lines = ["# Clues", ""]
    lines += [
        f"{number}. {' '.join(clue.text.split())}"
        for number, clue in enumerate(findable_clues(project), start=1)
    ]
    lines += ["", "# Claims", ""]
    lines += [
        f"- Claim {label}: {' '.join(deductions[ident].claim.split())}"
        for label, ident in claims(project.config.solver)
    ]
    return "\n".join(lines) + "\n"


def solver_key(project: Project) -> str:
    """Build the solver key: which claim is which deduction, and which should hold."""
    solver = project.config.solver
    lines = ["# Solver key", "", "| Claim | Deduction | Should be |", "|---|---|---|"]
    for label, ident in claims(solver):
        expected = "provable" if ident in solver.must_prove else "not provable"
        lines.append(f"| {label} | `{ident}` | {expected} |")
    return "\n".join(lines) + "\n"


def build_packet(project: Project, kind: str, key: bool) -> str:
    """Build the packet or key for `kind`, "cold-read" or "solver"."""
    if kind == "cold-read":
        return cold_read_key(project) if key else cold_read_packet(project)
    return solver_key(project) if key else solver_packet(project)


# ---------------------------------------------------------------------------
# config: the resolved configuration as JSON
# ---------------------------------------------------------------------------


def _templates_json(project: Project, plugin_root: Path) -> dict[str, str]:
    overrides = template_overrides(project.config)
    result = {}
    for layer, (_file, default) in TEMPLATE_FILES.items():
        override = overrides.get(layer)
        result[layer] = (
            override if override in project.files else str(plugin_root / default)
        )
    return result


def _review_json(config: Config) -> dict[str, dict]:
    cold, solver = config.cold_read, config.solver
    return {
        "cold_read": {} if cold is None else asdict(cold),
        "solver": {} if solver is None else asdict(solver),
    }


def _paths_json(paths: Layout) -> dict[str, str]:
    return {
        "canon": paths.canon,
        "spine": paths.spine,
        "treatment": paths.treatment,
        "beats": paths.beats,
        "scenes": paths.scenes,
        "ink": paths.ink,
        "reviews": paths.reviews,
    }


def _canon_json(project: Project) -> dict[str, dict]:
    return {
        name: {
            "path": project.paths.canon_file(name),
            "exists": canon_exists(project, name),
        }
        for name in CANON_FILES
    }


def _ink_json(project: Project) -> dict[str, object]:
    ink = project.config.ink
    return {
        "dir": project.paths.ink,
        "main": ink.main,
        "globals": ink.globals,
        "knot": ink.knot,
        "tags": None if ink.tags is None else list(ink.tags),
    }


def config_json(project: Project, project_dir: Path, plugin_root: Path) -> dict:
    """Build the `config` command's JSON (contract §7).

    Project paths are relative to `project_dir`; plugin paths are absolute.
    A template override is used when its file exists. `ink.knot` and
    `ink.tags` are null when knot.toml doesn't set them.
    """
    config = project.config
    return {
        "project": config.name,
        "project_dir": str(project_dir),
        "plugin_root": str(plugin_root),
        "root": config.root,
        "truth": list(config.truth),
        "points": list(config.points),
        "paths": _paths_json(project.paths),
        "canon": _canon_json(project),
        "templates": _templates_json(project, plugin_root),
        "clues": {"min_routes": config.min_routes},
        "ink": _ink_json(project),
        "checks": list(config.checks),
        "rules": [asdict(rule) for rule in config.rules],
        "review": _review_json(config),
    }


# ---------------------------------------------------------------------------
# Report format (§7)
# ---------------------------------------------------------------------------


def _code_order(issue: Issue) -> tuple[str, int]:
    return issue.code[0], int(issue.code[1:])


def format_issue(issue: Issue) -> str:
    """Format one issue as `  E7 story/canon/clues.toml clues.c_record: message`."""
    where = f"{issue.file} {issue.entry}" if issue.entry else issue.file
    return f"  {issue.code} {where}: {issue.message}"


def format_report(issues: Sequence[Issue]) -> str:
    """Format issues under Errors and Warnings, by rule code, with a count line."""
    if not issues:
        return "No issues.\n"
    errors = sorted(
        (i for i in issues if i.severity is Severity.ERROR), key=_code_order
    )
    warnings = sorted(
        (i for i in issues if i.severity is Severity.WARNING), key=_code_order
    )
    lines = []
    if errors:
        lines.append(f"Errors ({len(errors)}):")
        lines.extend(format_issue(issue) for issue in errors)
    if warnings:
        lines.append(f"Warnings ({len(warnings)}):")
        lines.extend(format_issue(issue) for issue in warnings)
    lines.append(f"{len(errors)} error(s), {len(warnings)} warning(s).")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Reading the project: the only code that reads files
# ---------------------------------------------------------------------------


def find_project(start: Path) -> Path | None:
    """Walk up from `start` to the first folder holding `knot.toml`, as git finds `.git`."""
    for folder in (start, *start.parents):
        if (folder / KNOT_TOML).is_file():
            return folder
    return None


def locate(project: Path | None, cwd: Path) -> Path | None:
    """Return the project dir: `--project` if it holds `knot.toml`, else a walk up."""
    if project is None:
        return find_project(cwd.resolve())
    folder = project.resolve()
    return folder if (folder / KNOT_TOML).is_file() else None


def read_text(path: Path) -> str | None:
    """Read a UTF-8 file, or return None if it can't be read."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def list_files(project_dir: Path, folder: str, pattern: str) -> list[str]:
    """List project-relative paths of files matching a glob under a folder.

    `folder` must be relative; `parse_config` rejects an absolute root or
    ink dir with E1.
    """
    base = project_dir / folder
    if not base.is_dir():
        return []
    matches = [path for path in base.glob(pattern) if path.is_file()]
    return sorted(path.relative_to(project_dir).as_posix() for path in matches)


def wanted_files(project_dir: Path, config: Config) -> list[str]:
    """List every file knot reads, relative to the project dir."""
    paths = layout(config)
    wanted = [paths.canon_file(name) for name in CANON_FILES]
    wanted += [join(extra.file) for extra in config.extra]
    wanted += list(template_overrides(config).values())
    wanted += list_files(project_dir, paths.treatment, "**/*.md")
    wanted += list_files(project_dir, paths.beats, "*.md")
    wanted += list_files(project_dir, paths.scenes, "*.md")
    wanted += list_files(project_dir, paths.ink, "**/*.ink")
    return wanted


def read_snapshot(project_dir: Path, config: Config) -> Mapping[str, str]:
    """Read every file knot needs into a snapshot keyed by relative path.

    A file that doesn't exist or can't be read is left out.
    """
    files = {}
    for relative in wanted_files(project_dir, config):
        text = read_text(project_dir / relative)
        if text is not None:
            files[relative] = text
    return MappingProxyType(files)


def open_project(project_dir: Path) -> Project | Rejected:
    """Read and parse a whole project.

    Returns:
        The Project, or Rejected when `knot.toml` can't be read or used.
    """
    text = read_text(project_dir / KNOT_TOML)
    if text is None:
        return Rejected((error("E1", KNOT_TOML, "", "can't be read."),))
    parsed = parse_config(text)
    if isinstance(parsed, Rejected):
        return parsed
    files = read_snapshot(project_dir, parsed.config)
    return build_project(parsed.config, files, parsed.issues)


# ---------------------------------------------------------------------------
# Commands: each returns its Output, and main prints it
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Output:
    """What a command prints, and its exit code. Only `main` prints it."""

    code: int
    stdout: str = ""
    stderr: str = ""


@dataclass(frozen=True)
class Opened:
    """A located, parsed project."""

    project_dir: Path
    project: Project


def _refusal(issues: Sequence[Issue], on_stdout: bool) -> Output:
    """Exit 1 with a report: on stdout for check and ink, else on stderr."""
    report = format_report(issues)
    if on_stdout:
        return Output(1, stdout=report)
    return Output(1, stderr=report)


def _open(args: argparse.Namespace, report_on_stdout: bool) -> Opened | Output:
    """Locate and open the project, or return the Output that says why not."""
    project_dir = locate(args.project, Path.cwd())
    if project_dir is None:
        where = args.project if args.project is not None else "here or any parent"
        return Output(2, stderr=f"knot.py: no knot.toml in {where}.\n")
    result = open_project(project_dir)
    if isinstance(result, Rejected):
        return _refusal(result.issues, report_on_stdout)
    return Opened(project_dir, result)


def cmd_config(args: argparse.Namespace) -> Output:
    """The resolved configuration as JSON."""
    opened = _open(args, report_on_stdout=False)
    if isinstance(opened, Output):
        return opened
    data = config_json(opened.project, opened.project_dir, PLUGIN_ROOT)
    return Output(0, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def cmd_check(args: argparse.Namespace) -> Output:
    """The check report. Exits 1 on any error, else 0."""
    opened = _open(args, report_on_stdout=True)
    if isinstance(opened, Output):
        return opened
    issues = check_project(opened.project)
    if args.strict:
        issues = promote(issues)
    return Output(1 if has_errors(issues) else 0, format_report(issues))


def cmd_ink(args: argparse.Namespace) -> Output:
    """The ink report, compiling with inklecate when it's on PATH."""
    opened = _open(args, report_on_stdout=True)
    if isinstance(opened, Output):
        return opened
    project = opened.project
    issues = ink_issues(project)
    inklecate = shutil.which("inklecate")
    if inklecate is None:
        text = format_report(issues) + COMPILE_SKIPPED + "\n"
    else:
        issues += compile_ink(opened.project_dir, project.paths.ink_main, inklecate)
        text = format_report(issues)
    return Output(1 if has_errors(issues) else 0, text)


def cmd_packet(args: argparse.Namespace) -> Output:
    """A fresh-reader packet, or its key with `--key`."""
    opened = _open(args, report_on_stdout=False)
    if isinstance(opened, Output):
        return opened
    project = opened.project
    cold_read = args.kind == "cold-read"
    settings = project.config.cold_read if cold_read else project.config.solver
    if settings is None:
        name = "cold_read" if cold_read else "solver"
        return Output(2, stderr=f"knot.py: knot.toml has no [review.{name}] table.\n")
    issues = packet_issues(project, args.kind)
    if issues:
        return _refusal(issues, on_stdout=False)
    return Output(0, build_packet(project, args.kind, args.key))


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for config, check, ink, and packet."""
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--project",
        type=Path,
        help="folder holding knot.toml (default: walk up from the working directory)",
    )
    parser = argparse.ArgumentParser(
        prog="knot.py", description="Check a knot project."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    config = commands.add_parser(
        "config", parents=[common], help="print the config as JSON"
    )
    config.set_defaults(handler=cmd_config)
    check = commands.add_parser(
        "check", parents=[common], help="check canon and story files"
    )
    check.add_argument("--strict", action="store_true", help="treat warnings as errors")
    check.set_defaults(handler=cmd_check)
    ink = commands.add_parser("ink", parents=[common], help="check and compile the Ink")
    ink.set_defaults(handler=cmd_ink)
    packet = commands.add_parser(
        "packet", parents=[common], help="print a review packet"
    )
    packet.add_argument("kind", choices=("cold-read", "solver"))
    packet.add_argument(
        "--key", action="store_true", help="print the answer key instead"
    )
    packet.set_defaults(handler=cmd_packet)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line, print its output, and return the exit code."""
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2
    output = args.handler(args)
    sys.stdout.write(output.stdout)
    sys.stderr.write(output.stderr)
    return output.code


if __name__ == "__main__":
    sys.exit(main())
