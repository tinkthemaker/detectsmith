from __future__ import annotations

from collections import Counter
from typing import Any

from detectsmith.models import LintFinding, LintReport, LintSummary, Rule, RuleLintResult

ALLOWED_LEVELS = {"informational", "low", "medium", "high", "critical"}
ALLOWED_STATUSES = {"experimental", "test", "stable"}

REQUIRED_FIELDS = (
    "title",
    "id",
    "description",
    "logsource",
    "detection",
    "level",
    "status",
)


def lint_rules(rules: list[Rule]) -> LintReport:
    id_counts = Counter(str(rule.raw.get("id")) for rule in rules if rule.raw.get("id"))
    results = [_lint_rule(rule, id_counts) for rule in rules]
    errors = sum(1 for result in results for finding in result.findings if finding.severity == "error")
    warns = sum(1 for result in results for finding in result.findings if finding.severity == "warn")
    infos = sum(1 for result in results for finding in result.findings if finding.severity == "info")
    valid = sum(1 for result in results if not any(f.severity == "error" for f in result.findings))
    average = round(sum(result.score for result in results) / len(results), 2) if results else 0.0
    return LintReport(
        rules=results,
        summary=LintSummary(
            rules_total=len(results),
            rules_valid=valid,
            findings_error=errors,
            findings_warn=warns,
            findings_info=infos,
            average_score=average,
        ),
    )


def _lint_rule(rule: Rule, id_counts: Counter[str]) -> RuleLintResult:
    findings: list[LintFinding] = []
    raw = rule.raw
    rule_path = _path(rule)

    for field in REQUIRED_FIELDS:
        if not _has_value(raw.get(field)):
            findings.append(
                _finding(
                    rule_path,
                    "error",
                    f"missing_{field}",
                    f"Rule is missing required field '{field}'.",
                    f"Add a meaningful '{field}' field to the rule.",
                )
            )

    detection = raw.get("detection")
    if not isinstance(detection, dict) or not _has_value(detection.get("condition")):
        findings.append(
            _finding(
                rule_path,
                "error",
                "missing_detection_condition",
                "Rule is missing required field 'detection.condition'.",
                "Add detection.condition, usually 'selection' for v0.1 rules.",
            )
        )

    level = raw.get("level")
    if _has_value(level) and str(level) not in ALLOWED_LEVELS:
        findings.append(
            _finding(rule_path, "error", "invalid_level", f"Invalid level '{level}'.", "Use informational, low, medium, high, or critical.")
        )

    status = raw.get("status")
    if _has_value(status) and str(status) not in ALLOWED_STATUSES:
        findings.append(
            _finding(rule_path, "error", "invalid_status", f"Invalid status '{status}'.", "Use experimental, test, or stable.")
        )

    rule_id = raw.get("id")
    if _has_value(rule_id) and id_counts[str(rule_id)] > 1:
        findings.append(
            _finding(rule_path, "error", "duplicate_id", f"Duplicate rule id '{rule_id}'.", "Give each rule a stable unique id.")
        )

    if not _has_value(raw.get("references")):
        findings.append(
            _finding(rule_path, "warn", "missing_references", "Rule is missing references.", "Add links to ATT&CK, vendor docs, research, or relevant detection guidance.")
        )

    falsepositives = raw.get("falsepositives")
    if not _has_value(falsepositives):
        findings.append(
            _finding(rule_path, "warn", "missing_falsepositives", "Rule is missing falsepositives.", "Add realistic benign causes and tuning notes.")
        )
    elif _has_generic_falsepositive(falsepositives):
        findings.append(
            _finding(rule_path, "warn", "generic_falsepositives", "False positive guidance is too generic.", "Replace generic entries with realistic benign causes.")
        )

    tags = raw.get("tags")
    if not _has_value(tags):
        findings.append(
            _finding(rule_path, "warn", "missing_attack_tags", "Rule is missing ATT&CK tags.", "Add tactic and technique tags such as attack.execution and attack.t1059.001.")
        )
        findings.append(
            _finding(rule_path, "warn", "missing_specific_attack_technique", "Rule is missing a specific ATT&CK technique tag.", "Add at least one tag like attack.t1059.001 when applicable.")
        )
    elif not _has_specific_attack_technique(tags):
        findings.append(
            _finding(rule_path, "warn", "missing_specific_attack_technique", "Rule is missing a specific ATT&CK technique tag.", "Add at least one tag like attack.t1059.001 when applicable.")
        )

    title = raw.get("title")
    if _has_value(title) and str(title).strip().lower() in {"suspicious activity", "malware detection", "bad process"}:
        findings.append(
            _finding(rule_path, "warn", "weak_title", "Rule title is too generic.", "Use a behavior-focused title that names the suspicious action.")
        )

    score = _score(findings)

    return RuleLintResult(
        path=rule_path,
        id=str(rule_id) if _has_value(rule_id) else None,
        title=str(raw.get("title")) if _has_value(raw.get("title")) else None,
        status=str(status) if _has_value(status) else None,
        level=str(level) if _has_value(level) else None,
        score=score,
        derived_maturity=_derived_maturity(score),
        findings=findings,
    )


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _has_specific_attack_technique(tags: Any) -> bool:
    if isinstance(tags, str):
        tags = [tags]
    if not isinstance(tags, list):
        return False
    return any(str(tag).lower().startswith("attack.t") and any(char.isdigit() for char in str(tag)) for tag in tags)


def _has_generic_falsepositive(falsepositives: Any) -> bool:
    if isinstance(falsepositives, str):
        values = [falsepositives]
    elif isinstance(falsepositives, list):
        values = falsepositives
    else:
        return False
    generic = {"unknown", "none", "legitimate activity"}
    return any(str(value).strip().lower() in generic for value in values)


SCORE_PENALTIES = {
    "missing_references": 5,
    "missing_falsepositives": 10,
    "generic_falsepositives": 5,
    "missing_attack_tags": 10,
    "missing_specific_attack_technique": 8,
    "weak_title": 5,
}


def _score(findings: list[LintFinding]) -> int:
    if any(finding.severity == "error" for finding in findings):
        return 0
    score = 100 - sum(SCORE_PENALTIES.get(finding.check_id, 0) for finding in findings)
    return max(0, min(100, score))


def _path(rule: Rule) -> str:
    return rule.path.as_posix()


def _finding(rule_path: str, severity: str, check_id: str, message: str, recommendation: str) -> LintFinding:
    return LintFinding(rule_path=rule_path, severity=severity, check_id=check_id, message=message, recommendation=recommendation)


def _derived_maturity(score: int) -> str:
    if score == 0:
        return "invalid"
    if score < 75:
        return "experimental"
    if score < 90:
        return "test"
    return "stable"
