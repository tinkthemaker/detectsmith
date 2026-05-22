from pathlib import Path
import json

from detectsmith.gap_analyzer import (
    map_service_to_techniques,
)


def test_port_to_technique_mapping():
    """Static port → ATT&CK mapping covers common services."""
    from detectsmith.gap_analyzer import PORT_TO_TECHNIQUES

    # High-confidence port mappings
    assert 22 in PORT_TO_TECHNIQUES          # SSH
    assert 445 in PORT_TO_TECHNIQUES         # SMB
    assert 3389 in PORT_TO_TECHNIQUES        # RDP
    assert 1433 in PORT_TO_TECHNIQUES        # MSSQL

    # RDP maps to T1021.006
    rdp_techniques = PORT_TO_TECHNIQUES[3389]["tcp"]
    tids = [t[0] for t in rdp_techniques]
    assert "T1021.006" in tids


def test_service_to_techniques_exposes_smb():
    from detectsmith.gap_analyzer import ExposedService

    svc = ExposedService(
        ip="192.168.1.1", port=445, protocol="tcp",
        name="smb", product="SMB", version="",
        finding_severity="High", cve_ids=[],
    )
    techniques = map_service_to_techniques(svc)
    tids = [t[0] for t in techniques]
    assert "T1021.002" in tids   # SMB remote services
    assert "T1021.003" in tids   # Windows admin shares


def test_service_to_techniques_exposes_ssh():
    from detectsmith.gap_analyzer import ExposedService

    svc = ExposedService(
        ip="10.0.0.5", port=22, protocol="tcp",
        name="ssh", product="OpenSSH", version="8.0",
        finding_severity="Medium", cve_ids=[],
    )
    techniques = map_service_to_techniques(svc)
    tids = [t[0] for t in techniques]
    assert "T1021.004" in tids   # SSH remote services


def test_cve_to_technique_log4shell():
    from detectsmith.gap_analyzer import CVE_TO_TECHNIQUE

    assert CVE_TO_TECHNIQUE["CVE-2021-44228"] == "T1190"
    assert CVE_TO_TECHNIQUE["CVE-2019-0708"] == "T1190"


def test_gap_priority_order():
    from detectsmith.gap_analyzer import GapEntry

    # KEV vuln should rank higher
    kev_gap = GapEntry(
        technique_id="T1190", technique_name="Exploit Public-Facing App",
        confidence="high", source="cve",
        exposed_on=["10.0.0.5"], cve_ids=["CVE-2021-44228"],
        in_kev=True, epss_score=0.3, cvss_score=10.0,
    )

    non_kev_gap = GapEntry(
        technique_id="T1021.004", technique_name="SSH",
        confidence="low", source="port",
        exposed_on=["10.0.0.6"], cve_ids=[],
        in_kev=False, epss_score=None, cvss_score=None,
    )

    assert kev_gap.priority() > non_kev_gap.priority()


def test_product_to_techniques_elasticsearch():
    from detectsmith.gap_analyzer import PRODUCT_TO_TECHNIQUES

    assert "elasticsearch" in PRODUCT_TO_TECHNIQUES
    tids = [t[0] for t in PRODUCT_TO_TECHNIQUES["elasticsearch"]]
    assert "T1021.001" in tids
    assert "T1005" in tids