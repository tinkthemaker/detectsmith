from pathlib import Path

from detectsmith.docs import generate_rule_page, write_docs_site
from detectsmith.models import Rule


def sample_rule() -> Rule:
    return Rule(
        path=Path("rules/windows/example.yml"),
        raw={
            "title": "PowerShell Encoded Command",
            "id": "rule-1",
            "description": "Detects PowerShell encoded command execution behavior.",
            "status": "test",
            "level": "medium",
            "logsource": {"product": "windows", "category": "process_creation"},
            "falsepositives": ["Administrative scripts may use encoded commands."],
            "references": ["https://attack.mitre.org/techniques/T1059/001/"],
            "tags": ["attack.execution", "attack.t1059.001"],
        },
    )


def test_generate_rule_page_contains_core_sections():
    page = generate_rule_page(sample_rule())

    assert "# PowerShell Encoded Command" in page
    assert "## Logsource" in page
    assert "attack.t1059.001" in page
    assert "Administrative scripts" in page


def test_write_docs_site_creates_index_and_rule_page(tmp_path: Path):
    result = write_docs_site([sample_rule()], tmp_path)

    assert (tmp_path / "index.md").exists()
    assert result.rule_pages_written == 1
    assert result.pages[0].page.endswith("powershell-encoded-command.md")
