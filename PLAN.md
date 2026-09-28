# Phase plan

Tracking document for the build described in [SPEC.md](SPEC.md). Check items off as they
land. Each phase has a goal, tasks, and exit criteria copied from SPEC.md section 21. Do not
start a phase until the previous phase's exit criteria are all checked. Security actions
(A01 to A15) come from SPEC.md section 16.14. Open questions (Qnn) are in section 25.3.

Effort assumes evenings and weekends, about 10 to 12 hours per week. A "day" is about 4 hours.

## Status

| Field | Value |
|---|---|
| Current phase | 0 |
| Started | 2026-09-26 |
| Last updated | 2026-09-26 |
| Next milestone | Phase 0 exit: `make lint` passes and the config loader prints a redacted config |
| Blockers | None |

Progress log (newest first):

- 2026-09-26: D24 recorded: whole local stack in WSL2 on the workstation (64 GB, i9-14900K, RTX 5090). SPEC.md 0.2.1.
- 2026-09-26: NVD API key received (Q15 closed). `.env.example` created.
- 2026-09-26: SPEC.md 0.2.0 committed. Plan created. Nothing built yet.

## Before Phase 0

- [x] Request an NVD API key (https://nvd.nist.gov/developers/request-an-api-key). Received 2026-09-26. Stored in local `.env` as `NVD_API_KEY`, never committed.
- [ ] Read SPEC.md section 25.1 and confirm or change the nine assumptions.
- [x] Decide where Phase 1 runs. Decided 2026-09-26 (D24): the whole stack runs in WSL2 on the workstation; no Proxmox VM.
- [ ] Decide whether to pull A04, A05, A13 (image signing, AI BOM, red team pass) forward from Phase 6 to Phase 4.

## Phase 0: repository skeleton (about 2 days)

Goal: the directory tree, config loading, and quality gates exist before any service runs.

- [ ] Create the directory tree from SPEC.md section 20 with a README stub in each top-level directory
- [ ] `pyproject.toml` with `uv`; extras `agent`, `jobs`, `dags`, `evals`, `tools`
- [ ] `config/base.yaml`, `config/local.yaml`, `config/cloudera.yaml` with every key named in section 8.4, values pointing at environment variables for secrets
- [ ] `agent/config.py`: merge base and env YAML, resolve env vars, validate required keys, print redacted
- [x] `.env.example` listing every secret and endpoint name with no values (created 2026-09-26; extend as services land)
- [ ] `.pre-commit-config.yaml`: ruff, secret scan, em-dash check for `*.md`
- [ ] `Makefile` targets: `lint`, `generate`, `up-phase1`, `up`, `eval`, `replay` (later targets can be stubs that fail with a message)
- [ ] `tests/` with one test for the config loader
- [ ] GitHub Actions workflow running `make lint` and `pytest`
- [ ] CI check that docs/ai/ files changed whenever SPEC.md changed in the same commit (warning only)

Exit criteria:

- [ ] `make lint` passes
- [ ] `python -m agent.config --env local` prints a redacted config
- [ ] CI is green on `main`

## Phase 1: foundation (about 5 days)

Goal: Ozone, Polaris, and Spark running, with one Iceberg table written by Spark and read by
Trino. Nothing else starts until this exits.

- [ ] Resolve Q08: confirm the `apache/spark:3.5.x-python3` tag and the Iceberg 1.11.0 runtime for Spark 3.5 (Scala 2.12 or 2.13)
- [ ] `infra/local/docker-compose.yml` with the `foundation` profile: Ozone (SCM, OM, DataNode, S3 gateway, Recon), Polaris 1.7, Spark master and worker, Trino 483
- [ ] `infra/local/.env` with pinned image tags
- [ ] Ozone: single DataNode, `ozone.replication=1`, S3 gateway on 9878, bucket `oag-warehouse` created by an init script
- [ ] Polaris bootstrap script: create the catalog with `--storage-type s3 --endpoint http://ozone-s3g:9878 --no-sts --path-style-access`, a principal, and a principal role with grants on namespace `oag`
- [ ] `infra/local/spark/spark-defaults.conf`: REST catalog config (`type=rest`, `uri`, `warehouse`, `credential`, `scope=PRINCIPAL_ROLE:ALL`), S3 keys, no vended credentials
- [ ] Spark jar download script: Iceberg runtime, Hadoop AWS, `spark-xml`
- [ ] `jobs/spark/lib/session.py`: Spark session factory reading `config/<env>.yaml`
- [ ] `jobs/spark/lib/wap.py`: helpers for `spark.wap.branch`, `fast_forward`, `rollback_to_snapshot`
- [ ] Trino catalog file for the Polaris REST catalog with `vended-credentials-enabled=false`
- [ ] `tools/smoke_phase1.py`: create `oag.smoke_test` with `write.wap.enabled`, write 1,000 rows on branch `stage_smoke`, fast-forward `main`, read the count through Trino, print snapshot ids
- [ ] `docs/runbooks/phase1.md`: how to bring the stack up from a clean host, ports, known issues

Exit criteria:

- [ ] `make up-phase1` from a clean host brings up the `foundation` profile with all health checks passing
- [ ] `tools/smoke_phase1.py` succeeds: Spark writes on a branch, fast-forwards main, Trino returns 1000
- [ ] Ozone Recon shows the data files
- [ ] Runbook written and followed once from scratch

## Phase 2: ontology and reference data (about 12 days)

Goal: LinkML schema v0.1 with generators; every reference source loaded through NiFi and Spark,
scheduled by Airflow, published through WAP with pySHACL validation.

Ontology:

- [ ] `schema/prefixes.yaml` and the seven modules in section 6.5
- [ ] Enums and closure annotations from section 6.3 and 6.7
- [ ] `tools/linkml_iceberg/`: custom `gen-iceberg-ddl` generator (types, partitions, `write.wap.enabled`, `oag.classification` property, A02)
- [ ] `gen-shacl` plus `schema/shacl/extra.ttl` merged into `generated/shacl/`
- [ ] `gen-pydantic`, `gen-json-schema` (top class `ClaimSet` and extraction templates), `gen-owl`, `gen-doc`
- [ ] `generated/closure.yaml` export
- [ ] `make generate` and a CI check that `generated/` is up to date

Ingest (NiFi 2.12, Compose profile `ingest`):

- [ ] NiFi and Airflow 2.11 services added to Compose; resolve Q09 (Airflow image tag)
- [ ] Parameter contexts `local` and `cloudera` (sensitive values excluded from export)
- [ ] Flow `cisa_kev` (JSON to S3; second branch with `PutIcebergRecord` as the learning exercise)
- [ ] Flow `first_epss_daily`
- [ ] Flow `mitre_cwe`, `mitre_capec`, `mitre_attack_stix` (both v16.1 and v19.2 bundles)
- [ ] Flow `nist_oscal_800_53`, `ctid_mappings`
- [ ] Flow `nvd_cve_incremental` with stateful pagination, `ControlRate`, retry, and error landing
- [ ] Flow `nvd_cpe_dictionary`
- [ ] Every flow exported to `ingest/nifi/flows/<name>.json`

Spark loaders:

- [ ] `load_kev`, `load_epss`, `load_cwe_capec`, `load_attack` (with `ops.attack_version_bridge`), `load_oscal_controls`, `load_ctid_mappings`, `load_cpe_products`
- [ ] `load_raw_nvd` and `normalize_vulnerability` (CVSS handling, `cpe_config_status`, `cwe_status`, `exploitation_status`)
- [ ] `validate_branch`: referential checks, RDF serialization of changed rows, pySHACL, per-source delta thresholds (A06), results to `ops.validation_result`
- [ ] `publish_branch` with dependency ordering
- [ ] `ops.pipeline_run` written by every job

Airflow:

- [ ] `dags/lib/operators.py` with the `spark_task()` factory and `dags/lib/nifi.py`
- [ ] DAGs `reference_weekly`, `nvd_daily`, `kev_6h`, `epss_daily`, `maintenance_weekly`
- [ ] Pools `reference_tables`, `vuln_tables`, `epss`, `maintenance`

Exit criteria:

- [ ] All reference tables populated on `main`; row counts within 1 percent of the source counts in SPEC.md section 7
- [ ] A seeded bad row (for example a `not_implemented` control implementation with no assessment date) is blocked by `validate_branch`
- [ ] Airflow shows green runs for 3 consecutive days
- [ ] `ops.attack_version_bridge` built from the two ATT&CK bundles

## Phase 3: assets and graph (about 10 days)

Goal: the synthetic agency, SBOM scans, findings, alignment, PuppyGraph and AGE, and every
template query. First demoable milestone: CQ06 answered as a graph query.

- [ ] `config/synthetic/images.yaml` with 29 images and pinned digests; `config/synthetic/bsr.yaml`
- [ ] Flow `sbom_scan` (Syft and Grype in the NiFi container) or the Airflow `DockerOperator` alternative
- [ ] `load_sbom_findings` with closed-finding logic and `sbom_status` (one image deliberately missing an SBOM)
- [ ] `generate_synthetic_agency` (systems, actors, control implementations from OSCAL baseline profiles; resolve Q11); every row flagged synthetic; BSR-SYS-05 mostly `unknown`
- [ ] `align_components` deterministic part (Syft CPEs, Grype match details)
- [ ] `assets_weekly` DAG
- [ ] Compose profile `graph`: pgvector, AGE, PuppyGraph 1.12
- [ ] Resolve Q01 and Q02: PuppyGraph reading Iceberg on Ozone through Polaris; schema JSON keys
- [ ] `tools/linkml_puppygraph/`: custom `gen-puppygraph` generator, local and Cloudera variants
- [ ] `puppygraph_refresh_schema` Airflow task
- [ ] `agent/adapters/bolt_graph.py` and `age_graph.py`; `export_graph_to_age` job
- [ ] Template queries for every CQ in `agent/retrieval/queries/`, with `.age.cypher` variants where needed
- [ ] Adapter parity test in `tests/`
- [ ] A12: load ATLAS STIX alongside ATT&CK; resolve Q19
- [ ] `docs/runbooks/phase3.md`

Exit criteria:

- [ ] Every T1, T2, T3 template query returns correct rows on PuppyGraph and AGE for the seeded data
- [ ] CQ06 and CQ09 shown in the PuppyGraph UI
- [ ] `ops.attack_version_bridge` resolves at least 95 percent of CTID technique ids to live v19.2 techniques
- [ ] First demo rehearsed: CQ06 in the PuppyGraph UI plus `make generate` showing one schema producing five artifacts

## Phase 4: agent and serving (about 15 days)

Goal: vLLM on the 5090, grounding, retrieval, guided generation, critic, Langfuse, and the
agent API. Second demoable milestone: CQ08 and CQ15 end to end with citations and an "unknown".

Serving:

- [ ] vLLM 0.30 launch script for Ministral 3 14B FP8 with the flags in SPEC.md section 19.2; resolve Q07 with a 30 minute FP8 versus AWQ benchmark
- [ ] A03: `safetensors` only, no `trust_remote_code`, read-only model cache, pinned revision with recorded hash
- [ ] Embeddings endpoint (BGE-M3 on vLLM or in-process); dimension in config
- [ ] vLLM as a Compose service on the shared network (D24); `model.base_url` is `http://vllm:8000/v1` in containers; raise `.wslconfig` to 48 GB and 16 processors first
- [ ] `evals/structured_output_conformance.py` passing against vLLM

Documents and retrieval:

- [ ] `chunk_documents`, `ground_chunks`, `embed_chunks`, `refresh_vector_index`
- [ ] pgvector table with HNSW index and GIN index on `mentioned_curies`
- [ ] Grounder: regex pass, lexicon pass (`generated/lexicon/`), model pass with candidate-only selection
- [ ] Intent classifier over CQ templates
- [ ] Factual blocks, absence blocks, greedy minimal cover (`agent/retrieval/cover.py`), chunk scoping, reserve list

Generation and critic:

- [ ] Versioned prompts in `agent/generation/prompts/`; registered in Langfuse
- [ ] `OpenAICompatModel` adapter with `response_format` json_schema; `NimModel` subclass with `guided_json` (untested until Phase 8)
- [ ] Claims to RDF, pySHACL runner, violation mapping, critic loop limit of 2, partial answers
- [ ] A01: imperative text check on `answer_summary`
- [ ] A09: documented rule that prompts carry no security-relevant content

Agent and API:

- [ ] LangGraph graph with the nodes and edges in SPEC.md section 14
- [ ] FastAPI `/ask`, `/health`, `/ingest/landed`; bearer tokens mapped to synthetic actors
- [ ] A11: per-actor rate limits and daily token quotas; Airflow pool shared with extraction jobs
- [ ] A15: "report this answer" event
- [ ] Compose profile `agent`: Langfuse v4 stack (resolve Q06: Ozone as the blob store), agent API
- [ ] A02: Langfuse mask function for secret patterns
- [ ] `tools/replay.py`

Evaluation:

- [ ] `evals/cases/` for every T1 to T4 competency question (T4 with three variants each)
- [ ] `evals/harness.py`, `evals/report.py`, `evals/thresholds.yaml`
- [ ] Baselines `naive_rag.py` and `graph_only.py`
- [ ] `eval_nightly` DAG

Exit criteria:

- [ ] All T1 to T4 cases pass thresholds: T1 at 95 percent, T2 at 85 percent, T3 at 85 percent, T4 unknown correctness at 100 percent with zero closed-world false negatives after the critic
- [ ] Langfuse shows a full trace for CQ08 with per-node spans and cost
- [ ] `tools/replay.py` reproduces an answer from an audit event
- [ ] Second demo rehearsed: CQ08 and CQ15 end to end

## Phase 5: actions and extraction loop (about 12 days)

Goal: POA&M, ticket, and VEX drafting with approval; extraction candidates from advisories;
the review queue. Third demoable milestone: the 10 minute demo runs end to end.

Actions:

- [ ] `agent/actions/`: drafting for `poam_create`, `ticket_create`, `vex_create`
- [ ] OSCAL POA&M JSON Schema validation with the vendored schema; resolve Q18 (milestone placement)
- [ ] SHACL shapes `POAMItemShape`, `VexStatementShape` in `schema/shacl/actions.ttl`
- [ ] `authorize` with action roles; A08 requester and approver must differ
- [ ] Approval UI with evidence, rule trace, SHACL result; A07 HTML escaping
- [ ] `S3ActionSink` writing to Ozone and committing to `actions/`; `ops.action_request`, `ops.action_record`
- [ ] Rollback as an approved action
- [ ] OpenVEX output fed to `grype --vex` in the next `sbom_scan`; resolve Q17
- [ ] A14: kill switch flags and `docs/runbooks/incident.md`
- [ ] T5 eval cases asserting artifact validity and that nothing was written

Extraction loop:

- [ ] Flow `advisory_text` with a NiFi Python processor for HTML extraction; resolve Q10
- [ ] Extraction templates in `schema/extract/` (affected product, exploitation, weakness)
- [ ] `extract_candidates` (project extractor; OntoGPT comparison in `evals/` through a `ModelPort`-backed duck-typed client, see SPEC.md 11.2 finding)
- [ ] Alignment rules (exact id, lexical, embedding, thresholds)
- [ ] `validate_candidates` on a WAP branch with the candidate shapes
- [ ] Review queue in the approval UI; approve, reject, defer
- [ ] `documents_daily` DAG with `ExternalTaskSensor` on `nvd_daily`
- [ ] `evals/extraction/labels.yaml` (100 hand-labeled chunks) and the precision metric
- [ ] `align_components` LLM pass for unresolved rows into the candidate table

Exit criteria:

- [ ] CQ20 to CQ22 produce valid artifacts held for approval; approving writes to S3 and git and the finding shows a POA&M on the next publish
- [ ] The next scan consumes the VEX file
- [ ] Extraction precision on the labeled sample at or above 80 percent for auto-published candidates
- [ ] The 10 minute demo (SPEC.md section 23.1) runs end to end within time

## Phase 6: hardening and CI (about 6 days)

Goal: ontology regression CI, security items, documentation, demo rehearsal.

- [ ] `ontology_ci` DAG and the matching GitHub Actions workflow (lint, generate, diff, DDL on a scratch branch, eval suite, regression gate)
- [ ] Seeded injection cases in `evals/cases/injection/`
- [ ] A04: cosign-signed project images, scanned with Syft and Grype in CI; KEV findings fail the build
- [ ] A05: AI BOM (`make aibom`, resolve Q21) and `docs/security/model-card.md`
- [ ] A13: weekly red team pass with garak and promptfoo; results in `docs/evals/`
- [ ] `docs/security/`: threat model page, `atlas-mapping.yaml`, 800-53 self-mapping
- [ ] Runbooks for every phase; `docs/decisions/` ADRs for D01 to D23
- [ ] Both demo scripts rehearsed and timed; slides source in `docs/demo/`

Exit criteria:

- [ ] A deliberate schema regression (removing a closure declaration) fails CI
- [ ] Injection cases pass; the red team report shows no successful goal hijack or leakage probe
- [ ] Project images are signed and have no KEV findings
- [ ] Both demos run within time

## Phase 7: optional governance and Kubernetes (about 8 days)

- [ ] Ranger 2.9 in Compose with the Trino plugin (profile `governance`)
- [ ] Ranger tests A through C from SPEC.md section 16.4; results in `docs/decisions/ranger-bypass.md`
- [ ] A10: role-based predicates in `agent/retrieval/policy.py` applied to graph and vector queries if bypass is confirmed
- [ ] Helm charts in `infra/k8s/` for agent API, approval UI, Langfuse, PuppyGraph
- [ ] Agent tier running on k3s against the Compose data plane

Exit criteria:

- [ ] Ranger tests recorded with pass or fail
- [ ] Agent API and Langfuse running on k3s

## Phase 8: Cloudera validation (when access exists, about 5 days on site)

- [ ] Run the twelve-item checklist in SPEC.md section 22.2
- [ ] Fill in `config/cloudera.yaml`
- [ ] Ranger test D
- [ ] Resolve Q04, Q05, Q12, Q13, Q14, Q20
- [ ] Record any code change outside `config/` and `infra/cloudera/` in SPEC.md section 25 (target: none)

Exit criteria:

- [ ] Every checklist item has a recorded result

## Open questions tracker

Copied from SPEC.md section 25.3 so they can be checked off here. Update SPEC.md when resolved.

- [ ] Q01 PuppyGraph reads Iceberg on Ozone via S3 gateway (Phase 3)
- [ ] Q02 PuppyGraph 1.12 schema JSON keys for Polaris and S3-compatible storage (Phase 3)
- [ ] Q03 PuppyGraph snapshot or branch pinning (Phase 4)
- [ ] Q04 Cloudera REST catalog branch operations (Phase 8)
- [ ] Q05 NIM guided decoding parameter shape and Mistral NIM availability (Phase 8)
- [ ] Q06 Ozone S3 gateway as the Langfuse blob store (Phase 4)
- [ ] Q07 FP8 versus AWQ throughput on the 5090 under WSL2 (Phase 4)
- [ ] Q08 Spark 3.5 image tag and Iceberg runtime Scala variant (Phase 1)
- [ ] Q09 Airflow 2.11 image tag (Phase 2)
- [ ] Q10 CISA advisories listing endpoint (Phase 5)
- [ ] Q11 OSCAL baseline profile paths (Phase 3)
- [ ] Q12 Agent Studio and LangGraph compatibility (Phase 8)
- [ ] Q13 Cloudera services inside the FedRAMP boundary (Phase 8)
- [ ] Q14 Syft and Grype inside CDF NiFi (Phase 8)
- [x] Q15 NVD API key requested (before Phase 2). Received 2026-09-26.
- [ ] Q16 CPRT deep link format for 800-53 controls (Phase 2)
- [ ] Q17 OpenVEX version accepted by Grype (Phase 5)
- [ ] Q18 OSCAL POA&M milestone placement (Phase 5)
- [ ] Q19 ATLAS technique IDs for the threat model (Phase 3)
- [ ] Q20 High-impact AI classification (Phase 8)
- [ ] Q21 AIBOM generator output against CycloneDX 1.7 (Phase 6)
