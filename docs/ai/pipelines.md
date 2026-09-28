# Pipelines (SPEC.md section 10, 11)

Rules: NiFi acquires and lands to s3://oag-raw/<source>/<ingest_date>/<file> with attrs source, source_version, fetch_ts, sha256. Spark transforms and writes on WAP branches. Airflow orchestrates (HttpOperator/HttpSensor to NiFi REST; spark_task() factory → SparkSubmitOperator local, CdeRunJobOperator on CDE). All jobs idempotent; raw MERGE on (source_system, source_record_id, source_version). Only embed_chunks, ground_chunks, extract_candidates, align_components call the model, via jobs/spark/lib/model_client.py (ModelPort, batches of 16 in mapInPandas).

## NiFi flows (ingest/nifi/flows/<name>.json; NiFi 2.12)

nvd_cve_incremental: daily 02:00 via Airflow; GenerateFlowFile(lastModStartDate from DistributedMapCache) → InvokeHTTP services.nvd.nist.gov/rest/json/cves/2.0 resultsPerPage=2000 apiKey header → EvaluateJsonPath totalResults,startIndex → RouteOnAttribute loop → ControlRate 50/30s with key → UpdateAttribute → PutS3Object. Retry x3 backoff; 403/503 wait 60s; errors to errors/.
nvd_cpe_dictionary: weekly Sun 03:00; same pattern on /cpes/2.0, resultsPerPage 10000.
cisa_kev: every 6h; InvokeHTTP KEV JSON → EvaluateJsonPath catalogVersion,dateReleased,count → DetectDuplicate catalogVersion → PutS3Object; branch SplitJson → PutIcebergRecord (RESTIcebergCatalog) raw.kev_entry (exercise only).
first_epss_daily: daily 04:00; epss.empiricalsecurity.com/epss_scores-YYYY-MM-DD.csv.gz → PutS3Object; 404 → Wait 2h, 6 tries.
mitre_cwe: weekly; cwec_latest.xml.zip → UnpackContent → S3. mitre_capec: weekly; capec_latest.xml. mitre_attack_stix: weekly; enterprise-attack.json plus versioned 16.1 and 19.2; also stix-atlas.json.
nist_oscal_800_53: monthly; NIST_SP-800-53_rev5_catalog.json. ctid_mappings: monthly; mappings-explorer nist_800_53-rev5_attack-16.1-enterprise.json.
advisory_text: daily; CISA advisories listing (Q10) → SplitRecord → InvokeHTTP html → Python processor (trafilatura) → S3 advisory/; trust_level authoritative (CISA) or vendor.
sbom_scan: weekly + on demand; ExecuteStreamCommand syft <image> -o cyclonedx-json → S3 → grype sbom:<file> -o json --add-cpes-if-none [--vex openvex file] → S3.
Common tail: PutS3Object success → InvokeHTTP POST agent /ingest/landed.

## Spark jobs (jobs/spark/<name>.py; args --run-id --env --ingest-date)

load_raw_nvd → raw.nvd_cve | normalize_vulnerability → oag.vulnerability, edge_has_weakness, edge_affects_product (statuses derived from vulnStatus; exploitation from KEV/SSVC) | load_cpe_products → oag.product | load_kev → kev_entry, edge_kev_for_vulnerability | load_epss → epss_score partition overwrite | load_cwe_capec (spark-xml) → weakness, attack_pattern, edge_related_attack_pattern, edge_maps_to_technique | load_attack → technique, tactic, edge_belongs_to_tactic, edge_subtechnique_of, ops.attack_version_bridge; also ATLAS | load_oscal_controls → control, control_family, edge_in_family, edge_enhancement_of | load_ctid_mappings → edge_mitigates_technique | load_sbom_findings → software_component, container_image, vulnerability_finding, four edges; unseen findings closed with closed_reason=not_in_latest_scan | generate_synthetic_agency (seeded; config/synthetic/bsr.yaml) → information_system, actor, control_implementation, edge_part_of_system, edge_has_implementation, edge_of_control | align_components → edge_instance_of_product (deterministic conf 1.0); LLM candidates to ops.extraction_candidate | load_documents → oag.document | chunk_documents (~400 tokens, 60 overlap) → doc.chunk | ground_chunks → mentioned_curies | embed_chunks → embedding | extract_candidates → ops.extraction_candidate | validate_candidates | validate_branch | publish_branch | refresh_vector_index → pgvector | export_graph_to_age | snapshot_diff (VERSION AS OF x2) | synthetic_scale_findings (optional)

## Airflow DAGs (dags/<name>.py; Airflow 2.11; TaskFlow)

reference_weekly Sun 03:00: trigger_nifi[cwe,capec,attack,oscal,ctid,cpe] → s3_landing_sensor each → loaders (parallel) → validate_branch → publish_branch → puppygraph_refresh_schema → notify; retries 2/10min; pool reference_tables=1
nvd_daily 02:00: trigger → sensor → load_raw_nvd → normalize_vulnerability → validate → publish; retries 3; pool vuln_tables=1
kev_6h: trigger → sensor → load_kev → normalize_vulnerability(incremental) → validate → publish → kev_delta_alert (CQ14 for new entries → audit_event); pool vuln_tables
epss_daily 04:30: trigger → sensor → load_epss → publish; retries 6/30min; pool epss
assets_weekly Sat 01:00: trigger[sbom_scan] → sensor → load_sbom_findings → generate_synthetic_agency → align_components → validate → publish; pool asset_tables
documents_daily 05:00: ExternalTaskSensor(nvd_daily) → trigger[advisory_text] → sensor → load_documents → chunk → ground → embed → extract_candidates → validate_candidates → refresh_vector_index; pool docs
ontology_ci (webhook/manual): linkml_lint → linkml_generate → schema_diff_report → apply_ddl_on_branch → run_eval_suite → gate_on_regression; retries 0
eval_nightly 06:00 after documents_daily: run_eval_suite (OAG, naive RAG, graph-only) → write_eval_report → langfuse_export_costs; pool eval=1 (ingest DAGs also take it)
maintenance_weekly Sun 07:00: expire_snapshots(30d), remove_orphan_files, rewrite_data_files, drop_stale_branches

## Extraction loop (section 11)

Templates schema/extract/: advisory_affected_product (CVE, vendor, product, version_range, span) | advisory_exploitation (CVE, claim active|poc|none_observed, span, date) | advisory_weakness (CVE, CWE id or name, span). SPIRES style: LinkML template → prompt → JSON schema guided decode → parse to generated Pydantic → ground. OntoGPT is a Phase 5 comparison in evals/ only, never in the extraction path (SPEC 11.2 finding: pseudo-YAML parsing not JSON schema, sys.exit on API errors, hidden Translator mapper and global LiteLLM cache, grounds model strings not text spans). Its client is duck-typed (complete(prompt) -> str) so a ModelPort wrapper works without LiteLLM traffic. Templates must stay OntoGPT-runnable: prompt/annotators/examples annotations, id_prefixes, AUTO: prefix.
Alignment: exact id regex → lexical (Trino over product, weakness names) → pgvector top5 on entity names; aligned if top≥0.85 and runner-up<0.6; else ambiguous; none → new_entity (never auto-created).
Validation: aligned and conf≥0.8 → WAP branch → pySHACL (AffectsProductShape, ExploitationStatusShape: advisory may not overwrite KEV active; advisory none_observed always rejected; ClaimEvidenceShape).
Auto-publish only conf≥0.95 and trust_level=authoritative. Else review queue (ops.extraction_candidate review_status=unreviewed): approve/reject(reason)/defer → audit_event candidate_approved.
Metrics per run in ops.pipeline_run.metrics: chunks, extracted, aligned, ambiguous, new_entity, conforming, violations by shape, auto_published, queued, approved, rejected, mean_conf, tokens, cost, wall time.
