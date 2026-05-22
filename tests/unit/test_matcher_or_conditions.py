from pathlib import Path

import pytest

from detectsmith.matcher import UnsupportedConditionError, rule_matches_event
from detectsmith.models import Rule


def make_rule(detection: dict, name: str = "rule.yml") -> Rule:
    return Rule(path=Path(name), raw={"title": "Test", "id": "test", "detection": detection})


class TestOrConditions:
    def test_one_of_selection_matches_first(self):
        rule = make_rule({
            "selection_cmd": {"CommandLine|contains": "cmd.exe"},
            "selection_ps": {"CommandLine|contains": "powershell.exe"},
            "condition": "1 of selection_*",
        })
        assert rule_matches_event(rule, {"CommandLine": "cmd.exe /c dir"}) is True

    def test_one_of_selection_matches_second(self):
        rule = make_rule({
            "selection_cmd": {"CommandLine|contains": "cmd.exe"},
            "selection_ps": {"CommandLine|contains": "powershell.exe"},
            "condition": "1 of selection_*",
        })
        assert rule_matches_event(rule, {"CommandLine": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe -enc ..."}) is True

    def test_one_of_selection_none_match(self):
        rule = make_rule({
            "selection_cmd": {"CommandLine|contains": "cmd.exe"},
            "selection_ps": {"CommandLine|contains": "powershell.exe"},
            "condition": "1 of selection_*",
        })
        assert rule_matches_event(rule, {"CommandLine": "whoami"}) is False

    def test_any_of_keyword_alias_for_one_of(self):
        rule = make_rule({
            "selection_http": {"Url|contains": "http"},
            "selection_https": {"Url|contains": "https"},
            "condition": "any of selection_*",
        })
        assert rule_matches_event(rule, {"Url": "https://evil.com"}) is True
        assert rule_matches_event(rule, {"Url": "http://evil.com"}) is True

    def test_one_of_with_multiple_fields_per_selection(self):
        rule = make_rule({
            "selection_rundll32": {"CommandLine|contains": "rundll32", "ProcessName|contains": "rundll32"},
            "selection_regsvr32": {"CommandLine|contains": "regsvr32", "ProcessName|contains": "regsvr32"},
            "condition": "1 of selection_*",
        })
        assert rule_matches_event(rule, {"CommandLine": "rundll32.exe thing.dll", "ProcessName": "rundll32.exe"}) is True
        assert rule_matches_event(rule, {"CommandLine": "rundll32.exe thing.dll", "ProcessName": "explorer.exe"}) is False

    def test_condition_not_found_raises_unsupported(self):
        rule = make_rule({
            "selection": {"CommandLine|contains": "cmd"},
            "condition": "1 of nonexistent_*",
        })
        with pytest.raises(UnsupportedConditionError, match="matched no selections"):
            rule_matches_event(rule, {"CommandLine": "cmd.exe"})

    def test_condition_with_wrong_type_target_raises_unsupported(self):
        rule = make_rule({
            "selection": "not a dict",
            "condition": "1 of selection",
        })
        with pytest.raises(UnsupportedConditionError, match="matched no selections"):
            rule_matches_event(rule, {"CommandLine": "anything"})

    def test_one_of_exact_keyname_no_wildcard(self):
        rule = make_rule({
            "selection_a": {"CommandLine|contains": "alpha"},
            "selection_b": {"CommandLine|contains": "beta"},
            "condition": "1 of selection_a",
        })
        assert rule_matches_event(rule, {"CommandLine": "alpha executable"}) is True
        assert rule_matches_event(rule, {"CommandLine": "beta executable"}) is False