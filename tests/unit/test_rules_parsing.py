from pathlib import Path

import pytest

from detectsmith.rules import RuleParseError, parse_rule_file


def test_parse_rule_file_preserves_source_path_and_raw_yaml(tmp_path: Path):
    rule_path = tmp_path / "rule.yml"
    rule_path.write_text(
        """
title: Example Rule
id: example-id
detection:
  selection:
    Image: cmd.exe
  condition: selection
""".strip(),
        encoding="utf-8",
    )

    rule = parse_rule_file(rule_path)

    assert rule.path == rule_path
    assert rule.raw["title"] == "Example Rule"
    assert rule.raw["detection"]["condition"] == "selection"


def test_parse_rule_file_rejects_non_mapping_yaml(tmp_path: Path):
    rule_path = tmp_path / "bad.yml"
    rule_path.write_text("- not\n- a\n- mapping\n", encoding="utf-8")

    with pytest.raises(RuleParseError) as exc:
        parse_rule_file(rule_path)

    assert str(rule_path) in str(exc.value)
    assert "top-level mapping" in str(exc.value)


def test_parse_rule_file_surfaces_yaml_errors_with_path(tmp_path: Path):
    rule_path = tmp_path / "broken.yml"
    rule_path.write_text("title: [unterminated\n", encoding="utf-8")

    with pytest.raises(RuleParseError) as exc:
        parse_rule_file(rule_path)

    assert str(rule_path) in str(exc.value)
    assert "YAML" in str(exc.value)
