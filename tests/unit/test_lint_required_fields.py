from pathlib import Path

from detectsmith.lint import lint_rules
from detectsmith.models import Rule


def make_rule(raw: dict, name: str = "rule.yml") -> Rule:
    return Rule(path=Path(name), raw=raw)


def test_lint_required_fields_reports_errors_for_missing_metadata():
    rule = make_rule({"title": "Only Title"})

    report = lint_rules([rule])

    error_ids = {finding.check_id for result in report.rules for finding in result.findings if finding.severity == "error"}
    assert "missing_id" in error_ids
    assert "missing_description" in error_ids
    assert "missing_logsource" in error_ids
    assert "missing_detection" in error_ids
    assert "missing_detection_condition" in error_ids
    assert "missing_level" in error_ids
    assert "missing_status" in error_ids
    assert report.rules[0].score == 0


def test_lint_required_fields_accepts_minimal_valid_rule():
    rule = make_rule(
        {
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
    )

    report = lint_rules([rule])

    assert report.rules[0].score == 100
    assert not [finding for finding in report.rules[0].findings if finding.severity == "error"]
