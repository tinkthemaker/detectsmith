from __future__ import annotations

import ipaddress
import re as re_module
from typing import Any

from detectsmith.models import Rule

SUPPORTED_MODIFIERS = {"contains", "startswith", "endswith", "re", "cidr"}


class UnsupportedConditionError(ValueError):
    """Raised when a rule uses matcher semantics outside v0.1 scope."""


def rule_matches_event(rule: Rule, event: dict[str, Any]) -> bool:
    detection = rule.raw.get("detection", {})
    if not isinstance(detection, dict):
        return False
    condition = str(detection.get("condition", "selection")).strip()
    selection = detection.get("selection")

    if condition in ("selection", ""):
        if not isinstance(selection, dict):
            return False
        return all(_field_matches(expr, expected, event) for expr, expected in selection.items())

    if condition.startswith("1 of ") or condition.startswith("any of "):
        pattern = condition.split(" ", 2)[2].strip()
        matching_items = _expand_wildcard(detection, pattern)
        if not matching_items:
            raise UnsupportedConditionError(f"{rule.path}: condition '{pattern}' matched no selections")
        return any(
            all(_field_matches(expr, expected, event) for expr, expected in item.items())
            if isinstance(item, dict) else False
            for item in matching_items
        )

    raise UnsupportedConditionError(f"{rule.path}: unsupported condition '{condition}'")


def _expand_wildcard(detection: dict[str, Any], pattern: str) -> list[dict[str, Any]]:
    """Return all detection sub-dicts whose keys match the glob pattern."""
    if "*" not in pattern:
        result = detection.get(pattern)
        return [result] if isinstance(result, dict) else []
    prefix = pattern.rstrip("*")
    return [detection[k] for k in sorted(detection) if k.startswith(prefix) and isinstance(detection[k], dict)]


def _field_matches(expression: str, expected: Any, event: dict[str, Any]) -> bool:
    field, modifier = _split_expression(expression)
    actual = event.get(field)
    if isinstance(expected, list):
        return any(_value_matches(actual, value, modifier) for value in expected)
    return _value_matches(actual, expected, modifier)


def _split_expression(expression: str) -> tuple[str, str | None]:
    if "|" not in expression:
        return expression, None
    field, modifier = expression.split("|", 1)
    if modifier not in SUPPORTED_MODIFIERS:
        raise UnsupportedConditionError(f"unsupported modifier '{modifier}'")
    return field, modifier


def _value_matches(actual: Any, expected: Any, modifier: str | None) -> bool:
    if actual is None:
        return False
    actual_s = str(actual).lower()
    expected_s = str(expected).lower()
    if modifier == "contains":
        return expected_s in actual_s
    if modifier == "startswith":
        return actual_s.startswith(expected_s)
    if modifier == "endswith":
        return actual_s.endswith(expected_s)
    if modifier == "re":
        try:
            pattern = re_module.compile(expected_s, re_module.IGNORECASE)
            return pattern.search(actual_s) is not None
        except re_module.error as e:
            raise UnsupportedConditionError(f"invalid regex '{expected}': {e}") from e
    if modifier == "cidr":
        try:
            ip = ipaddress.ip_address(actual_s)
            network = ipaddress.ip_network(expected_s, strict=False)
            return ip in network
        except ValueError as e:
            raise UnsupportedConditionError(f"invalid CIDR '{expected}': {e}") from e
    return actual_s == expected_s