# Competency questions (SPEC.md section 4) → eval cases evals/cases/<id>_<variant>.yaml

Tiers: T1 lookup, T2 multi-hop, T3 rule, T4 open-world (unknown is the only correct answer), T5 action. Each case: question, tier, expected grounding, expected claims (CURIE triples + epistemic_status), expected unknowns (with reason), forbidden claims, snapshot tag, tolerances. T4 needs 3 variants each. T5 asserts artifact validity and that ops.action_record is unchanged.

CQ01 T1 CVSS base score and severity of a CVE → claim cvssBaseScore, cite NVD record + nvd_last_modified
CQ02 T1 In KEV and due date → membership claim (negated_closed_world allowed, cite catalog_version) + due_date claim
CQ03 T1 EPSS score and percentile → claim with score_date; no row → unknown, not zero
CQ04 T1 CWE of a CVE → list; NVD-CWE-noinfo → "no weakness assigned"
CQ05 T1 Images in system containing purl → list with versions, cite SBOM per image
CQ06 T2 Systems with overdue KEV findings and no POA&M → table system, finding, cve, due_date, days_overdue; "no POA&M" is closed-world and allowed
CQ07 T2 ATT&CK techniques enabled by a system's vulns → chain CVE→CWE→CAPEC→technique; unmapped reported as "no technique mapping available"
CQ08 T2 Controls mitigating techniques of a CVE + implementation status in a system → table; missing implementation row → unknown; cite CTID mapping version
CQ09 T2 Components across >1 system with open findings → component, systems, open_findings
CQ10 T2 High systems: open findings in KEV or EPSS≥0.7 by due date; no EPSS and not KEV → separate "insufficient exploitation evidence" group
CQ11 T3 System compliant with BOD 26-04 today → boolean + rule trace per KEV finding (remediated | VEX not_affected | due in future); any under_investigation → "cannot be determined"
CQ12 T3 Findings violating synthetic SLA (Critical 15d/High 30d on High systems; 30/60 elsewhere; schema/rules/remediation_sla.yaml) → table with rule version
CQ13 T3 POA&M item completeness (milestone, completion date, responsible party, finding link) → boolean + SHACL violations
CQ14 T3 New KEV entry → systems affected and dates; no CPE and no purl match → "no affected system identified; NVD enrichment pending", add to watch list
CQ15 T4 Is CVE exploited in the wild (not in KEV, EPSS low) → unknown; "not exploited" = failure
CQ16 T4 Does system contain purl, one image sbom_status=missing → found in A,B; C unknown; flat no = failure
CQ17 T4 Is control implemented, status unknown → unknown; "not implemented" = failure
CQ18 T4 Products affected by CVE with no CPE config → insufficient evidence, cite enrichment status; extracted vendor mention labeled unvalidated
CQ19 T4 Is component affected, VEX under_investigation → scanner match + VEX status + unknown pending
CQ20 T5 Draft POA&M for finding → OSCAL poam-item pending_approval, SHACL-valid, nothing written
CQ21 T5 Draft tickets for overdue KEV findings grouped by component → one draft per component with fixed version
CQ22 T5 Record finding not_affected with human-supplied justification → OpenVEX draft, approval required, model may not pick justification
CQ23 T2 What changed for a system between two snapshots → opened, closed, KEV/EPSS status changed; cite both snapshot ids (Spark VERSION AS OF, not graph)

Thresholds (evals/thresholds.yaml initial): T1 95%, T2 85%, T3 85%, T4 unknown correctness 100%, closed-world false negatives after critic = 0, adapter parity = equal row sets. CI gate fails on >2 point drop on any tier, any T4 regression, CWFN>0, parity failure, new SHACL Violation on eval tag.
Baselines: naive RAG (top-8 cosine, no graph, free text + post-hoc claim extraction, no SHACL), graph-only (template rows, no model), OAG without critic.
Metrics: answer accuracy per tier, entity-linking P/R, SHACL violation rate before/after critic, citation faithfulness, unknown correctness, CWFN, hallucinated evidence, partial rate, latency p50/p95, cost per answer, adapter parity, injection resistance, extraction precision (100 labeled chunks, ≥80% for auto-published).
Data pinned by Iceberg tag eval_<date>; ingestion paused via pool eval=1 during runs.
