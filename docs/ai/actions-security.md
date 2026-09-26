# Actions and security (SPEC.md sections 15, 16)

## Actions (agent/actions/)

poam_create: OSCAL poam-item (vendored schema/oscal/oscal_poam_schema.json, OSCAL 1.2.3; Q18 milestone placement); fields: finding refs, milestones ≥1, scheduled completion = KEV due_date else SLA date, responsible party = system ISSO, related controls from CQ08 chain, remarks with evidence summary; props carry CURIEs, is_synthetic, ontology_version, action_request_id. Sink s3://oag-actions/poam/<system>/<id>.json + git commit in actions/ + oag.poam_item row.
ticket_create: one per component: purl, fixed_version (Grype), image_ids, finding_ids, systems, owners. Sink s3://oag-actions/tickets/ + git + oag.remediation_ticket. Ticket → verified_closed when next scan closes findings.
vex_create: OpenVEX statement {status, justification (human-supplied only), impact_statement, products (image purl), vulnerability, timestamp, author}. Sink s3://oag-actions/vex/<image>.openvex.json (append) + oag.vex_statement. Next sbom_scan passes file to grype --vex. not_affected on a KEV finding requires impact_statement ≥50 words.
Flow: intent (ambiguity → ask) → grounded retrieval → rule preconditions (no POA&M for closed finding) → authorize → draft (JSON schema guided) → validate (JSON Schema then SHACL POAMItemShape: milestone≥1, completion not past, responsible party exists, findings exist and open; VexStatementShape: enums, assertedBy present, approvedBy when approved) → ops.action_request pending_approval → approval UI (evidence, rule trace, SHACL result; HTML-escaped, A07) → approve/reject by authenticated actor → execute via ActionSinkPort (S3, git, entity row on WAP branch, publish, ops.action_record with receipt and snapshot ids) → rollback is an approved action (rollback_to_snapshot, git revert, S3 tag rolled_back, action_record rollback_of).
Roles (config actions.approval_roles; oag.actor.role): isso, analyst draft all; isso, ciso approve poam_create and vex_create; system_owner approves ticket_create. Requester ≠ approver (A08).
Audit: audit_event at request, decision, execution/rollback; each with actor_id, trace_id, snapshot_ids, ontology/model/prompt/rule versions, artifact hash; same fields in S3 metadata and git message.
Never without approval: write to any sink; change finding status (except scanner loader); create entity from candidate; choose VEX justification; publish candidate conf<0.95 or non-authoritative; roll back; change ontology, rule, or prompt version at runtime.

## Security controls in code

- Chunks delimited, labeled trust_level, declared data. No tools during generation. Output schema-constrained. Evidence required (EvidenceRefShape). Injection classifier at ingest (enum benign|instruction_like); flagged chunks excluded and listed. Seeded injection cases evals/cases/injection/.
- TLS validation in NiFi InvokeHTTP; sha256 on landed files; source allowlist in parameter contexts; per-source delta thresholds in validate_branch (KEV count may not drop; NVD daily change >5% → manual publish) (A06).
- Model: pinned HF revision + sha256 in config; safetensors only; trust_remote_code never; read-only cache; --served-model-name; --api-key; LAN only (A03).
- Secrets: env vars only; NiFi sensitive params; pre-commit secret scan; Langfuse mask function (A02).
- Identities: agent read-only on graph/vector; read-write only ops.*; Polaris and Postgres roles per adapter.
- Separation of duties enforced in authorize. Kill switch flags in config/base.yaml changeable at runtime by ciso: actions.enabled, retrieval.enabled, extraction.auto_publish; changes audited (A14).
- Test greps agent/ for exec, eval, dynamic query construction (ASI05).
- Vector queries get role predicates if Ranger test confirms bypass (A10, policy.py).
- UI "report this answer" → audit_event user_report (A15).
- Every table property oag.classification: public|synthetic|derived|operational. PII slots annotated pii: true → Ranger mask list.
- Project images: cosign-signed, Syft+Grype scanned in CI, KEV finding fails build (A04). AI BOM CycloneDX 1.7 machine-learning-model + modelCard, model card docs/security/model-card.md (A05). Weekly garak + promptfoo pass (A13). Optional guard model ibm-granite/granite-guardian-4.1-8b.
- Prompt change → eval suite must pass (same gate as ontology).

## Security actions by phase

A06, A02(ddl) Phase 2 | A12 Phase 3 | A01, A02(langfuse), A03, A09, A11, A15 Phase 4 | A07, A08, A14 Phase 5 | A04, A05, A13 Phase 6 | A10 Phase 7

## Ranger test (section 16.4)

Ranger 2.9 + Trino access-control.name=ranger. Row filter analyst_low → fips199_overall='low' on oag.information_system; column mask actor.email. A: Trino as analyst_low → only low, masked. B: PuppyGraph with that principal, CQ06 → all rows = bypass confirmed (expected). C: Polaris grant at namespace/table → record. D: Cloudera REST catalog + Ranger. If bypass: PuppyGraph principal must be at least as restrictive as most restrictive user, and role predicates in retrieval/policy.py on every template query.
