# config/

Runtime configuration. `base.yaml` is environment independent; `local.yaml` and `cloudera.yaml` hold endpoints and adapter names. Secrets are never here: YAML names an environment variable and the adapter reads it. `synthetic/` holds the Bureau of Synthetic Records definitions (Phase 3).
