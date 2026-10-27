# 6. YAML pipeline registry and `agents` CLI

Date: 2026-10-27
Status: Accepted

## Context

The CrewAI track had one hard-coded chain (topic → design → Dockerfile → audit). We want several use cases (audit real projects, later PR review, CI generation) without new Python per use case, and a CLI usable from other repos.

## Decision

- Pipelines live in `src/agent_framework/pipelines.yaml`: each has an `input` kind (`topic` or `project`) and ordered steps (role, goal, backstory, task, expected_output, output file, context).
- `registry.py` validates them (context may only point to earlier steps). `AgentFactory.create(step)` and `TaskFactory.create(step, ...)` are generic.
- `project` pipelines get the target's files inlined as `{project_files}` (`project.py`), with line numbers and size limits, skipping `.git`, `.env`, lock files and `KNOWN_ISSUES.md`. Agents still have no tools (ADR 0003).
- CLI: `agents list`, `agents run <pipeline> [topic] [--project PATH] [--model M] [-v]`. `run-agents` stays as an alias for `agents run generate`.
- Default `max_tokens` raised to 4096: at 2048 Gemma's reasoning used the whole budget and returned empty answers.

## Consequences

- New use case = YAML only.
- Inlining files caps project size (~60 KB). Larger repos need file selection or tools.
- Artifacts are written to `./output/` relative to the current directory, so running from another repo writes there.
