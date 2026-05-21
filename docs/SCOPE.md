# Detectsmith Scope

## One-sentence goal

Detectsmith is a local Python CLI for linting Sigma-style detection rules, regression-testing them against sample logs, measuring ATT&CK coverage, and generating documentation.

## Why this project exists

The portfolio signal is not “I wrote some rules.” The signal is:

- I understand detection content as code.
- I can define rule quality standards.
- I can test detections against known-good and known-bad telemetry.
- I can measure ATT&CK coverage and gaps.
- I can generate analyst-friendly documentation.
- I can automate the lifecycle in CI.
- I can later wrap the workflow in a focused Charm TUI without changing the detection engine.

## v0.1 deliverables

### CLI commands

v0.1 includes these commands:

```bash
detectsmith lint rules/
detectsmith test tests/expected.yml
detectsmith coverage rules/
detectsmith docs rules/ --out site/
```

### Rule corpus

Include a small, high-quality starter pack:

```text
rules/windows/
  proc_creation_powershell_encoded_command.yml
  proc_creation_regsvr32_scriptlet.yml
  proc_creation_rundll32_javascript.yml
  proc_creation_schtasks_persistence.yml
  registry_run_key_persistence.yml

rules/linux/
  proc_creation_curl_pipe_shell.yml
  proc_creation_reverse_shell.yml

rules/cloud/aws/
  cloudtrail_disable_logging.yml
  iam_access_key_created_for_privileged_user.yml
  security_group_open_to_world.yml

rules/m365/
  inbox_rule_external_forwarding.yml
  oauth_app_consent_grant.yml
```

These are examples, not a claim of production coverage.

### Rule metadata required for v0.1

Each rule should include:

```yaml
title: Human-readable title
id: UUID or stable unique ID
status: experimental | test | stable
description: Clear explanation of behavior detected
references:
  - https://example.com/reference
author: Name or handle
date: YYYY/MM/DD
logsource:
  product: windows | linux | aws | m365
  category: process_creation | registry_set | cloudtrail | audit
  service: optional service name
detection:
  selection:
    Field|modifier: value
  condition: selection
falsepositives:
  - Realistic benign explanation
level: informational | low | medium | high | critical
tags:
  - attack.execution
  - attack.t1059.001
```

### Test data

Use local fixture data only:

```text
tests/fixtures/**/*.jsonl
tests/expected.yml
```

Each test case maps one rule to one fixture and says whether a match is expected.

### Reports

v0.1 should generate:

```text
reports/lint.json
reports/test_results.json
reports/attack_coverage.json
reports/attack_coverage.md
reports/docs.json
site/index.md
site/rules/*.md
```

Exact output paths may be configurable later, but keep defaults simple. JSON report schemas and exit codes are documented in `docs/REPORT_SCHEMAS.md` because automation and the future Charm TUI will depend on them.

## v0.1 non-goals

Do not implement these in v0.1:

- Full Sigma specification support.
- SIEM deployment.
- Live log ingestion.
- Web dashboard.
- Charm TUI before the CLI/report contracts are stable.
- Database storage.
- User accounts.
- Cloud API access.
- Network scanning.
- Public target testing.
- Offensive execution or Atomic Red Team runner.
- AI rule authoring.

## Supported Sigma subset for testing

v0.1 only needs enough matching logic for local regression tests:

- Exact field equals value.
- List values mean any match.
- String modifiers:
  - `contains`
  - `startswith`
  - `endswith`
- Basic case-insensitive string comparison.
- `condition: selection`.
- Optional v0.1.1 support:
  - `selection and not filter`
  - `selection1 or selection2`

Unsupported semantics must fail clearly with an “unsupported condition/modifier” message.

## Quality bar

The project should prefer ten well-documented, tested rules over one hundred shallow rules.

A rule is considered portfolio-quality when it has:

- Clear behavior-focused title.
- Explanation of attacker behavior.
- Data source requirements.
- ATT&CK tags.
- Realistic false positives.
- At least one positive fixture.
- At least one negative fixture where practical.
- Generated documentation.

## Definition of done for v0.1

v0.1 is complete when:

- CLI package installs locally.
- All four commands work.
- Unit tests pass.
- Example rules lint successfully or produce intentional warnings.
- Regression tests run against sample JSONL fixtures.
- ATT&CK coverage report is generated.
- Rule documentation is generated.
- GitHub Actions runs tests and CLI checks.
- README explains portfolio value and limitations.

## Future TUI scope

Detectsmith should eventually include a Go Charm TUI for interactive demos and review, but this is not part of v0.1.

The future TUI must be a thin frontend over the CLI and JSON reports:

```text
detectsmith-tui -> detectsmith CLI -> reports/*.json
```

The TUI must not reimplement detection parsing, linting, matching, test-running, or coverage logic. See `docs/TUI_ROADMAP.md`.
