from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Rule:
    """Parsed Sigma-style rule with source path preserved."""

    path: Path
    raw: dict[str, Any]


@dataclass(frozen=True)
class LintFinding:
    rule_path: str
    severity: str
    check_id: str
    message: str
    recommendation: str


@dataclass(frozen=True)
class RuleLintResult:
    path: str
    id: str | None
    title: str | None
    status: str | None
    level: str | None
    score: int
    derived_maturity: str
    findings: list[LintFinding] = field(default_factory=list)


@dataclass(frozen=True)
class LintSummary:
    rules_total: int
    rules_valid: int
    findings_error: int
    findings_warn: int
    findings_info: int
    average_score: float


@dataclass(frozen=True)
class LintReport:
    rules: list[RuleLintResult]
    summary: LintSummary


@dataclass(frozen=True)
class TestResult:
    name: str
    rule: str
    fixture: str
    should_match: bool
    matched: bool
    matched_events: int
    status: str
    failure_reason: str | None = None


@dataclass(frozen=True)
class TestSummary:
    tests_total: int
    tests_passed: int
    tests_failed: int
    rules_tested: int


@dataclass(frozen=True)
class TestReport:
    tests: list[TestResult]
    summary: TestSummary


@dataclass(frozen=True)
class CoverageItem:
    tag: str
    rules: int
    rule_paths: list[str]


@dataclass(frozen=True)
class CoverageSummary:
    rules_total: int
    tactics_covered: int
    techniques_covered: int
    rules_missing_attack_tags: int


@dataclass(frozen=True)
class CoverageReport:
    tactics: list[CoverageItem]
    techniques: list[CoverageItem]
    rules_missing_attack_tags: list[str]
    summary: CoverageSummary
