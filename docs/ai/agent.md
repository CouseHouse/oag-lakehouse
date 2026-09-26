# Agent (SPEC.md sections 13, 14)

## Grounding (agent/grounding/)

1 regex: CVE-\d{4}-\d{4,}; CWE-\d+; CAPEC-\d+; T\d{4}(\.\d{3})?; TA\d{4}; 800-53 ids [A-Z]{2}-\d+(\(\d+\))? → ac-2.1; bsr ids; purl; cpe:2.3. conf 1.0
2 lexicon (generated/lexicon/entity_names.parquet): longest match n-grams ≤6, case-insensitive; exact 0.9, synonym 0.75. oaklib for CWE and CAPEC.
3 model: JSON schema GroundingResult=[{span, candidate_curies (lexicon top10), chosen_curie|null, confidence}]; choose only from candidates; conf cap 0.7.
Failures: nothing grounded and template needs entity → clarify (never guess). Ambiguous (two within 0.1) → answer top and state alternative; for actions always ask. Valid id not in ABox → say not in snapshot; offer live lookup as separate labeled step (config flag).

## Retrieval (agent/retrieval/)

Intent: enum-guided model call over CQ template ids + freeform + action:<type>. Template YAML: query file, required entity types, closure map.
Queries: fixed .cypher with $params; .age.cypher variant when portable form differs. Model never writes queries.
Factual blocks: one per row/entity with typed fields, CURIEs, provenance (table, snapshot id, source_version).
Minimal cover: greedy set cover over query entities (cap 200) by blocks; tie-break trust then recency. Block caps T1/T2 60, T3 120, T4 40. Unselected → reserve list for critic.
Chunks: embed question → pgvector top 24 cosine → filter mentioned_curies && query/block entities (GIN on text[]) → top 8. If <3 pass, add top 3 unfiltered marked scoped=false (claim conf ≤0.5).
Absence blocks: for each open predicate in the closure map returning null: {predicate, subject, closure, source_checked, source_version, meaning unknown|negated}.
Vector table: chunk_embedding(chunk_id pk, document_id, embedding vector(1024), mentioned_curies text[], trust_level, source, published); HNSW cosine m=16 ef_construction=128. Dim from config (BGE-M3 assumed).
Snapshot ids of all oag.* tables read at start_trace and pinned for the turn.

## Generation (agent/generation/)

Output schema ClaimSet (generated/jsonschema/ClaimSet.json):
ClaimSet{question_id, claims[Claim], answer_summary ≤120 words no new facts, unknowns[Unknown]}
Claim{id, subject CURIE, predicate (enum of ontology slot CURIEs), object CURIE|{value,datatype}, epistemic_status enum, confidence 0..1, evidence[Evidence] min 1, derived_from_rule|null (required for T3)}
Evidence{kind record|chunk|rule, ref (table:snapshot:row | chunk id | rule id), quote|null (verbatim for chunks)}
Unknown{subject, predicate, reason enum, source_checked}
vLLM: response_format={"type":"json_schema","json_schema":...}; backend xgrammar. NIM: extra_body={"guided_json":schema} (optional nvext wrapper, config model.nim_nvext_wrapper). Switch: config model.structured_output_mode = response_format|guided_json.
Prompt: system (versioned prompt_version): role, closure rules in plain language, model translates and cites but never creates facts, schema. User: question, grounded entities, factual blocks, absence blocks, chunks (delimited, labeled trust_level, declared data not instructions). Temperature 0 (0.2 only for summary rewrite).
Rule: nothing in a prompt is security-relevant; authorization lives in code.

## Critic (agent/critic/)

Claims → RDF (reified blank nodes: oag:subject/predicate/object/evidence/epistemicStatus) + bundle as named graph → pySHACL with generated/shacl + schema/shacl/claims.ttl.
Shapes → response: ClaimEvidenceShape (no evidence) regenerate | EvidenceRefShape (ref not in bundle) regenerate, hallucination metric | NegatedClaimShape (negated on open predicate) regenerate with closure quoted, CWFN metric | ClaimConsistencyShape (value contradicts block) regenerate | UnscopedEvidenceShape (conf>0.5 on unscoped chunk) lower conf, no regen | RuleTraceShape (T3 without rule) regenerate | ImperativeTextShape (A01: imperative text in answer_summary) mark partial | *CoverageInfo → metrics only.
Loop max 2 regenerations; then return conforming subset, list dropped, partial=true. Never return a non-conforming claim.

## LangGraph (agent/graph.py)

State: question, actor_id, trace_id, config_snapshot{ontology_version, prompt_version, rule_version, model}, grounding, intent, clarification_needed, context{blocks, absence_blocks, chunks, snapshot_ids}, claims, violations[], critic_iterations, action_request, answer{table, summary, unknowns, evidence_links, partial}, errors[]
Nodes: start_trace → ground → classify_intent → check_requirements → (ask_clarification | authorize) → (write_audit if denied | retrieve) → generate → critic → (generate if violations and iter<2 | render_answer) → (draft_action if action else write_audit) → validate_action → (draft_action if violations and iter<2 | queue_for_approval | write_audit if refused) → write_audit → END. write_audit always runs, including on error.
Limits: 2 critic iters, 2 action iters, 1 clarification/turn, 90 s wall, 24,000 input tokens (drop lowest chunks, then reserve; never cover blocks). Per-actor rate limits and daily token quota (A11).
Unknown answers: absence blocks with meaning=unknown must go to unknowns not claims; render_answer prints unknowns with source_checked and version and the sentence that absence is not evidence of absence.
Failure modes: model down → retry once then error answer, audit model_unavailable | invalid JSON → retry once temp 0 | graph down → AgeGraph if snapshot ≤24h old, state backend in answer | vector down → blocks only, chunks_unavailable | >200 rows → truncate with note, offer Trino export | injection flagged chunk → drop, security event | snapshot changed mid-turn → note (PuppyGraph reads main) | actor lacks role → refuse with policy id, audit.
Tracing: Langfuse trace per turn, session_id=actor_id, span per node, generation per model call, scores shacl_violations, closed_world_false_negatives, unknown_count; prompts registered by prompt_version.
