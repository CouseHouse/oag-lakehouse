# AI reference index

Compact, task-scoped extracts of SPEC.md. Load only what the task needs. Each file names the
SPEC.md sections it summarizes; go there for rationale or detail. Keep these files in sync with
SPEC.md in the same commit.

| Task | Load |
|---|---|
| Schema, classes, enums, closure, CURIEs, generators | ontology.md |
| Iceberg tables, columns, partitions, WAP | tables.md |
| NiFi flows, Spark jobs, Airflow DAGs | pipelines.md |
| Grounding, retrieval, generation schema, critic, LangGraph nodes | agent.md |
| Action drafting, approval, roles, sinks, security rules and actions | actions-security.md |
| Compose services, versions, ports, config keys, vLLM launch | infra.md |
| Competency questions and expected answer shapes (eval cases) | cqs.md |
| Decisions and open questions | decisions.md |

Always loaded: CLAUDE.md (rules and conventions).
