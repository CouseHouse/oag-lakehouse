# oag-lakehouse: agent instructions

OAG (Ontology-Augmented Generation) reference implementation for federal vulnerability and
compliance management. Lakehouse on Iceberg, LinkML ontology, PuppyGraph, LangGraph agent,
vLLM. Must transfer to Cloudera by config only.

Human spec: SPEC.md (source of truth, long). AI references: docs/ai/ (compact, load per task).
Tracking: PLAN.md. Handoff: NEXT.md (read first in a new session). Read docs/ai/00-index.md to
pick the right reference file. Do not load SPEC.md whole; cite it by section when a detail is
missing from docs/ai/.

## Hard rules

1. No hosted model API as a dependency. `agent/adapters/hosted.py` is eval-only; any import
   of it outside `evals/` fails CI.
2. All infrastructure access goes through ports in `agent/ports/`. Adapters in
   `agent/adapters/` are the only modules that import vendor SDKs. Interfaces allowed: S3 API,
   Iceberg REST catalog, OpenAI-compatible API, openCypher over Bolt, NiFi JSON flows,
   Airflow Python DAGs, PySpark.
3. Nothing hardcoded. Endpoints, buckets, catalog URIs, model names come from
   `config/base.yaml` + `config/<env>.yaml` (`OAG_ENV=local|cloudera`). Secrets only via env
   vars named in YAML. Never write a secret to a file.
4. The model never has tools during generation and never writes Cypher or SQL. Queries are
   fixed templates in `agent/retrieval/queries/` with parameters.
5. No write to any sink without human approval. Requester and approver must differ.
6. Never assert a negative on an open-world predicate. Closure per predicate is in
   `generated/closure.yaml`. Absence on an open predicate is reported as `unknown`.
7. Every synthetic row carries `is_synthetic=true` and `synthetic_note`. The fictional agency
   is the Bureau of Synthetic Records (BSR). Never present BSR data as real.
8. Spark writes to `oag.*` go to a WAP branch `stage_<run_id>`; only `publish_branch`
   fast-forwards `main` after pySHACL passes.
9. Every claim the agent emits has at least one evidence ref that exists in the context bundle.
10. No em-dashes in any Markdown. Pre-commit enforces it.
11. Never read the live `.env` file or any `.env.*` variant other than `.env.example`, by any
    means: not Read, not Grep, not `cat`, `source`, `sed`, `head`, a `printenv` after loading
    it, or a script that loads it. `.env.example` lists the variable names; that is all Claude
    needs. Enforced by `.claude/settings.json` (Read deny rules plus a PreToolUse hook that
    blocks any Bash, Read, Grep, or Glob call whose text mentions such a file). If a task seems
    to need a value from the live file, stop and ask the user to run the command themselves.
    Side effect: a shell command whose text merely mentions the file name is also blocked, so
    edit documents that mention it with the Edit tool, not with a shell heredoc.

## Conventions

- Python 3.12, `uv`, ruff. Type hints everywhere. Pydantic models come from
  `generated/pydantic/`; never hand-write entity models.
- Spark 3.5 (parity with Cloudera Data Engineering), Airflow 2.11, Iceberg 1.11, NiFi 2.12.
- Table names `snake_case` singular; namespaces `raw`, `oag`, `doc`, `ops`. Ids are CURIEs in
  column `id`. Edge tables `oag.edge_<predicate>` with `src_id`, `dst_id`.
- Every table has `source_system`, `source_version`, `source_record_id`, `ingested_at`,
  `is_synthetic`, `synthetic_note`.
- `generated/` is committed and never hand-edited. Run `make generate` after any change under
  `schema/` and commit the diff.
- One Spark job per file in `jobs/spark/`, args `--run-id --env --ingest-date`. One DAG per
  file in `dags/`. Use `dags/lib/operators.spark_task()`; never instantiate
  `SparkSubmitOperator` directly.
- Prompts in `agent/generation/prompts/` carry a version string; changing one requires
  running the eval suite.
- Tests in `tests/`, pytest. Adapters get a fake in `tests/fakes/`.

## Commands

- `make lint` ruff + secret scan + em-dash check
- `make generate` LinkML to DDL, SHACL, Pydantic, JSON schema, PuppyGraph schema, OWL
- `make up-phase1` Compose profile `foundation` + smoke test
- `make up` all profiles
- `make eval` full competency question suite (needs the agent profile up)
- `python -m agent.config --env local` print resolved config, redacted

## Current state

See PLAN.md status table. Do not start work in a later phase than the current one.
