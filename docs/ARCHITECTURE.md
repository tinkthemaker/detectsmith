# Detectsmith Architecture

## Design principle

Detectsmith v0.1 should be a small, deterministic Python CLI. Avoid services, databases, background processes, and live external dependencies.

The architecture should leave room for a future Go Charm TUI, but the TUI must remain a frontend over the Python CLI and JSON reports. Do not design v0.1 around UI state or duplicate detection logic in Go.

## Planned stack

- Python 3.11+
- `pyyaml` for YAML parsing
- `typer` or `click` for CLI commands
- `rich` for readable terminal output
- `pytest` for tests
- `jinja2` optional for documentation templates

Dependency choices should stay minimal. Do not add heavy frameworks without explicit approval.

## Proposed package layout

```text
detectsmith/
  detectsmith/
    __init__.py
    cli.py
    models.py
    rules.py
    lint.py
    matcher.py
    test_runner.py
    coverage.py
    docs.py
    reporting.py
  rules/
    windows/
    linux/
    cloud/aws/
    m365/
  tests/
    unit/
    fixtures/
    expected.yml
  docs/
    SCOPE.md
    ARCHITECTURE.md
    QUALITY_MODEL.md
    TESTING_STRATEGY.md
    REPORT_SCHEMAS.md
    TUI_ROADMAP.md
    plans/
  reports/
    .gitkeep
  site/
    .gitkeep
  .github/workflows/
    detection-ci.yml
  AGENTS.md
  README.md
  pyproject.toml
  # Future, not v0.1:
  # tui/ or cmd/detectsmith-tui/  # Go Charm TUI frontend
```

## Module responsibilities

### `detectsmith/cli.py`

Owns command-line interface and argument parsing.

Commands:

```bash
detectsmith lint rules/
detectsmith test tests/expected.yml
detectsmith coverage rules/
detectsmith docs rules/ --out site/
```

CLI should call library functions and keep business logic out of command handlers.

### `detectsmith/models.py`

Defines small dataclasses or typed structures for:

- `Rule`
- `LintFinding`
- `LintReport`
- `TestCase`
- `TestResult`
- `CoverageReport`

Prefer plain dataclasses over complex validation frameworks for v0.1.

### `detectsmith/rules.py`

Loads and parses Sigma-style YAML files.

Responsibilities:

- Recursively discover `.yml` and `.yaml` files.
- Parse YAML safely.
- Preserve source path for diagnostics.
- Return structured rule objects or parse errors.
- Detect duplicate IDs.

### `detectsmith/lint.py`

Applies metadata and quality checks.

Responsibilities:

- Required-field validation.
- Quality scoring.
- Finding severity assignment.
- Human-readable recommendations.

No file I/O except where explicitly needed; most functions should accept `Rule` objects.

### `detectsmith/matcher.py`

Evaluates the constrained Sigma subset against one JSON event.

Responsibilities:

- Exact matching.
- `contains`, `startswith`, `endswith` modifiers.
- List value matching.
- Simple condition handling.
- Clear unsupported-feature errors.

This module should have the strongest unit test coverage.

### `detectsmith/test_runner.py`

Runs rule/fixture expectations.

Responsibilities:

- Load `tests/expected.yml`.
- Load JSONL fixtures.
- Run matcher against every event.
- Decide pass/fail for each test case.
- Produce machine-readable and human-readable results.

### `detectsmith/coverage.py`

Generates ATT&CK coverage summaries from rule tags.

Responsibilities:

- Extract `attack.t####` and `attack.t####.###` tags.
- Count rules per technique.
- Count rules per tactic tag.
- Identify rules missing ATT&CK tags.
- Emit Markdown and JSON reports.

### `detectsmith/docs.py`

Generates documentation site files.

Responsibilities:

- Generate one Markdown page per rule.
- Generate an index page.
- Include metadata, ATT&CK tags, false positives, references, and test status where available.

### `detectsmith/reporting.py`

Shared output helpers.

Responsibilities:

- JSON serialization.
- Markdown table helpers.
- Rich terminal tables.
- Common report envelope and schema fields from `docs/REPORT_SCHEMAS.md`.

## Data flow

### Lint flow

```text
rules directory
  -> rules.discover_rules()
  -> rules.parse_rule()
  -> lint.lint_rules()
  -> terminal table + optional JSON report
```

### Test flow

```text
expected.yml
  -> test_runner.load_expectations()
  -> rules.parse_rule(rule path)
  -> load fixture JSONL
  -> matcher.match(rule, event)
  -> pass/fail report
```

### Coverage flow

```text
rules directory
  -> parse tags
  -> aggregate by tactic/technique/platform
  -> reports/attack_coverage.md + reports/attack_coverage.json
```

### Docs flow

```text
rules directory + optional test results
  -> rule docs
  -> index
  -> coverage link/summary
```

### Future TUI flow

Not part of v0.1 implementation, but the intended integration boundary is:

```text
detectsmith-tui
  -> runs detectsmith lint/test/coverage/docs as subprocesses
  -> reads reports/lint.json, reports/test_results.json, reports/attack_coverage.json, reports/docs.json
  -> renders dashboard, rule findings, test results, coverage, and docs status
```

The TUI should not parse human-readable terminal output except for last-resort error display. It should rely on `docs/REPORT_SCHEMAS.md` and `docs/TUI_ROADMAP.md`.

## Error handling philosophy

Errors should be specific and actionable.

Bad:

```text
Invalid rule.
```

Good:

```text
rules/windows/example.yml: detection.condition uses unsupported expression 'selection1 near selection2'. v0.1 supports 'selection' and simple 'selection and not filter'.
```

## CI architecture

GitHub Actions should run:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
detectsmith lint rules/ --format json --output reports/lint.json
detectsmith test tests/expected.yml --format json --output reports/test_results.json
detectsmith coverage rules/ --format json --output reports/attack_coverage.json
detectsmith docs rules/ --out site/ --format json --output reports/docs.json
```

## Future extension points

These are intentionally not v0.1, but architecture should not block them:

- Additional Sigma condition support.
- Backend query conversion through pySigma.
- SARIF output for lint findings.
- GitHub Pages publishing.
- Importing selected public detection corpora for analysis.
- Go Charm TUI frontend after JSON report schemas and exit codes are stable.

Do not implement these until the v0.1 CLI is stable.
