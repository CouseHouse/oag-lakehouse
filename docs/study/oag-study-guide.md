# OAG study guide

A guide to the source material behind this project: Ling Huang's "From RAG to OAG" and the
primary works it draws on. Written for the author of this repository, who knows infrastructure
and federal compliance well and is newer to ontologies, knowledge graphs, and constrained
generation. Sources were checked on 2026-09-26.

## 0. How to use this guide

Reading path, in order, with rough time:

| Step | Read | Time | Then |
|---|---|---|---|
| 1 | Section 1 of this guide (the article's argument) | 30 min | Write the Feynman page (section 8) from memory, badly. Keep it. |
| 2 | Section 2 (concepts primer) | 60 min | Start the Anki deck (`anki-cards.csv`). |
| 3 | OG-RAG paper abstract and sections 3 and 4 (https://arxiv.org/abs/2412.15235) | 60 min | Lab 3 (greedy set cover). |
| 4 | OWL 2 Primer section 2 (https://www.w3.org/TR/owl2-primer/) and SHACL spec sections 1 and 2 (https://www.w3.org/TR/shacl/) | 60 min | Lab 2 (pySHACL). |
| 5 | LinkML overview and tutorial parts 1 to 3 (https://linkml.io/linkml/intro/tutorial.html) | 60 min | Lab 1 (LinkML to SHACL and Pydantic). |
| 6 | SPIRES paper abstract and the OntoGPT custom template page (https://monarch-initiative.github.io/ontogpt/custom/) | 45 min | Section 4 of this guide. |
| 7 | Palantir Ontology overview, core concepts, action types, submission criteria (links in section 5) | 45 min | Section 5 of this guide. |
| 8 | Sections 6 and 7 (mapping to this project; self-test) | 45 min | Rewrite the Feynman page. Compare. |
| 9 | Lab 4 and Lab 5 | 90 min | Start Phase 1. |

About seven hours in total. Spread it over two weeks alongside Phase 0.

## 1. The article's argument

### 1.1 What could be verified

"From RAG to OAG" by Ling Huang, Medium, published 2026-09-14, about a five minute read,
member-only. URL: https://medium.com/@linghuang_76674/from-rag-to-oag-68e3ac807c29

Section headings, in order: Naive RAG; Advanced RAG with Rerank; Modular RAG; Agentic RAG with
Planning and Critique; Ontology Augmented Generation. Each heading is followed by a diagram.

The definition, quoted from the portion available before the paywall:

> In this context, OAG (Ontology-Augmented Generation) utilizes an ontology as the "normative
> schema layer" for knowledge. It pre-defines the domain's concepts (classes), the
> relationships between them, and the mandatory constraints or axioms (e.g., SHACL, OWL). Both
> retrieval and generation operate within this framework of "ontological discipline."
>
> In essence, OAG represents a convergence of the preceding five generations (building from
> premises to conclusion) and inherits key features from them:

The text is cut off there by the paywall. Everything below in this section, and everything
this project attributes to the article about core components, the operational pipeline, the
three practices, the five criteria, and the four risks, comes from the summary in the prompt
that produced SPEC.md, not from the article text. Treat it as a faithful paraphrase until you
read the full article as a Medium member. **Action:** read the full article once and note any
difference from the summary below in `reading-log.md`.

### 1.2 The argument as summarized

**Lineage.** RAG evolves in stages: naive RAG (embed, retrieve chunks, generate), advanced RAG
(add reranking), modular RAG (swap components), GraphRAG (retrieve over a graph of entities),
agentic RAG (plan, retrieve, critique, loop), then OAG. Each stage keeps what came before. OAG
does not replace chunk retrieval or reranking or orchestration. It changes what a retrieval
unit is (an ontology-shaped block rather than a text window) and what a valid output is (a
typed, constrained claim rather than free text).

**Core components.**
1. Constraint-based retrieval: retrieve a task-relevant ontology subgraph with minimal
   coverage. The reference is OG-RAG's hypergraph and greedy minimal set cover.
2. Grounding: link text to ontology concepts by identifier (CURIEs). The reference tool family
   is the Ontology Access Kit.
3. Constrained generation: output governed by SHACL or OWL constraints, produced with
   constrained decoding (Outlines-style, or grammar and JSON-schema guided decoding).
4. Agent orchestration: the ontology as the semantic layer, or operating system API, for the
   agent.
5. Extract, align, validate: a closed loop that improves the knowledge base from new documents.
6. Structured fact output: answers as typed claims tied to ontology identifiers.

**Operational pipeline (Palantir-style).** Intent understanding (natural language to structured
query), grounded retrieval of entities (the ABox), rule validation, permission and constraint
checks (RBAC), action execution with write-back, and pre-write SHACL validation with an audit
trail. The LLM translates intent; it does not create facts.

**Three practices.** OG-RAG (grounded retrieval), OntoGPT and SPIRES (schema-driven extraction
with LinkML), Palantir (operational actions on an ontology). The article's point: these are
different things and a project should say which it does.

**When OAG is worth it.** Five criteria: high decision frequency; the same business object
lives in multiple systems; explicit, formalizable rules; results must be accountable (audit
trail); action results can be fed back. The warning: high business value plus unreliable data
plus implicit rules is the most commonly misidentified candidate. If no consensus on structure
exists, an ontology freezes chaos into a schema.

**Four risks.** Ontology supply chain (construction is expensive expert labor). Ontology
evolution and drift (an outdated ontology plus a live LLM confidently outputs an obsolete
worldview; regression testing after ontology change is immature). Closed-world versus
open-world assumption (mainstream OAG assumes missing means no; many domains need missing means
unknown; the mismatch is dangerous in risk scenarios). Vendor lock-in (switching cost rises as
logic accumulates on the ontology).

### 1.3 A tension worth knowing

The summary describes the ontology as "a semantic layer, or operating system API, for the
agent." Palantir's own architecture documentation says the opposite about its Ontology: "The
Ontology is not a 'semantic layer'; the fourfold integration and operationalization of data,
logic, action, and security cannot be accomplished with a thin semantic layer or a monolithic
design," and "semantics must be paired with kinetics." Palantir's Ontology has semantic
elements (objects, properties, links) and kinetic elements (actions, functions, dynamic
security). The "operating system for AI agents" phrasing comes from third-party commentary,
not Palantir. When you present, say "the ontology defines both the data model and the
permitted actions" rather than "semantic layer"; it is more accurate and it is what this
project builds.

Also: Palantir uses the term "Ontology-Augmented Generation" itself, in a blog series and a
documentation page, for retrieval and tool use over its Ontology. Huang's article and this
project use the broader sense. Be ready for the question "is this the Palantir thing?" The
answer: same term, same instinct, but this design is open standards and open source, and it
implements the three practices separately.

## 2. Concepts primer

Each entry: what it is, why it matters here, where it lives in this project.

**Ontology.** A formal description of a domain: its classes, the relationships between them,
and constraints on both. Not a taxonomy (a taxonomy is only a hierarchy) and not a data model
(a data model describes storage; an ontology describes meaning, and several data models can
implement one ontology). Here: `schema/` in LinkML.

**TBox and ABox.** From description logic. The TBox (terminological box) is the schema: classes
and relationships. The ABox (assertional box) is the facts: this CVE affects that product. Here:
TBox is LinkML, ABox is the `oag.*` Iceberg tables. The article's "grounded retrieval of
entities (ABox)" means retrieving facts, not schema.

**RDF.** The W3C data model: subject, predicate, object triples. Everything is a node or an
edge; identifiers are IRIs. RDF 1.2 is at Candidate Recommendation as of April 2026 and adds
triple terms (a triple as a node). Here: RDF is transient. Claims and changed rows are
serialized to Turtle for pySHACL and discarded.

**OWL.** The Web Ontology Language, W3C Recommendation, second edition December 2012. Adds
logical semantics to RDF: subclass, equivalence, disjointness, property characteristics, and
reasoning (a reasoner infers facts not stated). OWL assumes open world. Here: an OWL export
exists for documentation only; no reasoner runs.

**SHACL.** Shapes Constraint Language, W3C Recommendation July 2017. Validates an RDF graph
against shapes: cardinality, datatype, value ranges, patterns, and SPARQL-based constraints.
SHACL validates the data as given, which makes it closed-world in effect, and `sh:closed`
forbids properties not listed. SHACL 1.2 Core is a Working Draft dated 2026-09-18. Here: the
critic and the WAP validator. Severities: Violation blocks, Warning and Info do not.

**Closed-world assumption (CWA) and open-world assumption (OWA).** CWA: anything not stated is
false. Correct for a database that is a complete enumeration (the KEV catalog for a given
version). OWA: anything not stated is unknown. Correct when the source is incomplete (whether a
CVE is exploited). The OWL 2 Primer states it directly: "If some fact is not present in a
database, it is usually considered false (the so-called closed-world assumption) whereas in the
case of an OWL 2 document it may simply be missing (but possibly true), following the
open-world assumption." Here: closure is declared per predicate in `generated/closure.yaml`;
the agent reports absence on open predicates as unknown; a SHACL shape rejects any negated
claim on an open predicate.

**CURIE.** Compact URI: a prefix and a local identifier, `cve:CVE-2024-3094`, expanded through
a prefix map. Here: `schema/prefixes.yaml`; every id column holds a CURIE.

**LinkML.** A YAML modeling language with generators. One schema produces JSON Schema, SHACL,
OWL, Pydantic, SQL DDL, and more. Here: the single source of truth. The two custom generators
(Iceberg DDL, PuppyGraph schema) exist because LinkML ships neither.

**Grounding.** Mapping a span of text to an identifier. OntoGPT calls the components that do
this "annotators" and uses OAK's text annotator, which by default builds a lexical index from an
ontology's labels and synonyms and does string matching. Here: three passes (regex, lexicon,
model choosing from candidates). Ungrounded terms are never invented; SPIRES assigns `AUTO:`
ids to ungrounded terms and this project assigns `new_entity` status.

**Hypergraph and minimal coverage.** In OG-RAG, each factual block (a set of ontology
relationships extracted from a document) is a hyperedge over hypernodes (key-value pairs).
Retrieval finds relevant hypernodes by embedding similarity and then picks hyperedges by greedy
set cover: at each step add the hyperedge covering the most uncovered nodes. The result is the
smallest context that touches every relevant entity. Here: `agent/retrieval/cover.py` over
factual blocks built from graph query rows.

**Guided (constrained) decoding.** Restricting the token choices at each decoding step so the
output conforms to a grammar or JSON schema. The model cannot emit a value outside an enum or a
malformed structure. Libraries: Outlines, XGrammar, llguidance. Here: vLLM `response_format`
with a JSON schema generated from LinkML; NIM `guided_json` on Cloudera.

**Typed claim.** A structured assertion: subject, predicate, object, plus here an epistemic
status, a confidence, and evidence references. Here: the `ClaimSet` schema; the summary is
derived from claims and may add no facts.

**Write-audit-publish.** Write to an isolated branch, validate, publish atomically. Here:
Iceberg branches and `fast_forward`.

## 3. OG-RAG in depth

"OG-RAG: Ontology-Grounded Retrieval-Augmented Generation for Large Language Models," Kartik
Sharma, Peeyush Kumar, Yunqing Li (Microsoft Research). arXiv 2412.15235 (December 2024),
published at EMNLP 2025. Code: https://github.com/microsoft/ograg2 (MIT).

**Construction.** An LLM maps each document onto the ontology's entities and attributes,
producing factual blocks: sets of ontology relationships whose values are extracted text or
ontology entities. Nested blocks are flattened. Each flattened block becomes a hyperedge; the
hypernodes are key-value pairs from the domain vocabulary.

**Retrieval.** Embed the query, find the top-k hypernodes by key and value similarity, then run
greedy set cover: "In each iteration, we add the hyperedge that covers the largest number of
uncovered nodes to the context and remove those nodes from further consideration," until a
budget of hyperedges is reached or all relevant nodes are covered.

**Results.** From the abstract: recall of accurate facts up 55 percent, response correctness up
40 percent across four LLMs, attribution 30 percent faster, fact-based reasoning accuracy up 27
percent against baselines (RAG, RAPTOR, GraphRAG). Datasets: agriculture (85 expert documents)
and news (149 long articles from MultiHop-RAG).

**What this project takes.** The block-and-cover idea, applied to rows from graph queries
rather than to LLM-mapped documents. The graph is built from structured standards, so the
expensive LLM mapping step in OG-RAG is only needed for advisory text (the extraction loop).
**What it does not take.** OG-RAG's ontology-learning module for building the ontology from
documents; this project reuses published standards instead.

**Question to hold in mind.** OG-RAG's gains were measured on domains where the ontology was
built for the documents. Does minimal coverage help as much when the blocks come from
authoritative structured sources? The eval baselines (naive RAG, graph-only) are how this
project answers that.

## 4. OntoGPT and SPIRES in depth

"Structured prompt interrogation and recursive extraction of semantics (SPIRES): A method for
populating knowledge bases using zero-shot learning," Caufield et al., Bioinformatics 40(3),
2024; arXiv 2304.02711. Docs: https://monarch-initiative.github.io/ontogpt/

**Method.** "Given a detailed, user-defined knowledge schema and an input text, SPIRES
recursively performs prompt interrogation against GPT-3+ to obtain a set of responses matching
the provided schema. SPIRES uses existing ontologies and vocabularies to provide identifiers for
all matched elements." The schema is a LinkML template. When a slot's range is another class,
extraction recurses into it. Annotators (OAK adapters such as `sqlite:obo:chebi`) ground each
extracted mention to an identifier; unmatched mentions get `AUTO:` identifiers.

**Templates.** A template is a LinkML schema subset: prefixes, classes, slots, enums, with
`prompt` annotations that override slot descriptions in the generated prompt. 71 bundled
templates exist in 1.2.0, mostly biomedical.

**What this project takes.** The template idea (`schema/extract/`), grounding to existing
identifiers, and the rule that ungrounded mentions are proposals, not facts. **What it changes.**
Output goes to a candidate table with SHACL validation and human review before anything reaches
the knowledge base; SPIRES itself writes what it extracts.

**What the source shows (1.2.0, read 2026-09-28).** The prompt is `field: <description>` lines
and the parser scrapes pseudo-YAML; there is no JSON schema mode. The bundled client routes
through LiteLLM and exits the process on API errors. The engine is duck-typed, though: any
object with `complete(prompt) -> str` can be passed as the client. Grounding happens on the
extracted string (label dictionary, then OAK annotators), not on spans in the source text, and
unmapped prefixes are sent to the NCATS Translator service by default. Interview line: "we
kept SPIRES's template conventions and its rule that ungrounded mentions are proposals, but
replaced the free-text parse with schema-constrained decoding and ground against spans so every
candidate carries evidence."

## 5. Palantir's Ontology in depth

Documentation: overview https://www.palantir.com/docs/foundry/ontology/overview; core concepts
https://www.palantir.com/docs/foundry/ontology/core-concepts; action types
https://www.palantir.com/docs/foundry/action-types/overview; submission criteria
https://www.palantir.com/docs/foundry/action-types/submission-criteria; architecture
https://www.palantir.com/docs/foundry/architecture-center/ontology-system.

**Vocabulary.** Object type: the schema of a real-world entity or event. Link type: the schema
of a relationship between two object types. Action type: the schema of a set of edits to
objects, properties, and links that a user can take at once. Function: code logic over the
Ontology. Interface: the shape and capabilities of an object type. Submission criteria: the
conditions that determine whether an action can be submitted; "Actions can only be submitted if
all the submission criteria are met." Writeback: "Edits are written to the writeback dataset and
not the dataset backing an object type or link type."

**LLMs and actions.** AIP Logic lets an LLM use tools (query objects, call functions, apply
actions). "The Ontology will not be edited unless the Logic function is executed from an
action," so every LLM-initiated edit passes through an action type and its submission
criteria, and edits "can be automatically applied or staged for human review."

**What this project takes.** The separation of semantic (classes, relationships) from kinetic
(actions with preconditions, permissions, and write-back to a separate store), the rule that
the model reaches the data only through validated actions, and staging for human review.
**What it changes.** Every action is staged; none auto-applies. Write-back goes to files and
git, not a live system. SHACL replaces submission criteria as the validation language.

## 6. Mapping the article to this project

| Article element | Where it lives | Depth |
|---|---|---|
| Ontology as normative schema layer | `schema/` (LinkML), `generated/` | Full |
| Constraint-based retrieval, minimal coverage | `agent/retrieval/cover.py`, templates, absence blocks | Full |
| Grounding with CURIEs | `agent/grounding/`, `generated/lexicon/` | Full |
| Constrained generation (SHACL, guided decoding) | `agent/generation/`, `agent/critic/`, `generated/jsonschema/`, `generated/shacl/` | Full |
| Agent orchestration | `agent/graph.py` (LangGraph) | Full, single agent, no tools during generation |
| Extract, align, validate | `agent/extract/`, `documents_daily` DAG, review queue | Bounded: three templates |
| Structured fact output | `ClaimSet` schema, `ops.audit_event.claims_json` | Full |
| Operational pipeline | `agent/actions/`, approval UI, `ops.action_*` | Bounded: three actions, file and git sinks |
| Five criteria | SPEC.md section 2 scoring | Used as the rubric |
| Risk: supply chain | Reuse of 14 standards; CQs gate additions | |
| Risk: drift | Source versions everywhere; ATT&CK bridge; ontology CI | |
| Risk: CWA versus OWA | Closure per predicate; `NegatedClaimShape`; five T4 questions; CWFN metric at zero | |
| Risk: lock-in | Open interfaces; LinkML; derived read-only graph | |

## 7. Self-test

Answer without looking. Model answers follow each question; cover them.

1. **What does OAG change relative to agentic RAG?** It keeps retrieval, reranking, and the plan-critique loop, and changes the retrieval unit (ontology-shaped blocks with minimal coverage) and the output contract (typed, validated claims). The LLM translates intent and cites; it does not create facts.

2. **What is the difference between the TBox and the ABox, in this project's terms?** TBox is the LinkML schema; ABox is the Iceberg entity and edge tables. Retrieval is over the ABox; validation is against the TBox's constraints.

3. **Why does SHACL and not OWL do the validation?** OWL is open-world and inference-oriented; it cannot say "this record is invalid," only "this is inconsistent." SHACL validates data as given and reports violations with severities, which is what a critic and a publish gate need.

4. **Explain closed-world versus open-world with two predicates from this project.** KEV membership is closed per catalog version: absence means not listed, and the system may say so. Exploitation status is open: absence from KEV means unknown, and the system may never say "not exploited."

5. **Describe minimal coverage in three sentences.** Retrieved facts are grouped into blocks. Each block covers some of the entities the question mentions. Pick blocks greedily, largest number of uncovered entities first, until every entity is covered, and send only those.

6. **What is guided decoding and what can it not do?** It restricts token choices so output conforms to a schema; it cannot produce an invalid enum or structure. It cannot make the content true. That is why SHACL runs after it.

7. **Name the three practices and the depth this project implements each.** OG-RAG retrieval (full). SPIRES extraction (bounded to three templates with review). Palantir-style actions (bounded to three drafts, file sinks, always staged).

8. **Which of the five criteria does healthcare program integrity fail, and why does that matter?** Explicit rules. Fraud patterns are implicit and adversarial; an ontology would freeze guesses into a schema and the model would defend them. That is the article's trap.

9. **What is the ontology drift risk in this project concretely?** CTID mappings target ATT&CK 16.1; ATT&CK is at 19.2; CAPEC is dormant since 2023; NVD stopped enriching most CVEs in April 2026. Answers built on stale mappings look authoritative. Mitigations: source versions on every row and claim, the version bridge, ontology CI reruns every competency question on schema change.

10. **What makes an answer reproducible here?** Iceberg snapshot ids per table, ontology version, model revision hash, prompt version, rule version, all on the audit event, plus a replay tool.

11. **Why is the graph read-only and derived?** So the lakehouse remains the single system of record, any engine can rebuild the graph, and the switching cost from PuppyGraph is configuration.

12. **Give the two-minute answer to "when should an agency not do this?"** When rules are implicit, when data is unreliable and unowned, when it is a one-off analysis, or when nobody will maintain the ontology. And keep the ontology on open standards so leaving stays cheap.

13. **What is a hyperedge in OG-RAG?** A flattened factual block: a set of ontology relationships extracted from a document, connecting the key-value hypernodes it mentions.

14. **What is a SPIRES template?** A LinkML schema subset (classes, slots, enums, prompt annotations, annotators) that defines what to extract and how to ground each mention.

15. **What is a Palantir submission criterion and what is this project's equivalent?** A condition that must hold for an action to be submitted. Here: rule preconditions plus OSCAL and SHACL validation before an action is queued, plus the role check.

## 8. The Feynman page

Write one page, by hand, explaining OAG to an agency CISO. No notes. Save it as
`docs/study/feynman-v1.md`. After finishing the reading path, write `feynman-v2.md`. Compare
both against SPEC.md section 23.3. The differences are your study list.

## 9. Mini-labs

Each lab is under an hour, runs on the workstation, and needs no Compose stack. Do them in
order before Phase 1.

- [ ] **Lab 1: LinkML.** `uv pip install linkml`. Write a schema with `Vulnerability` and
  `KEVEntry`, an enum `ExploitationStatus`, a required slot, and a multivalued slot. Run
  `gen-shacl`, `gen-pydantic`, `gen-json-schema`. Read all three outputs. Note which constraint
  appears in which output and which do not (multivalued cardinality, required, enum).
- [ ] **Lab 2: pySHACL.** Write ten triples in Turtle for two vulnerabilities and one KEV entry.
  Make one of them wrong (a KEV entry with no due date). Run `pyshacl -s shapes.ttl data.ttl`.
  Read the validation report. Change the shape's severity to `sh:Info` and run again.
- [ ] **Lab 3: greedy set cover.** In 20 to 30 lines of Python, given `blocks: dict[str, set[str]]`
  and `entities: set[str]`, return the ordered list of blocks chosen greedily. Add a budget
  parameter. Test on a case where greedy is not optimal (it exists; find one).
- [ ] **Lab 4: guided decoding.** Start vLLM with a small model (or any OpenAI-compatible server
  you have). Send a chat completion with `response_format` json_schema containing an enum of
  three values. Try prompts that ask for a fourth value. Observe. Then remove
  `response_format` and repeat.
- [ ] **Lab 5: openCypher.** `docker run` Apache AGE. Create a graph with two vulnerabilities,
  one KEV entry, and the `KEV_FOR` edge. Write the CQ02 query from SPEC.md section 12.2 with
  `OPTIONAL MATCH` and see the null for the CVE not in KEV.
- [ ] **Lab 6: Iceberg branch (after Phase 1).** In the Phase 1 stack, write on a branch, query
  `VERSION AS OF` the branch and `main`, fast-forward, query again.

## 10. Further reading

Primary sources, verified 2026-09-26:

- Huang, "From RAG to OAG," Medium, 2026-09-14. https://medium.com/@linghuang_76674/from-rag-to-oag-68e3ac807c29 (member-only)
- Sharma, Kumar, Li, "OG-RAG," arXiv 2412.15235; EMNLP 2025. https://arxiv.org/abs/2412.15235 ; code https://github.com/microsoft/ograg2
- Caufield et al., "SPIRES," Bioinformatics 2024; arXiv 2304.02711. https://arxiv.org/abs/2304.02711 ; OntoGPT https://monarch-initiative.github.io/ontogpt/
- Ontology Access Kit. https://incatools.github.io/ontology-access-kit/ ; text annotator interface https://incatools.github.io/ontology-access-kit/packages/interfaces/text-annotator.html
- Palantir Ontology documentation (links in section 5). Palantir's own OAG page: https://www.palantir.com/docs/foundry/ontology/ontology-augmented-generation
- W3C SHACL 1.0, 2017. https://www.w3.org/TR/shacl/ ; SHACL 1.2 Core WD 2026-09-18 https://www.w3.org/TR/shacl12-core/
- W3C OWL 2 Primer. https://www.w3.org/TR/owl2-primer/ ; Overview https://www.w3.org/TR/owl2-overview/
- W3C RDF 1.2 Concepts, CR 2026-04-07. https://www.w3.org/TR/rdf12-concepts/
- LinkML. https://linkml.io/linkml/ ; generators https://linkml.io/linkml/generators/index.html
- Edge et al., "From Local to Global: A Graph RAG Approach to Query-Focused Summarization," arXiv 2404.16130. https://arxiv.org/abs/2404.16130
- Singh et al., "Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG," arXiv 2501.09136. https://arxiv.org/abs/2501.09136
- Allemang, Hendler, Gandon, Semantic Web for the Working Ontologist, 3rd ed., ACM Books 2020. https://dl.acm.org/doi/book/10.1145/3382097 (the open-world chapter is the one to read)

Related work found but not verified in detail (arXiv ids from search results; check before citing): OntologyRAG 2502.18992; OntoRAG 2506.00664; KG-Infused RAG 2506.09542; EvoOntology 2609.15779; OaK, "Toward Effective and Reliable LLM Agents via Dynamic Ontology," 2608.22974; "Provably Auditable and Safe LLM Agents from Human-Authored Ontologies," 2606.04903; "Ontology-Constrained Neural Reasoning in Enterprise Agentic Systems," 2604.00555.
