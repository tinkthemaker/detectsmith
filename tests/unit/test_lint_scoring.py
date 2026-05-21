from pathlib import Path

from detectsmith.lint import lint_rules
from detectsmith.models import Rule


def make_rule(raw: dict, name: str = "rule.yml") -> Rule:
    return Rule(path=Path(name), raw=raw)


def valid_rule(**overrides) -> dict:
    raw = {
        "title": "PowerShell Encoded Command",
        "id": "rule-1",
        "description": "Detects PowerShell encoded command execution behavior.",
        "logsource": {"product": "windows", "category": "process_creation"},
        "detection": {"selection": {"CommandLine|contains": " -enc "}, "condition": "selection"},
        "level": "medium",
        "status": "test",
        "references": ["https://attack.mitre.org/techniques/T1059/001/"],
        "falsepositives": ["Administrative scripts may use encoded commands."],
        "tags": ["attack.execution", "attack.t1059.001"],
    }
    raw.update(overrides)
    return raw


def test_lint_subtracts_points_for_recommended_metadata_gaps():
    rule = make_rule(valid_rule(references=[], falsepositives=[], tags=[]))

    result = lint_rules([rule]).rules[0]

    assert result.score == 67
    check_ids = {finding.check_id for finding in result.findings}
    assert "missing_references" in check_ids
    assert "missing_falsepositives" in check_ids
    assert "missing_attack_tags" in check_ids
    assert "missing_specific_attack_technique" in check_ids


def test_lint_detects_duplicate_ids_and_scores_affected_rules_zero():
    first = make_rule(valid_rule(id="duplicate"), "one.yml")
    second = make_rule(valid_rule(id="duplicate"), "two.yml")

    report = lint_rules([first, second])

    assert [result.score for result in report.rules] == [0, 0]
    assert all(any(f.check_id == "duplicate_id" for f in result.findings) for result in report.rules)


def test_lint_penalizes_generic_title_and_false_positive():
    rule = make_rule(valid_rule(title="Suspicious Activity", falsepositives=["Unknown"]))

    result = lint_rules([rule]).rules[0]

    assert result.score == 90
    assert {finding.check_id for finding in result.findings} >= {"weak_title", "generic_falsepositives"}
