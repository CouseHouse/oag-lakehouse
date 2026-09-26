# oag-lakehouse

Ontology-Augmented Generation (OAG) reference implementation for federal vulnerability
and compliance management, built on an open source lakehouse and designed to transfer to
the Cloudera platform by configuration.

The full build-ready specification is in [SPEC.md](SPEC.md).

## What it does

- Ingests NVD, CISA KEV, EPSS, CWE, CAPEC, MITRE ATT&CK, NIST SP 800-53 Rev 5 (OSCAL), and
  CTID control mappings into Apache Iceberg with NiFi, Spark, and Airflow.
- Scans real open source container images with Syft and Grype as the assets of a fictional
  agency (the Bureau of Synthetic Records). All agency records are flagged synthetic.
- Aligns everything under one LinkML ontology that generates Iceberg DDL, SHACL shapes,
  Pydantic models, JSON schemas for guided decoding, and the PuppyGraph schema.
- Answers analyst questions with a LangGraph agent: grounding to CURIEs, minimal-coverage
  graph retrieval over PuppyGraph, guided decoding to typed claims on vLLM, and pySHACL
  validation of every claim. Says "unknown" when the sources cannot support an answer.
- Drafts OSCAL POA&M items, remediation tickets, and OpenVEX statements, validates them,
  and holds them for human approval before any write.

## Stack

| Layer | Local | Cloudera |
|---|---|---|
| Object storage | Apache Ozone (S3 gateway) | Ozone |
| Table format and catalog | Apache Iceberg, Apache Polaris (REST) | Iceberg, Cloudera REST catalog or Polaris |
| Processing | Spark 3.5, NiFi 2.x, Airflow 2.11 | Data Engineering, DataFlow |
| SQL | Trino | Trino or Impala |
| Graph | PuppyGraph Developer Edition (Apache AGE fallback) | PuppyGraph |
| Model serving | vLLM on RTX 5090 | Cloudera AI Inference (NIM) |
| Agent | LangGraph, LinkML, pySHACL, Langfuse | AI Workbench |

## Status

Specification drafted 2026-09-26. Phase 1 (Ozone, Polaris, Spark, one Iceberg table
written by Spark and read by Trino) has not started. See SPEC.md section 21 for milestones.
