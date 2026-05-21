import pytest

from detectsmith.matcher import UnsupportedConditionError, rule_matches_event
from detectsmith.models import Rule


def make_rule(detection: dict) -> Rule:
    return Rule(path="rule.yml", raw={"detection": detection})


def test_rule_matches_exact_field_value_case_insensitive():
    rule = make_rule({"selection": {"Image": "cmd.exe"}, "condition": "selection"})

    assert rule_matches_event(rule, {"Image": "CMD.EXE"}) is True
    assert rule_matches_event(rule, {"Image": "powershell.exe"}) is False


def test_rule_matches_contains_startswith_and_endswith_modifiers():
    rule = make_rule(
        {
            "selection": {
                "CommandLine|contains": " -enc ",
                "Image|startswith": "C:\\Windows",
                "ParentImage|endswith": "\\explorer.exe",
            },
            "condition": "selection",
        }
    )

    event = {
        "CommandLine": "powershell.exe -enc SQBFAFgA",
        "Image": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
        "ParentImage": "C:\\Windows\\explorer.exe",
    }

    assert rule_matches_event(rule, event) is True


def test_rule_list_values_match_any_value():
    rule = make_rule({"selection": {"Image|endswith": ["\\powershell.exe", "\\pwsh.exe"]}, "condition": "selection"})

    assert rule_matches_event(rule, {"Image": "C:\\Program Files\\PowerShell\\7\\pwsh.exe"}) is True


def test_multiple_fields_in_selection_must_all_match():
    rule = make_rule({"selection": {"Image|endswith": "\\powershell.exe", "CommandLine|contains": " -enc "}, "condition": "selection"})

    assert rule_matches_event(rule, {"Image": "x\\powershell.exe", "CommandLine": "powershell -nop"}) is False


def test_unsupported_condition_raises_clear_error():
    rule = make_rule({"selection": {"Image": "cmd.exe"}, "condition": "selection near filter"})

    with pytest.raises(UnsupportedConditionError):
        rule_matches_event(rule, {"Image": "cmd.exe"})
