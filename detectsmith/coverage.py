from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from detectsmith.models import CoverageItem, CoverageReport, CoverageSummary, Rule
from detectsmith.reporting import coverage_report_envelope, write_json_report


def build_coverage_report(rules: list[Rule]) -> CoverageReport:
    tactics: dict[str, list[str]] = defaultdict(list)
    techniques: dict[str, list[str]] = defaultdict(list)
    missing: list[str] = []

    for rule in rules:
        path = rule.path.as_posix()
        tags = _tags(rule)
        attack_tags = [tag for tag in tags if tag.startswith("attack.")]
        if not attack_tags:
            missing.append(path)
        for tag in attack_tags:
            if _is_technique(tag):
                techniques[tag].append(path)
            elif _is_tactic(tag):
                tactics[tag].append(path)

    tactic_items = _items(tactics)
    technique_items = _items(techniques)
    return CoverageReport(
        tactics=tactic_items,
        techniques=technique_items,
        rules_missing_attack_tags=sorted(missing),
        summary=CoverageSummary(
            rules_total=len(rules),
            tactics_covered=len(tactic_items),
            techniques_covered=len(technique_items),
            rules_missing_attack_tags=len(missing),
        ),
    )


def _tags(rule: Rule) -> list[str]:
    raw_tags = rule.raw.get("tags", [])
    if isinstance(raw_tags, str):
        return [raw_tags.lower()]
    if isinstance(raw_tags, list):
        return [str(tag).lower() for tag in raw_tags]
    return []


def _is_technique(tag: str) -> bool:
    return tag.startswith("attack.t") and any(char.isdigit() for char in tag)


def _is_tactic(tag: str) -> bool:
    return tag.startswith("attack.") and not _is_technique(tag)


def _items(mapping: dict[str, list[str]]) -> list[CoverageItem]:
    return [CoverageItem(tag=tag, rules=len(paths), rule_paths=sorted(paths)) for tag, paths in sorted(mapping.items())]


def coverage_report_markdown(report: CoverageReport) -> str:
    lines = [
        "# ATT&CK Coverage Report",
        "",
        "## Summary",
        "",
        f"- Total rules: {report.summary.rules_total}",
        f"- Tactics covered: {report.summary.tactics_covered}",
        f"- Techniques covered: {report.summary.techniques_covered}",
        f"- Rules missing ATT&CK tags: {report.summary.rules_missing_attack_tags}",
        "",
        "## Techniques",
        "",
        "| Technique | Rules |",
        "|---|---:|",
    ]
    for item in report.techniques:
        lines.append(f"| {item.tag} | {item.rules} |")
    lines.extend(["", "## Tactics", "", "| Tactic | Rules |", "|---|---:|"])
    for item in report.tactics:
        lines.append(f"| {item.tag} | {item.rules} |")
    if report.rules_missing_attack_tags:
        lines.extend(["", "## Rules Missing ATT&CK Tags", ""])
        lines.extend(f"- {path}" for path in report.rules_missing_attack_tags)
    return "\n".join(lines) + "\n"


def write_coverage_reports(report: CoverageReport, json_path: Path, markdown_path: Path) -> None:
    write_json_report(coverage_report_envelope(report, Path.cwd()), json_path)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(coverage_report_markdown(report), encoding="utf-8")
