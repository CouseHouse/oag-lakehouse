"""Config loader tests (SPEC.md section 8.4)."""

from pathlib import Path

import pytest

from agent.config import ConfigError, load_config, referenced_env_vars

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
FAKE_ENV = {
    "OAG_S3_ACCESS_KEY": "ak",
    "OAG_S3_SECRET_KEY": "sk",  # pragma: allowlist secret
    "PGVECTOR_PASSWORD": "pgv-secret",  # pragma: allowlist secret
    "AGE_PASSWORD": "age-secret",  # pragma: allowlist secret
}


@pytest.mark.parametrize("env", ["local", "cloudera"])
def test_each_env_loads_and_validates(env: str) -> None:
    cfg = load_config(env, directory=CONFIG_DIR, environ=FAKE_ENV)
    assert cfg.env == env
    assert cfg.model.structured_output_mode in {"response_format", "guided_json"}
    assert cfg.model.hosted.enabled is False


def test_base_values_are_overlaid_by_env() -> None:
    local = load_config("local", directory=CONFIG_DIR, environ=FAKE_ENV)
    cloudera = load_config("cloudera", directory=CONFIG_DIR, environ=FAKE_ENV)
    assert local.model.structured_output_mode == "response_format"
    assert cloudera.model.structured_output_mode == "guided_json"
    assert local.ontology_version == cloudera.ontology_version


def test_secrets_are_expanded_then_redacted() -> None:
    cfg = load_config("local", directory=CONFIG_DIR, environ=FAKE_ENV)
    assert "pgv-secret" in cfg.vector.dsn
    dumped = str(cfg.redacted())
    assert "pgv-secret" not in dumped
    assert "age-secret" not in dumped
    assert "***" in dumped


def test_missing_secret_is_tolerated_unless_required() -> None:
    cfg = load_config("local", directory=CONFIG_DIR, environ={})
    assert "${" not in cfg.vector.dsn
    with pytest.raises(ConfigError, match="PGVECTOR_PASSWORD"):
        load_config("local", directory=CONFIG_DIR, environ={}, require_secrets=True)


def test_unknown_env_fails() -> None:
    with pytest.raises(ConfigError, match="does not exist"):
        load_config("staging", directory=CONFIG_DIR, environ=FAKE_ENV)


def test_missing_required_key_fails(tmp_path: Path) -> None:
    (tmp_path / "base.yaml").write_text((CONFIG_DIR / "base.yaml").read_text())
    (tmp_path / "broken.yaml").write_text("storage:\n  bucket: only-a-bucket\n")
    with pytest.raises(ConfigError, match="storage.endpoint_url"):
        load_config("broken", directory=tmp_path, environ=FAKE_ENV)


@pytest.mark.parametrize("env", ["local", "cloudera"])
def test_every_referenced_env_var_is_listed_in_env_example(env: str) -> None:
    cfg = load_config(env, directory=CONFIG_DIR, environ=FAKE_ENV)
    example = (CONFIG_DIR.parent / ".env.example").read_text()
    declared = {line.split("=", 1)[0] for line in example.splitlines() if "=" in line}
    missing = [name for name in referenced_env_vars(cfg) if name not in declared]
    assert not missing, f"add to .env.example: {missing}"
