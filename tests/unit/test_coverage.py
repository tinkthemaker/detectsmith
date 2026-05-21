from pathlib import Path

from detectsmith.coverage import build_coverage_report
from detectsmith.models import Rule


def make_rule(tags, path="rule.yml"):
    return Rule(path=Path(path), raw={"title": path, "tags": tags, "logsource": {"product": "windows"}})


def test_coverage_extracts_tactics_and_techniques():
    rules = [
        make_rule(["attack.execution", "attack.t1059.001"], "one.yml"),
        make_rule(["attack.persistence", "attack.t1053"], "two.yml"),
    ]

    report = build_coverage_report(rules)

    assert report.summary.rules_total == 2
    assert report.summary.tactics_covered == 2
    assert report.summary.techniques_covered == 2
    assert {item.tag for item in report.tactics} == {"attack.execution", "attack.persistence"}
    assert {item.tag for item in report.techniques} == {"attack.t1059.001", "attack.t1053"}


def test_coverage_identifies_rules_missing_attack_tags():
    report = build_coverage_report([make_rule([], "missing.yml")])

    assert report.summary.rules_missing_attack_tags == 1
    assert report.rules_missing_attack_tags == ["missing.yml"]
