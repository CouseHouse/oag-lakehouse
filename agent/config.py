"""Configuration loader (SPEC.md section 8.4).

Merges ``config/base.yaml`` with ``config/<env>.yaml`` (``OAG_ENV=local|cloudera``),
expands ``${VAR}`` references from the process environment, validates required keys, and
prints the result with every expanded secret redacted. No endpoint, bucket, model name, or
secret is defined in code.

Run ``python -m agent.config --env local`` to print the resolved, redacted config.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

ENV_VAR_NAME = "OAG_ENV"
DEFAULT_ENV = "local"
REDACTED = "***"
_REF = re.compile(r"\$\{([A-Z][A-Z0-9_]*)\}")


class ConfigError(RuntimeError):
    """Raised when the configuration cannot be loaded or is incomplete."""


class _Section(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)


class StorageConfig(_Section):
    endpoint_url: str
    bucket: str
    region: str
    path_style: bool
    access_key_env: str
    secret_key_env: str


class CatalogAuth(_Section):
    type: Literal["oauth2", "bearer", "kerberos-via-knox"]


class CatalogConfig(_Section):
    uri: str
    warehouse: str
    auth: CatalogAuth
    namespace_prefix: str = ""


class GraphConfig(_Section):
    uri: str
    user: str
    dialect: Literal["puppygraph", "age"]
    pg_dsn: str | None = None


class VectorConfig(_Section):
    dsn: str
    table: str
    dim: int


class HostedModelConfig(_Section):
    enabled: bool = False


class ModelConfig(_Section):
    base_url: str
    name: str
    api_key_env: str
    structured_output_mode: Literal["response_format", "guided_json"]
    nim_nvext_wrapper: bool = False
    max_context: int
    hosted: HostedModelConfig = Field(default_factory=HostedModelConfig)


class EmbeddingConfig(_Section):
    base_url: str
    model: str
    dim: int


class SqlConfig(_Section):
    host: str
    port: int
    catalog: str
    auth: Mapping[str, Any]


class TraceConfig(_Section):
    host: str
    public_key_env: str
    secret_key_env: str


class ActionsConfig(_Section):
    bucket: str
    prefix: str
    git_repo: str
    approval_roles: list[str]
    enabled: bool


class RetrievalConfig(_Section):
    enabled: bool


class ExtractionConfig(_Section):
    auto_publish: bool


class AirflowConfig(_Section):
    spark_backend: Literal["local", "cde"]
    connections: Mapping[str, str]


class Config(BaseModel):
    """The resolved configuration. Every field is required unless it has a default."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    env: str
    ontology_version: str
    prompt_version: str
    rule_version: str
    temperature: float
    token_budget: int
    gpu_price_per_token: float
    storage: StorageConfig
    catalog: CatalogConfig
    graph: GraphConfig
    vector: VectorConfig
    model: ModelConfig
    embedding: EmbeddingConfig
    sql: SqlConfig
    trace: TraceConfig
    actions: ActionsConfig
    retrieval: RetrievalConfig
    extraction: ExtractionConfig
    airflow: AirflowConfig
    secret_values: frozenset[str] = Field(default_factory=frozenset, exclude=True, repr=False)
    """Values expanded from the environment; used only to redact output."""

    def redacted(self) -> dict[str, Any]:
        """Return the config as a plain dict with expanded secrets replaced."""
        return _redact(self.model_dump(mode="json"), self.secret_values)


def config_dir() -> Path:
    """The ``config/`` directory next to this package, overridable with ``OAG_CONFIG_DIR``."""
    override = os.environ.get("OAG_CONFIG_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent.parent / "config"


def load_config(
    env: str | None = None,
    *,
    directory: Path | None = None,
    environ: Mapping[str, str] | None = None,
    require_secrets: bool = False,
) -> Config:
    """Load, merge, expand, and validate the configuration for ``env``.

    ``environ`` defaults to ``os.environ``. With ``require_secrets`` every ``${VAR}`` must be
    set; otherwise an unset variable expands to an empty string and is reported by ``check``.
    """
    environ = os.environ if environ is None else environ
    env = env or environ.get(ENV_VAR_NAME, DEFAULT_ENV)
    directory = directory or config_dir()
    base = _read_yaml(directory / "base.yaml")
    overlay_path = directory / f"{env}.yaml"
    if not overlay_path.exists():
        raise ConfigError(f"no config for env {env!r}: {overlay_path} does not exist")
    merged = _deep_merge(base, _read_yaml(overlay_path))
    merged["env"] = env
    expanded, secrets, missing = _expand(merged, environ)
    if missing and require_secrets:
        raise ConfigError("unset environment variables: " + ", ".join(sorted(missing)))
    try:
        return Config(**expanded, secret_values=frozenset(secrets))
    except ValidationError as exc:
        raise ConfigError(_format_validation_error(env, exc)) from exc


def referenced_env_vars(cfg: Config) -> list[str]:
    """Every environment variable the config names, by ``*_env`` key or ``${VAR}`` reference."""
    names: set[str] = set()

    def walk(node: Any) -> None:
        if isinstance(node, Mapping):
            for key, value in node.items():
                if isinstance(key, str) and key.endswith("_env") and isinstance(value, str):
                    names.add(value)
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(cfg.model_dump(mode="json"))
    raw_dir = config_dir()
    for path in (raw_dir / "base.yaml", raw_dir / f"{cfg.env}.yaml"):
        if path.exists():
            names.update(_REF.findall(path.read_text()))
    return sorted(names)


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConfigError(f"missing config file: {path}")
    with path.open() as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ConfigError(f"{path} must contain a mapping at the top level")
    return data


def _deep_merge(base: Mapping[str, Any], overlay: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = dict(base)
    for key, value in overlay.items():
        if isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _expand(node: Any, environ: Mapping[str, str]) -> tuple[Any, set[str], set[str]]:
    secrets: set[str] = set()
    missing: set[str] = set()

    def sub(value: Any) -> Any:
        if isinstance(value, str):

            def repl(match: re.Match[str]) -> str:
                name = match.group(1)
                found = environ.get(name)
                if found is None or found == "":
                    missing.add(name)
                    return ""
                secrets.add(found)
                return found

            return _REF.sub(repl, value)
        if isinstance(value, Mapping):
            return {k: sub(v) for k, v in value.items()}
        if isinstance(value, list):
            return [sub(v) for v in value]
        return value

    return sub(node), secrets, missing


def _redact(node: Any, secrets: frozenset[str]) -> Any:
    if isinstance(node, str):
        for secret in secrets:
            if secret and secret in node:
                node = node.replace(secret, REDACTED)
        return node
    if isinstance(node, dict):
        return {k: _redact(v, secrets) for k, v in node.items()}
    if isinstance(node, list):
        return [_redact(v, secrets) for v in node]
    return node


def _format_validation_error(env: str, exc: ValidationError) -> str:
    lines = [f"config for env {env!r} is invalid:"]
    for err in exc.errors():
        loc = ".".join(str(p) for p in err["loc"]) or "<root>"
        lines.append(f"  {loc}: {err['msg']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m agent.config",
        description="Print the resolved configuration with secrets redacted.",
    )
    parser.add_argument(
        "--env",
        default=None,
        help=f"environment name (default: ${ENV_VAR_NAME}, else {DEFAULT_ENV})",
    )
    parser.add_argument(
        "--require-secrets",
        action="store_true",
        help="fail if any referenced environment variable is unset (use at service start)",
    )
    args = parser.parse_args(argv)
    try:
        cfg = load_config(args.env, require_secrets=args.require_secrets)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(yaml.safe_dump(cfg.redacted(), sort_keys=False))
    unset = [name for name in referenced_env_vars(cfg) if not os.environ.get(name)]
    status = "all set" if not unset else "unset: " + ", ".join(unset)
    print(f"# env vars referenced: {len(referenced_env_vars(cfg))}; {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
