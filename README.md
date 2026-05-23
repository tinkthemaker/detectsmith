# Detectsmith

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-62%20passing-brightgreen)](https://github.com/tinkthemaker/detectsmith)
[![Go](https://img.shields.io/badge/Go%20TUI-1.24+-00ADD8?logo=go)](https://go.dev)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Detection-as-code workbench for writing, testing, scoring, and documenting Sigma-style detections.

## Project status

This repository is intentionally scope-locked by documentation first. Before adding code, read:

1. [`docs/SCOPE.md`](docs/SCOPE.md) — what v0.1 is and is not.
2. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — modules, commands, data flow, file layout.
3. [`docs/QUALITY_MODEL.md`](docs/QUALITY_MODEL.md) — rule scoring and linter philosophy.
4. [`docs/TESTING_STRATEGY.md`](docs/TESTING_STRATEGY.md) — regression test approach and supported Sigma subset.
5. [`docs/REPORT_SCHEMAS.md`](docs/REPORT_SCHEMAS.md) — JSON report and exit-code contracts for automation and future UI work.
6. [`docs/TUI_ROADMAP.md`](docs/TUI_ROADMAP.md) — future Charm TUI direction, explicitly deferred until the CLI is stable.
7. [`docs/plans/0001-detectsmith-v0.1.md`](docs/plans/0001-detectsmith-v0.1.md) — implementation plan.
8. [`AGENTS.md`](AGENTS.md) — instructions for AI agents and future context resets.

## Goal

Build a focused, portfolio-quality detection engineering project that demonstrates:

- Detection-as-code discipline.
- Sigma-style rule authoring.
- Rule metadata quality checks.
- Fixture-based detection regression testing.
- MITRE ATT&CK coverage reporting.
- Analyst-facing documentation generation.
- GitHub Actions CI for detection content.

## v0.1 commands

The first implementation target is a Python CLI with four commands:

```bash
detectsmith lint rules/
detectsmith test tests/expected.yml
detectsmith coverage rules/
detectsmith docs rules/ --out site/
```

## Non-goals for v0.1

Detectsmith v0.1 is not a SIEM, EDR, scanner, offensive tool, live log collector, or full Sigma engine. It deliberately supports a small, documented subset of Sigma-like matching so the first version remains buildable and trustworthy.

## Future TUI

Detectsmith should eventually have a Charm ecosystem TUI for interactive review and demos. That TUI is intentionally **not** part of v0.1. The planned architecture is:

```text
Python CLI/core first → stable JSON reports → Go Charm TUI frontend
```

The TUI should invoke the CLI and read JSON reports rather than reimplementing detection logic. See [`docs/TUI_ROADMAP.md`](docs/TUI_ROADMAP.md).

## Portfolio positioning

The project should tell this story:

> Threat behavior → detection rule → metadata quality → sample telemetry → regression test → ATT&CK coverage → analyst-facing docs → CI validation → eventual interactive TUI review.

That story is more important than broad platform support.
