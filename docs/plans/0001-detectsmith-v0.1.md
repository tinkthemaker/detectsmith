# Detectsmith v0.1 Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build a local Python CLI that lints Sigma-style rules, regression-tests them against JSONL fixtures, generates ATT&CK coverage reports, and creates Markdown documentation.

**Architecture:** Small Python package with pure modules for parsing, linting, matching, testing, coverage, and docs generation. No services, databases, network calls, or live SIEM integrations in v0.1.

**Tech Stack:** Python 3.11+, pytest, pyyaml, typer or click, rich, optional jinja2.

**Future UI:** A Go Charm TUI is planned after the CLI/report contracts are stable. v0.1 should prepare for it by producing documented JSON reports, but must not implement the TUI yet.

---

## Context reset contract

If this plan is read after a context reset, first read:

1. `AGENTS.md`
2. `docs/SCOPE.md`
3. `docs/ARCHITECTURE.md`
4. `docs/QUALITY_MODEL.md`
5. `docs/TESTING_STRATEGY.md`
6. `docs/REPORT_SCHEMAS.md`
7. `docs/TUI_ROADMAP.md`

Do not expand scope without user approval.

---

## Phase 0: Repository foundation

### Task 0.1: Initialize project metadata

**Objective:** Add Python packaging metadata and basic project directories.

**Files:**
- Create: `pyproject.toml`
- Create: `detectsmith/__init__.py`
- Create: `detectsmith/cli.py`
- Create: `tests/unit/.gitkeep`
- Create: `reports/.gitkeep`
- Create: `site/.gitkeep`

**Implementation notes:**

Use package name `detectsmith`. Define console script:

```toml
[project.scripts]
detectsmith = "detectsmith.cli:app"
```

Prefer `typer` if chosen. Keep dependencies minimal.

**Verification:**

```bash
python -m pip install -e ".[dev]"
detectsmith --help
python -m pytest -q
```

Expected: command exists; tests may be empty initially but should run.

---

## Phase 1: Rule loading

### Task 1.1: Add YAML rule discovery

**Objective:** Discover `.yml` and `.yaml` rule files recursively.

**Files:**
- Create: `detectsmith/rules.py`
- Create: `tests/unit/test_rules_discovery.py`

**Test first:**

Create temp directories with mixed files and assert only YAML files are returned, sorted deterministically.

**Verification:**

```bash
python -m pytest tests/unit/test_rules_discovery.py -q
```

Expected: pass.

### Task 1.2: Parse rules safely

**Objective:** Parse YAML into structured rule objects while preserving source path and parse errors.

**Files:**
- Create: `detectsmith/models.py`
- Modify: `detectsmith/rules.py`
- Create: `tests/unit/test_rules_parsing.py`

**Requirements:**

- Use `yaml.safe_load`.
- Reject non-mapping top-level YAML.
- Preserve original raw dict.
- Surface parse errors with file path.

**Verification:**

```bash
python -m pytest tests/unit/test_rules_parsing.py -q
```

Expected: pass.

---

## Phase 2: Linter

### Task 2.1: Implement required-field lint checks

**Objective:** Validate required metadata from `docs/SCOPE.md`.

**Files:**
- Create: `detectsmith/lint.py`
- Create: `tests/unit/test_lint_required_fields.py`

**Checks:**

- `title`
- `id`
- `description`
- `logsource`
- `detection`
- `detection.condition`
- `level`
- `status`

**Verification:**

```bash
python -m pytest tests/unit/test_lint_required_fields.py -q
```

Expected: pass.

### Task 2.2: Implement quality scoring

**Objective:** Apply scoring model from `docs/QUALITY_MODEL.md`.

**Files:**
- Modify: `detectsmith/lint.py`
- Create: `tests/unit/test_lint_scoring.py`

**Requirements:**

- Clamp scores to 0..100.
- Duplicate IDs score 0 for affected rules.
- Missing recommended metadata subtracts configured points.
- Return findings with `rule_path`, `severity`, `check_id`, `message`, and `recommendation`.

**Verification:**

```bash
python -m pytest tests/unit/test_lint_scoring.py -q
```

Expected: pass.

### Task 2.3: Add `detectsmith lint` CLI

**Objective:** Expose linter through CLI.

**Files:**
- Modify: `detectsmith/cli.py`
- Create: `tests/unit/test_cli_lint.py`

**Requirements:**

- Command: `detectsmith lint rules/`
- Support `--format text|json` and `--output reports/lint.json` for future TUI/automation use.
- Print readable summary.
- Write `reports/lint.json` by default or via option.
- Exit non-zero on `error` findings.

**Verification:**

```bash
python -m pytest tests/unit/test_cli_lint.py -q
detectsmith lint rules/
```

Expected: CLI works once sample rules exist; tests should use temp fixtures.

---

## Phase 3: Matcher and regression testing

### Task 3.1: Implement exact and modifier matching

**Objective:** Match one rule selection against one event for the v0.1 subset.

**Files:**
- Create: `detectsmith/matcher.py`
- Create: `tests/unit/test_matcher.py`

**Supported:**

- Exact equality.
- `contains`.
- `startswith`.
- `endswith`.
- List values as any-match.
- Multiple fields as all-match.
- Case-insensitive string comparison.

**Verification:**

```bash
python -m pytest tests/unit/test_matcher.py -q
```

Expected: pass.

### Task 3.2: Implement expected test runner

**Objective:** Load `tests/expected.yml`, run fixtures, and report pass/fail.

**Files:**
- Create: `detectsmith/test_runner.py`
- Create: `tests/unit/test_test_runner.py`

**Requirements:**

- JSONL fixture loading.
- `should_match: true/false` support.
- Clear failure details.
- Unsupported detection semantics fail clearly.

**Verification:**

```bash
python -m pytest tests/unit/test_test_runner.py -q
```

Expected: pass.

### Task 3.3: Add `detectsmith test` CLI

**Objective:** Expose regression testing through CLI.

**Files:**
- Modify: `detectsmith/cli.py`
- Create: `tests/unit/test_cli_test.py`

**Requirements:**

- Command: `detectsmith test tests/expected.yml`
- Support `--format text|json` and `--output reports/test_results.json` for future TUI/automation use.
- Exit non-zero if any detection regression fails.

**Verification:**

```bash
python -m pytest tests/unit/test_cli_test.py -q
detectsmith test tests/expected.yml
```

Expected: command returns non-zero if any detection regression fails.

---

## Phase 4: ATT&CK coverage

### Task 4.1: Extract ATT&CK tags

**Objective:** Parse tactic and technique tags from rule metadata.

**Files:**
- Create: `detectsmith/coverage.py`
- Create: `tests/unit/test_coverage.py`

**Requirements:**

- Extract `attack.execution` style tactic tags.
- Extract `attack.t1059` and `attack.t1059.001` technique tags.
- Identify rules missing ATT&CK tags.

**Verification:**

```bash
python -m pytest tests/unit/test_coverage.py -q
```

Expected: pass.

### Task 4.2: Add coverage report outputs

**Objective:** Generate JSON and Markdown coverage reports.

**Files:**
- Modify: `detectsmith/coverage.py`
- Create: `tests/unit/test_coverage_reports.py`

**Outputs:**

- `reports/attack_coverage.json`
- `reports/attack_coverage.md`

**Verification:**

```bash
python -m pytest tests/unit/test_coverage_reports.py -q
```

Expected: pass.

### Task 4.3: Add `detectsmith coverage` CLI

**Objective:** Expose coverage reporting through CLI.

**Files:**
- Modify: `detectsmith/cli.py`
- Create: `tests/unit/test_cli_coverage.py`

**Requirements:**

- Command: `detectsmith coverage rules/`
- Support `--format text|json` and `--output reports/attack_coverage.json` for future TUI/automation use.
- Continue generating `reports/attack_coverage.md` for human-readable docs.

**Verification:**

```bash
python -m pytest tests/unit/test_cli_coverage.py -q
detectsmith coverage rules/
```

Expected: reports generated.

---

## Phase 5: Documentation generator

### Task 5.1: Generate rule Markdown pages

**Objective:** Create one Markdown page per parsed rule.

**Files:**
- Create: `detectsmith/docs.py`
- Create: `tests/unit/test_docs_generator.py`

**Page includes:**

- Title.
- Description.
- Status and level.
- Logsource.
- ATT&CK tags.
- False positives.
- References.
- Source path.

**Verification:**

```bash
python -m pytest tests/unit/test_docs_generator.py -q
```

Expected: pass.

### Task 5.2: Generate docs index

**Objective:** Create `site/index.md` linking all rule pages and coverage report.

**Files:**
- Modify: `detectsmith/docs.py`
- Create: `tests/unit/test_docs_index.py`

**Verification:**

```bash
python -m pytest tests/unit/test_docs_index.py -q
```

Expected: pass.

### Task 5.3: Add `detectsmith docs` CLI

**Objective:** Expose docs generation through CLI.

**Files:**
- Modify: `detectsmith/cli.py`
- Create: `tests/unit/test_cli_docs.py`

**Requirements:**

- Command: `detectsmith docs rules/ --out site/`
- Support `--format text|json` and `--output reports/docs.json` for future TUI/automation use.
- Include generated page paths in the JSON report.

**Verification:**

```bash
python -m pytest tests/unit/test_cli_docs.py -q
detectsmith docs rules/ --out site/
```

Expected: docs generated.

---

## Phase 6: Example content

### Task 6.1: Add starter rule corpus

**Objective:** Add the v0.1 sample rules listed in `docs/SCOPE.md`.

**Files:**
- Create: `rules/windows/*.yml`
- Create: `rules/linux/*.yml`
- Create: `rules/cloud/aws/*.yml`
- Create: `rules/m365/*.yml`

**Requirements:**

Each rule includes required metadata, realistic false positives, ATT&CK tags, and conservative wording.

**Verification:**

```bash
detectsmith lint rules/
```

Expected: no `error` findings. Warnings are acceptable only if intentional and documented.

### Task 6.2: Add fixture logs and expected cases

**Objective:** Add positive and negative JSONL fixtures for example rules.

**Files:**
- Create: `tests/fixtures/**/*.jsonl`
- Create: `tests/expected.yml`

**Verification:**

```bash
detectsmith test tests/expected.yml
```

Expected: all cases pass.

---

## Phase 7: CI and final polish

### Task 7.1: Add GitHub Actions workflow

**Objective:** Run tests and Detectsmith commands on push/PR.

**Files:**
- Create: `.github/workflows/detection-ci.yml`

**Workflow commands:**

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
detectsmith lint rules/ --format json --output reports/lint.json
detectsmith test tests/expected.yml --format json --output reports/test_results.json
detectsmith coverage rules/ --format json --output reports/attack_coverage.json
detectsmith docs rules/ --out site/ --format json --output reports/docs.json
```

**Verification:**

Run commands locally before relying on GitHub Actions.

### Task 7.2: Update README with demo output

**Objective:** Make the repo portfolio-ready.

**Files:**
- Modify: `README.md`

**Include:**

- What this demonstrates.
- Quick start.
- Example CLI outputs.
- Methodology.
- Limitations.
- Safe-use note.

**Verification:**

README should be understandable to a recruiter, SOC manager, or detection engineer without reading the whole codebase.

### Task 7.3: Final integration review

**Objective:** Verify the complete project matches scope.

**Checks:**

```bash
python -m pytest -q
detectsmith lint rules/ --format json --output reports/lint.json
detectsmith test tests/expected.yml --format json --output reports/test_results.json
detectsmith coverage rules/ --format json --output reports/attack_coverage.json
detectsmith docs rules/ --out site/ --format json --output reports/docs.json
```

Also review:

- No v0.1 non-goals accidentally implemented.
- Docs match actual behavior.
- Example rules avoid overclaiming.
- All generated artifacts are either committed intentionally or ignored intentionally.

---

## Orchestration method

Use subagent-driven development for implementation:

1. Fresh implementer subagent per task.
2. Spec compliance review after each task.
3. Code quality review after spec passes.
4. Continue only when both reviews pass.
5. Keep this plan updated if scope changes.

For tasks touching the same files, run sequentially, not in parallel.

## Context budget policy

If the session gets long, stop after completing the current task and summarize:

- Completed tasks.
- Current failing tests, if any.
- Files changed.
- Next task from this plan.

The next session must resume by reading `AGENTS.md` and this plan.
