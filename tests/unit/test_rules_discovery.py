from pathlib import Path

from detectsmith.rules import discover_rule_files


def test_discovers_yaml_rule_files_recursively_sorted(tmp_path: Path):
    rules = tmp_path / "rules"
    (rules / "windows").mkdir(parents=True)
    (rules / "linux").mkdir(parents=True)
    (rules / "README.md").write_text("not a rule", encoding="utf-8")
    (rules / "windows" / "b_rule.yaml").write_text("title: B", encoding="utf-8")
    (rules / "linux" / "a_rule.yml").write_text("title: A", encoding="utf-8")

    discovered = discover_rule_files(rules)

    assert discovered == [
        rules / "linux" / "a_rule.yml",
        rules / "windows" / "b_rule.yaml",
    ]


def test_discover_rule_files_returns_empty_for_missing_directory(tmp_path: Path):
    assert discover_rule_files(tmp_path / "missing") == []
