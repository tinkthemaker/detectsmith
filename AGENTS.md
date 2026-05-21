# Instructions for AI Agents Working on Detectsmith

This file exists to preserve project scope across Hermes context resets and future agent sessions.

## Prime directive

Build the boring, disciplined MVP first. Do not turn Detectsmith into a SIEM, EDR, threat-intel platform, live scanner, log collector, or generic AI cybersecurity product.

## Required reading before edits

Before modifying code or docs, read these files in order:

1. `README.md`
2. `docs/SCOPE.md`
3. `docs/ARCHITECTURE.md`
4. `docs/QUALITY_MODEL.md`
5. `docs/TESTING_STRATEGY.md`
6. `docs/REPORT_SCHEMAS.md`
7. `docs/TUI_ROADMAP.md`
8. `docs/plans/0001-detectsmith-v0.1.md`

If a requested change conflicts with these docs, stop and ask for scope approval before editing.

## User preference

The project owner prefers analysis first and check-in before implementation. For non-trivial changes, present the analysis and plan before modifying files. Small documentation updates that preserve scope are acceptable when explicitly requested.

## v0.1 scope lock

v0.1 builds a Python CLI with exactly these primary commands:

```bash
detectsmith lint rules/
detectsmith test tests/expected.yml
detectsmith coverage rules/
detectsmith docs rules/ --out site/
```

Supported rule format:

- Sigma-style YAML files.
- Required metadata fields documented in `docs/SCOPE.md`.
- A constrained matching subset documented in `docs/TESTING_STRATEGY.md`.

Outputs:

- Human-readable CLI output.
- Stable JSON reports for automation and the future Charm TUI.
- Markdown reports/docs.

## Future TUI scope

Detectsmith should eventually include a Go Charm TUI, but not in v0.1. Treat `docs/TUI_ROADMAP.md` as the source of truth.

The TUI must be a frontend over the Python CLI/report contracts:

```text
Go Charm TUI -> detectsmith CLI -> reports/*.json
```

Do not duplicate rule parsing, linting, matching, regression testing, or coverage logic in Go without a new approved plan.

## Explicit non-goals

Do not add these without a new approved plan:

- Live SIEM integrations.
- Splunk/Elastic/Sentinel deployment.
- Full Sigma semantics.
- AI-generated detections as a primary feature.
- Network scanning or public-target testing.
- Malware execution, exploit tooling, or adversary automation.
- Web app/dashboard before the CLI works.
- Charm TUI before the CLI/report schemas are stable.
- Database persistence.
- Authentication/user accounts.
- Background services.

## Engineering discipline

Use TDD for code tasks:

1. Write failing tests.
2. Run tests and verify failure.
3. Implement minimal code.
4. Run tests and verify pass.
5. Update docs if behavior changes.

Prefer small modules, small commits, and simple data structures.

## Documentation policy

Every durable decision must be captured in docs, not only chat. If you change scope, commands, data formats, scoring rules, or supported matching semantics, update the corresponding document in the same change.

## Security posture

Detectsmith is a defensive portfolio project. Keep examples safe, local, and fixture-based. Avoid public-target scanning, credential handling, or instructions that enable misuse.

## Verification commands

Once implementation exists, the expected verification set is:

```bash
python -m pytest -q
detectsmith lint rules/
detectsmith test tests/expected.yml
detectsmith coverage rules/
detectsmith docs rules/ --out site/
```

Until code exists, verify documentation changes by reading the docs and checking path consistency.
