# Detectsmith Charm TUI Roadmap

## Decision

Detectsmith should eventually include a Charm ecosystem terminal UI, but not as part of the v0.1 MVP.

The v0.1 priority remains a stable, scriptable Python CLI with documented JSON outputs. The future Go TUI should be a thin frontend over those CLI/report contracts.

## Why defer the TUI

A TUI will be valuable for demos and daily use, but building it before the CLI is stable risks duplicating logic, changing scope, and turning Detectsmith into a UI project instead of a detection engineering workbench.

The correct sequence is:

```text
v0.1  Python CLI/core works and is tested
v0.2  JSON report schemas and exit codes are stable
v0.3  Charm TUI frontend over the CLI/report contracts
```

A minimal read-only TUI may be considered in `v0.1.5` only if the CLI commands and JSON reports are already stable.

## Architecture rule

The TUI must not reimplement detection logic.

Preferred architecture:

```text
Go Charm TUI
  -> executes detectsmith CLI commands
  -> reads JSON reports from reports/*.json
  -> renders summaries, lists, details, and Markdown

Python Detectsmith CLI/core
  -> owns rule parsing
  -> owns linting/scoring
  -> owns matcher semantics
  -> owns regression testing
  -> owns ATT&CK coverage generation
  -> owns docs generation
```

Avoid Python embedding, RPC services, databases, and duplicated Go detection engines unless a future approved plan explicitly changes this.

## Planned TUI binary

Proposed binary name:

```bash
detectsmith-tui
```

It may live in one of these layouts, to be decided later:

```text
cmd/detectsmith-tui/          # Go module inside same repo
```

or:

```text
tui/                          # Go module subdirectory
  cmd/detectsmith-tui/
```

The final layout should be chosen when TUI implementation begins.

## Charm stack

Use Charm v2 libraries:

```go
charm.land/bubbletea/v2
charm.land/bubbles/v2
charm.land/lipgloss/v2
github.com/charmbracelet/glamour
```

Likely Bubbles components:

- `list` for rules, findings, and tests.
- `table` for summaries.
- `viewport` for rule details and Markdown output.
- `spinner` while CLI commands run.
- `help` for keybindings.

Avoid `huh` initially unless the TUI needs forms. The first TUI should favor navigation, execution, and review over complex input workflows.

## Initial TUI screens

### Dashboard

Shows:

- Total rule count.
- Lint errors/warnings.
- Passing/failing regression tests.
- ATT&CK techniques covered.
- Generated docs status.
- Last command run and timestamp.

Actions:

- Run lint.
- Run tests.
- Run coverage.
- Generate docs.
- Run all checks.

### Rules screen

Shows:

- Rule list.
- Platform/category/status/level.
- Lint score.
- ATT&CK tags.
- Test coverage indicator.

Details pane:

- Description.
- Logsource.
- False positives.
- References.
- Findings.
- Source path.

### Test results screen

Shows:

- Test case list.
- Pass/fail status.
- Rule path.
- Fixture path.
- Expected vs actual match.
- Failure reason.

### Coverage screen

Shows:

- Tactics covered.
- Techniques covered.
- Rules per technique.
- Rules missing ATT&CK tags.
- Optional configured gap list.

### Docs screen

Shows:

- Generated site path.
- Rule docs generated.
- Coverage report path.
- Markdown preview using Glamour where useful.

## Required CLI/report contracts before TUI work

Before the TUI is implemented, the Python CLI should support stable JSON output for each command:

```bash
detectsmith lint rules/ --format json --output reports/lint.json
detectsmith test tests/expected.yml --format json --output reports/test_results.json
detectsmith coverage rules/ --format json --output reports/attack_coverage.json
detectsmith docs rules/ --out site/ --format json --output reports/docs.json
```

The schemas are documented in `docs/REPORT_SCHEMAS.md`.

## Exit code contract

The TUI should rely on stable CLI exit codes:

```text
0 success
1 valid command completed with findings or failed detection tests
2 usage/configuration error
3 parse/load error
4 unsupported rule semantics
5 unexpected internal error
```

Exit code details are also documented in `docs/REPORT_SCHEMAS.md`.

## Windows considerations

The TUI should run on Windows because the project owner works on Windows. Use normal Go subprocess execution rather than shell-specific scripts when possible.

When the TUI invokes the CLI:

- Prefer `exec.CommandContext` with explicit args.
- Do not rely on PowerShell or cmd builtins.
- Surface missing `detectsmith` binary errors clearly.
- Show command, working directory, exit code, and report path in failure views.

## Non-goals for the first TUI

Do not implement these in the first TUI:

- Editing rules in-place.
- Full rule authoring wizard.
- Live file watchers.
- Background daemon.
- Database persistence.
- SIEM deployment.
- Remote execution.
- AI detection authoring.
- Full ATT&CK matrix visualization if a simple coverage table is enough.

## TUI definition of done

The first TUI is complete when it can:

- Locate or accept a Detectsmith project root.
- Run the four core CLI commands.
- Show spinner/progress while commands run.
- Read JSON reports.
- Display dashboard summaries.
- Browse lint findings by rule.
- Browse regression test results.
- Browse ATT&CK coverage summaries.
- Show clear errors for missing CLI, invalid project root, failed command, or malformed report JSON.

## Portfolio value

The TUI should improve demo quality without changing the core project story:

> Threat behavior → detection rule → metadata quality → sample telemetry → regression test → ATT&CK coverage → analyst-facing docs → CI validation → interactive TUI review.
