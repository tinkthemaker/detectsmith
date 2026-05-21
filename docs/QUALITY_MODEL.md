# Detectsmith Rule Quality Model

## Purpose

The linter should teach what good detection content looks like. It should not only reject malformed YAML; it should explain how to make rules more useful, testable, and maintainable.

## Scoring philosophy

Scores are guidance, not truth. A low score means the rule needs review. A high score means the rule meets metadata and maintainability standards, not that it is guaranteed to catch threats in production.

## Severity levels

Lint findings use these severities:

- `error` — rule is invalid or cannot be safely processed.
- `warn` — rule is usable but weak, incomplete, or risky.
- `info` — improvement suggestion.
- `pass` — optional internal result for reporting successful checks.

## Suggested score bands

```text
90-100  Excellent: portfolio-quality rule with strong metadata and tests.
75-89   Good: usable rule with minor documentation or quality gaps.
60-74   Needs work: meaningful but incomplete or noisy.
1-59    Poor: likely too broad, underdocumented, or hard to maintain.
0       Invalid: cannot parse or missing critical structure.
```

## Required checks

These should produce `error` findings when missing or invalid:

- Valid YAML.
- Top-level mapping/object.
- `title` exists and is non-empty.
- `id` exists and is unique across the corpus.
- `description` exists.
- `logsource` exists.
- `detection` exists.
- `detection.condition` exists.
- `level` exists and is one of the allowed values.
- `status` exists and is one of the allowed values.

## Strongly recommended checks

These should produce `warn` findings:

- Missing `references`.
- Missing `falsepositives`.
- Missing `tags`.
- Missing ATT&CK technique tag like `attack.t1059.001`.
- Description too short to explain behavior.
- Title too generic, such as:
  - `Suspicious Activity`
  - `Malware Detection`
  - `Bad Process`
- False positive entry too generic, such as:
  - `Unknown`
  - `None`
  - `Legitimate activity`
- Rule uses only a single process name with no command-line, parent, path, or behavior context.
- Rule has no test fixture listed in `tests/expected.yml`.

## Informational checks

These should produce `info` findings:

- No `author` field.
- No `date` field.
- No `modified` field for stable rules.
- No tactic-level tag like `attack.execution`.
- Rule level may not match suspiciousness of behavior.
- Rule could benefit from data source notes.

## Score weights for v0.1

Start with 100 points and subtract:

```text
Critical parse/structure errors: score = 0
Missing required metadata: -15 each
Duplicate ID: score = 0 for affected rules
Missing references: -5
Missing false positives: -10
Generic false positives: -5
Missing ATT&CK tags: -10
Missing specific ATT&CK technique tag: -8
Weak/generic title: -5
Short description: -5
No associated test case: -10
Unsupported detection semantics: -15
Overly broad single-field detection: -10
```

Scores must be clamped between 0 and 100.

## Rule maturity labels

The linter may assign a derived maturity label:

```text
invalid       score = 0 or parse failure
experimental score < 75
test          score 75-89
stable        score >= 90 and has passing positive test
```

Do not automatically rewrite the rule's declared `status`. Report the derived maturity separately.

## Finding format

Each finding should include:

```json
{
  "rule_path": "rules/windows/example.yml",
  "severity": "warn",
  "check_id": "missing_falsepositives",
  "message": "Rule is missing falsepositives.",
  "recommendation": "Add realistic benign causes, such as admin scripts, software deployment tools, or known management platforms where applicable."
}
```

## Output requirements

`detectsmith lint rules/` should produce:

- Terminal summary table.
- Non-zero exit for `error` findings.
- Optional or default JSON report at `reports/lint.json`.

## What the linter must not claim

Do not claim:

- A high score means the rule is production-ready everywhere.
- A rule has low false positives without environment-specific validation.
- A rule detects a threat actor unless the logic is actor-specific and referenced.

Use conservative language:

- “This rule has strong metadata.”
- “This rule has fixture coverage.”
- “This rule may require environment-specific tuning.”
