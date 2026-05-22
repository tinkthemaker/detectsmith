from pathlib import Path

import pytest

from detectsmith.matcher import UnsupportedConditionError, rule_matches_event
from detectsmith.models import Rule


def make_rule(detection: dict, name: str = "rule.yml") -> Rule:
    return Rule(path=Path(name), raw={"title": "Test", "id": "test", "detection": detection})


class TestRegexModifier:
    def test_re_match_anywhere_in_field(self):
        rule = make_rule({"selection": {"CommandLine|re": "pow.*shell"}})
        event = {"CommandLine": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe -enc ..."}
        assert rule_matches_event(rule, event) is True

    def test_re_match_false_when_pattern_not_present(self):
        rule = make_rule({"selection": {"CommandLine|re": "pow.*shell"}})
        event = {"CommandLine": "C:\\Windows\\System32\\cmd.exe /c whoami"}
        assert rule_matches_event(rule, event) is False

    def test_re_match_is_case_insensitive(self):
        rule = make_rule({"selection": {"CommandLine|re": "Pow.*Shell"}})
        event = {"CommandLine": "C:\\Windows\\System32\\POWERSHELL.EXE -enc ..."}
        assert rule_matches_event(rule, event) is True

    def test_re_match_with_special_characters(self):
        rule = make_rule({"selection": {"ProcessName|re": ".*\\\\system32\\\\.*"}})
        event = {"ProcessName": "C:\\Windows\\System32\\svchost.exe"}
        assert rule_matches_event(rule, event) is True

    def test_re_invalid_pattern_raises_unsupported_condition(self):
        rule = make_rule({"selection": {"CommandLine|re": "[invalid("}})
        event = {"CommandLine": "some command"}
        with pytest.raises(UnsupportedConditionError, match="invalid regex"):
            rule_matches_event(rule, event)

    def test_re_with_list_values_matches_any(self):
        rule = make_rule({"selection": {"CommandLine|re": ["pow.*shell", "cmd.*exe"]}})
        assert rule_matches_event(rule, {"CommandLine": "powershell -enc ..."}) is True
        assert rule_matches_event(rule, {"CommandLine": "cmd.exe /c dir"}) is True
        assert rule_matches_event(rule, {"CommandLine": "hostname"}) is False