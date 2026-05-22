"""Detection gap analyzer — cross-references SepulchrynScan findings with Detectsmith coverage.

Usage:
    python -m detectsmith.gap_analyzer scan_db <scan.db> [--coverage reports/attack_coverage.json]
    python -m detectsmith.gap_analyzer report <scan.db>
    python -m detectsmith.gap_analyzer backlog <scan.db> [--coverage reports/attack_coverage.json]
    python -m detectsmith.gap_analyzer --help

Architecture:
  1. Read exposed services + CVE findings from SepulchrynScan SQLite DB
  2. Map each exposed service to ATT&CK technique candidates
  3. Load Detectsmith's coverage map (attack_coverage.json)
  4. Output gaps: techniques you have exposure to but no detection for

The port-to-ATT&CK mapping is static knowledge embedded in this module.
New mappings should be added to PORT_TO_TECHNIQUES.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ----------------------------------------------------------------------
# Static port/service → ATT&CK technique mappings
# Based on MITRE ATT&CK Enterprise matrix and common exposure patterns.
# Format: {port: {protocol: [(technique_id, technique_name, confidence)]}}
# confidence: high/medium/low — how strongly this port implies this technique
# ----------------------------------------------------------------------
PORT_TO_TECHNIQUES: dict[int, dict[str, list[tuple[str, str, str]]]] = {
    21: {"tcp": [("T1021.002", "Remote Services: FTP/SMB", "medium")]},
    22: {"tcp": [
        ("T1021.004", "Remote Services: SSH", "high"),
        ("T1550.001", "Persistence: SSH Keys", "medium"),
    ]},
    23: {"tcp": [("T1021.004", "Remote Services: Telnet", "medium")]},
    25: {"tcp": [("T1071.002", "Application Layer: SMTP", "low")]},
    53: {"tcp": [("T1071.002", "DNS", "low")]},
    80: {"tcp": [("T1071.001", "Web Services", "high")]},
    110: {"tcp": [("T1071.002", "Email Client", "low")]},
    135: {"tcp": [("T1021.003", "Windows Admin Shares via RPC", "high")]},
    139: {"tcp": [("T1021.003", "Windows Admin Shares", "high")]},
    143: {"tcp": [("T1071.001", "Email Services (IMAP)", "low")]},
    161: {"tcp": [("T1016", "System Network Config Discovery (SNMP)", "medium")]},
    389: {"tcp": [
        ("T1558.003", "Credential Access: LDAP Pass-through", "medium"),
        ("T1556.001", "Modify Authentication Process: LDAP", "medium"),
    ]},
    443: {"tcp": [
        ("T1071.001", "Web Services (HTTPS)", "high"),
        ("T1071.002", "Application Layer: HTTPS", "medium"),
        ("T1190", "Exploit Public-Facing Application", "high"),
    ]},
    445: {"tcp": [
        ("T1021.002", "SMB/Windows Admin Shares", "high"),
        ("T1021.003", "Remote Services via SMB", "high"),
        ("T1547.010", "Boot Initialization: SMB exploited", "high"),
    ]},
    465: {"tcp": [("T1071.002", "Email (SMTPS)", "low")]},
    514: {"udp": [("T1016", "Network Sniffing (Syslog)", "medium")]},
    587: {"tcp": [("T1071.002", "Email Submission (SMTP)", "low")]},
    636: {"tcp": [("T1558.003", "LDAPS", "medium")]},
    993: {"tcp": [("T1071.002", "IMAPS", "low")]},
    995: {"tcp": [("T1071.002", "POP3S", "low")]},
    1433: {"tcp": [
        ("T1021.001", "Remote Services: MSSQL", "high"),
        ("T1133", "External Remote Services (MSSQL)", "high"),
    ]},
    1521: {"tcp": [("T1021.001", "Oracle Database", "high")]},
    2049: {"tcp": [("T1021.004", "NFS", "medium")]},
    3306: {"tcp": [
        ("T1021.001", "Remote Services: MySQL", "high"),
        ("T1005", "Data from Local System (MySQL dump)", "medium"),
    ]},
    3389: {"tcp": [
        ("T1021.006", "Remote Services: RDP", "high"),
        ("T1133", "External Remote Services (RDP)", "high"),
    ]},
    5432: {"tcp": [
        ("T1021.001", "Remote Services: PostgreSQL", "high"),
        ("T1005", "Data from Local System (PG dump)", "medium"),
    ]},
    5900: {"tcp": [
        ("T1021.006", "Remote Services: VNC", "high"),
        ("T1210", "Exploitation of Remote Services (VNC)", "high"),
    ]},
    5985: {"tcp": [
        ("T1021.006", "WinRM", "high"),
        ("T1021.004", "Remote Services via WinRM", "high"),
    ]},
    6379: {"tcp": [
        ("T1021.001", "Redis", "high"),
        ("T1005", "Data from Local System (Redis)", "high"),
    ]},
    8080: {"tcp": [
        ("T1071.001", "Web Services (HTTP alt)", "high"),
        ("T1190", "Exploit Public-Facing Application", "high"),
    ]},
    8443: {"tcp": [("T1071.001", "HTTPS Alt", "high")]},
    9200: {"tcp": [
        ("T1021.001", "Elasticsearch", "high"),
        ("T1005", "Data from Local System (ES)", "high"),
    ]},
    27017: {"tcp": [
        ("T1021.001", "MongoDB", "high"),
        ("T1005", "Data from Local System (MongoDB)", "high"),
    ]},
}

# CVE ID → ATT&CK technique mappings (CISA KEV-enriched CVEs known to map to techniques)
CVE_TO_TECHNIQUE: dict[str, str] = {
    # Remote code execution via public-facing app
    "CVE-2021-26855": "T1190",       # Exchange SSRF
    "CVE-2022-41040": "T1190",       # Exchange RCE
    "CVE-2017-0144": "T1190",       # EternalBlue / SMB
    "CVE-2017-0145": "T1190",
    "CVE-2019-0708": "T1190",       # BlueKeep RDP
    "CVE-2021-34527": "T1190",      # PrintNightmare
    "CVE-2021-44228": "T1190",      # Log4Shell
    "CVE-2022-22965": "T1190",       # Spring4Shell
    "CVE-2023-22515": "T1190",      # Atlassian Confluence RCE

    # Privilege escalation
    "CVE-2021-4034": "T1068",        # PwnKit (polkit)
    "CVE-2022-0847": "T1068",        # Dirty Pipe
    "CVE-2023-32629": "T1068",       # Ubuntu kernel privilege escalation

    # Credential access
    "CVE-2021-36934": "T1003.003",  # SAM database extraction (HiveNightmare)
    "CVE-2022-24521": "T1003.003",  # Windows SAM/LSASS exfil

    # Initial access via phishing / valid accounts
    "CVE-2022-30190": "T1566.001",  # Follina (msdt)
}

# Product/service → ATT&CK technique candidates (when version info is sparse)
PRODUCT_TO_TECHNIQUES: dict[str, list[tuple[str, str]]] = {
    "ssh": [("T1021.004", "SSH Remote Services"), ("T1550.001", "SSH Keys")],
    "mysql": [("T1021.001", "Remote Services: MySQL"), ("T1005", "Data from Local System")],
    "postgresql": [("T1021.001", "Remote Services: PostgreSQL"), ("T1005", "Data from Local System")],
    "redis": [("T1021.001", "Remote Services: Redis"), ("T1005", "Data from Local System")],
    "mongodb": [("T1021.001", "Remote Services: MongoDB"), ("T1005", "Data from Local System")],
    "elasticsearch": [("T1021.001", "Remote Services: Elasticsearch"), ("T1005", "Data from Local System")],
    "smb": [("T1021.002", "SMB/Windows Admin Shares")],
    "http": [("T1071.001", "Web Services"), ("T1190", "Exploit Public-Facing Application")],
    "apache": [("T1071.001", "Web Services"), ("T1190", "Exploit Public-Facing Application")],
    "nginx": [("T1071.001", "Web Services"), ("T1190", "Exploit Public-Facing Application")],
    "iis": [("T1071.001", "Web Services"), ("T1190", "Exploit Public-Facing Application")],
    "rdp": [("T1021.006", "Remote Services: RDP")],
    "vnc": [("T1021.006", "Remote Services: VNC")],
    "mssql": [("T1021.001", "Remote Services: MSSQL")],
    "oracle": [("T1021.001", "Remote Services: Oracle")],
    "nfs": [("T1021.004", "NFS")],
    "telnet": [("T1021.004", "Remote Services: Telnet")],
}


# ----------------------------------------------------------------------
# Data models
# ----------------------------------------------------------------------
@dataclass
class ExposedService:
    ip: str
    port: int
    protocol: str
    name: str
    product: str
    version: str
    finding_severity: str
    cve_ids: list[str]
    mapped_techniques: list[tuple[str, str, str]] = field(default_factory=list)  # (technique_id, name, confidence)


@dataclass
class GapEntry:
    technique_id: str
    technique_name: str
    confidence: str
    source: str  # "port" or "cve"
    exposed_on: list[str]  # IPs
    cve_ids: list[str]
    in_kev: bool
    epss_score: float | None
    cvss_score: float | None

    def priority(self) -> int:
        """Higher = more urgent. Based on CVSS, KEV status, EPSS."""
        score = 0
        if self.in_kev:
            score += 50
        if self.cvss_score is not None:
            score += self.cvss_score * 5
        if self.epss_score is not None:
            score += self.epss_score * 100
        if self.confidence == "high":
            score += 10
        return int(score)


@dataclass
class GapReport:
    scan_id: str
    scan_target: str
    total_exposed_services: int
    total_findings: int
    techniques_exposed: int
    techniques_covered: int
    gaps: list[GapEntry]
    coverage_rate: float
    generated_at: str


# ----------------------------------------------------------------------
# Core logic
# ----------------------------------------------------------------------
def load_sepulchryn_services(scan_db: Path) -> list[ExposedService]:
    """Read services and findings from a SepulchrynScan SQLite DB."""
    conn = sqlite3.connect(f"file:{scan_db}?mode=ro", uri=True)

    rows = conn.execute("""
        SELECT h.ip, s.port, s.protocol, s.name, s.product, s.version,
               f.severity, f.cve_id, f.in_kev, f.epss_score, f.cvss_v3_score
        FROM services s
        JOIN hosts h ON h.id = s.host_id
        LEFT JOIN findings f ON f.host_ip = h.ip AND (f.port = s.port OR f.port IS NULL)
        ORDER BY h.ip, s.port
    """).fetchall()

    services: dict[tuple[str, int, str], ExposedService] = {}
    cve_map: dict[tuple[str, int, str], list[str]] = {}

    for row in rows:
        ip, port, protocol, name, product, version, severity, cve_id, in_kev, epss, cvss = row
        key = (ip, port, protocol)
        if key not in services:
            services[key] = ExposedService(
                ip=ip, port=port, protocol=protocol,
                name=name or "", product=product or "", version=version or "",
                finding_severity=severity or "None",
                cve_ids=[],
            )
        if cve_id:
            cve_map.setdefault(key, []).append(cve_id)
            services[key].cve_ids = cve_map[key]

    return list(services.values())


def load_sepulchryn_findings(scan_db: Path) -> list[dict]:
    """Read all findings from SepulchrynScan DB."""
    conn = sqlite3.connect(f"file:{scan_db}?mode=ro", uri=True)
    rows = conn.execute("""
        SELECT f.severity, f.title, f.cve_id, f.in_kev, f.epss_score,
               f.cvss_v3_score, f.host_ip, f.port, f.protocol
        FROM findings f
        ORDER BY f.host_ip, f.port
    """).fetchall()
    return [
        {
            "severity": r[0], "title": r[1], "cve_id": r[2],
            "in_kev": bool(r[3]), "epss_score": r[4],
            "cvss_v3_score": r[5], "host_ip": r[6], "port": r[7], "protocol": r[8],
        }
        for r in rows
    ]


def load_detectsmith_coverage(coverage_json: Path) -> tuple[set[str], set[str]]:
    """Load Detectsmith's covered tactics and techniques from a coverage JSON."""
    with open(coverage_json) as f:
        report = json.load(f)

    data = report.get("data", report)

    covered_tactics = {t["tag"] for t in data.get("tactics", [])}
    covered_techniques = {t["tag"] for t in data.get("techniques", [])}
    return covered_tactics, covered_techniques


def map_service_to_techniques(service: ExposedService) -> list[tuple[str, str, str]]:
    """Map an exposed service to ATT&CK technique candidates."""
    techniques = []

    # Port-based mapping
    if service.port in PORT_TO_TECHNIQUES:
        for proto, entries in PORT_TO_TECHNIQUES[service.port].items():
            if service.protocol == proto or proto == "tcp":
                for tid, tname, conf in entries:
                    techniques.append((tid, tname, conf))

    # Product-based fallback
    service_key = service.name.lower() if service.name else service.product.lower()
    for product, candidates in PRODUCT_TO_TECHNIQUES.items():
        if product in service_key and product not in ("http", "https"):
            for tid, tname in candidates:
                if not any(t[0] == tid for t in techniques):
                    techniques.append((tid, tname, "medium"))

    return techniques


def map_cve_to_technique(cve_ids: list[str]) -> list[tuple[str, str]]:
    """Map CVE IDs to ATT&CK technique IDs via static mapping."""
    results = []
    for cve in cve_ids:
        if cve in CVE_TO_TECHNIQUES:
            results.append((CVE_TO_TECHNIQUES[cve], cve))
    return results


def build_gap_report(
    services: list[ExposedService],
    findings: list[dict],
    covered_tactics: set[str],
    covered_techniques: set[str],
) -> GapReport:
    """Cross-reference exposed services + CVEs against Detectsmith coverage."""
    gaps_by_technique: dict[str, GapEntry] = {}

    # Process services → technique gaps
    for svc in services:
        mapped = map_service_to_techniques(svc)
        svc.mapped_techniques = mapped

        for tid, tname, conf in mapped:
            key = f"port:{tid}"
            if key not in gaps_by_technique:
                gaps_by_technique[key] = GapEntry(
                    technique_id=tid,
                    technique_name=tname,
                    confidence=conf,
                    source="port",
                    exposed_on=[svc.ip],
                    cve_ids=svc.cve_ids,
                    in_kev=False,
                    epss_score=None,
                    cvss_score=None,
                )
            elif svc.ip not in gaps_by_technique[key].exposed_on:
                gaps_by_technique[key].exposed_on.append(svc.ip)

    # Enrich gaps with CVE data from findings
    cve_in_kev: dict[str, bool] = {}
    cve_epss: dict[str, float | None] = {}
    cve_cvss: dict[str, float | None] = {}

    for f in findings:
        cve = f.get("cve_id")
        if cve:
            if f.get("in_kev"):
                cve_in_kev[cve] = True
            if f.get("epss_score") is not None:
                cve_epss[cve] = f["epss_score"]
            if f.get("cvss_v3_score") is not None:
                cve_cvss[cve] = f["cvss_v3_score"]

    for gap in gaps_by_technique.values():
        for cve in gap.cve_ids:
            if cve_in_kev.get(cve):
                gap.in_kev = True
            if gap.epss_score is None and cve_epss.get(cve) is not None:
                gap.epss_score = cve_epss[cve]
            if gap.cvss_score is None and cve_cvss.get(cve) is not None:
                gap.cvss_score = cve_cvss[cve]

    # Filter to only gaps (techniques Detectsmith does NOT cover)
    uncovered_gaps = [
        g for g in gaps_by_technique.values()
        if g.technique_id not in covered_techniques and g.technique_id not in covered_tactics
    ]

    uncovered_gaps.sort(key=lambda g: g.priority(), reverse=True)

    exposed_technique_ids = {g.technique_id for g in gaps_by_technique.values()}
    total_techniques = len(exposed_technique_ids)
    covered_count = len(exposed_technique_ids) - len(uncovered_gaps)
    coverage_rate = (covered_count / total_techniques * 100) if total_techniques > 0 else 100.0

    return GapReport(
        scan_id="",
        scan_target="",
        total_exposed_services=len(services),
        total_findings=len(findings),
        techniques_exposed=total_techniques,
        techniques_covered=covered_count,
        gaps=uncovered_gaps,
        coverage_rate=coverage_rate,
        generated_at="",
    )


# ----------------------------------------------------------------------
# CLI commands
# ----------------------------------------------------------------------
def cmd_gap(scan_db: Path, coverage_json: Path | None) -> int:
    """Run gap analysis and print to stdout."""
    from datetime import datetime, timezone

    services = load_sepulchryn_services(scan_db)
    findings = load_sepulchryn_findings(scan_db)

    if not services:
        print("No services found in SepulchrynScan DB.", file=sys.stderr)
        return 1

    covered_tactics: set[str] = set()
    covered_techniques: set[str] = set()

    if coverage_json and coverage_json.exists():
        covered_tactics, covered_techniques = load_detectsmith_coverage(coverage_json)
    else:
        print("Note: --coverage not provided or not found. Reporting all exposed techniques (no coverage filter).", file=sys.stderr)

    report = build_gap_report(services, findings, covered_tactics, covered_techniques)
    report.scan_id = scan_db.stem
    report.scan_target = "n/a"
    report.generated_at = datetime.now(timezone.utc).isoformat()

    # Print summary
    print(f"\nDetection Gap Analysis")
    print(f"{'─' * 60}")
    print(f"  Exposed services:     {report.total_exposed_services}")
    print(f"  Total findings:       {report.total_findings}")
    print(f"  Techniques exposed:  {report.techniques_exposed}")
    print(f"  Techniques covered:  {report.techniques_covered}")
    print(f"  Coverage rate:        {report.coverage_rate:.0f}%")
    print(f"  Uncovered gaps:       {len(report.gaps)}")

    if report.gaps:
        print(f"\n{'─' * 60}")
        print(f"  PRIORITIZED DETECTION GAPS (uncovered exposures)")
        print(f"{'─' * 60}")
        for i, gap in enumerate(report.gaps[:20], 1):
            kev_marker = " [KEV]" if gap.in_kev else ""
            epss_str = f" EPSS:{gap.epss_score:.3f}" if gap.epss_score else ""
            cvss_str = f" CVSS:{gap.cvss_score:.1f}" if gap.cvss_score else ""
            print(f"  {i}. {gap.technique_id} — {gap.technique_name}")
            print(f"     Source: {gap.source}  |  Confidence: {gap.confidence}  |  Exposed on: {', '.join(gap.exposed_on)}{kev_marker}{epss_str}{cvss_str}")
            if gap.cve_ids:
                print(f"     CVEs: {', '.join(gap.cve_ids)}")

    return 0


def cmd_backlog(scan_db: Path, coverage_json: Path | None, output: Path | None) -> int:
    """Generate a backlog JSON report for further processing."""
    services = load_sepulchryn_services(scan_db)
    findings = load_sepulchryn_findings(scan_db)

    covered_tactics: set[str] = set()
    covered_techniques: set[str] = set()
    if coverage_json and coverage_json.exists():
        covered_tactics, covered_techniques = load_detectsmith_coverage(coverage_json)

    report = build_gap_report(services, findings, covered_tactics, covered_techniques)
    report.scan_id = scan_db.stem
    report.scan_target = "n/a"
    from datetime import datetime, timezone
    report.generated_at = datetime.now(timezone.utc).isoformat()

    output_data = {
        "schema_version": "1.0",
        "command": "gap_analyzer backlog",
        "scan_id": report.scan_id,
        "total_exposed_services": report.total_exposed_services,
        "techniques_exposed": report.techniques_exposed,
        "techniques_covered": report.techniques_covered,
        "coverage_rate": report.coverage_rate,
        "gaps": [
            {
                "technique_id": g.technique_id,
                "technique_name": g.technique_name,
                "confidence": g.confidence,
                "source": g.source,
                "exposed_on": g.exposed_on,
                "cve_ids": g.cve_ids,
                "in_kev": g.in_kev,
                "epss_score": g.epss_score,
                "cvss_score": g.cvss_score,
                "priority": g.priority(),
            }
            for g in report.gaps
        ],
        "generated_at": report.generated_at,
    }

    if output:
        output.write_text(json.dumps(output_data, indent=2))
        print(f"Backlog written to {output}")
    else:
        print(json.dumps(output_data, indent=2))

    return 0


# ----------------------------------------------------------------------
# CLI entrypoint
# ----------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detection gap analyzer — cross-reference SepulchrynScan with Detectsmith coverage.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    gap_parser = sub.add_parser("gap", help="Run gap analysis and print summary")
    gap_parser.add_argument("scan_db", type=Path, help="Path to SepulchrynScan SQLite DB (e.g. data/sepulchryn.db)")
    gap_parser.add_argument("--coverage", type=Path, default=None, help="Path to Detectsmith attack_coverage.json")

    backlog_parser = sub.add_parser("backlog", help="Generate backlog JSON")
    backlog_parser.add_argument("scan_db", type=Path)
    backlog_parser.add_argument("--coverage", type=Path, default=None)
    backlog_parser.add_argument("--output", type=Path, default=None, help="Output file (default: stdout)")

    args = parser.parse_args()

    if args.command == "gap":
        return cmd_gap(args.scan_db, args.coverage)
    elif args.command == "backlog":
        return cmd_backlog(args.scan_db, args.coverage, args.output)

    return 0


if __name__ == "__main__":
    sys.exit(main())