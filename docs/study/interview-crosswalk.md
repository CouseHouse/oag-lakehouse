# Interview crosswalk

Likely questions for a Federal Civilian Senior Solutions Engineer role at Cloudera Government
Solutions, and the artifact in this repository that answers each. Rehearse the answer, then
point at the artifact.

| Likely question | Two-sentence answer | Artifact |
|---|---|---|
| Tell me about Iceberg branching and when you would use it. | Write-audit-publish: every load writes to a branch, validation runs on the branch, and only a passing branch is fast-forwarded to main. Consumers never see unvalidated data and rollback is a snapshot operation. | SPEC.md 9.6; `jobs/spark/lib/wap.py` |
| How do you keep a Spark job idempotent? | Key raw loads on source record id and version and MERGE INTO; partition overwrite for daily time series; deterministic seeds for generated data. Re-running with the same inputs yields the same branch content. | SPEC.md 10.2 |
| What is hard about NiFi at scale? | State and back-pressure: paginating an API with rate limits means stateful pagination, ControlRate, and retry with landing of failures for provenance. Parameter contexts separate environments. | `ingest/nifi/flows/nvd_cve_incremental.json` |
| How do you move Airflow DAGs between environments? | Keep DAGs as plain Python, isolate the one environment-specific choice (the Spark operator) behind a factory, and use pools and connections for the rest. | `dags/lib/operators.py` |
| Why Iceberg REST catalog instead of Hive Metastore? | It is the interface Polaris, Cloudera, Trino, Spark, and PuppyGraph all speak, so the catalog becomes a config value. Credential vending is the one behavior that differs by backend. | SPEC.md 8.4, 19.4 |
| How would you secure an LLM application in an agency boundary? | Treat every ingested text as untrusted, give the model no tools during generation, constrain output to a schema, require evidence on every claim, and hold every action for a human. Map it to OWASP and 800-53 so an assessor can follow. | SPEC.md 16; `docs/ai/actions-security.md` |
| Does a graph engine reading Iceberg directly bypass Ranger? | Expected yes for row-level policies enforced in Trino, unless the catalog or storage enforces them. I wrote a four-case test and the design response is a restrictive catalog principal plus role predicates in retrieval. | SPEC.md 16.4 |
| When would you not recommend a knowledge graph or ontology? | When the rules are implicit, the data is unreliable and unowned, or nobody will maintain the schema. The article's five criteria are my checklist. | SPEC.md 23.3 |
| How do you evaluate a RAG system honestly? | Competency questions tiered by difficulty including ones where unknown is the only right answer, baselines (naive RAG, graph-only), and a CI gate that fails on regression when the schema changes. | SPEC.md 17; `evals/` |
| What is the Cloudera Anywhere Cloud story in one minute? | Iceberg tables, an open catalog, and engines that read them in place, including PuppyGraph for graph queries with zero ETL. This project is that architecture built on open source, and it moves by configuration. | `docs/decks/gamma-prompts.md` deck 5 |
| What is your experience with vLLM and structured outputs? | Served Ministral 3 14B FP8 on a single RTX 5090 with JSON schema guided decoding through XGrammar, and wrote the adapter that maps the same request to NIM's guided_json on Cloudera AI Inference. | SPEC.md 13.3, 19.2 |
| How do you handle FIPS and FedRAMP questions? | Say what is verified and what is not. Cloudera for Government holds FedRAMP Moderate; FIPS mode exists on premises with validated modules; every other component is marked verify with the question that resolves it. | SPEC.md 16.5, 16.13 |
| Explain open-world versus closed-world to a CISO. | Not in the KEV list means not listed, because the list is complete. Not in the KEV list does not mean not exploited, because exploitation is not fully known. The system knows which is which per fact. | SPEC.md 6.7 |
| What did you learn building this? | Fill in from `reading-log.md` as you go. | `docs/study/reading-log.md` |
