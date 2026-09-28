# ADR-0025: project extractor is primary; OntoGPT is a comparison only

Status: accepted 2026-09-28. SPEC.md section 11.2 finding.

## Context

OntoGPT 1.2.0 (commit 9224d33, 2026-09-10) implements SPIRES, the schema-driven extraction
method this project follows. Its source was read to decide whether to depend on it.

## Decision

The project's own extractor in `agent/extract/` is the extraction path: LinkML template,
project prompt, JSON schema structured output through `ModelPort`, parse to the generated
Pydantic model, span-level grounding with confidence. OntoGPT runs only under `evals/` as a
Phase 5 comparison, driven by a `ModelPort`-backed object with a `complete(prompt) -> str`
method rather than its LiteLLM client. The three templates in `schema/extract/` use OntoGPT's
template conventions so it can run them unchanged.

## Consequences

Why not primary: no structured output (pseudo-YAML prompt and parser), `sys.exit` on API
errors inside the bundled client, a default identifier mapper that calls the NCATS Translator
web service plus a process-global LiteLLM disk cache, grounding on model output strings rather
than source spans with no confidence levels, and about 27 direct dependencies in the agent
image and AI BOM. What is kept: the template conventions (`prompt`, `annotators`, `examples`,
`id_prefixes`, `AUTO:` prefix) and the rule that ungrounded mentions are proposals.
