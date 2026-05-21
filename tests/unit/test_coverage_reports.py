from pathlib import Path

from detectsmith.coverage import build_coverage_report, coverage_report_markdown, write_coverage_reports
from detectsmith.models import Rule


def test_coverage_report_markdown_includes_summary_and_techniques():
    report = build_coverage_report([Rule(path=Path("one.yml"), raw={"tags": ["attack.execution", "attack.t1059.001"]})])

    markdown = coverage_report_markdown(report)

    assert "# ATT&CK Coverage Report" in markdown
    assert "attack.t1059.001" in markdown


def test_write_coverage_reports_writes_json_and_markdown(tmp_path: Path):
    report = build_coverage_report([Rule(path=Path("one.yml"), raw={"tags": ["attack.execution", "attack.t1059.001"]})])

    write_coverage_reports(report, tmp_path / "coverage.json", tmp_path / "coverage.md")

    assert (tmp_path / "coverage.json").exists()
    assert (tmp_path / "coverage.md").exists()
    assert '"command": "coverage"' in (tmp_path / "coverage.json").read_text(encoding="utf-8")
