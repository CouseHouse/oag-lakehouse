# Iceberg tables (SPEC.md section 9)

Namespaces: raw (landing, append only, raw JSON/XML string col) | oag (ABox entities and edges,
DDL generated from LinkML) | doc (documents, chunks) | ops (candidates, validation, audit, actions, runs).
Standard cols on every table: source_system, source_version, source_record_id, ingested_at,
is_synthetic, synthetic_note. Ids are CURIE strings in `id`. Timestamps UTC, dates as date.

## oag entity tables (key cols → notable cols; partition)

vulnerability: id → description, published ts, nvd_last_modified ts, cvss31_base_score double, cvss31_severity, cvss31_vector, cvss40_vector, cvss_source, exploitation_status, exploitation_status_source, cpe_config_status, nvd_vuln_status, cwe_status; years(published)
weakness: id → name, abstraction, status, description, cwe_version
attack_pattern: id → name, abstraction, likelihood, severity, capec_version
technique: id → stix_id, name, is_subtechnique bool, parent_id, attack_version, revoked bool, deprecated bool, framework (attack|atlas)
tactic: id → name, shortname, attack_version, framework
control: id → title, family_id, is_enhancement bool, parent_id, statement, statement_text, oscal_catalog_version
control_family: id → title
product: id → part, vendor, product, cpe_name, title, deprecated; bucket(32,id)
software_component: id → purl, name, version, ecosystem, cpe_candidates array<string>, product_link_status (linked|unlinked|ambiguous); bucket(16,id)
container_image: id → image_ref, digest, registry, sbom_status, sbom_document_id, last_scan_id, is_synthetic=true
information_system: id → name, fips199_confidentiality, fips199_integrity, fips199_availability, fips199_overall, ato_date, ato_expires, isso_actor_id, owner_actor_id, is_synthetic=true
actor: id → display_name, role (isso|analyst|system_owner|ciso), email, is_synthetic=true
control_implementation: id → system_id, control_id, status, last_assessed date nullable, assessor, is_synthetic=true
vulnerability_finding: id → image_id, component_id, vulnerability_id, scanner, scanner_version, db_version, severity_reported, fix_state, fixed_version, first_seen_scan_id, last_seen_scan_id, first_seen_at, last_seen_at, status, closed_reason, match_type; days(first_seen_at)
kev_entry: id → vulnerability_id, vendor_project, product, date_added, due_date, known_ransomware_use, required_action, catalog_version, cwes array<string>, forensic_triage, raw_extra map
epss_score: (vulnerability_id, score_date) → epss double, percentile double, model_version; months(score_date)
vex_statement: id → finding_id, status, justification, detail, asserted_by_actor_id, asserted_at, approved_by_actor_id, approved_at
poam_item: id → system_id, title, description, scheduled_completion, responsible_actor_id, status, oscal_json, approved_by_actor_id, approved_at, action_request_id
remediation_ticket: id → component_id, fixed_version, image_ids array, finding_ids array, status, approved_by_actor_id, action_request_id
document: id → source, source_url, title, published, retrieved_at, content_type, object_key, trust_level; partition source

## oag edge tables

All: src_id, dst_id, source_system, source_version, confidence double (1.0 authoritative), mapping_type nullable, plus standard cols.
Tables: edge_has_weakness, edge_related_attack_pattern, edge_maps_to_technique, edge_belongs_to_tactic, edge_subtechnique_of, edge_mitigates_technique, edge_in_family, edge_enhancement_of, edge_affects_product (+version_range), edge_instance_of_product, edge_contains_component, edge_part_of_system, edge_finding_on_image, edge_finding_in_component, edge_finding_for_vulnerability, edge_kev_for_vulnerability, edge_has_implementation, edge_of_control, edge_vex_for_finding, edge_poam_addresses, edge_poam_related_control, edge_ticket_addresses, edge_document_mentions.
EPSS is a vertex from epss_score with computed id vulnerability_id|score_date and derived edge EPSS_FOR (fallback: Spark view oag.epss_score_latest with id col).

## doc

chunk: id, document_id, ordinal int, text, token_count, embedding array<float> (dim from config), embedding_model, mentioned_curies array<string>, trust_level, created_at; partition document_source. Iceberg is system of record; pgvector is a rebuilt index.

## ops

extraction_candidate: id, run_id, document_id, chunk_id, subject_id, predicate, object_id, object_literal, confidence, extractor, extractor_version, template_version, alignment_status (aligned|new_entity|ambiguous|failed), validation_status (pending|conforms|violation|rejected|approved), review_status (unreviewed|approved|rejected), reviewer_actor_id, created_at; days(created_at)
validation_result: id, run_id, target_kind (branch|claimset|action), target_id, shape_id, severity, focus_node, result_path, message, conforms, ontology_version, created_at
audit_event: id, event_ts, event_type, actor_id, trace_id, question_text, answer_id, snapshot_ids map<string,string>, ontology_version, model_name, model_version, prompt_version, rule_version, claims_json, violations_count, unknown_count, latency_ms, input_tokens, output_tokens, cost_usd; days(event_ts)
action_request: id, requested_at, requested_by_actor_id, action_type (poam_create|ticket_create|vex_create), artifact_json, shacl_conforms, status, decided_by_actor_id, decided_at, decision_note, trace_id
action_record: id, action_request_id, executed_at, sink, receipt, rollback_of, snapshot_id_before, snapshot_id_after
pipeline_run: run_id, dag_id, task_id, started_at, finished_at, status, rows_in, rows_out, branch, published, metrics map
attack_version_bridge: old_id, new_id, relation (revoked_by|deprecated|same), old_version, new_version
eval_result: case_id, system, run_id, metrics map, claims_json, violations_json

## WAP

1. Airflow passes run_id. 2. Job sets spark.wap.branch=stage_<run_id>; tables have write.wap.enabled. 3. validate_branch reads VERSION AS OF 'stage_<run_id>', Spark SQL checks, RDF of changed rows, pySHACL, per-source delta thresholds; writes ops.validation_result. 4. If no Violation: CALL <cat>.system.fast_forward('oag.<t>','main','stage_<run_id>') per table, entities before edges; any failure publishes nothing. 5. Drop branch after 7 days (failed: 30). 6. Rollback: rollback_to_snapshot(snapshot_id_before), recorded in ops.action_record. Airflow pool size 1 per table group serializes writers. Consumers read main only.
Retention: raw 400 days; oag snapshots 30 days, eval/demo tags kept; ops audit and actions never expired.
