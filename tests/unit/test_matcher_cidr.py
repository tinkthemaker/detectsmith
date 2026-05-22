import ipaddress
from pathlib import Path

import pytest

from detectsmith.matcher import UnsupportedConditionError, rule_matches_event
from detectsmith.models import Rule


def make_rule(detection: dict, name: str = "rule.yml") -> Rule:
    return Rule(path=Path(name), raw={"title": "Test", "id": "test", "detection": detection})


class TestCidrMatching:
    def test_cidr_match_internal_private_ip(self):
        rule = make_rule({"selection": {"SourceIp|cidr": "10.0.0.0/8"}})
        assert rule_matches_event(rule, {"SourceIp": "10.45.67.1"}) is True
        assert rule_matches_event(rule, {"SourceIp": "192.168.1.1"}) is False

    def test_cidr_match_specific_subnet(self):
        rule = make_rule({"selection": {"SourceIp|cidr": "192.168.1.0/24"}})
        assert rule_matches_event(rule, {"SourceIp": "192.168.1.100"}) is True
        assert rule_matches_event(rule, {"SourceIp": "192.168.2.1"}) is False

    def test_cidr_match_single_ip(self):
        rule = make_rule({"selection": {"DstIp|cidr": "192.168.1.100/32"}})
        assert rule_matches_event(rule, {"DstIp": "192.168.1.100"}) is True
        assert rule_matches_event(rule, {"DstIp": "192.168.1.101"}) is False

    def test_cidr_match_ipv6(self):
        rule = make_rule({"selection": {"ClientIp|cidr": "fe80::/10"}})
        assert rule_matches_event(rule, {"ClientIp": "fe80::1"}) is True
        assert rule_matches_event(rule, {"ClientIp": "2001:db8::1"}) is False

    def test_cidr_match_false_when_field_missing(self):
        rule = make_rule({"selection": {"SourceIp|cidr": "10.0.0.0/8"}})
        assert rule_matches_event(rule, {}) is False

    def test_cidr_with_list_values(self):
        rule = make_rule({"selection": {"SrcIp|cidr": ["10.0.0.0/8", "172.16.0.0/12"]}})
        assert rule_matches_event(rule, {"SrcIp": "10.50.100.1"}) is True
        assert rule_matches_event(rule, {"SrcIp": "172.20.5.1"}) is True
        assert rule_matches_event(rule, {"SrcIp": "192.168.1.1"}) is False

    def test_cidr_invalid_format_raises_unsupported_condition(self):
        rule = make_rule({"selection": {"Ip|cidr": "not-a-cidr"}})
        with pytest.raises(UnsupportedConditionError, match="invalid CIDR"):
            rule_matches_event(rule, {"Ip": "10.0.0.1"})