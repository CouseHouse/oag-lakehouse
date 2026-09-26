# Ontology reference (SPEC.md section 6)

Source: LinkML in `schema/`. Modules: prefixes, oag_core (Identified, Provenance mixins, Claim,
Evidence, epistemic enums), oag_vuln, oag_control, oag_asset, oag_action, oag_document; top
file oag.yaml. Extraction templates in schema/extract/. Rules as data in schema/rules/.

## Prefixes

cve → https://www.cve.org/CVERecord?id= | cwe → cwe.mitre.org/data/definitions/ (CWE-79) |
capec (CAPEC-63) | attack (T1190, T1190.001, TA0001) | sp800-53r5 (ac-2, ac-2.1) |
cpe23 (percent-encoded cpe:2.3 remainder) | purl (percent-encoded pkg: remainder) |
kev (kev:CVE-...) | epss (epss:CVE-...|YYYY-MM-DD) | bsr (synthetic agency) | doc | chunk |
claim | oag (ontology terms) | oscal | cdx | openvex | ssvc

## Classes (id pattern, source)

Vulnerability (cve:, NVD) | Weakness (cwe:, CWE 4.20) | AttackPattern (capec:, CAPEC 3.9) |
Technique (attack:T, ATT&CK 19.2 and 16.1; framework col also holds atlas) | Tactic (attack:TA) |
Control (sp800-53r5:, OSCAL Rev 5.2.0) | ControlFamily | Product (cpe23:, CPE dict) |
SoftwareComponent (purl:, Syft) | ContainerImage (bsr:BSR-IMG-NN, synthetic assignment) |
InformationSystem (bsr:BSR-SYS-NN, synthetic) | Actor (bsr:ACT-NN, synthetic) |
ControlImplementation (bsr:CI-<sys>-<control>, synthetic) | VulnerabilityFinding (bsr:BSR-FND-NNNN, Grype) |
KEVEntry (kev:, KEV) | EPSSScore (epss:, EPSS daily) | VexStatement (bsr:VEX-NNNN) |
POAMItem (bsr:BSR-POAM-NNNN) | RemediationTicket (bsr:BSR-TKT-NNNN) | Document (doc:) |
DocumentChunk (chunk:) | Claim, Evidence (agent output only, not in graph)

## Relationships (domain → range, card, edge table)

hasWeakness Vulnerability→Weakness 0..* edge_has_weakness
relatedAttackPattern Weakness→AttackPattern 0..* edge_related_attack_pattern
mapsToTechnique AttackPattern→Technique 0..* edge_maps_to_technique
belongsToTactic Technique→Tactic 1..* edge_belongs_to_tactic
subtechniqueOf Technique→Technique 0..1 edge_subtechnique_of
mitigatesTechnique Control→Technique 0..* edge_mitigates_technique (props mapping_type, attack_version=16.1)
inFamily Control→ControlFamily 1..1 edge_in_family
enhancementOf Control→Control 0..1 edge_enhancement_of
affectsProduct Vulnerability→Product 0..* edge_affects_product (prop version_range)
instanceOfProduct SoftwareComponent→Product 0..1 edge_instance_of_product (confidence<1)
containsComponent ContainerImage→SoftwareComponent 0..* edge_contains_component
partOfSystem ContainerImage→InformationSystem 1..1 edge_part_of_system
onImage Finding→ContainerImage 1..1 edge_finding_on_image
inComponent Finding→SoftwareComponent 1..1 edge_finding_in_component
forVulnerability Finding|KEVEntry|EPSSScore→Vulnerability 1..1 edge_finding_for_vulnerability, edge_kev_for_vulnerability, EPSS_FOR derived
hasImplementation InformationSystem→ControlImplementation 0..* edge_has_implementation
ofControl ControlImplementation→Control 1..1 edge_of_control
isso, owner InformationSystem→Actor 1..1 (columns isso_actor_id, owner_actor_id)
forFinding VexStatement→Finding 1..1 edge_vex_for_finding
assertedBy 1..1, approvedBy 0..1 (required when status>=approved) Vex|POAM|Ticket→Actor
addressesFinding POAM|Ticket→Finding 1..* edge_poam_addresses, edge_ticket_addresses
relatedControl POAM→Control 0..* edge_poam_related_control
responsibleParty POAM→Actor 1..1
forSystem POAM|ControlImplementation→InformationSystem 1..1
hasChunk Document→DocumentChunk 1..*
mentions Document→entity 0..* edge_document_mentions
hasEvidence Claim→Evidence 1..* (SHACL Violation if 0)

Graph edge labels = upper snake of the edge table suffix (HAS_WEAKNESS, KEV_FOR, ON_IMAGE, ADDRESSES, ...).

## Enums

exploitation_status: active | poc | none_observed | unknown (active from KEV authoritative; none_observed only from SSVC with date; never derived from KEV absence)
cpe_config_status: present | absent_pending_enrichment | absent_not_scheduled | absent_rejected | unknown
cwe_status: assigned | noinfo | other | unknown
ControlImplementation.status: implemented | partially_implemented | planned | alternative_implementation | not_applicable | not_implemented | unknown (not_implemented requires last_assessed)
sbom_status: present | partial | missing
fix_state: fixed | not_fixed | wont_fix | unknown
Finding.status: open | closed | suppressed (closed requires closed_reason)
VexStatement.status: affected | not_affected | fixed | under_investigation
VexStatement.justification: OpenVEX enum, chosen by human only
fips199_*: low | moderate | high
trust_level: authoritative | vendor | community | untrusted
epistemic_status: asserted | negated_closed_world | unknown | insufficient_evidence
Unknown.reason: source_open_world | no_record | sbom_missing | enrichment_pending | under_investigation | ambiguous_grounding
poam status: draft | pending_approval | approved | rejected | open | closed
action_request status: pending_approval | approved | rejected | executed | rolled_back

## Closure (generated/closure.yaml)

closed: KEV membership per catalog_version; POA&M existence; Finding existence per (scanner, db_version, scan_id); containsComponent when sbom_status=present (per cataloger set); hasWeakness when cwe_status=assigned
open: exploitation_status; affectsProduct; containsComponent when sbom_status in (partial, missing); ControlImplementation.status unless row with last_assessed; mitigatesTechnique; mapsToTechnique; hasWeakness when cwe_status in (noinfo, unknown)
Rule: minCount shapes on open predicates are sh:Info with suffix CoverageInfo; never turned into negated claims. Query with OPTIONAL MATCH; null → closure meaning. NegatedClaimShape rejects negated_closed_world on open predicates.

## Generators (make generate → generated/)

gen-iceberg-ddl (custom, tools/linkml_iceberg): CREATE TABLE IF NOT EXISTS per class and edge; TBLPROPERTIES write.wap.enabled=true, format-version=2, oag.classification=<public|synthetic|derived|operational>; partition from annotation iceberg_partition; types string/int/bigint/double/date/timestamp/array<>.
gen-shacl + schema/shacl/extra.ttl, claims.ttl, actions.ttl → generated/shacl/oag.shacl.ttl
gen-pydantic → generated/pydantic/oag_models.py
gen-json-schema --top-class ClaimSet and per template → generated/jsonschema/
gen-puppygraph (custom, tools/linkml_puppygraph) → generated/puppygraph/schema.json and schema.cloudera.json
gen-owl, gen-doc, lexicon script → generated/lexicon/entity_names.parquet
Class annotations used: iceberg_table, iceberg_partition, puppygraph_label, classification, pii. Slot annotations: edge_table, edge_direction, closure.

## Versioning

version in oag.yaml, semver. Enum, closure, rename, removal = major. ontology_version stored as table property and on every audit event. ATT&CK bridge: ops.attack_version_bridge from STIX revoked-by; bridged edges confidence 0.9, prop bridged=true.
