# oag-lakehouse

Ontology-Augmented Generation (OAG) reference implementation for federal vulnerability
and compliance management, built on an open source lakehouse and designed to transfer to
the Cloudera platform by configuration.

The full build-ready specification is in [SPEC.md](SPEC.md). Build progress is tracked in [PLAN.md](PLAN.md).

For AI-assisted development, [CLAUDE.md](CLAUDE.md) holds the hard rules and conventions and
[docs/ai/](docs/ai/00-index.md) holds compact, task-scoped extracts of the spec (about 8,000
tokens in total versus about 55,000 for SPEC.md). SPEC.md remains the source of truth; a change
to the spec updates the matching file in docs/ai/ in the same commit.

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

## What OAG means here

This project builds toward the definition of Ontology-Augmented Generation in Ling Huang's
article "From RAG to OAG" (Medium, September 2026). The summary below is what we assume
from that source and where each idea lands in this repository.

**Definition.** OAG uses an ontology as the normative schema layer for knowledge. The
ontology predefines the domain's classes, the relationships between them, and mandatory
constraints (SHACL, OWL). Both retrieval and generation operate inside that framework.
The LLM translates intent and cites evidence. It does not create facts.

**Lineage.** OAG sits at the top of a progression: naive RAG, advanced RAG with rerank,
modular RAG, GraphRAG, agentic RAG with planning and critique, then OAG. It keeps chunk
retrieval, reranking, and orchestration from the earlier stages, but the ontology reshapes
what a retrieval unit is and what a valid output is.

**Core components** and where they live here:

| Component from the article | What it means | Where in this project |
|---|---|---|
| Constraint-based retrieval | Retrieve a task-relevant ontology subgraph with minimal coverage (OG-RAG: factual blocks, greedy minimal set cover over query entities) | `agent/retrieval/` (SPEC.md section 13.2) |
| Grounding | Link text to ontology concepts as CURIEs (oaklib-style) | `agent/grounding/` (SPEC.md section 13.1) |
| Constrained generation | Output governed by SHACL and OWL, produced with guided decoding (JSON schema or grammar) | `agent/generation/` and `agent/critic/` (SPEC.md sections 13.3 and 13.4) |
| Agent orchestration | The ontology acts as the semantic layer, or operating system API, for the agent | `agent/graph.py` (SPEC.md section 14) |
| Extract, align, validate | A closed loop that improves the knowledge base from new documents | `agent/extract/` and the `documents_daily` DAG (SPEC.md section 11) |
| Structured fact output | Answers expressed as typed claims tied to ontology IDs, each with evidence | The `ClaimSet` schema generated from LinkML (SPEC.md section 13.3, Appendix D) |

**The operational pipeline** (the article's Palantir-style loop): intent understanding,
grounded retrieval of entities, rule validation, permission and constraint checks, action
execution with write-back, and pre-write SHACL validation with an audit trail. This is
`agent/actions/` (SPEC.md section 15). Every action is held for human approval.

**Three practices the article names, and how deep we go:**

| Practice | Representative project | Depth here |
|---|---|---|
| Grounded retrieval | OG-RAG | Full |
| Schema-driven extraction | OntoGPT / SPIRES with LinkML templates | Bounded: three templates over advisory text, output to a candidate table with human review |
| Operational actions | Palantir ontology as an operating system | Bounded: POA&M, ticket, and VEX drafts written to object storage and git, never to a live GRC system |

**When OAG is worth it.** The article gives five conditions, used in SPEC.md section 2 as
the scoring rubric for choosing the use case:

1. High decision frequency.
2. Cross-system business object alignment (the same entity lives in several systems).
3. Explicit, formalizable rules.
4. Results must be accountable (an audit trail is required).
5. Action results can be fed back into the system.

The article warns that scenarios with high business value but unreliable source data and
implicit rules are the most commonly misidentified OAG candidates. If no consensus on
structure exists, an ontology freezes chaos into a schema. Federal vulnerability and
compliance management passes all five conditions. The rejected candidates did not.

**Four risks the article raises, and the mitigation in this design:**

| Risk | Mitigation |
|---|---|
| Ontology supply chain: building an ontology is expensive expert labor | Reuse published standards (CVE, CWE, CAPEC, ATT&CK, CPE, OSCAL, CycloneDX, SSVC) for most classes; competency questions gate every addition; LinkML generates everything downstream from one source |
| Ontology evolution and drift: an outdated ontology plus a live LLM confidently outputs an obsolete worldview | Source versions on every row and claim; an ATT&CK version bridge; ontology regression CI that reruns the full eval suite on every schema change |
| Closed-world versus open-world: mainstream OAG assumes missing means no, but many domains need missing means unknown | Closure declared per predicate in the ontology; absence blocks in retrieval; a forced epistemic status on every claim; a SHACL shape that rejects negated claims on open predicates; five competency questions where "unknown" is the only correct answer |
| Vendor lock-in as logic accumulates on the ontology | Ontology in LinkML; identifiers from public standards; interfaces limited to S3, Iceberg REST, the OpenAI API, openCypher, NiFi JSON, Airflow Python, and PySpark; the graph is derived and read-only, so the lakehouse tables remain the system of record |

## Security and governance

SPEC.md section 16 maps the design to named frameworks with cited versions: the OWASP Top 10
for LLM Applications (2025, with 2026 IDs noted), the OWASP Top 10 for Agentic Applications
(December 2025), MITRE ATLAS (loaded as STIX next to ATT&CK), the system's own NIST SP 800-53
Rev 5 controls, data and model governance (classification labels, retention, model card,
CycloneDX AI BOM, signed and scanned project images), separation of duties, a kill switch,
an incident runbook, weekly automated red teaming, and alignment with OMB M-25-21, NIST AI
RMF and the Generative AI Profile, CISA secure AI deployment guidance, and FedRAMP 20x.
The model never has tools during generation and never writes queries; every action is held
for a human approver who is not the requester.

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
