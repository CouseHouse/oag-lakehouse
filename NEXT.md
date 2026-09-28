# NEXT.md: handoff for the next session

Read this first after clearing context. Then CLAUDE.md (loaded automatically), then PLAN.md
for the current phase, then the one or two docs/ai/ files the task needs. Do not load SPEC.md
whole.

Last updated: 2026-09-28, end of the second session.

## State of the repository

Repository: https://github.com/CouseHouse/oag-lakehouse (private). Local: /home/butters/projects/oag_project. Branch main, clean, pushed.

Phase 0 (repository skeleton) exited on 2026-09-28 with CI green: directory tree, `pyproject.toml` with uv, config loader, Makefile, pre-commit, lint tools, tests, GitHub Actions. No service runs yet. Phase 1 has not started. Before Phase 1 the owner must raise `.wslconfig` and enable Docker Desktop WSL integration (item 12 below).

| File | Purpose | Status |
|---|---|---|
| SPEC.md | The full specification, 26 sections plus appendices, about 39,000 words. Source of truth. Version 0.2.0. | Complete. Section 25.1 lists nine assumptions the user has not yet confirmed. |
| PLAN.md | Phase tracking with checkboxes and exit criteria. | Two items checked (NVD key, .env.example). Everything else open. |
| CLAUDE.md | Hard rules, conventions, commands for AI sessions. Eleven rules. | Complete. |
| docs/ai/*.md | Compact, task-scoped extracts of the spec (about 8,000 tokens total). | Complete. Keep in sync with SPEC.md in the same commit. |
| docs/study/ | Study guide for the source article and primary sources, Anki CSV (60 cards), interview crosswalk, reading log. | Complete. |
| docs/decks/gamma-prompts.md | Six Gamma.app deck prompts with card outlines. | Complete. |
| README.md | Project overview, OAG source summary, security summary, stack table, links. | Complete. |
| .env.example | Every secret and endpoint variable name, no values. | Complete. A test fails if a config YAML references a variable not listed here. |
| pyproject.toml, Makefile, .pre-commit-config.yaml, .github/workflows/ci.yml | Toolchain and gates. `uv sync --all-extras` then `make lint` and `make test`. | Live. `make generate`, `up-phase1`, `up`, `eval`, `replay` are stubs that exit 1 with a message. |
| config/*.yaml, agent/config.py | Base plus env overlay, `${VAR}` expansion from the environment, Pydantic validation of required keys, redacted print. `OAG_CONFIG_DIR` overrides the directory. | Live. Keys follow SPEC.md 8.4. |
| tools/check_emdash.py, tools/check_hosted_import.py | Hard rules 10 and 1 as lint checks; run by `make lint`, pre-commit, and tests. | Live. |
| docs/decisions/ | ADR index plus ADR-0024 (WSL2 host) and ADR-0025 (project extractor, not OntoGPT). ADRs for D01 to D23 are a Phase 6 item. | Started. |
| .claude/settings.json and .claude/hooks/block-env-read.sh | Read deny rules and a PreToolUse hook. | Live and tested. |
| Memory (outside repo) | ~/.claude/projects/-home-butters-projects-oag-project/memory/ holds a user profile and a project summary. | Current. |

## Things a fresh session will not know from the files

1. **The env-read hook blocks on the file name anywhere in a Bash command's text**, not only on actual reads. A shell heredoc that writes a document mentioning the file will be denied. Use the Edit or Write tool for such documents and keep the literal name out of commit messages. This is deliberate. Do not loosen the hook.
2. **Plain `git push` hung for several minutes** because the global git config points at the Windows Git Credential Manager, which waits for a GUI prompt under WSL2. Fixed at the repo level: `.git/config` resets the credential helper list and uses `!gh auth git-credential`. If a push hangs again, check `git config --local --get-all credential.helper` and kill any stray `git-remote-https` process.
3. **The source article is member-only.** Only its title, date, section headings, and the two-sentence OAG definition were verified. Everything the spec attributes to the article about components, practices, criteria, and risks comes from the summary in the prompt that produced SPEC.md. The study guide says so. If the user reads the full article and finds differences, update SPEC.md section 1 and the study guide.
4. **BOD 22-01 was superseded by BOD 26-04 on 2026-06-10.** The spec and all references use 26-04. KEV due dates are now per entry and are read from the catalog, never computed.
5. **NVD moved to risk-based enrichment on 2026-04-15.** Most new CVEs lack CPE, CWE, and CVSS. This is why the open-world design and the extraction loop exist. Do not design anything that assumes NVD enrichment is complete.
6. **CTID mappings target ATT&CK 16.1; ATT&CK is at 19.2.** The design loads both STIX bundles and bridges technique ids. This is a Phase 2 and 3 task, not optional.
7. **vLLM 0.30 removed the `guided_*` request parameters.** Use `response_format` with `json_schema`. NIM on Cloudera still uses `guided_json`. The difference lives in one adapter (`NimModel`).
8. **Spark 3.5 and Airflow 2.11 are deliberate**, for parity with Cloudera Data Engineering 1.26 (Spark 3.4/3.5, Airflow 2.11.2). Do not upgrade to Spark 4 or Airflow 3 without an ADR.
9. **The primary model is Ministral 3 14B Instruct (official FP8).** Fallback Mistral Small 3.2 24B FP8 for batch only. A community report showed poor FP8 throughput on the RTX 5090 under WSL2; benchmark FP8 against AWQ before committing (Q07).
10. **Palantir's own docs reject the phrase "semantic layer"** for its Ontology. When describing this project, say "data model plus permitted actions" rather than "semantic layer".
11. **All verification dates are 2026-09-26.** Versions in SPEC.md section 19 and docs/ai/infra.md will drift; re-check tags at the start of each phase (PLAN.md has Q08 and Q09 for the two most likely to bite).
12. **Decided (D24, 2026-09-26): everything runs in WSL2 on the workstation.** Measured: i9-14900K, 64 GB, RTX 5090 32 GB, Docker Desktop installed but WSL integration for the Ubuntu distro was not yet enabled, `.wslconfig` capped at 16 GB and 8 processors. The user must raise `.wslconfig` (24 GB for Phases 1 to 3, 48 GB from Phase 4) and enable Docker Desktop WSL integration before Phase 1. Claude must not edit `.wslconfig` or run `wsl --shutdown`: both kill the session.

## Open decisions for the user

None. All four pre-Phase 0 decisions were answered on 2026-09-28: assumptions 2 to 9 confirmed, D24 for the host, A04/A05/A13 stay in Phase 6, Claude scaffolds Phase 0 and the owner reviews.

## Next steps, in order

1. Phase 1: Compose `foundation` profile (Ozone 2.2.1, Polaris 1.7.0, Spark 3.5.x, Trino 483), Polaris catalog on Ozone with `--no-sts` and path-style access, `tools/smoke_phase1.py`. Resolve Q08 first (Spark image tag and Iceberg runtime Scala variant). Exit criteria in PLAN.md.
2. Update PLAN.md status table and progress log at the end of every session. Check off items as they land.

## Conventions for the next session

- No em-dashes anywhere. `grep -c $'\xe2\x80\x94' <file>` must return 0 before commit.
- Commit messages end with the attribution lines the harness supplies.
- When SPEC.md changes, change the matching docs/ai/ file in the same commit and bump the SPEC.md change log.
- New open questions get a Q-number in SPEC.md section 25.3, PLAN.md, and docs/ai/decisions.md.
- New decisions get a D-number in SPEC.md section 25.2 and docs/ai/decisions.md, and an ADR in docs/decisions/ once that directory exists (Phase 0).
