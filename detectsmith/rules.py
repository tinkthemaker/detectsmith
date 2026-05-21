from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from detectsmith.models import Rule

RULE_SUFFIXES = {".yml", ".yaml"}


class RuleParseError(ValueError):
    """Raised when a rule file cannot be parsed into a mapping."""


def discover_rule_files(root: Path) -> list[Path]:
    """Return YAML rule files below root in deterministic order."""
    if not root.exists() or not root.is_dir():
        return []
    return sorted(
        path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in RULE_SUFFIXES
    )


def parse_rule_file(path: Path) -> Rule:
    """Parse a Sigma-style YAML rule file, preserving source path and raw content."""
    try:
        loaded: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RuleParseError(f"{path}: YAML parse error: {exc}") from exc
    except OSError as exc:
        raise RuleParseError(f"{path}: could not read rule file: {exc}") from exc

    if not isinstance(loaded, dict):
        raise RuleParseError(f"{path}: rule must be a top-level mapping")

    return Rule(path=path, raw=loaded)
