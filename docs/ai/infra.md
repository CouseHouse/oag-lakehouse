# Infrastructure (SPEC.md section 19, 8.4, 22)

Versions checked 2026-09-26; pin in infra/local/.env; verify tags at phase start.

## Compose services (profile: image; host ports; notes)

foundation: ozone-scm/om/datanode/s3g/recon apache/ozone:2.2.1; 9876, 9874, 9882, 9878 (S3), 9888 (Recon); replication 1; bucket oag-warehouse | polaris apache/polaris:1.7.0; 8181; catalog created --storage-type s3 --endpoint http://ozone-s3g:9878 --no-sts --path-style-access; no credential vending | spark-master/worker apache/spark:3.5.x-python3 (Q08); 7077, 8080, worker UI 8083; jars iceberg-spark-runtime-3.5 1.11.0, hadoop-aws, spark-xml | trino trinodb/trino:483; 8443; iceberg.catalog.type=rest, rest-catalog.uri http://polaris:8181/api/catalog, security OAUTH2, vended-credentials-enabled=false
ingest: nifi apache/nifi:2.12.0; 8444→8443; mounts tools (syft, grype), python | airflow-webserver/scheduler apache/airflow:2.11.x-python3.12 (Q09); 8082; airflow-db postgres:17
graph: pgvector pgvector/pgvector:0.8.6-pg17; 5432 | age apache/age:release_PG17_1.7.0; 5433 | puppygraph puppygraph/puppygraph:1.12.0; 8081 UI/REST, 7687 Bolt, 8182 Gremlin; default creds puppygraph/puppygraph123 (change)
agent: langfuse-web langfuse/langfuse:4; 3000 | langfuse-worker langfuse/langfuse-worker:4 | langfuse-db postgres:17 | clickhouse clickhouse/clickhouse-server:25.12 | redis redis:7 maxmemory-policy noeviction | blob store = Ozone bucket langfuse (Q06; fallback MinIO) | agent-api project image py3.12 FastAPI LangGraph 1.2.x; 8090 | approval-ui; 8091
governance (Phase 7): ranger apache/ranger:2.9.0; 6080 + ranger-db
Startup: ozone (scm→om→datanode→s3g,recon) → polaris → postgres → spark, trino, nifi, airflow → puppygraph → langfuse (clickhouse, redis first) → agent-api. depends_on condition service_healthy.
Sizing: Phase 1 8 vCPU/24 GB; full stack min 48 GB RAM/500 GB, recommended 16 vCPU/96 GB/1 TB NVMe. Phase 1 may run in WSL2 on the workstation.

## Spark catalog config

spark.sql.catalog.oag=org.apache.iceberg.spark.SparkCatalog; .type=rest; .uri=http://polaris:8181/api/catalog; .warehouse=oag-warehouse; .credential=<id>:<secret>; .scope=PRINCIPAL_ROLE:ALL; s3 endpoint/keys/path-style set on the catalog io; no vended credentials.

## vLLM on the workstation (WSL2, RTX 5090 32 GB)

Primary mistralai/Ministral-3-14B-Instruct-2512 (official FP8, Apache 2.0, 256k ctx). Fallback RedHatAI/Mistral-Small-3.2-24B-Instruct-2506-FP8 (batch only, max-num-seqs 4, max-model-len 32768). Benchmark FP8 vs AWQ under WSL2 first (Q07).
docker run --gpus all -p 8000:8000 -v /mnt/models:/root/.cache/huggingface:ro -e VLLM_API_KEY vllm/vllm-openai:v0.30.0 --model mistralai/Ministral-3-14B-Instruct-2512 --revision <sha> --served-model-name oag-primary --tokenizer_mode mistral --config_format mistral --load_format mistral --enable-auto-tool-choice --tool-call-parser mistral --max-model-len 65536 --kv-cache-dtype fp8 --gpu-memory-utilization 0.90 --max-num-seqs 16 --max-num-batched-tokens 8192 --limit-mm-per-prompt '{"image":0}' --structured-outputs-config.backend xgrammar
Verify flags against vLLM 0.30 CLI. CUDA ≥12.9 image variant if 13.0 fails. Embeddings: BAAI/bge-m3 on port 8001 (--task embed, gpu util 0.08) or CPU sentence-transformers.
WSL2 networking: .wslconfig networkingMode=mirrored, else netsh portproxy + firewall rule. Config model.base_url http://<workstation-ip>:8000/v1.

## Config keys (config/base.yaml + config/<env>.yaml; secrets = env var names)

storage.endpoint_url, bucket, region, path_style | catalog.uri, warehouse, auth.type (oauth2|bearer|kerberos-via-knox), namespace_prefix | graph.uri (bolt://), user, dialect (puppygraph|age), pg_dsn | vector.dsn, table, dim | model.base_url, name, api_key_env, structured_output_mode (response_format|guided_json), nim_nvext_wrapper, max_context, hosted.enabled=false | embedding.base_url, model, dim | sql.host, port, catalog, auth | trace.host, public_key_env, secret_key_env | actions.bucket, prefix, git_repo, approval_roles, enabled | retrieval.enabled | extraction.auto_publish | airflow.spark_backend (local|cde), connections.* | base: ontology_version, prompt_version, rule_version, temperature, token_budget, gpu_price_per_token
Startup prints resolved config redacted; missing required key → refuse to start.

## Ports (agent/ports/) and adapters (agent/adapters/)

StoragePort → S3Storage | CatalogPort → RestCatalog (pyiceberg) | GraphPort → BoltGraph (neo4j driver), AgeGraph | VectorPort → PgVector | ModelPort → OpenAICompatModel, NimModel(subclass), HostedModel (eval only) | EmbeddingPort | SqlPort → TrinoSql (ImpalaSql future) | TracePort → Langfuse (OTLP future) | ActionSinkPort → S3ActionSink (GrcActionSink future)

## Cloudera mapping (config-only target)

Ozone/S3 → storage.* | Cloudera Iceberg REST catalog or Polaris (Knox/OAuth2) → catalog.* | CDE 1.26 Spark 3.5.4 → airflow.spark_backend=cde, jobs unchanged | CDF NiFi 2.x → import flow JSON, parameter context cloudera | CDE Airflow 2.11.2 → same DAGs | CDW Trino/Impala → sql.* | PuppyGraph → generated/puppygraph/schema.cloudera.json | pgvector or platform store → vector.* | Cloudera AI Inference (NIM) → model.* guided_json | Workbench app → agent | Langfuse on Workbench or OTLP → trace.*. Checklist SPEC.md 22.2 (12 items).
