# Detectsmith Testing Strategy

## Purpose

Detectsmith tests two things:

1. The Detectsmith Python code behaves correctly.
2. Example detection rules match known-positive fixtures and avoid known-negative fixtures.

Both matter. Code tests prove the tool works. Detection regression tests prove the rule corpus is not changing accidentally.

## Test types

### Unit tests

Located under:

```text
tests/unit/
```

Unit tests cover:

- YAML parsing.
- Required field validation.
- Rule quality scoring.
- ATT&CK tag extraction.
- Matcher behavior.
- Expected-test file parsing.
- Markdown/JSON report generation.

### Detection regression fixtures

Located under:

```text
tests/fixtures/
tests/expected.yml
```

Fixtures are local JSONL files. Each line is one event object.

Example:

```json
{"Image":"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe","CommandLine":"powershell.exe -enc SQBFAFgA","ParentImage":"C:\\Windows\\explorer.exe"}
```

Expected cases map fixtures to rules:

```yaml
tests:
  - name: powershell_encoded_positive
    rule: rules/windows/proc_creation_powershell_encoded_command.yml
    fixture: tests/fixtures/windows/powershell_encoded_positive.jsonl
    should_match: true

  - name: powershell_encoded_negative_admin_script
    rule: rules/windows/proc_creation_powershell_encoded_command.yml
    fixture: tests/fixtures/windows/powershell_encoded_negative_admin_script.jsonl
    should_match: false
```

## Supported matching subset for v0.1

The matcher intentionally supports a constrained Sigma-style subset.

### Exact match

```yaml
detection:
  selection:
    Image: C:\Windows\System32\cmd.exe
  condition: selection
```

Passes when event field `Image` equals the value.

### Contains

```yaml
detection:
  selection:
    CommandLine|contains: " -enc "
  condition: selection
```

Passes when the event field contains the string.

### Startswith

```yaml
detection:
  selection:
    Image|startswith: C:\Windows\
  condition: selection
```

### Endswith

```yaml
detection:
  selection:
    Image|endswith: \powershell.exe
  condition: selection
```

### List values

```yaml
detection:
  selection:
    Image|endswith:
      - \powershell.exe
      - \pwsh.exe
  condition: selection
```

List values mean any value may match.

### Multiple fields in one selection

```yaml
detection:
  selection:
    Image|endswith: \powershell.exe
    CommandLine|contains: " -enc "
  condition: selection
```

Multiple fields in one selection mean all fields must match.

## Unsupported in initial v0.1 unless explicitly added

- Full Sigma condition grammar.
- Near/temporal matching.
- Aggregations.
- Regular expressions.
- Field aliases and backend pipelines.
- Full pySigma conversion semantics.
- Multiple log events forming one detection.
- Nested field normalization beyond simple key lookup.

Unsupported constructs should fail clearly, not silently pass or ignore logic.

## Exit behavior

`detectsmith test tests/expected.yml` should:

- Exit `0` when all expected cases pass.
- Exit non-zero when any case fails or a rule cannot be processed.
- Print a summary table.
- Include enough detail to identify the failing rule and fixture.
- Produce JSON output compatible with `docs/REPORT_SCHEMAS.md` when called with `--format json --output reports/test_results.json`.

## Test quality bar for example rules

Each example rule should have:

- At least one positive fixture.
- At least one negative fixture where practical.
- Fixture events that are small but realistic.
- Test names that explain behavior.

## CI verification

GitHub Actions should run:

```bash
python -m pytest -q
detectsmith lint rules/ --format json --output reports/lint.json
detectsmith test tests/expected.yml --format json --output reports/test_results.json
detectsmith coverage rules/ --format json --output reports/attack_coverage.json
detectsmith docs rules/ --out site/ --format json --output reports/docs.json
```

## Safety

Fixtures must be inert data. Do not include working malware, exploit code, real credentials, private logs, or sensitive customer data.
