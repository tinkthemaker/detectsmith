from __future__ import annotations

from typing import Any

from detectsmith.models import Rule

SUPPORTED_MODIFIERS = {"contains", "startswith", "endswith"}


class UnsupportedConditionError(ValueError):
    """Raised when a rule uses matcher semantics outside v0.1 scope."""


def rule_matches_event(rule: Rule, event: dict[str, Any]) -> bool:
    detection = rule.raw.get("detection", {})
    if not isinstance(detection, dict):
        return False
    condition = str(detection.get("condition", "")).strip()
    if condition != "selection":
        raise UnsupportedConditionError(f"{rule.path}: unsupported condition '{condition}'")
    selection = detection.get("selection")
    if not isinstance(selection, dict):
        return False
    return all(_field_matches(expression, expected, event) for expression, expected in selection.items())


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
    return actual_s == expected_s
