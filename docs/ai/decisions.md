# Decisions and open questions (SPEC.md section 25)

## Decisions (do not relitigate; add an ADR in docs/decisions/ to change)

D01 use case A: federal vulnerability and compliance | D02 LinkML as ontology source | D03 property graph (PuppyGraph) for retrieval, RDF transient for pySHACL only; no SPARQL, no OWL reasoning | D04 Spark 3.5, Airflow 2.11 for CDE parity | D05 one edge table per relationship | D06 Iceberg WAP branches + fast_forward | D07 closure per predicate | D08 KEV due date read from catalog (BOD 26-04) | D09 OpenVEX output (Grype consumes it) | D10 Ministral 3 14B FP8 primary, Mistral Small 3.2 24B FP8 fallback | D11 response_format on vLLM, guided_json on NIM, behind ModelPort | D12 NiFi lands files, Spark loads; PutIcebergRecord exercise only | D13 human approval for every action | D14 two ATT&CK bundles (16.1, 19.2) + bridge | D15 pgvector behind adapter, Iceberg is system of record for embeddings | D16 separate Postgres containers for pgvector and AGE | D17 Langfuse v4 | D18 no Kubernetes in Phase 1 | D19 graph read-only, writes to Iceberg | D20 six synthetic systems with deliberate gaps | D21 model has no tools during generation; fixed query templates | D22 Granite Guardian as optional guard model | D23 security mappings as documents, ATLAS loaded as STIX

## Assumptions (change in SPEC.md 25.1 if wrong)

VM 16 vCPU/96 GB/1 TB (Phase 1 may run in WSL2) | Spark 3.5 + Airflow 2.11 | Ministral 3 14B | 6 systems, 29 images, synthetic SLA | Langfuse v4 | action sinks = S3 + git | Ozone unsecured Phases 1 to 6 | BGE-M3 1024-dim | no Kafka | system is not high-impact AI under OMB M-25-21

## Open questions (phase)

Q01 PuppyGraph reads Iceberg on Ozone via S3 gateway (3) | Q02 PuppyGraph 1.12 schema JSON keys for Polaris + S3-compatible (3) | Q03 PuppyGraph snapshot/branch pinning (4) | Q04 Cloudera REST catalog branch ops (8) | Q05 NIM guided decoding shape; Mistral NIM availability (8) | Q06 Ozone S3G as Langfuse blob store (4) | Q07 FP8 vs AWQ on 5090 under WSL2 (4) | Q08 Spark 3.5 image tag; Iceberg runtime Scala variant (1) | Q09 Airflow 2.11 image tag (2) | Q10 CISA advisories listing endpoint (5) | Q11 OSCAL baseline profile paths (3) | Q12 Agent Studio + LangGraph (8) | Q13 Cloudera services in FedRAMP boundary (8) | Q14 Syft/Grype inside CDF NiFi (8) | Q15 NVD API key requested (before 2) | Q16 CPRT deep link format (2) | Q17 OpenVEX version accepted by Grype (5) | Q18 OSCAL POA&M milestone placement (5) | Q19 ATLAS technique IDs for threat model (3) | Q20 high-impact AI classification (8) | Q21 AIBOM generator vs CycloneDX 1.7 (6)

## Known upstream facts that shaped the design

BOD 26-04 superseded BOD 22-01 (2026-06-10); KEV dueDate per entry, new forensicTriage field | NVD risk-based enrichment since 2026-04-15: most new CVEs lack CPE/CWE/CVSS | CTID mappings target ATT&CK 16.1; ATT&CK is 19.2 | CAPEC dormant since 2023 (v3.9) | EPSS v5 (model v2026.06.15), CSV at epss.empiricalsecurity.com | OSCAL catalog file is Rev 5.2.0, oscal-version 1.2.2; POA&M schema OSCAL 1.2.3 | Grype --vex accepts OpenVEX only | vLLM 0.30 removed guided_* params | CDE 1.26 = Spark 3.5.4, Airflow 2.11.2 | Trino Ranger plugin built in since 466 | Cloudera for Government FedRAMP Moderate (2025-05-07)
