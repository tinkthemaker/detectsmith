from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from detectsmith.matcher import rule_matches_event
from detectsmith.models import TestReport, TestResult, TestSummary
from detectsmith.rules import parse_rule_file


def run_expected_tests(expected_path: Path) -> TestReport:
    spec = yaml.safe_load(expected_path.read_text(encoding="utf-8")) or {}
    cases = spec.get("tests", [])
    results: list[TestResult] = []

    for case in cases:
        name = str(case["name"])
        rule_path = Path(case["rule"])
        fixture_path = Path(case["fixture"])
        should_match = bool(case["should_match"])
        rule = parse_rule_file(rule_path)
        events = _load_jsonl(fixture_path)
        matched_events = sum(1 for event in events if rule_matches_event(rule, event))
        matched = matched_events > 0
        status = "passed" if matched == should_match else "failed"
        failure_reason = None if status == "passed" else f"Expected match={should_match}, got match={matched}."
        results.append(
            TestResult(
                name=name,
                rule=rule_path.as_posix(),
                fixture=fixture_path.as_posix(),
                should_match=should_match,
                matched=matched,
                matched_events=matched_events,
                status=status,
                failure_reason=failure_reason,
            )
        )

    passed = sum(1 for result in results if result.status == "passed")
    failed = sum(1 for result in results if result.status == "failed")
    rules_tested = len({result.rule for result in results})
    return TestReport(
        tests=results,
        summary=TestSummary(tests_total=len(results), tests_passed=passed, tests_failed=failed, rules_tested=rules_tested),
    )


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            loaded = json.loads(line)
            if isinstance(loaded, dict):
                events.append(loaded)
    return events
