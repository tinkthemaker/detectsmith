from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from detectsmith.models import Rule


@dataclass(frozen=True)
class DocsPage:
    rule: str
    page: str


@dataclass(frozen=True)
class DocsResult:
    output_dir: str
    rule_pages_written: int
    index_written: bool
    pages: list[DocsPage]


def generate_rule_page(rule: Rule) -> str:
    raw = rule.raw
    title = str(raw.get("title", rule.path.stem))
    lines = [
        f"# {title}",
        "",
        str(raw.get("description", "No description provided.")),
        "",
        "## Metadata",
        "",
        f"- ID: {raw.get('id', '')}",
        f"- Status: {raw.get('status', '')}",
        f"- Level: {raw.get('level', '')}",
        f"- Source: `{rule.path.as_posix()}`",
        "",
        "## Logsource",
        "",
        _format_mapping(raw.get("logsource", {})),
        "",
        "## ATT&CK Tags",
        "",
        _format_list(raw.get("tags", [])),
        "",
        "## False Positives",
        "",
        _format_list(raw.get("falsepositives", [])),
        "",
        "## References",
        "",
        _format_list(raw.get("references", [])),
        "",
    ]
    return "\n".join(lines)


def write_docs_site(rules: list[Rule], out_dir: Path) -> DocsResult:
    out_dir.mkdir(parents=True, exist_ok=True)
    rules_dir = out_dir / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    pages: list[DocsPage] = []
    for rule in rules:
        filename = f"{_slug(str(rule.raw.get('title', rule.path.stem)))}.md"
        page_path = rules_dir / filename
        page_path.write_text(generate_rule_page(rule), encoding="utf-8")
        pages.append(DocsPage(rule=rule.path.as_posix(), page=page_path.as_posix()))
    index = _index_markdown(pages)
    (out_dir / "index.md").write_text(index, encoding="utf-8")
    return DocsResult(output_dir=out_dir.as_posix(), rule_pages_written=len(pages), index_written=True, pages=pages)


def _format_mapping(value: Any) -> str:
    if not isinstance(value, dict) or not value:
        return "No logsource provided."
    return "\n".join(f"- {key}: `{val}`" for key, val in value.items())


def _format_list(value: Any) -> str:
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list) or not value:
        return "None documented."
    return "\n".join(f"- {item}" for item in value)


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "rule"


def _index_markdown(pages: list[DocsPage]) -> str:
    lines = ["# Detectsmith Rule Documentation", "", "## Rules", ""]
    for page in pages:
        rel = Path(page.page).name
        lines.append(f"- [{page.rule}](rules/{rel})")
    return "\n".join(lines) + "\n"
