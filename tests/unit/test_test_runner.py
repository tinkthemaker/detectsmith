from pathlib import Path

from detectsmith.test_runner import run_expected_tests


def write_rule(path: Path):
    path.write_text(
        """
title: PowerShell Encoded Command
id: rule-1
description: Detects PowerShell encoded command execution behavior.
logsource:
  product: windows
  category: process_creation
detection:
  selection:
    CommandLine|contains: " -enc "
  condition: selection
level: medium
status: test
""".strip(),
        encoding="utf-8",
    )


def test_run_expected_tests_passes_positive_and_negative_cases(tmp_path: Path):
    rule_path = tmp_path / "rule.yml"
    positive = tmp_path / "positive.jsonl"
    negative = tmp_path / "negative.jsonl"
    expected = tmp_path / "expected.yml"
    write_rule(rule_path)
    positive.write_text('{"CommandLine":"powershell.exe -enc SQBFAFgA"}\n', encoding="utf-8")
    negative.write_text('{"CommandLine":"powershell.exe -nop"}\n', encoding="utf-8")
    expected.write_text(
        f"""
tests:
  - name: positive
    rule: {rule_path.as_posix()}
    fixture: {positive.as_posix()}
    should_match: true
  - name: negative
    rule: {rule_path.as_posix()}
    fixture: {negative.as_posix()}
    should_match: false
""".strip(),
        encoding="utf-8",
    )

    report = run_expected_tests(expected)

    assert report.summary.tests_total == 2
    assert report.summary.tests_passed == 2
    assert report.summary.tests_failed == 0
    assert all(result.status == "passed" for result in report.tests)


def test_run_expected_tests_reports_failure_details(tmp_path: Path):
    rule_path = tmp_path / "rule.yml"
    fixture = tmp_path / "fixture.jsonl"
    expected = tmp_path / "expected.yml"
    write_rule(rule_path)
    fixture.write_text('{"CommandLine":"powershell.exe -nop"}\n', encoding="utf-8")
    expected.write_text(
        f"""
tests:
  - name: should_have_matched
    rule: {rule_path.as_posix()}
    fixture: {fixture.as_posix()}
    should_match: true
""".strip(),
        encoding="utf-8",
    )

    report = run_expected_tests(expected)

    assert report.summary.tests_failed == 1
    assert report.tests[0].status == "failed"
    assert "Expected match=True" in report.tests[0].failure_reason
