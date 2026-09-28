# oag-lakehouse. Targets from CLAUDE.md. Later targets are stubs until their phase lands.
.PHONY: lint test config generate up-phase1 up eval replay sync

UV ?= uv

sync:
	$(UV) sync --all-extras

lint:
	$(UV) run ruff check .
	$(UV) run ruff format --check .
	$(UV) run detect-secrets-hook --baseline .secrets.baseline $$(git ls-files)
	$(UV) run python tools/check_emdash.py
	$(UV) run python tools/check_hosted_import.py

test:
	$(UV) run pytest

config:
	$(UV) run python -m agent.config --env $${OAG_ENV:-local}

generate:
	@echo "make generate: LinkML generators land in Phase 2 (PLAN.md)." && exit 1

up-phase1:
	@echo "make up-phase1: Compose foundation profile lands in Phase 1 (PLAN.md)." && exit 1

up:
	@echo "make up: all Compose profiles land by Phase 4 (PLAN.md)." && exit 1

eval:
	@echo "make eval: the competency question suite lands in Phase 4 (PLAN.md)." && exit 1

replay:
	@echo "make replay: tools/replay.py lands in Phase 4 (PLAN.md)." && exit 1
