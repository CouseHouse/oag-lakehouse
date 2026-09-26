# Gamma.app prompts for the OAG lakehouse decks

Six decks, one per audience. Each has a generation prompt (paste into Gamma's "Generate"
box) and a card outline (paste into "Paste in text" with "one card per section" selected, or
paste under the prompt as context). Text amount: choose "Detailed" for the technical decks and
"Brief" for the executive deck. Image style suggestion is included in each prompt. Export as
PowerPoint from Gamma when done.

House rules to paste at the top of every prompt:

> Style rules: plain declarative sentences, no marketing language, no em-dashes, no emoji.
> Name specific tools and standards. Every synthetic data item must be labeled "synthetic".
> Use tables for mappings and matrices. Dark navy and slate palette with one accent color.
> Diagrams should be simple boxes and arrows. Speaker notes on every card.

Deck list:

| Deck | Audience | Cards | Use |
|---|---|---|---|
| 1. OAG in 10 minutes | Agency mixed audience | 12 | Companion to the 10 minute demo |
| 2. What OAG is | Anyone learning the concept | 14 | Study aid and interview warm-up |
| 3. Technical deep dive | Applied AI and data engineering | 22 | Companion to the 30 minute deep dive |
| 4. Security and governance | ISSO, CISO, assessors | 14 | Standalone security review |
| 5. Cloudera transfer story | Cloudera pre-sales, customers | 10 | Platform migration pitch |
| 6. Build plan | Yourself, hiring managers | 10 | Project status and roadmap |

---

## Deck 1: OAG in 10 minutes (agency audience)

Generation prompt:

> Create a 12-card presentation titled "Answering the KEV question with evidence" for a
> federal civilian agency audience of ISSOs, system owners, and an authorizing official. Half
> the audience is non-technical. The topic is an Ontology-Augmented Generation (OAG) system
> for vulnerability and compliance management built on an open source lakehouse. Tone: calm,
> factual, no hype. Each card has one idea, a short headline, at most four bullets, and
> speaker notes of 60 to 100 words. Use an image style of clean flat illustrations in navy and
> slate. Include the style rules below. Follow the card outline exactly.

Card outline:

1. **The question every agency gets asked.** "Are we compliant with the CISA KEV directive today?" Today the answer is a spreadsheet rebuilt by hand from the scanner, the KEV list, and a control matrix. Two analysts get two answers. Neither can show their work.
2. **Why the answer is hard.** The same vulnerability lives in eight places: NVD, CISA KEV, EPSS, CWE, CAPEC, MITRE ATT&CK, NIST SP 800-53, and your own inventory. Each uses different identifiers. NVD no longer enriches most new CVEs. SBOMs are incomplete.
3. **What we built.** A system that ingests those sources into one lakehouse, aligns them under one ontology, and answers questions with cited evidence. It says "unknown" when the sources cannot support an answer. It drafts POA&M entries and holds them for human approval.
4. **One question, many systems.** Demo card: "Which systems have KEV findings past due with no POA&M?" Show the answer table: system, finding, CVE, due date, days overdue, evidence link per row. The system walked a graph, it did not search documents.
5. **The "unknown" moment.** "Is CVE-2024-99999 exploited in the wild?" The system answers: not in KEV catalog 2026.09.25, EPSS 0.02, exploitation status unknown. A chatbot would say "no". That is the answer that gets an agency in trouble.
6. **From finding to control.** Demo card: for Log4Shell on one system, the techniques it enables, the 800-53 controls that mitigate them, and the implementation status per control, including two marked unknown because nobody has assessed them.
7. **The action, held for a human.** A POA&M draft in OSCAL format: milestones, due date from KEV, the ISSO as responsible party, related controls, a green validation check. Nothing is written until the ISSO approves. The approver cannot be the requester.
8. **The audit trail.** Every answer records the data snapshot, ontology version, model version, and prompt version. Any answer can be replayed. "What changed since last week?" is a query, not a meeting.
9. **What the system never does.** Writes without approval. Asserts "not exploited" or "not affected" from absence of evidence. Presents synthetic data as real. Executes anything the model wrote.
10. **Why this transfers.** Built on open source at home: Ozone, Iceberg, Polaris, Spark, NiFi, Airflow, Trino, PuppyGraph, vLLM. Every interface is one Cloudera exposes. Moving to Cloudera is a configuration change, not a rewrite.
11. **When not to do this.** Use OAG when decisions are frequent, entities cross systems, rules are written down, answers must survive audit, and actions feed back. Do not use it where rules are implicit or data is unreliable; an ontology would freeze the chaos into a schema.
12. **Next steps.** Pilot on one FISMA system with real scan data inside the agency boundary. Validate on Cloudera with the 12-item checklist. Contact and repository link.

---

## Deck 2: What OAG is (concept primer)

Generation prompt:

> Create a 14-card educational presentation titled "From RAG to OAG" explaining
> Ontology-Augmented Generation, based on Ling Huang's September 2026 article of the same
> name. Audience: engineers and architects new to knowledge graphs. Tone: teaching, precise,
> no hype. Define every term the first time it appears. Use one diagram per concept card, simple
> boxes and arrows. Speaker notes of 80 to 120 words per card. Include the style rules below.
> Follow the card outline exactly.

Card outline:

1. **Title.** From RAG to OAG: using an ontology as the schema for retrieval and generation.
2. **The lineage.** Naive RAG, advanced RAG with reranking, modular RAG, GraphRAG, agentic RAG with planning and critique, then OAG. Each stage keeps what came before. OAG changes what a retrieval unit is and what a valid output is.
3. **Definition.** An ontology is a formal description of a domain's classes, relationships, and constraints. OAG uses it as the normative schema layer: retrieval and generation both operate inside it. The LLM translates intent and cites evidence. It does not create facts.
4. **TBox and ABox.** TBox: the classes and relationships (the schema). ABox: the individual facts (the data). In a lakehouse, TBox is a LinkML schema and ABox is Iceberg tables.
5. **Constraint-based retrieval.** Retrieve a task-relevant ontology subgraph with minimal coverage: group facts into blocks, then pick the smallest set of blocks that covers every entity in the question. This is the OG-RAG approach (hypergraph, greedy minimal set cover).
6. **Grounding.** Map spans of text to ontology identifiers (CURIEs like cve:CVE-2024-3094). Three passes: pattern, lexicon, model. The model may only choose from candidates, never invent an identifier.
7. **Constrained generation.** The model's output is forced to a schema at decoding time (guided decoding with a JSON schema). Enums cannot be violated. Then SHACL validates the output against the ontology's constraints.
8. **Structured fact output.** Answers are typed claims: subject, predicate, object, epistemic status, confidence, evidence. Every claim cites a record or a text span. A summary is derived from claims, never the other way round.
9. **Agent orchestration.** The ontology is the semantic layer, or operating system API, for the agent. The operational pipeline: intent to structured query, grounded retrieval, rule validation, permission checks, action with write-back, pre-write validation, audit trail.
10. **Extract, align, validate.** New documents produce candidate facts under the schema (OntoGPT and SPIRES style), candidates are aligned to existing entities, validated with SHACL, and reviewed by a human before publishing. This is how the knowledge base improves.
11. **Three practices, not one.** OG-RAG (grounded retrieval), OntoGPT/SPIRES (schema-driven extraction), Palantir (operational actions). Do not conflate them. A project should state which it implements and how deep.
12. **When OAG is worth it.** Five criteria: high decision frequency, cross-system entity alignment, explicit formalizable rules, accountability required, action results feed back. The trap: high value plus implicit rules plus unreliable data.
13. **Four risks.** Ontology supply chain (expensive expert labor). Ontology drift (obsolete worldview stated confidently). Closed-world versus open-world mismatch (missing means no, or missing means unknown). Vendor lock-in as logic accumulates.
14. **Closed world versus open world.** Closed: anything not stated is false, correct for complete lists like the KEV catalog. Open: anything not stated is unknown, correct for exploitation status and control implementation. A system must declare which applies per predicate.

---

## Deck 3: Technical deep dive (applied AI team)

Generation prompt:

> Create a 22-card technical presentation titled "OAG reference implementation: architecture
> and design" for an applied AI and data engineering audience. Tone: precise engineering
> documentation, no marketing. Use tables for mappings and one architecture diagram card with
> boxes and arrows. Name specific tools and versions. Speaker notes of 80 to 120 words per card.
> Include the style rules below. Follow the card outline exactly.

Card outline:

1. **Title and scope.** Federal vulnerability and compliance management. Open source at home, transfers to Cloudera by configuration. Three practices implemented: OG-RAG retrieval (full), SPIRES extraction (bounded), Palantir-style actions (bounded).
2. **Use case selection.** Scoring matrix summary: vulnerability and compliance 71 of 75, healthcare program integrity 53, grants compliance 49. Winner has published ontologies for most classes and explicit rules. Healthcare fell into the implicit-rules trap.
3. **Logical architecture.** Diagram: sources (NVD, KEV, EPSS, CWE, CAPEC, ATT&CK, OSCAL, CTID, advisories, container images) to NiFi to Ozone S3 to Iceberg via Polaris; Spark and Airflow in the middle; PuppyGraph, pgvector, Trino, vLLM serving; LangGraph agent on top; Langfuse across.
4. **Component table.** Local versus Cloudera: Ozone/Ozone, Iceberg/Iceberg, Polaris/Cloudera REST catalog, Spark 3.5/Data Engineering, NiFi 2.12/DataFlow, Airflow 2.11/Airflow in CDE, Trino 483/Trino or Impala, PuppyGraph/PuppyGraph, pgvector/platform vector store, vLLM/AI Inference with NIM, LangGraph/AI Workbench, Langfuse/Langfuse.
5. **Ports and adapters.** Every dependency behind a Python Protocol: storage, catalog, graph, vector, model, embedding, SQL, trace, action sink. Adapters selected by config. No module outside adapters imports a vendor SDK. Hosted model adapter is eval-only.
6. **The ontology as contract.** LinkML source in seven modules. One `make generate` produces Iceberg DDL, SHACL, Pydantic, JSON schemas for guided decoding, PuppyGraph schema, OWL, docs. Two custom generators: Iceberg DDL and PuppyGraph.
7. **Reused standards.** Table: CVE (NVD API 2.0), KEV, EPSS v5, CWE 4.20, CAPEC 3.9, ATT&CK 19.2 STIX plus 16.1 for the CTID mappings, CPE 2.3, SP 800-53 Rev 5.2.0 OSCAL, OSCAL POA&M 1.2.3, CTID mappings, CycloneDX 1.7, OpenVEX, SSVC. 14 of 22 classes come from standards.
8. **Classes and relationships.** The 22 classes and the key chain: Vulnerability to Weakness to AttackPattern to Technique to Control to ControlImplementation to InformationSystem. Findings link images, components, and vulnerabilities.
9. **Closure per predicate.** Table: closed (KEV membership per catalog version, POA&M existence, finding existence per scan) versus open (exploitation status, affected products, control implementation, control-to-technique mappings). Coverage shapes are Info severity and never infer absence.
10. **Iceberg data model.** Namespaces raw, oag, doc, ops. One table per class, one per edge. Provenance columns everywhere. Partitioning choices. Embeddings stored in Iceberg; pgvector is a derived index.
11. **Write-audit-publish.** Spark writes to branch stage_<run_id>. Validate: Spark SQL checks, RDF of changed rows, pySHACL, delta thresholds. Publish: fast_forward per table, entities before edges. Rollback: rollback_to_snapshot. Consumers read main only.
12. **NiFi flows.** Ten flows. The instructive one: NVD incremental with stateful pagination, ControlRate, retry, error landing. KEV flow includes a PutIcebergRecord branch through the REST catalog. Advisory flow uses a Python processor.
13. **Spark jobs and Airflow DAGs.** 24 jobs, 9 DAGs, pools serialize writers per table group. Only four jobs call the model, all through one client. The spark_task factory swaps SparkSubmitOperator for CdeRunJobOperator on Cloudera.
14. **Graph layer.** PuppyGraph reads Iceberg through Polaris with zero ETL. One table per label. Apache AGE fallback copies data. Portability rules: OPTIONAL MATCH instead of EXISTS subqueries, date math in Python, no CALL procedures, graph is read-only.
15. **Grounding.** Regex, lexicon (longest match, oaklib for CWE and CAPEC), model pass choosing only from candidates. Failure: clarify, never guess. Actions never tolerate ambiguity.
16. **Retrieval.** Intent classifier over 23 query templates. Factual blocks with provenance. Greedy minimal set cover with tier-specific caps. Chunks scoped by mentioned_curies. Absence blocks for null open predicates.
17. **Generation.** ClaimSet schema: claims with epistemic status and evidence, unknowns with reasons, summary of at most 120 words. vLLM response_format json_schema with xgrammar. NIM uses guided_json; the difference lives in one adapter. Temperature 0.
18. **Critic.** Claims to RDF, pySHACL. Shapes: evidence required, evidence ref must exist in bundle, no negated claim on open predicate, value must match block, rule trace required for rule questions. Two regenerations, then partial answer with dropped claims listed.
19. **Agent graph.** LangGraph nodes: start_trace, ground, classify_intent, check_requirements, authorize, retrieve, generate, critic, render_answer, draft_action, validate_action, queue_for_approval, write_audit. Limits: 90 seconds, 24,000 input tokens, no tools during generation.
20. **Property graph versus RDF.** PuppyGraph: zero-ETL openCypher over the lakehouse, no SPARQL, no OWL reasoning, no native SHACL. RDF: standard validation, needs a copy. Choice: property graph for retrieval, RDF only transiently for SHACL over claims and changed rows.
21. **Evaluation.** Baselines: naive RAG, graph-only, OAG without critic. Metrics: accuracy per tier, entity linking, SHACL violation rate, citation faithfulness, unknown correctness, closed-world false negatives (gated at zero), latency, cost. Ontology CI reruns everything on every schema change.
22. **Open problems.** ATT&CK drift against CTID mappings, NVD enrichment policy, PuppyGraph snapshot pinning, Ranger bypass by direct Iceberg readers, extraction precision.

---

## Deck 4: Security and governance

Generation prompt:

> Create a 14-card presentation titled "Security and governance of an LLM system inside a
> federal boundary" for ISSOs, a CISO, and third-party assessors. Tone: assessor-facing, direct,
> every claim mapped to a control or framework by name. Use tables. Speaker notes of 80 to 120
> words. Include the style rules below. Follow the card outline exactly.

Card outline:

1. **Title.** Security and governance for the OAG reference implementation. Frameworks cited with versions and dates as of September 2026.
2. **Threat model.** Six threats: prompt injection through ingested text, knowledge base poisoning, output and audit manipulation, model supply chain, credential leakage, excessive agency. One line of mitigation each.
3. **Untrusted input by design.** CVE descriptions, advisories, and SBOM metadata are attacker-influenced. Chunks are labeled by trust level, delimited, and declared data. The model has no tools during generation. Output is schema-constrained. Every claim needs evidence that exists in the context.
4. **OWASP Top 10 for LLM Applications.** Table of all ten items (2025 edition, 2026 IDs noted) with the control in this design and the gap closed: unbounded consumption (per-actor quotas), output handling (escaping), supply chain (signed images, AI BOM).
5. **OWASP Top 10 for Agentic Applications.** Table of the ten items. Several are eliminated by construction: no tools, no code execution, fixed query templates, single agent. Remaining items: goal hijack, privilege abuse, memory poisoning, cascading failures, human trust exploitation, each with its control.
6. **MITRE ATLAS.** The AI-specific counterpart to ATT&CK, loaded as STIX into the same graph. Threat model rows mapped to ATLAS technique IDs. The system's own threat model lives next to the customer's.
7. **The system's own 800-53 controls.** Table: AC-3, AC-5, AC-6, AU-2, AU-3, AU-9, AU-10, AU-12, CM-2, CM-3, CM-8, IA-2, IA-5, RA-5, SA-11, SC-8, SI-3, SI-4, SI-7, SI-10, SR-3, SR-4, PL-8, each with the implementation. The system that tracks controls states its own.
8. **Audit trail.** Every answer reproducible from Iceberg snapshot ids, ontology version, model revision hash, prompt version, rule version. Three independent records: the audit table, Langfuse, git. A replay tool re-runs any answer.
9. **Human oversight and separation of duties.** No write without approval. Requester and approver differ. The approval screen shows evidence, rule trace, and validation result. Monthly review of approval rates. A "report this answer" button.
10. **Data governance.** Classification label on every table (public, synthetic, derived, operational). Retention per namespace. Lineage through provenance columns locally and Atlas on Cloudera. PII columns annotated for masking. Traces contain no secrets.
11. **Model and supply chain governance.** Pinned model revisions with hashes, safetensors only, no remote code, model card, CycloneDX AI BOM, cosign-signed project images scanned by the project's own Syft and Grype pipeline with KEV findings failing the build, weekly automated red teaming.
12. **Kill switch and incident response.** Three runtime flags: actions, retrieval, auto-publish. Runbook for suspected injection, poisoning, credential exposure, and model compromise. Rollback by snapshot.
13. **The Ranger question.** Does a graph engine reading Iceberg directly bypass row-level policies enforced at Trino? Expected: yes. Test plan with four cases and the design response: restrictive catalog principal plus role predicates in retrieval.
14. **Federal AI governance.** OMB M-25-21 minimum practices (met whether or not the system is classified high-impact), NIST AI RMF and the Generative AI Profile mapped to sections, SP 800-218A, CISA secure AI deployment guidance, FedRAMP Moderate for Cloudera for Government, FedRAMP 20x AI change notification, FIPS 140 items marked verify.

---

## Deck 5: Cloudera transfer story

Generation prompt:

> Create a 10-card presentation titled "Built at home, runs on Cloudera: the OAG lakehouse
> transfer story" for a Cloudera pre-sales audience and prospective agency customers. Tone:
> confident but precise; every transfer claim is either verified or marked "to verify". Use
> tables. Speaker notes of 60 to 100 words. Include the style rules below. Follow the card
> outline exactly.

Card outline:

1. **Title.** One codebase, two environments, configuration is the only difference.
2. **The interface contract.** Seven interfaces the code depends on: S3 API, Iceberg REST catalog, OpenAI-compatible inference API, openCypher over Bolt, NiFi JSON flow definitions, Airflow Python DAGs, PySpark. Nothing else.
3. **Component mapping.** Table from the technical deck, with a third column "what changes": endpoint, auth, catalog URI, submission operator, parameter context, schema variant, model name.
4. **Cloudera Anywhere Cloud.** Announced August 19, 2026: Iceberg, Polaris catalog interoperability, Spark, Kafka, Trino. PuppyGraph quoted as a partner querying Iceberg as a knowledge graph with zero ETL. This project is that architecture.
5. **Cloudera AI Inference.** OpenAI-compatible API on KServe and NVIDIA NIM. The model adapter switches from vLLM's response_format to NIM's guided_json. The Mistral partnership (September 10, 2026) aligns with the Ministral 3 model choice.
6. **Cloudera Data Engineering.** Ships Spark 3.5.4 and Airflow 2.11.2. The local build pins the same majors. DAGs swap one operator through a factory function. Jobs are unchanged.
7. **Cloudera DataFlow.** NiFi flow definitions import as JSON. Parameter contexts hold the environment differences. Sensitive parameters are re-entered, never exported.
8. **Governance in SDX.** Ranger policies, Atlas lineage, the Cloudera Iceberg REST catalog with Ranger and Knox. The open question on direct Iceberg readers and the test plan.
9. **The 12-item checklist.** Storage, catalog config, branch operations, Spark job, NiFi flow, Airflow DAG, SQL, graph, structured output conformance, agent deployment, Ranger tests, config diff. Each item is a command and a recorded result.
10. **What still needs verifying.** Catalog branch operations, NIM guided decoding parameter shape, Mistral NIM availability, PuppyGraph authentication through Knox, FedRAMP boundary for each service, FIPS status per component.

---

## Deck 6: Build plan and status

Generation prompt:

> Create a 10-card presentation titled "OAG lakehouse: build plan" for a project status
> review. Tone: plain project management. Use a timeline card and checklist tables. Speaker
> notes of 50 to 80 words. Include the style rules below. Follow the card outline exactly.

Card outline:

1. **Title and goals.** Four requirements: open source at home, transfers to Cloudera by config, federal civilian use case, hands-on Spark, NiFi, and Airflow.
2. **Timeline.** Phases 0 to 8 with effort in working days: 2, 5, 12, 10, 15, 12, 6, 8 optional, 5 on site. About 62 days through Phase 6 at evenings and weekends, roughly five to six months.
3. **Phase 1: foundation.** Ozone, Polaris, Spark, Trino only. Exit: Spark writes one Iceberg table on a branch, fast-forwards main, Trino reads it. Nothing else starts first.
4. **Phase 2: ontology and reference data.** LinkML schema and generators, ten NiFi flows, Spark loaders, first four DAGs, WAP validation with pySHACL.
5. **Phase 3: assets and graph.** Synthetic agency of six systems and 29 real container images, SBOM scans, PuppyGraph and AGE, all query templates. First demo: the overdue KEV question in the graph UI.
6. **Phase 4: agent and serving.** vLLM on the RTX 5090, grounding, retrieval, guided generation, critic, Langfuse, eval harness with baselines. Second demo: two questions end to end, one answered "unknown".
7. **Phase 5: actions and extraction.** POA&M, ticket, VEX drafting with approval; advisory extraction with review queue. Third demo: the full 10 minute script.
8. **Phase 6: hardening.** Ontology regression CI, signed and scanned images, AI BOM, red teaming, runbooks, demo rehearsal.
9. **Hands-on value.** Where Spark, NiFi, and Airflow practice concentrates: MERGE and branches and time travel in Spark; stateful pagination and record processing in NiFi; pools, sensors, and cross-DAG dependencies in Airflow.
10. **Risks and open questions.** Top five: PuppyGraph on Ozone, GPU memory under WSL2, Cloudera catalog branch support, scope creep, time. Twenty-one open questions tracked with the phase that resolves each.
