from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from detectsmith.models import CoverageReport, LintReport, TestReport
from detectsmith.docs import DocsResult


def lint_report_envelope(report: LintReport, project_root: Path, status: str) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "command": "lint",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "project_root": project_root.resolve().as_posix(),
        "status": status,
        "summary": _to_jsonable(report.summary),
        "data": {"rules": [_to_jsonable(rule) for rule in report.rules]},
        "errors": [],
    }


def write_json_report(payload: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def test_report_envelope(report: TestReport, project_root: Path, status: str) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "command": "test",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "project_root": project_root.resolve().as_posix(),
        "status": status,
        "summary": _to_jsonable(report.summary),
        "data": {"tests": [_to_jsonable(test) for test in report.tests]},
        "errors": [],
    }


def coverage_report_envelope(report: CoverageReport, project_root: Path, status: str = "success") -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "command": "coverage",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "project_root": project_root.resolve().as_posix(),
        "status": status,
        "summary": _to_jsonable(report.summary),
        "data": {
            "tactics": [_to_jsonable(item) for item in report.tactics],
            "techniques": [_to_jsonable(item) for item in report.techniques],
            "rules_missing_attack_tags": report.rules_missing_attack_tags,
        },
        "errors": [],
    }


def docs_report_envelope(result: DocsResult, project_root: Path, status: str = "success") -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "command": "docs",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "project_root": project_root.resolve().as_posix(),
        "status": status,
        "summary": {
            "rules_total": result.rule_pages_written,
            "rule_pages_written": result.rule_pages_written,
            "index_written": result.index_written,
            "output_dir": result.output_dir,
        },
        "data": {"pages": [_to_jsonable(page) for page in result.pages], "index": f"{result.output_dir}/index.md"},
        "errors": [],
    }


def _to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    return value
