# AGENTS.md — SepulchrynScan

Guide for AI agents working in this repository. Read this before making changes.

## Essential Commands

```bash
# Run tests (101 tests expected)
pytest -v

# Format and lint (run before committing)
black .
ruff check --fix .

# CLI entrypoint (always via python -m)
python -m sepulchrynscan.cli scan <target>
python -m sepulchrynscan.cli report <scan_id>
python -m sepulchrynscan.cli list
python -m sepulchrynscan.cli diff <scan_id_a> <scan_id_b>
python -m sepulchrynscan.cli demo
```

## Architecture & Data Flow

```
CLI (cli.py)
  └─ scan command
       1. allowlist check → target_allowed()
       2. discovery.run() → Nmap subprocess → list[Host] (services carry raw CVE IDs)
       3. cve.enrich() → cache/NVD lookup → KEV/EPSS/Exploit-DB enrichment → list[Finding]
       4. checks.run_all() → HTTP headers, TLS, exposed services, admin panels → list[Finding]
       5. All persisted to SQLite via db.py
  └─ report command
       db.get_scan() → report.render() → Jinja2 + Plotly → technical.html + executive.html
```

**Key principle:** `models.py` is the inter-module spine. Every module consumes and emits Pydantic models. Never change model shapes without updating all consumers in the same change.

## Module Responsibilities

| Module | Role | Contract |
|--------|------|----------|
| `models.py` | Pydantic v2 data contracts | `Severity`, `CVE`, `Service`, `Host`, `Finding`, `Scan` |
| `config.py` | Paths, URLs, constants, tunables | Single source of all config values |
| `db.py` | SQLite persistence, raw SQL, no ORM | All functions take `sqlite3.Connection` |
| `discovery.py` | Nmap wrapper, CVE ID extraction | `run(target) -> list[Host]` |
| `cve.py` | NVD API 2.0 + cache orchestration | `enrich(conn, hosts, offline) -> list[Finding]` |
| `kev.py` | CISA KEV catalog + EPSS scoring | `enrich_cves(cves) -> None` (mutates in-place) |
| `exploit.py` | Exploit-DB CSV lookup | `enrich_cves(cves) -> None` (mutates in-place) |
| `checks.py` | HTTP headers, TLS, exposed services, admin panels | `run_all(hosts) -> list[Finding]` |
| `risk.py` | Pure risk score functions | `risk_score(findings) -> float` |
| `diff.py` | Scan comparison | `diff_scans(scan_a, scan_b) -> DiffResult` |
| `report.py` | Jinja2 + Plotly HTML rendering | `render(scan, out_dir) -> (tech_path, exec_path)` |
| `cli.py` | argparse entrypoint, allowlist enforcement | 5 subcommands: scan, report, demo, list, diff |

## Critical Rules (Load-Bearing Decisions)

1. **No ORM.** `db.py` uses raw SQL only. Never introduce SQLAlchemy.
2. **No plugin loaders.** Checks are hardcoded functions in `checks.py`. To add a check, write a function and call it from `run_all`.
3. **No native PDF libraries.** Reports are HTML + Plotly JSON via CDN. Browser print-to-PDF. Never pull in WeasyPrint or ReportLab.
4. **Detect only.** No exploitation, no hardcoded credentials, no `shell=True`.
5. **Allowlist gate.** Every network-bound code path must go through `target_allowed()` in `cli.py`.
6. **Regenerate over patch.** If a file has drifted, rewrite it whole rather than surgical edits — the flat structure and small files are designed for this.

## Testing Patterns

- Tests use **in-memory SQLite** (`db.connect(db_path=Path(":memory:"))`) — no file artifacts.
- Network I/O is mocked with `unittest.mock.patch` and `requests_mock`.
- Nmap is mocked via `unittest.mock.patch("sepulchrynscan.discovery.nmap.PortScanner")`.
- TLS checks use `unittest.mock.patch` for `socket` and `ssl`; test certs are generated with `cryptography`.
- KEV/EPSS/exploit enrichment are patched out in `test_cve.py` with `patch.object(kev, "enrich_cves")` and `patch.object(exploit, "enrich_cves")`.
- The exploit module's `_load_exploitdb_index` is `@lru_cache` decorated — call `exploit._load_exploitdb_index.cache_clear()` in tests when swapping fixture files.
- Tests live in `tests/` with one file per module: `test_<module>.py`.

## Non-Obvious Gotchas

- **CVE pipeline is two-stage:** `discovery.py` extracts CVE IDs via regex from vulners NSE output. `cve.py` scores them from NVD. Risk scoring uses NVD CVSS exclusively, never vulners' potentially stale scores.
- **CVSS fallback chain:** `cve.py:fetch_cve_from_nvd` tries v3.1 → v3.0 → v2 in that order.
- **Rate limiting:** NVD API sleeps `config.NVD_RATE_LIMIT_SLEEP_SEC` (6s) after every successful call. Tests must `patch("sepulchrynscan.cve.time.sleep")` to avoid slowness.
- **Offline mode:** Controlled by `--offline` flag or `SEPULCHRYN_OFFLINE=1` env var. Skips NVD fetches for uncached CVEs, skips Exploit-DB network fetch. Cached data still used.
- **Schema migration:** `db.py:_migrate_schema()` adds columns that may be missing from older DBs via `ALTER TABLE`. New columns should be added here with `NOT NULL DEFAULT` for backward compatibility.
- **NVD API key:** Optional env var `NVD_API_KEY`. Raises rate limit from 5/30s to 50/30s.
- **Demo uses custom Nmap args:** `_cmd_demo` overrides nmap args to `-sV -p 3000 --script vulners` because Juice Shop's port 3000 is outside `--top-ports 1000`.
- **JSON fields in SQLite:** `references_json`, `cve_ids`, `exploit_refs_json` are stored as JSON text. Always `json.dumps()` on write, `json.loads()` on read, with `or "[]"` fallback for null safety.
- **`config.ROOT`** resolves to the repo root (one level up from `sepulchrynscan/`). `DATA_DIR`, `REPORTS_DIR`, `DB_PATH`, `ALLOWLIST_PATH` are all derived from it.

## Enrichment Chain Order

In `cve.enrich()`, enrichment happens in this order after CVE resolution:
1. `kev.enrich_cves()` — sets `in_kev` and `epss_score` on CVE objects
2. `exploit.enrich_cves()` — sets `exploit_refs` on CVE objects

Both mutate CVE objects in-place. Both degrade gracefully on network failure (warnings, not crashes).

## File Size Budget

Each source file is under ~300 lines. If a file grows beyond that, split it. The flat `sepulchrynscan/` package structure is intentional — no subpackages.

## Key Reference Documents

- `PROJECT_SPEC.md` — Single source of truth for architecture, requirements, and scope
- `HANDOFF.md` — Current state, what worked, what was rejected, contributor rules
- `EXPLOIT_INTEGRATION_PLAN.md` — Design doc for the Exploit-DB feature (now implemented, kept for reference)
- `INSTALL.md` — Platform-specific install instructions

## Dependencies

Runtime: `pydantic>=2.5`, `python-nmap>=0.7.1`, `requests>=2.31`, `cryptography>=42.0`, `jinja2>=3.1`, `plotly>=5.18`

Dev: `pytest>=7.4`, `requests-mock>=1.11`, `black>=24.1`, `ruff>=0.2`

No `setup.py` or `pyproject.toml` — the package is run via `python -m sepulchrynscan.cli`.
