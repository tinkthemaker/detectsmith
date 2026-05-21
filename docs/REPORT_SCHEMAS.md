# Detectsmith Report Schemas and CLI Contracts

## Purpose

This document defines the machine-readable contracts that the future Charm TUI and GitHub Actions workflows can rely on.

These schemas should be treated as stable once v0.2 begins. During v0.1 they may evolve, but changes must update this document in the same commit.

## Output format convention

Every core command should eventually support:

```bash
--format text|json
--output PATH
```

Recommended commands:

```bash
detectsmith lint rules/ --format json --output reports/lint.json
detectsmith test tests/expected.yml --format json --output reports/test_results.json
detectsmith coverage rules/ --format json --output reports/attack_coverage.json
detectsmith docs rules/ --out site/ --format json --output reports/docs.json
```

Human-readable terminal output remains the default. JSON output exists for automation, CI, and the future TUI.

## Exit code contract

```text
0 success
1 valid command completed with findings or failed detection tests
2 usage/configuration error
3 parse/load error
4 unsupported rule semantics
5 unexpected internal error
```

Examples:

- `detectsmith lint` returns `1` when rules parse but contain `error` findings.
- `detectsmith test` returns `1` when one or more expected cases fail.
- `detectsmith test` returns `4` when a rule uses unsupported matcher semantics.
- Any command returns `2` for missing required arguments or invalid paths.
- Any command returns `3` when YAML/JSONL files cannot be parsed.

## Common report envelope

All JSON reports should use this top-level envelope:

```json
{
  "schema_version": "0.1",
  "command": "lint",
  "generated_at": "2026-05-21T12:34:56Z",
  "project_root": "E:/AI backups/detectsmith",
  "status": "success",
  "summary": {},
  "data": {},
  "errors": []
}
```

Fields:

- `schema_version`: report schema version, not app version.
- `command`: one of `lint`, `test`, `coverage`, `docs`.
- `generated_at`: ISO-8601 UTC timestamp.
- `project_root`: absolute or normalized project root path.
- `status`: `success`, `completed_with_findings`, `failed`, or `error`.
- `summary`: small object for dashboard cards.
- `data`: command-specific payload.
- `errors`: command-level errors not tied to one rule/test.

## `reports/lint.json`

Example shape:

```json
{
  "schema_version": "0.1",
  "command": "lint",
  "generated_at": "2026-05-21T12:34:56Z",
  "project_root": "E:/AI backups/detectsmith",
  "status": "completed_with_findings",
  "summary": {
    "rules_total": 12,
    "rules_valid": 12,
    "findings_error": 0,
    "findings_warn": 4,
    "findings_info": 7,
    "average_score": 86.5
  },
  "data": {
    "rules": [
      {
        "path": "rules/windows/proc_creation_powershell_encoded_command.yml",
        "id": "00000000-0000-0000-0000-000000000001",
        "title": "PowerShell Encoded Command",
        "status": "test",
        "level": "medium",
        "score": 88,
        "derived_maturity": "test",
        "findings": [
          {
            "severity": "warn",
            "check_id": "missing_modified_date",
            "message": "Stable or test rules should include a modified date after edits.",
            "recommendation": "Add modified: YYYY/MM/DD when changing an existing rule."
          }
        ]
      }
    ]
  },
  "errors": []
}
```

## `reports/test_results.json`

Example shape:

```json
{
  "schema_version": "0.1",
  "command": "test",
  "generated_at": "2026-05-21T12:34:56Z",
  "project_root": "E:/AI backups/detectsmith",
  "status": "success",
  "summary": {
    "tests_total": 24,
    "tests_passed": 24,
    "tests_failed": 0,
    "rules_tested": 12
  },
  "data": {
    "tests": [
      {
        "name": "powershell_encoded_positive",
        "rule": "rules/windows/proc_creation_powershell_encoded_command.yml",
        "fixture": "tests/fixtures/windows/powershell_encoded_positive.jsonl",
        "should_match": true,
        "matched": true,
        "matched_events": 1,
        "status": "passed",
        "failure_reason": null
      }
    ]
  },
  "errors": []
}
```

## `reports/attack_coverage.json`

Example shape:

```json
{
  "schema_version": "0.1",
  "command": "coverage",
  "generated_at": "2026-05-21T12:34:56Z",
  "project_root": "E:/AI backups/detectsmith",
  "status": "success",
  "summary": {
    "rules_total": 12,
    "tactics_covered": 5,
    "techniques_covered": 10,
    "rules_missing_attack_tags": 0
  },
  "data": {
    "tactics": [
      {
        "tag": "attack.execution",
        "rules": 4
      }
    ],
    "techniques": [
      {
        "tag": "attack.t1059.001",
        "rules": 1,
        "rule_paths": [
          "rules/windows/proc_creation_powershell_encoded_command.yml"
        ]
      }
    ],
    "rules_missing_attack_tags": []
  },
  "errors": []
}
```

## `reports/docs.json`

Example shape:

```json
{
  "schema_version": "0.1",
  "command": "docs",
  "generated_at": "2026-05-21T12:34:56Z",
  "project_root": "E:/AI backups/detectsmith",
  "status": "success",
  "summary": {
    "rules_total": 12,
    "rule_pages_written": 12,
    "index_written": true,
    "output_dir": "site"
  },
  "data": {
    "pages": [
      {
        "rule": "rules/windows/proc_creation_powershell_encoded_command.yml",
        "page": "site/rules/proc_creation_powershell_encoded_command.md"
      }
    ],
    "index": "site/index.md"
  },
  "errors": []
}
```

## Path conventions

Reports should use project-relative paths where possible. The common envelope may include an absolute `project_root` so the TUI can resolve paths.

Use forward slashes in JSON paths, even on Windows:

```json
"rules/windows/example.yml"
```

This keeps reports easier to read and avoids escaping backslashes.

## Backward compatibility policy

Before v0.2, schemas may change freely if docs are updated.

After v0.2:

- Additive fields are allowed.
- Removing fields requires a schema version bump.
- Renaming fields requires a schema version bump.
- Changing exit code meanings requires updating this doc and the TUI roadmap.

## TUI dependency

The future Charm TUI must treat these JSON reports and exit codes as its integration boundary. It should not parse human-readable terminal output except as a last-resort error display.
